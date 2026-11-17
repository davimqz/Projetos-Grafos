"""Contratos das seis funções já implementadas na orquestração da Parte 1."""

# [IA] Codex - testes de carga, CSV e análises, sem implementar algoritmos.
import csv
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


@pytest.mark.parametrize("tipo_caminho", [str, Path])
@pytest.mark.parametrize("nome", [None, "personalizado", ""])
def test_carregar_mapa_prepara_componentes_e_nome(tmp_path, tipo_caminho, nome):
    caminho = tmp_path / "duas_saidas.txt"
    caminho.write_text("; comentário\nG.\n.S\n", encoding="utf-8")

    dados = solve.carregar_mapa(tipo_caminho(caminho), nome=nome)

    assert dados.nome == ("duas_saidas" if nome is None else nome)
    assert dados.grade == ["G.", ".S"]
    assert dados.origem == "(1,1)|-|{}"
    assert dados.estados[dados.origem] == Estado(1, 1, frozenset(), frozenset())
    assert dados.fonte_consumivel is False
    assert set(dados.grafo_posicoes.nos()) == {"(0,0)", "(0,1)", "(1,0)", "(1,1)"}
    assert set(dados.grafo_estados.nos()) == set(dados.estados) | {"ALVO"}
    assert dados.grafo_estados.vizinhos("(0,0)|-|{}") == [("ALVO", 0)]
    assert list(tmp_path.iterdir()) == [caminho]


@pytest.mark.parametrize("consumivel", [False, True])
def test_carregar_mapa_encaminha_variante_da_fonte(carregar, consumivel):
    dados = carregar(["S*G"], fonte_consumivel=consumivel)

    assert dados.fonte_consumivel is consumivel
    assert dados.estados[dados.origem].bonus == frozenset()
    assert dados.grafo_posicoes.vizinhos("(0,0)") == [("(0,1)", -2)]
    rotulo_fonte = "(0,1)|-|{0}" if consumivel else "(0,1)|-|{}"
    assert dados.grafo_estados.vizinhos(dados.origem) == [(rotulo_fonte, -2)]
    assert dados.estados[rotulo_fonte].bonus == (frozenset({0}) if consumivel else frozenset())


def test_carregar_mapa_propaga_arquivo_ausente(tmp_path):
    with pytest.raises(FileNotFoundError):
        solve.carregar_mapa(tmp_path / "ausente.txt")


def test_carregar_mapa_propaga_validacao(carregar):
    with pytest.raises(ValueError, match="Símbolo inválido"):
        carregar(["S?G"])


@pytest.mark.parametrize("construtor", ["construir_grafo_estados", "construir_grafo_posicoes"])
def test_carregar_mapa_propaga_erro_dos_construtores(carregar, monkeypatch, construtor):
    erro = RuntimeError("falha do construtor")

    def falhar(*args, **kwargs):
        raise erro

    monkeypatch.setattr(solve, construtor, falhar)
    with pytest.raises(RuntimeError) as capturado:
        carregar(["SG"])
    assert capturado.value is erro


@pytest.mark.parametrize("usar_string", [False, True])
def test_exportar_arestas_preserva_ordem_movimentos_simbolos_e_pesos(carregar, tmp_path, usar_string):
    dados = carregar(["#,#", ".SG", "#~#"])
    caminho = tmp_path / "arestas.csv"

    solve.exportar_arestas(dados, str(caminho) if usar_string else caminho)

    with caminho.open(newline="", encoding="utf-8") as arquivo:
        linhas = list(csv.reader(arquivo))
    assert linhas == [
        ["origem", "destino", "movimento", "casa_destino", "peso"],
        ["(1,1)|-|{}", "(0,1)|-|{}", "N", ",", "3"],
        ["(1,1)|-|{}", "(1,2)|-|{}", "L", "G", "1"],
        ["(1,1)|-|{}", "(2,1)|-|{}", "S", "~", "5"],
        ["(1,1)|-|{}", "(1,0)|-|{}", "O", ".", "1"],
        ["(0,1)|-|{}", "(1,1)|-|{}", "S", "S", "1"],
        ["(1,2)|-|{}", "ALVO", "", "", "0"],
        ["(2,1)|-|{}", "(1,1)|-|{}", "N", "S", "1"],
        ["(1,0)|-|{}", "(1,1)|-|{}", "L", "S", "1"],
    ]


