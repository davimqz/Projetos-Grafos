"""Imprime em Markdown as tabelas factuais da seção 4 do relatório, lidas das saídas em out/parte1/.

Uso (na raiz do repositório):
    python -m scripts.tabelas_relatorio_parte1            # todas as tabelas
    python -m scripts.tabelas_relatorio_parte1 4.4 4.8    # só algumas seções

Só copia números que o código do grupo já gravou (metricas_global.json, camadas.json, comparacao_modelagem.csv,
solucoes.csv, dfs_classificacao.csv, armadilhas_<mapa>.csv, ciclo_negativo_m06.json, comparacao_bonus_m05.json).
Nenhum algoritmo roda aqui e nenhum texto de análise é gerado: os comentários de cada tabela são do grupo.
"""
# [IA] Claude Code – leitura das saídas da Parte 1 e formatação das tabelas em Markdown (IO, sem análise)
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "out" / "parte1"
MAPAS = ["m01", "m02", "m03", "m04", "m05", "m06", "m07", "m08", "g01_tres_depositos", "g02_poco_lateral"]


def _json(nome: str):
    return json.loads((OUT / "json" / nome).read_text(encoding="utf-8"))


def _csv(nome: str) -> list[dict]:
    with (OUT / "csv" / nome).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _n(v, casas: int = 4) -> str:
    if v is None or v == "":
        return "—"
    if isinstance(v, float):
        return f"{v:.{casas}f}".replace(".", ",")
    return str(v)


