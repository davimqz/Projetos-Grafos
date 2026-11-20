"""Matriz de contribuição: commits de cada integrante por pacote, a partir do git.

Uso (na raiz do repositório):
    python -m scripts.matriz_contribuicao                  # conta em origin/main
    python -m scripts.matriz_contribuicao --ref main
    python -m scripts.matriz_contribuicao --revisoes       # inclui quem revisou/mergeou PRs (precisa do gh)

Um commit conta uma vez em cada pacote cujos arquivos ele altera. Merges não contam.
A saída é uma tabela Markdown pronta para a seção 10.2 do relatório.
"""
# [IA] Claude Code – contagem de commits por pacote a partir do git (sem interpretação)
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from fnmatch import fnmatch

INTEGRANTES = ("Matheus", "Thomaz", "Davi", "Vagner")

# Nome do autor no git -> integrante.
AUTORES = {
    "Matheus Araujo": "Matheus",
    "Thomazrlima": "Thomaz",
    "Davi Marques Oliveira": "Davi",
    "Vagner Montenegro de Melo": "Vagner",
}
# Login do GitHub -> integrante (para as revisões de PR).
LOGINS = {
    "davimqz": "Davi", "MathhAraujo": "Matheus",
    "Thomazrlima": "Thomaz", "vagnermelo20": "Vagner",
}

PACOTES = ("P1", "P2", "P3", "P4a", "P4b", "P5a", "P5b", "P5c")

# Padrões testados na ordem; o primeiro que casar define o pacote do arquivo.
REGRAS: tuple[tuple[str, str], ...] = (
    ("src/graphs/io.py", "P1"), ("src/graphs/estados.py", "P1"),
    ("tests/test_io.py", "P1"), ("tests/test_estados.py", "P1"),
    ("src/graphs/graph.py", "P2"), ("src/graphs/algorithms.py", "P2"),
    ("tests/test_graph.py", "P2"), ("tests/test_bfs.py", "P2"), ("tests/test_dfs.py", "P2"),
    ("tests/test_dijkstra.py", "P2"), ("tests/test_bellman_ford.py", "P2"),
    ("src/solve.py", "P3"), ("src/parte1/*", "P3"), ("tests/parte1/*", "P3"),
    ("tests/test_solve.py", "P3"), ("tests/test_executar_parte1.py", "P3"), ("data/mapas_grupo/*", "P3"),
    ("out/parte1/*.csv", "P3"), ("out/parte1/*.json", "P3"),
    ("src/benchmark.py", "P4b"), ("tests/test_benchmark.py", "P4b"),
    ("scripts/figuras_benchmark.py", "P4b"), ("out/parte2/parte2_report.json", "P4b"),
    ("out/parte2/benchmark_*", "P4b"),
    ("notebooks/avd/*", "P5b"), ("out/parte2/avd/*", "P5b"),
    ("src/carga_parte2.py", "P4a"), ("src/casos_parte2.py", "P4a"),
    ("tests/test_carga_parte2.py", "P4a"), ("tests/test_casos_parte2.py", "P4a"),
    ("tests/test_graus_parte2.py", "P4a"), ("scripts/baixar_dataset.py", "P4a"),
    ("scripts/amostrar_dataset.py", "P4a"), ("scripts/graus_parte2.py", "P4a"),
    ("data/dataset_parte2/*", "P4a"), ("docs/PARTE2_DATASET.md", "P4a"),
    ("docs/relatorio/parte2.md", "P4a"), ("out/parte2/*", "P4a"),
    ("src/viz.py", "P5a"), ("src/visualizar_parte1.py", "P5a"), ("src/assets/*", "P5a"),
    ("tests/test_viz.py", "P5a"), ("tests/test_visualizar_parte1.py", "P5a"),
    ("tests/test_gerar_html_front.py", "P5a"), ("scripts/gerar_html_front.py", "P5a"),
    ("scripts/exportar_front.py", "P5a"), ("front-react/*", "P5a"),
    ("out/parte1/*", "P5a"),
    ("README.md", "P5c"), ("docs/*", "P5c"), ("scripts/gerar_pdf.py", "P5c"),
    ("scripts/matriz_contribuicao.py", "P5c"), ("tests/test_gerar_pdf.py", "P5c"),
    ("tests/test_matriz_contribuicao.py", "P5c"),
)


