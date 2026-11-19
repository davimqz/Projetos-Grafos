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


# [IA] Codex - cobertura dos contratos restantes, com mapas sintéticos e IO temporário.
# [IA] Codex - regressões de desempenho das análises, sem limites de tempo frágeis.
