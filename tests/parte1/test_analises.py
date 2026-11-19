"""Testes de analises da Parte 1 com mapas sintéticos."""

# [IA] Codex - testes existentes separados por responsabilidade.
import csv
from dataclasses import replace

import pytest

from src.graphs.graph import Grafo
from src.parte1 import analises, exportacao


def test_calcular_metricas_globais_separa_modelagens_e_exclui_alvo(carregar):
    dados = carregar(["SAG"])
    assert analises.calcular_metricas_globais(dados) == {
        "ordem_pos": 3, "tamanho_pos": 3, "densidade_pos": 0.5,
        "ordem_est": 1, "tamanho_est": 0, "densidade_est": 0,
        "teto_teorico": 3, "taxa_ocupacao": pytest.approx(1 / 3),
    }


def test_calcular_metricas_globais_remove_arco_virtual_ate_saida(carregar):
    assert analises.calcular_metricas_globais(carregar(["SG"])) == {
        "ordem_pos": 2, "tamanho_pos": 1, "densidade_pos": 0.5,
        "ordem_est": 2, "tamanho_est": 1, "densidade_est": 0.5,
        "teto_teorico": 2, "taxa_ocupacao": 1,
    }


@pytest.mark.parametrize("grade, consumivel, teto", [
    (["SaaG"], False, 8),
    (["S++G"], False, 16),
    (["S**G"], False, 4),
    (["S**G"], True, 16),
    (["Saa++**G"], False, 64),
    (["Saa++**G"], True, 256),
    (["#S.G,~abcdABCD><^v+*"], False, 608),
])
def test_calcular_metricas_globais_teto_por_casas_chaves_e_consumiveis(carregar, grade, consumivel, teto):
    dados = carregar(grade, fonte_consumivel=consumivel)
    metricas = analises.calcular_metricas_globais(dados)
    assert metricas["teto_teorico"] == teto
    assert metricas["taxa_ocupacao"] == pytest.approx(len(dados.estados) / teto)


def test_calcular_metricas_globais_vazias(vazio):
    assert analises.calcular_metricas_globais(vazio) == {
        "ordem_pos": 0, "tamanho_pos": 0, "densidade_pos": 0,
        "ordem_est": 0, "tamanho_est": 0, "densidade_est": 0,
        "teto_teorico": 0, "taxa_ocupacao": 0,
    }


def test_calcular_camadas_agrupa_bonus_pelas_chaves_e_exclui_alvo(carregar):
    assert analises.calcular_camadas(carregar(["Sa+G"])) == {
        "camadas": [
            {"camada": "-", "ordem": 1, "tamanho": 0, "densidade": 0},
            {"camada": "a", "ordem": 6, "tamanho": 8, "densidade": pytest.approx(8 / 30)},
        ],
        "arcos_entre_camadas": 1,
        "casas_geradoras": [{"linha": 0, "coluna": 1, "simbolo": "a"}],
    }


def test_calcular_camadas_ordena_chaves_e_deduplica_casas_geradoras(carregar):
    resultado = analises.calcular_camadas(carregar(["Sa", "bG"]))
    assert [camada["camada"] for camada in resultado["camadas"]] == ["-", "a", "b", "ab"]
    assert resultado["arcos_entre_camadas"] == 4
    assert resultado["casas_geradoras"] == [
        {"linha": 0, "coluna": 1, "simbolo": "a"},
        {"linha": 1, "coluna": 0, "simbolo": "b"},
    ]


def test_calcular_camadas_sem_chaves(carregar):
    assert analises.calcular_camadas(carregar(["SG"])) == {
        "camadas": [{"camada": "-", "ordem": 2, "tamanho": 1, "densidade": 0.5}],
        "arcos_entre_camadas": 0, "casas_geradoras": [],
    }


def test_calcular_camadas_vazias(vazio):
    assert analises.calcular_camadas(vazio) == {
        "camadas": [], "arcos_entre_camadas": 0, "casas_geradoras": [],
    }