def pacote_do_arquivo(caminho: str) -> str | None:
    """Pacote de um arquivo, ou None para estrutura comum (CLI, requirements, .gitignore, mapas fornecidos)."""
    for padrao, pacote in REGRAS:
        if fnmatch(caminho, padrao):
            return pacote
    return None


def ler_commits(ref: str) -> list[tuple[str, list[str]]]:
    """(autor, arquivos alterados) de cada commit sem merge alcançável por ``ref``."""
    saida = subprocess.run(
        ["git", "log", ref, "--no-merges", "--format=\x01%an", "--name-only"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    commits = []
    for bloco in saida.split("\x01")[1:]:
        linhas = [linha for linha in bloco.splitlines() if linha.strip()]
        commits.append((linhas[0], linhas[1:]))
    return commits


def contar(commits: list[tuple[str, list[str]]]) -> tuple[dict[str, dict[str, int]], dict[str, int]]:
    """Commits por integrante e pacote, e total de commits por integrante."""
    matriz: dict[str, dict[str, int]] = {nome: defaultdict(int) for nome in INTEGRANTES}
    totais: dict[str, int] = defaultdict(int)
    for autor, arquivos in commits:
        nome = AUTORES.get(autor)
        if nome is None:
            raise ValueError(f"Autor desconhecido no git: {autor!r}. Inclua em AUTORES.")
        totais[nome] += 1
        for pacote in {pacote_do_arquivo(a) for a in arquivos} - {None}:
            matriz[nome][pacote] += 1
    return matriz, totais


def tabela_markdown(matriz: dict[str, dict[str, int]], totais: dict[str, int]) -> str:
    linhas = [
        "| Integrante | " + " | ".join(PACOTES) + " | Pacotes com commit | Commits |",
        "|---|" + "---|" * (len(PACOTES) + 2),
    ]
    for nome in INTEGRANTES:
        valores = [str(matriz[nome].get(p, "")) for p in PACOTES]
        n_pacotes = sum(1 for p in PACOTES if matriz[nome].get(p))
        linhas.append(f"| {nome} | " + " | ".join(valores) + f" | {n_pacotes} | {totais.get(nome, 0)} |")
    return "\n".join(linhas)


def ler_revisoes() -> dict[str, list[int]]:
    """PRs mergeados que cada integrante revisou ou mergeou sem ser o autor (via gh)."""
    saida = subprocess.run(
        ["gh", "pr", "list", "--state", "merged", "--limit", "200",
         "--json", "number,author,mergedBy,reviews"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    revisoes: dict[str, set[int]] = defaultdict(set)
    for pr in json.loads(saida):
        autor = pr["author"]["login"]
        logins = {r["author"]["login"] for r in pr.get("reviews") or []}
        if pr.get("mergedBy"):
            logins.add(pr["mergedBy"]["login"])
        for login in logins - {autor}:
            if login in LOGINS:  # ignora bots de revisão automática
                revisoes[LOGINS[login]].add(pr["number"])
    return {nome: sorted(numeros) for nome, numeros in revisoes.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", default="origin/main", help="branch ou commit a contar (padrão: origin/main)")
    parser.add_argument("--revisoes", action="store_true", help="lista os PRs revisados por integrante (gh)")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # acentos no terminal do Windows

    matriz, totais = contar(ler_commits(args.ref))
    print(tabela_markdown(matriz, totais))
    if args.revisoes:
        print()
        for nome, numeros in sorted(ler_revisoes().items()):
            print(f"- {nome}: " + ", ".join(f"#{n}" for n in numeros))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