def _tabela(cab: list[str], linhas: list[list]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    # Rótulos de estado ficam entre crases: o conversor do PDF (Python-Markdown) não divide a célula nesse "|".
    out += ["| " + " | ".join(_n(c) for c in l) + " |" for l in linhas]
    return "\n".join(out)


def secao_44() -> str:
    m = _json("metricas_global.json")
    cam = _json("camadas.json")
    glob = _tabela(
        ["Mapa", "G_pos: ordem", "tamanho", "densidade", "G_est: ordem", "tamanho", "densidade", "teto teórico", "ocupação"],
        [[k, v["ordem_pos"], v["tamanho_pos"], v["densidade_pos"], v["ordem_est"], v["tamanho_est"], v["densidade_est"],
          v["teto_teorico"], v["taxa_ocupacao"]] for k, v in m.items()])
    linhas = []
    for k, v in cam.items():
        casas = ", ".join(f"({c['linha']},{c['coluna']}) {c['simbolo']}" for c in v["casas_geradoras"])
        for c in v["camadas"]:
            linhas.append([k, c["camada"], c["ordem"], c["tamanho"], c["densidade"]])
        linhas.append([k, "**entre camadas**", v["arcos_entre_camadas"], casas or "—", ""])
    return "#### Métricas globais\n\n" + glob + "\n\n#### Métricas por camada e arcos entre camadas\n\n" + _tabela(
        ["Mapa", "Camada (chaves)", "Ordem / arcos entre camadas", "Tamanho / casas que geram", "Densidade"], linhas)


def secao_45() -> str:
    m = _json("metricas_global.json")
    return _tabela(
        ["Mapa", "Maior grau de entrada", "estado", "Maior grau de saída", "estado", "Multiplicidade máx.", "casas", "Becos"],
        [[k, v["maior_grau_entrada"], f"`{v['estado_maior_grau_entrada']}`", v["maior_grau_saida"],
          f"`{v['estado_maior_grau_saida']}`", v["multiplicidade_maxima"], v["quantidade_casas_multiplicidade_maxima"],
          v["quantidade_becos"]] for k, v in m.items()])


def secao_46() -> str:
    return _tabela(["Mapa", "Abordagem", "Passos", "Caminho válido", "Observação"],
                   [[r["mapa"], r["abordagem"], r["passos"], r["caminho_valido"], r["observacao"]]
                    for r in _csv("comparacao_modelagem.csv")])


def secao_47() -> str:
    b = _json("comparacao_bonus_m05.json")
    pos, est = b["grafo_posicoes"], b["grafo_estados"]
    return _tabela(["Grafo", "Status", "Ciclo encontrado", "Custo do ciclo", "Custo até ALVO"], [
        ["G_pos com + fixo em −4", pos["status"], " → ".join(pos["ciclo_negativo"]) or "—", pos["custo_ciclo"], "—"],
        ["G_est", est["status"], " → ".join(est["ciclo_negativo"]) or "—", est["custo_ciclo"], est.get("custo_ate_alvo")],
    ])


def secao_48() -> str:
    sol = {}
    for r in _csv("solucoes.csv"):
        sol.setdefault(r["mapa"], {})[r["algoritmo"]] = r
    dfs = {r["mapa"]: r for r in _csv("dfs_classificacao.csv")}

    def cel(r):
        if r is None:
            return "—"
        return r["status"] if r["status"] != "OK" else f"{r['custo']} ({r['passos']} passos)"

    linhas = []
    for mapa, algs in sol.items():
        d = dfs.get(mapa, {})
        bfs = algs.get("BFS")
        linhas.append([mapa, bfs["passos"] if bfs and bfs["status"] == "OK" else (bfs or {}).get("status", "—"),
                       cel(algs.get("DIJKSTRA")), cel(algs.get("BELLMAN_FORD")),
                       f"{d.get('arvore', '—')} / {d.get('retorno', '—')} / {d.get('avanco', '—')} / {d.get('cruzamento', '—')}"])
    tab = _tabela(["Mapa", "BFS (passos)", "Dijkstra (custo / status)", "Bellman-Ford", "DFS: árvore / retorno / avanço / cruzamento"], linhas)
    ciclo = _json("ciclo_negativo_m06.json")
    tab += ("\n\nCiclo negativo do m06 (`ciclo_negativo_m06.json`): " + " → ".join(f"`{e}`" for e in ciclo["ciclo_negativo"])
            + f", custo {ciclo['custo_ciclo']}.")
    consumivel = OUT / "fonte_consumivel" / "csv" / "solucoes.csv"
    if consumivel.exists():
        with consumivel.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["mapa"] == "m06" and r["algoritmo"] == "BELLMAN_FORD":
                    tab += f"\nCom `--fonte-consumivel` (`out/parte1/fonte_consumivel/`): Bellman-Ford {r['status']}, custo {r['custo']}, {r['passos']} passos."
    return tab


def secao_49() -> str:
    m = _json("metricas_global.json")
    linhas = []
    for k in m:
        nome = k if (OUT / "csv" / f"armadilhas_{k}.csv").exists() else None
        if nome:
            n = len(_csv(f"armadilhas_{k}.csv"))
            linhas.append([k, m[k]["ordem_est"], n, f"{100 * n / m[k]['ordem_est']:.1f}%".replace(".", ",")])
    return _tabela(["Mapa", "Estados alcançáveis", "Estados-armadilha", "% do total"], linhas)


def secao_410() -> str:
    m = _json("metricas_global.json")
    sol = {(r["mapa"], r["algoritmo"]): r for r in _csv("solucoes.csv")}
    linhas = []
    for g in ("g01_tres_depositos", "g02_poco_lateral"):
        if g not in m:
            continue
        arm = len(_csv(f"armadilhas_{g}.csv"))
        bf = sol.get((g, "BELLMAN_FORD"), {})
        dij = sol.get((g, "DIJKSTRA"), {})
        custo = dij.get("custo") if dij.get("status") == "OK" else f"{bf.get('custo')} (BF; Dijkstra {dij.get('status')})"
        linhas.append([g, m[g]["ordem_est"], m[g]["tamanho_est"], sol.get((g, "BFS"), {}).get("passos"), custo,
                       f"{100 * arm / m[g]['ordem_est']:.1f}%".replace(".", ",")])
    return _tabela(["Mapa", "Estados", "Arcos", "Passos (BFS)", "Custo (Dijkstra ou BF)", "% armadilhas"], linhas)


SECOES = {"4.4": secao_44, "4.5": secao_45, "4.6": secao_46, "4.7": secao_47, "4.8": secao_48, "4.9": secao_49,
          "4.10": secao_410}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    pedidas = (argv if argv is not None else sys.argv[1:]) or list(SECOES)
    for s in pedidas:
        if s not in SECOES:
            print(f"Seção desconhecida: {s}. Opções: {', '.join(SECOES)}", file=sys.stderr)
            return 2
        print(f"### Tabela da seção {s}\n\n{SECOES[s]()}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
