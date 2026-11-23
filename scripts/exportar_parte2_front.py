"""Exporta para o front os casos da Parte 2 já calculados (fontes, pares e recortes do grafo).

Uso (na raiz do repositório):
    python -m scripts.exportar_parte2_front

Lê os JSONs gerados por src/casos_parte2.py em out/parte2/ (BFS, DFS, Dijkstra e Bellman-Ford),
o benchmark (out/parte2/parte2_report.json) e a classe de cada carteira (data/dataset_parte2/nos.csv),
e grava front-react/src/parte2.json. Nenhum algoritmo roda aqui: o arquivo só reorganiza os
resultados e recorta, para cada caso, um subgrafo pequeno o bastante para desenhar na tela.
"""
# [IA] Claude Code – reorganiza em JSON os resultados da Parte 2 para o front (IO, sem algoritmo)
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RESULTADOS = RAIZ / "out" / "parte2"
NOS = RAIZ / "data" / "dataset_parte2" / "nos.csv"
ARESTAS = RAIZ / "data" / "dataset_parte2" / "arestas.csv"
SAIDA = RAIZ / "front-react" / "src" / "parte2.json"
LIMITE_NOS = 40  # máximo de carteiras desenhadas por caso de BFS/DFS
LIMITE_REDE = 150  # carteiras na amostra em várias camadas (grafo interativo)
FILHOS_POR_CAMADA = (8, 4, 3, 2)  # filhos escolhidos por carteira, da origem para as camadas seguintes


