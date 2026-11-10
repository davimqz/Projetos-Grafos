"""Benchmark da Parte 2 (P4b)."""
# [IA] Claude Code – testes do benchmark

import json

import pytest

from src.benchmark import (FRACOES, custo_bellman_ford, custo_busca, executar_benchmark, maior_grau_saida,
                           tempo_medio)
from src.carga_parte2 import PASTA_PADRAO
from src.graphs.graph import Grafo


def test_relatorio_compara_os_algoritmos(tmp_path):
    # só 10% dos nós: o Bellman-Ford leva cerca de 45 s por execução no grafo inteiro
    executar_benchmark(PASTA_PADRAO, tmp_path, fracoes=[0.1])
    relatorio = json.loads((tmp_path / "parte2_report.json").read_text(encoding="utf-8"))
    assert [r["algoritmo"] for r in relatorio] == ["DFS", "BFS", "Bellman-Ford"]
    dfs, bfs, bellman_ford = relatorio
    assert dfs["origem"] is None and dfs["alcancados"] == dfs["nos"]
    assert dfs["tempo_por_custo_teorico_ms"] == pytest.approx(
        dfs["tempo_medio_ms"] / (dfs["nos"] + dfs["arestas"]), rel=0.05)
    assert bfs["origem"] == bellman_ford["origem"]
    assert bfs["alcancados"] == bellman_ford["alcancados"]
    assert bellman_ford["status"] == "OK" and bellman_ford["tempo_por_custo_teorico_ms"] is None
    assert (tmp_path / "benchmark_escalabilidade.png").exists()


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