def test_exportar_arestas_preserva_rotulos_com_bonus_e_pesos_negativos(carregar, tmp_path):
    dados = carregar(["S++G"])
    caminho = tmp_path / "arestas.csv"
    solve.exportar_arestas(dados, caminho)

    with caminho.open(newline="", encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    assert len(linhas) == dados.grafo_estados.tamanho()
    assert {
        "origem": "(0,1)|-|{0}", "destino": "(0,2)|-|{0,1}",
        "movimento": "L", "casa_destino": "+", "peso": "-4",
    } in linhas
    assert {
        "origem": "(0,2)|-|{0,1}", "destino": "(0,1)|-|{0,1}",
        "movimento": "O", "casa_destino": "+", "peso": "1",
    } in linhas


def test_exportar_arestas_vazias_escreve_cabecalho(vazio, tmp_path):
    caminho = tmp_path / "arestas.csv"
    solve.exportar_arestas(vazio, caminho)
    assert caminho.read_text(encoding="utf-8") == "origem,destino,movimento,casa_destino,peso\n"


def test_exportar_arestas_propaga_erro_de_escrita(vazio, tmp_path):
    with pytest.raises(FileNotFoundError):
        solve.exportar_arestas(vazio, tmp_path / "ausente" / "arestas.csv")


def test_calcular_metricas_globais_separa_modelagens_e_exclui_alvo(carregar):
    dados = carregar(["SAG"])
    assert solve.calcular_metricas_globais(dados) == {
        "ordem_pos": 3, "tamanho_pos": 3, "densidade_pos": 0.5,
        "ordem_est": 1, "tamanho_est": 0, "densidade_est": 0,
        "teto_teorico": 3, "taxa_ocupacao": pytest.approx(1 / 3),
    }


def test_calcular_metricas_globais_remove_arco_virtual_ate_saida(carregar):
    assert solve.calcular_metricas_globais(carregar(["SG"])) == {
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
    metricas = solve.calcular_metricas_globais(dados)
    assert metricas["teto_teorico"] == teto
    assert metricas["taxa_ocupacao"] == pytest.approx(len(dados.estados) / teto)


def test_calcular_metricas_globais_vazias(vazio):
    assert solve.calcular_metricas_globais(vazio) == {
        "ordem_pos": 0, "tamanho_pos": 0, "densidade_pos": 0,
        "ordem_est": 0, "tamanho_est": 0, "densidade_est": 0,
        "teto_teorico": 0, "taxa_ocupacao": 0,
    }


def test_calcular_camadas_agrupa_bonus_pelas_chaves_e_exclui_alvo(carregar):
    assert solve.calcular_camadas(carregar(["Sa+G"])) == {
        "camadas": [
            {"camada": "-", "ordem": 1, "tamanho": 0, "densidade": 0},
            {"camada": "a", "ordem": 6, "tamanho": 8, "densidade": pytest.approx(8 / 30)},
        ],
        "arcos_entre_camadas": 1,
        "casas_geradoras": [{"linha": 0, "coluna": 1, "simbolo": "a"}],
    }


def test_calcular_camadas_ordena_chaves_e_deduplica_casas_geradoras(carregar):
    resultado = solve.calcular_camadas(carregar(["Sa", "bG"]))
    assert [camada["camada"] for camada in resultado["camadas"]] == ["-", "a", "b", "ab"]
    assert resultado["arcos_entre_camadas"] == 4
    assert resultado["casas_geradoras"] == [
        {"linha": 0, "coluna": 1, "simbolo": "a"},
        {"linha": 1, "coluna": 0, "simbolo": "b"},
    ]


def test_calcular_camadas_sem_chaves(carregar):
    assert solve.calcular_camadas(carregar(["SG"])) == {
        "camadas": [{"camada": "-", "ordem": 2, "tamanho": 1, "densidade": 0.5}],
        "arcos_entre_camadas": 0, "casas_geradoras": [],
    }


def test_calcular_camadas_vazias(vazio):
    assert solve.calcular_camadas(vazio) == {
        "camadas": [], "arcos_entre_camadas": 0, "casas_geradoras": [],
    }


def test_calcular_graus_dirigidos_sem_arco_virtual_na_ordem_dos_estados(carregar):
    dados = carregar(["S.G"])
    dados = replace(dados, estados=dict(reversed(list(dados.estados.items()))))
    assert solve.calcular_graus(dados) == [
        {"estado": "(0,2)|-|{}", "grau_entrada": 1, "grau_saida": 0},
        {"estado": "(0,1)|-|{}", "grau_entrada": 1, "grau_saida": 2},
        {"estado": "(0,0)|-|{}", "grau_entrada": 1, "grau_saida": 1},
    ]


def test_calcular_graus_sem_saida_alcancavel(carregar):
    assert solve.calcular_graus(carregar(["S#G"])) == [
        {"estado": "(0,0)|-|{}", "grau_entrada": 0, "grau_saida": 0},
    ]


def test_calcular_graus_vazios(vazio):
    assert solve.calcular_graus(vazio) == []


def test_analisar_graus_rankings_e_exclusao_da_saida_dos_becos(carregar):
    assert solve.analisar_graus(carregar(["S.G"])) == {
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
    resultado = solve.analisar_graus(dados)
    assert resultado[f"estado_maior_grau_{sentido}"] == rotulo
    assert resultado[f"maior_grau_{sentido}"] == grau


def test_analisar_graus_multiplicidade_por_posicao_ignora_chaves_e_bonus(carregar):
    resultado = solve.analisar_graus(carregar(["Sa+G"]))
    assert resultado["multiplicidade_maxima"] == 3
    assert resultado["casas_multiplicidade_maxima"] == [
        {"linha": 0, "coluna": 0, "simbolo": "S"},
    ]
    assert resultado["quantidade_casas_multiplicidade_maxima"] == 1


def test_analisar_graus_identifica_beco_em_esteira(carregar):
    resultado = solve.analisar_graus(carregar(["S>#G"]))
    assert resultado["becos"] == ["(0,1)|-|{}"]
    assert resultado["quantidade_becos"] == 1


def test_analisar_graus_vazios(vazio):
    assert solve.analisar_graus(vazio) == {
        "estado_maior_grau_entrada": None, "maior_grau_entrada": 0,
        "estado_maior_grau_saida": None, "maior_grau_saida": 0,
        "multiplicidade_maxima": 0, "casas_multiplicidade_maxima": [],
        "quantidade_casas_multiplicidade_maxima": 0,
        "becos": [], "quantidade_becos": 0,
    }


@pytest.mark.parametrize("funcao", [
    solve.calcular_metricas_globais, solve.calcular_camadas,
    solve.calcular_graus, solve.analisar_graus, solve.exportar_arestas,
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
