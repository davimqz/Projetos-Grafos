"""Benchmark da Parte 2 (P4b)."""
# teste mínimo do benchmark

import json

from src.benchmark import executar_benchmark
from src.carga_parte2 import PASTA_PADRAO


def test_relatorio_tem_dfs_nas_tres_fracoes(tmp_path):
    executar_benchmark(PASTA_PADRAO, tmp_path)
    relatorio = json.loads((tmp_path / "parte2_report.json").read_text(encoding="utf-8"))
    assert [(r["algoritmo"], r["fracao"]) for r in relatorio] == [("DFS", 0.1), ("DFS", 0.5), ("DFS", 1.0)]
    assert (tmp_path / "benchmark_escalabilidade.png").exists()
