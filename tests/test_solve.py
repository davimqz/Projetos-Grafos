"""Contratos das funções da Parte 1; integração em test_executar_parte1.py."""

# [IA] Codex - testes de carga, CSV e análises, sem implementar algoritmos.
import csv
import json
import os
import subprocess
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from src import solve
from src.graphs.estados import Estado
from src.graphs.graph import Grafo


@pytest.fixture
def carregar(tmp_path):
    def preparar(grade, **opcoes):
        caminho = tmp_path / "mapa.txt"
        caminho.write_text("\n".join(grade) + "\n", encoding="utf-8")
        return solve.carregar_mapa(caminho, **opcoes)

    return preparar


@pytest.fixture
def vazio():
    return solve.DadosMapa("vazio", [], Grafo(), Grafo(), {}, "")


@pytest.mark.parametrize("funcao", [
    solve.calcular_metricas_globais, solve.calcular_camadas,
    solve.calcular_graus, solve.analisar_graus, solve.exportar_arestas,
    lambda dados: solve.resolver_mapa(dados, "BFS"),
    solve.classificar_arcos, solve.encontrar_armadilhas,
    solve.comparar_modelagens, solve.comparar_bonus,
])
def test_funcoes_preservam_dados_e_calculos_nao_gravam_arquivos(carregar, tmp_path, funcao):
    dados = carregar(["Sa+G"])
    # Inclui os dicionários internos dos grafos para detectar mutações.
    antes = deepcopy(vars(dados))
    arquivos = set(tmp_path.iterdir())
    if funcao is solve.exportar_arestas:
        funcao(dados, tmp_path / "arestas.csv")
    else:
        funcao(dados)
        assert set(tmp_path.iterdir()) == arquivos

    for campo in ("grafo_posicoes", "grafo_estados"):
        assert vars(getattr(dados, campo)) == vars(antes.pop(campo))
    assert {chave: valor for chave, valor in vars(dados).items() if chave in antes} == antes


# [IA] Codex - cobertura dos contratos restantes, com mapas sintéticos e IO temporário.
# [IA] Codex - regressões de desempenho das análises, sem limites de tempo frágeis.