def _ler(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def recorte_bfs(resultado: dict, limite: int = LIMITE_NOS) -> dict:
    """Primeiras carteiras da BFS, camada por camada, e os arcos da árvore entre elas."""
    nos: list[str] = []
    for camada in resultado["camadas"]:
        for no in camada:
            if len(nos) == limite:
                break
            nos.append(no)
    dentro = set(nos)
    arcos = [[u, v] for u, v in resultado["arvore"] if u in dentro and v in dentro]
    nivel = {no: resultado["distancia"][no] for no in nos}
    return {"nos": nos, "nivel": nivel, "arcos": arcos, "completo": len(nos) == resultado["alcancados"]}


# [IA] Claude Code – amostra da árvore BFS em várias camadas e arcos do dataset entre as carteiras escolhidas
def rede_bfs(resultado: dict, limite: int = LIMITE_REDE, por_pai: tuple[int, ...] = FILHOS_POR_CAMADA) -> dict:
    """Amostra da árvore BFS que desce várias camadas: cada carteira escolhida leva poucos filhos,
    primeiro os que também têm filhos, para o desenho mostrar a profundidade da rede e não só a camada 1."""
    filhos: dict[str, list[str]] = {}
    for u, v in resultado["arvore"]:
        filhos.setdefault(u, []).append(v)
    nos = [resultado["origem"]]
    fronteira = list(nos)
    camada = 0
    while fronteira and len(nos) < limite:
        k = por_pai[min(camada, len(por_pai) - 1)]
        proxima = []
        for pai in fronteira:
            candidatos = sorted(filhos.get(pai, []), key=lambda n: -len(filhos.get(n, [])))
            for filho in candidatos[:k]:
                if len(nos) == limite:
                    break
                nos.append(filho)
                proxima.append(filho)
        fronteira = proxima
        camada += 1
    dentro = set(nos)
    arvore = [[u, v] for u, v in resultado["arvore"] if u in dentro and v in dentro]
    return {"nos": nos, "nivel": {no: resultado["distancia"][no] for no in nos}, "arvore": arvore}


def arcos_entre(nos: list[str], arestas: pd.DataFrame, arvore: list[list[str]]) -> list[list[str]]:
    """Arcos do dataset entre as carteiras da amostra que não são arcos da árvore BFS (sem repetir pares)."""
    dentro = set(nos)
    ja = {tuple(a) for a in arvore}
    sel = arestas[arestas["origem"].isin(dentro) & arestas["destino"].isin(dentro)]
    outros = []
    for u, v in zip(sel["origem"], sel["destino"]):
        if u != v and (u, v) not in ja:
            ja.add((u, v))
            outros.append([u, v])
    return outros


def caso_busca(bfs: dict, dfs: dict, limite: int = LIMITE_NOS) -> dict:
    """Resumo de uma fonte: tamanho das camadas da BFS, arcos da DFS e o recorte para desenhar."""
    if bfs["origem"] != dfs["origem"]:
        raise ValueError(f"BFS e DFS com origens diferentes: {bfs['origem']} e {dfs['origem']}")
    return {
        "origem": bfs["origem"],
        "total_nos": bfs["total_nos"],
        "alcancados": bfs["alcancados"],
        "tamanho_camadas": [len(c) for c in bfs["camadas"]],
        "dfs": {
            "alcancados": dfs["alcancados"],
            "contagem_arcos": dfs["contagem_arcos"],
            "tem_ciclo": dfs["tem_ciclo"],
            "ordem_inicio": dfs["ordem"][:limite],
        },
        "recorte": recorte_bfs(bfs, limite),
    }


def caso_dijkstra(resultado: dict) -> dict:
    return {chave: resultado[chave] for chave in ("origem", "destino", "custo", "passos", "caminho", "arcos")}


def caso_bellman_ford(resultado: dict) -> dict:
    """Com ciclo negativo, o ciclo; sem ciclo, a árvore de caminhos mínimos (todos os alcançados)."""
    caso = {chave: resultado[chave] for chave in ("origem", "total_nos", "alcancados", "status", "tem_ciclo_negativo")}
    if resultado["tem_ciclo_negativo"]:
        caso.update(
            ciclo=resultado["ciclo_negativo"], arcos=resultado["arcos_ciclo"], custo_ciclo=resultado["custo_ciclo"]
        )
    else:
        pai = resultado["pai"]
        caso.update(
            arcos_negativos_alcancaveis=resultado["arcos_negativos_alcancaveis"],
            distancia=resultado["distancia"],
            arcos=[[p, no] for no, p in pai.items() if p is not None],
        )
    return caso


def carteiras_usadas(dados: dict) -> set[str]:
    nos: set[str] = set()
    for caso in dados["buscas"]:
        nos.update(caso["recorte"]["nos"])
        nos.update(caso.get("rede", {}).get("nos", []))
    for caso in dados["dijkstra"]:
        nos.update(caso["caminho"])
    for caso in dados["bellman_ford"]:
        nos.update(caso.get("ciclo", []))
        nos.update(caso.get("distancia", {}))
        nos.add(caso["origem"])
    return nos


def tempos(relatorio: list[dict]) -> list[dict]:
    """Linhas do benchmark no grafo inteiro (fração 1.0)."""
    campos = ("algoritmo", "nos", "arestas", "complexidade", "alcancados", "status", "tempo_medio_ms",
              "latencia_min_ms", "latencia_max_ms", "memoria_pico_kb")
    return [{c: linha.get(c) for c in campos} for linha in relatorio if linha.get("fracao") == 1.0]


def montar(pasta: Path = RESULTADOS, nos_csv: Path = NOS, limite: int = LIMITE_NOS,
           arestas_csv: Path | None = ARESTAS) -> dict:
    bfs = {r["origem"]: r for r in map(_ler, sorted(pasta.glob("bfs_*.json")))}
    dfs = {r["origem"]: r for r in map(_ler, sorted(pasta.glob("dfs_*.json")))}
    if not bfs:
        raise FileNotFoundError(f"Nenhum bfs_*.json em {pasta}. Rode antes os casos da Parte 2 (src/casos_parte2.py).")
    if set(bfs) != set(dfs):
        raise ValueError(f"Fontes de BFS e DFS não batem: {sorted(set(bfs) ^ set(dfs))}")

    dados = {
        "buscas": [caso_busca(bfs[o], dfs[o], limite) for o in sorted(bfs)],
        "dijkstra": [caso_dijkstra(_ler(c)) for c in sorted(pasta.glob("dijkstra_*.json"))],
        "bellman_ford": [caso_bellman_ford(_ler(c)) for c in sorted(pasta.glob("bellman_ford_*.json"))],
    }
    if arestas_csv is not None and Path(arestas_csv).is_file():
        arestas = pd.read_csv(arestas_csv, usecols=["origem", "destino"], dtype=str)
        for caso in dados["buscas"]:
            rede = rede_bfs(bfs[caso["origem"]])
            caso["rede"] = {**rede, "outros": arcos_entre(rede["nos"], arestas, rede["arvore"])}
    relatorio = pasta / "parte2_report.json"
    dados["tempos"] = tempos(_ler(relatorio)) if relatorio.is_file() else []

    usadas = carteiras_usadas(dados)
    classe = pd.read_csv(nos_csv, usecols=["endereco", "classe"], dtype=str).set_index("endereco")["classe"]
    faltando = sorted(usadas - set(classe.index))
    if faltando:
        raise ValueError(f"Carteiras fora de nos.csv: {faltando[:5]}")
    dados["classe"] = {no: classe[no] for no in sorted(usadas)}
    return dados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--resultados", type=Path, default=RESULTADOS, help="pasta com os JSONs da Parte 2")
    parser.add_argument("--nos", type=Path, default=NOS, help="nos.csv do recorte")
    parser.add_argument("--saida", type=Path, default=SAIDA, help="JSON gerado para o front")
    parser.add_argument("--limite", type=int, default=LIMITE_NOS, help="carteiras por recorte de BFS/DFS")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # acentos no terminal do Windows

    dados = montar(args.resultados, args.nos, args.limite)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    print(
        f"Gerado {args.saida} ({args.saida.stat().st_size // 1024} KB): {len(dados['buscas'])} fontes, "
        f"{len(dados['dijkstra'])} pares de Dijkstra, {len(dados['bellman_ford'])} casos de Bellman-Ford, "
        f"{len(dados['classe'])} carteiras."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
