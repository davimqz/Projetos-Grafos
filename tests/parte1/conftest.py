"""Mapas sintéticos e dados vazios compartilhados pelos testes da Parte 1."""

# [IA] Codex - reorganização das fixtures existentes.
import pytest

from src.graphs.graph import Grafo
from src.parte1 import carga
from src.parte1.modelos import DadosMapa


@pytest.fixture
def carregar(tmp_path):
    def preparar(grade, **opcoes):
        caminho = tmp_path / "mapa.txt"
        caminho.write_text("\n".join(grade) + "\n", encoding="utf-8")
        return carga.carregar_mapa(caminho, **opcoes)

    return preparar


@pytest.fixture
def vazio():
    return DadosMapa("vazio", [], Grafo(), Grafo(), {}, "")
