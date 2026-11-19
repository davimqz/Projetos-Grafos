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


def test_calcular_graus_dirigidos_sem_arco_virtual_na_ordem_dos_estados(carregar):
    dados = carregar(["S.G"])
    dados = replace(dados, estados=dict(reversed(list(dados.estados.items()))))
    assert analises.calcular_graus(dados) == [
        {"estado": "(0,2)|-|{}", "grau_entrada": 1, "grau_saida": 0},
        {"estado": "(0,1)|-|{}", "grau_entrada": 1, "grau_saida": 2},
        {"estado": "(0,0)|-|{}", "grau_entrada": 1, "grau_saida": 1},
    ]


def test_calcular_graus_sem_saida_alcancavel(carregar):
    assert analises.calcular_graus(carregar(["S#G"])) == [
        {"estado": "(0,0)|-|{}", "grau_entrada": 0, "grau_saida": 0},
    ]


def test_calcular_graus_vazios(vazio):
    assert analises.calcular_graus(vazio) == []


def test_analisar_graus_rankings_e_exclusao_da_saida_dos_becos(carregar):
    assert analises.analisar_graus(carregar(["S.G"])) == {
        "estado_maior_grau_entrada": "(0,0)|-|{}", "maior_grau_entrada": 1,
        "estado_maior_grau_saida": "(0,1)|-|{}", "maior_grau_saida": 2,
        "multiplicidade_maxima": 1,
        "casas_multiplicidade_maxima": [
            {"linha": 0, "coluna": 0, "simbolo": "S"},
            {"linha": 0, "coluna": 1, "simbolo": "."},
            {"linha": 0, "coluna": 2, "simbolo": "G"},
        ],
        "quantidade_casas_multiplicidade_maxima": 3,
        "becos": [], "quantidade_becos": 0,
    }


@pytest.mark.parametrize("sentido, grade, rotulo, grau", [
    ("entrada", ["S.G"], "(0,0)|-|{}", 1),
    ("saida", ["S..G"], "(0,1)|-|{}", 2),
])
def test_analisar_graus_desempata_por_rotulo_independente_da_insercao(carregar, sentido, grade, rotulo, grau):
    dados = carregar(grade)
    dados = replace(dados, estados=dict(reversed(list(dados.estados.items()))))
    resultado = analises.analisar_graus(dados)
    assert resultado[f"estado_maior_grau_{sentido}"] == rotulo
    assert resultado[f"maior_grau_{sentido}"] == grau


def test_analisar_graus_multiplicidade_por_posicao_ignora_chaves_e_bonus(carregar):
    resultado = analises.analisar_graus(carregar(["Sa+G"]))
    assert resultado["multiplicidade_maxima"] == 3
    assert resultado["casas_multiplicidade_maxima"] == [
        {"linha": 0, "coluna": 0, "simbolo": "S"},
    ]
    assert resultado["quantidade_casas_multiplicidade_maxima"] == 1


def test_analisar_graus_identifica_beco_em_esteira(carregar):
    resultado = analises.analisar_graus(carregar(["S>#G"]))
    assert resultado["becos"] == ["(0,1)|-|{}"]
    assert resultado["quantidade_becos"] == 1


def test_analisar_graus_vazios(vazio):
    assert analises.analisar_graus(vazio) == {
        "estado_maior_grau_entrada": None, "maior_grau_entrada": 0,
        "estado_maior_grau_saida": None, "maior_grau_saida": 0,
        "multiplicidade_maxima": 0, "casas_multiplicidade_maxima": [],
        "quantidade_casas_multiplicidade_maxima": 0,
        "becos": [], "quantidade_becos": 0,
    }


@pytest.mark.parametrize("grade, contagens, ciclo", [
    (["SG"], (2, 0, 0, 0), False),
    (["S.G"], (3, 1, 0, 0), True),
    (["S#G"], (0, 0, 0, 0), False),
])
def test_classificar_arcos_inclui_alvo_alcancavel_e_indica_ciclo(carregar, grade, contagens, ciclo):
    resultado = analises.classificar_arcos(carregar(grade))
    assert resultado == {
        "mapa": "mapa", **dict(zip(("arvore", "retorno", "avanco", "cruzamento"), contagens)),
        "tem_ciclo": ciclo,
    }


def test_classificar_arcos_mapeia_categorias_e_passa_origem(carregar, monkeypatch):
    dados = carregar(["SG"])
    contagens = {"arvore": 1, "retorno": 2, "avanco": 3, "cruzamento": 4}

    def dfs_simulada(grafo, origem):
        assert grafo is dados.grafo_estados and origem == dados.origem
        return {"contagem_arcos": contagens, "tem_ciclo": True}

    monkeypatch.setattr(analises, "dfs", dfs_simulada)
    assert analises.classificar_arcos(dados) == {"mapa": "mapa", **contagens, "tem_ciclo": True}


@pytest.mark.parametrize("inverter", [False, True])
@pytest.mark.parametrize("grade, esperado", [
    (["SG"], []),
    (["S#G"], ["(0,0)|-|{}"]),
    (["S.G", ".v#"], ["(1,1)|-|{}"]),
    (["S.G", ".><"], ["(1,1)|-|{}", "(1,2)|-|{}"]),
    (["S>.AG", "a####"], ["(0,1)|-|{}", "(0,2)|-|{}"]),
    (["S*G"], []),
])
def test_encontrar_armadilhas_reachabilidade_por_estado_e_ordem(carregar, grade, esperado, inverter):
    dados = carregar(grade)
    if inverter:
        dados = replace(dados, estados=dict(reversed(list(dados.estados.items()))))
        esperado = list(reversed(esperado))
    assert analises.encontrar_armadilhas(dados) == esperado


@pytest.mark.parametrize("funcao", [analises.calcular_graus, analises.analisar_graus])
def test_graus_consultam_cada_lista_de_vizinhos_uma_vez(carregar, monkeypatch, funcao):
    dados = carregar(["S" + "." * 100 + "G"])
    vizinhos = dados.grafo_estados.vizinhos
    consultas = []

    def consultar(no):
        consultas.append(no)
        return vizinhos(no)

    def varredura_repetida(*args):
        pytest.fail("Calcular cada grau de entrada separadamente volta a custar O(VE).")

    monkeypatch.setattr(dados.grafo_estados, "vizinhos", consultar)
    monkeypatch.setattr(Grafo, "grau_entrada", varredura_repetida)
    funcao(dados)

    assert consultas == list(dados.estados)


@pytest.mark.parametrize("operacao", ["metricas", "camadas", "arestas"])
def test_contagens_e_exportacao_nao_copiam_grafos_ou_lista_de_arcos(carregar, tmp_path, monkeypatch, operacao):
    dados = carregar(["Sa+G"])

    def copiar(*args):
        pytest.fail("Esta operação deve consultar os arcos sem materializar cópias completas.")

    monkeypatch.setattr(Grafo, "subgrafo_induzido", copiar)
    monkeypatch.setattr(Grafo, "arestas", copiar)
    if operacao == "metricas":
        assert analises.calcular_metricas_globais(dados)["ordem_est"] == len(dados.estados)
    elif operacao == "camadas":
        assert sum(c["ordem"] for c in analises.calcular_camadas(dados)["camadas"]) == len(dados.estados)
    else:
        exportacao.exportar_arestas(dados, tmp_path / "arestas.csv")
        with (tmp_path / "arestas.csv").open(newline="", encoding="utf-8") as arquivo:
            assert len(list(csv.DictReader(arquivo))) == dados.grafo_estados.tamanho()
