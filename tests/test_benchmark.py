"""Benchmark da Parte 2 (P4b)."""
# [IA] Claude Code – testes do benchmark

import json

import pytest

from src.benchmark import (FONTES_BELLMAN_FORD, FONTES_BUSCA, FRACOES, PARES_DIJKSTRA, custo_bellman_ford, custo_busca, executar_benchmark, maior_grau_saida,
                           pico_memoria, tempo_medio)
from src.carga_parte2 import PASTA_PADRAO
from src.graphs.graph import Grafo


def test_relatorio_compara_os_algoritmos(tmp_path):
    # só 10% dos nós: o Bellman-Ford leva cerca de 45 s por execução no grafo inteiro
    executar_benchmark(PASTA_PADRAO, tmp_path, fracoes=[0.1], com_casos=False)
    relatorio = json.loads((tmp_path / "parte2_report.json").read_text(encoding="utf-8"))["escalabilidade"]
    assert all(r["repeticoes"] == 5 for r in relatorio)
    assert [r["algoritmo"] for r in relatorio] == ["DFS", "BFS", "Dijkstra", "Bellman-Ford"]
    dfs, bfs, dijkstra, bellman_ford = relatorio
    assert dfs["origem"] is None and dfs["alcancados"] == dfs["nos"]
    assert dfs["tempo_por_custo_teorico_ms"] == pytest.approx(
        dfs["tempo_medio_ms"] / (dfs["nos"] + dfs["arestas"]), rel=0.05)
    assert bfs["origem"] == bellman_ford["origem"]
    assert bfs["alcancados"] == bellman_ford["alcancados"]
    assert dijkstra["origem"] == bfs["origem"]
    assert dijkstra["alcancados"] == bfs["alcancados"]
    assert dijkstra["tempo_por_custo_teorico_ms"] is not None
    assert bellman_ford["status"] == "OK" and bellman_ford["tempo_por_custo_teorico_ms"] is None
    assert all(r["memoria_pico_kb"] > 0 for r in relatorio)
    assert all(r["latencia_min_ms"] <= r["tempo_medio_ms"] <= r["latencia_max_ms"] for r in relatorio)
    assert (tmp_path / "benchmark_escalabilidade.png").exists()


def test_pico_memoria_conta_o_que_a_funcao_aloca():
    pequeno = pico_memoria(lambda _: [0] * 10, None)
    grande = pico_memoria(lambda _: [0] * 1_000_000, None)
    assert grande > 7_000_000 > pequeno  # 1 milhão de ponteiros de 8 bytes


def test_fracoes_do_plano():
    assert FRACOES == [0.1, 0.5, 1.0]


def test_tempo_medio_roda_5_vezes():
    chamadas = []
    tempo_medio(chamadas.append, "grafo")
    assert len(chamadas) == 5


def test_origem_e_custos():
    grafo = Grafo()
    grafo.adicionar_aresta("a", "b", 1)
    grafo.adicionar_aresta("c", "a", 1)
    grafo.adicionar_aresta("c", "d", 1)
    assert maior_grau_saida(grafo) == "c"
    assert custo_busca(grafo, {"ordem": ["a", "b"]}) == 4 + 1  # V + o único arco percorrido
    assert custo_bellman_ford(grafo, {"status": "CICLO_NEGATIVO"}) == 4 * 3
    assert custo_bellman_ford(grafo, {"status": "OK"}) is None


def test_casos_obrigatorios_batem_com_os_jsons():
    # [IA] Claude Code – confere que o report usa as mesmas fontes e pares dos JSONs da seção 5 (V1)
    from pathlib import Path
    pasta = Path(__file__).resolve().parents[1] / "out" / "parte2"
    assert {f"bfs_{o}.json" for o in FONTES_BUSCA} <= {p.name for p in pasta.glob("bfs_*.json")}
    assert {f"dijkstra_{o}_{d}.json" for o, d in PARES_DIJKSTRA} == {p.name for p in pasta.glob("dijkstra_*.json")}
    assert {f"bellman_ford_{o}.json" for o in FONTES_BELLMAN_FORD} == {p.name for p in pasta.glob("bellman_ford_*.json")}
