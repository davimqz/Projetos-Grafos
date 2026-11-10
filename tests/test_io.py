"""Leitura, validação e localização dos elementos dos mapas da Parte 1."""

# [IA] Codex - testes dos contratos de IO, erros e casos de borda da Parte 1.
from pathlib import Path

import pytest

from src.graphs.io import (
    encontrar_inicio,
    encontrar_saidas,
    enumerar_bonus,
    ler_mapa,
    validar_mapa,
)


def _escrever_mapa(tmp_path, conteudo):
    caminho = tmp_path / "mapa.txt"
    # Bytes preservam as quebras de linha do caso, inclusive CRLF no Windows.
    caminho.write_bytes(conteudo.encode("utf-8"))
    return caminho


@pytest.mark.parametrize(
    "grade",
    [
        pytest.param(["SG"], id="minimo-horizontal"),
        pytest.param(["S", "G"], id="uma-coluna"),
        pytest.param(["#.SG,~abcdABCD><^v+*"], id="todos-os-simbolos"),
        pytest.param(["SGG"], id="varias-saidas"),
        pytest.param(["S#G"], id="saida-inalcancavel"),
        pytest.param(["S..", ".G."], id="retangular"),
    ],
)
def test_validar_mapa_aceita_grade_valida_sem_modifica_la(grade):
    original = grade.copy()

    assert validar_mapa(grade) is None
    assert grade == original


@pytest.mark.parametrize(
    "grade, mensagem",
    [
        pytest.param([], "grade.*vazia", id="grade-vazia"),
        pytest.param([""], "linha 0.*vazia", id="primeira-linha-vazia"),
        pytest.param(["SG", ""], "linha 1.*vazia", id="linha-posterior-vazia"),
        pytest.param(
            ["SG", "G"], "linha 1.*largura 1.*esperada.*2", id="linha-curta"
        ),
        pytest.param(
            ["SG", "G.."], "linha 1.*largura 3.*esperada.*2", id="linha-longa"
        ),
        pytest.param([".G"], "exatamente um 'S'.*nenhum", id="sem-inicio"),
        pytest.param(
            ["SSG"], "exatamente um 'S'.*\\(0, 1\\)", id="inicios-na-mesma-linha"
        ),
        pytest.param(
            ["S.", "SG"],
            "exatamente um 'S'.*\\(1, 0\\)",
            id="inicios-em-linhas-diferentes",
        ),
        pytest.param(["S."], "pelo menos um 'G'.*nenhum", id="sem-saida"),
    ],
)
def test_validar_mapa_rejeita_grade_invalida_sem_modifica_la(grade, mensagem):
    original = grade.copy()

    with pytest.raises(ValueError, match=mensagem):
        validar_mapa(grade)

    assert grade == original


@pytest.mark.parametrize("simbolo", ["?", " ", "\t", "x", "s", "g", "é", ";"])
def test_validar_mapa_informa_simbolo_invalido_e_coordenadas(simbolo):
    with pytest.raises(ValueError, match="Símbolo inválido") as erro:
        validar_mapa(["S" + simbolo + "G"])

    assert repr(simbolo) in str(erro.value)
    assert "(0, 1)" in str(erro.value)


@pytest.mark.parametrize("tipo_caminho", [str, Path], ids=["str", "Path"])
def test_ler_mapa_aceita_caminho_string_e_path(tmp_path, tipo_caminho):
    caminho = _escrever_mapa(tmp_path, "S.\n.G\n")

    assert ler_mapa(tipo_caminho(caminho)) == ["S.", ".G"]


@pytest.mark.parametrize(
    "conteudo, esperado",
    [
        pytest.param("S.\n.G\n", ["S.", ".G"], id="quebras-lf"),
        pytest.param("S.\n.G", ["S.", ".G"], id="sem-quebra-final"),
        pytest.param("S.\r\n.G\r\n", ["S.", ".G"], id="quebras-crlf"),
        pytest.param(
            "; antes\nS.\n; entre\n.G\n; depois\n",
            ["S.", ".G"],
            id="comentarios-antes-entre-depois",
        ),
        pytest.param("; início do mapa\nSG\n", ["SG"], id="comentario-utf8"),
        pytest.param("SG\n; fim", ["SG"], id="comentario-sem-quebra-final"),
    ],
)
def test_ler_mapa_remove_quebras_e_comentarios(tmp_path, conteudo, esperado):
    caminho = _escrever_mapa(tmp_path, conteudo)

    assert ler_mapa(caminho) == esperado


@pytest.mark.parametrize(
    "conteudo, mensagem",
    [
        pytest.param("", "grade.*vazia", id="arquivo-vazio"),
        pytest.param("; comentário\n", "grade.*vazia", id="apenas-comentarios"),
        pytest.param("SG\n\n", "linha 1.*vazia", id="linha-em-branco"),
        pytest.param(
            "SSG\n", "exatamente um 'S'.*\\(0, 1\\)", id="propaga-validacao"
        ),
    ],
)
def test_ler_mapa_rejeita_conteudo_invalido(tmp_path, conteudo, mensagem):
    caminho = _escrever_mapa(tmp_path, conteudo)

    with pytest.raises(ValueError, match=mensagem):
        ler_mapa(caminho)


@pytest.mark.parametrize(
    "conteudo, simbolo, posicao",
    [
        pytest.param(" SG\n", " ", "(0, 0)", id="espaco-inicial"),
        pytest.param("SG \n", " ", "(0, 2)", id="espaco-final"),
        pytest.param("\tSG\n", "\t", "(0, 0)", id="tabulacao-inicial"),
        pytest.param("SG\t\n", "\t", "(0, 2)", id="tabulacao-final"),
        pytest.param(
            " ; comentário\nSG\n", " ", "(0, 0)", id="comentario-indentado"
        ),
    ],
)
def test_ler_mapa_preserva_espacos_e_tabulacoes_para_validacao(
    tmp_path, conteudo, simbolo, posicao
):
    caminho = _escrever_mapa(tmp_path, conteudo)

    with pytest.raises(ValueError, match="Símbolo inválido") as erro:
        ler_mapa(caminho)

    assert repr(simbolo) in str(erro.value)
    assert posicao in str(erro.value)


def test_ler_mapa_desconsidera_comentarios_nas_coordenadas_do_erro(tmp_path):
    caminho = _escrever_mapa(
        tmp_path, "; comentário inicial\nS.G\n; outro comentário\n..?\n"
    )

    with pytest.raises(ValueError, match="Símbolo inválido") as erro:
        ler_mapa(caminho)

    assert "'?'" in str(erro.value)
    assert "(1, 2)" in str(erro.value)


def test_ler_mapa_propaga_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        ler_mapa(tmp_path / "inexistente.txt")


def test_ler_mapa_propaga_erro_de_permissao(tmp_path, monkeypatch):
    falha = PermissionError("Acesso ao mapa negado")

    def negar_acesso(*args, **kwargs):
        raise falha

    monkeypatch.setattr("builtins.open", negar_acesso)

    with pytest.raises(PermissionError) as erro:
        ler_mapa(tmp_path / "mapa.txt")

    assert erro.value is falha


def test_ler_mapa_propaga_erro_de_utf8(tmp_path):
    caminho = tmp_path / "mapa.txt"
    caminho.write_bytes(b"; coment\xffrio\nSG\n")

    with pytest.raises(UnicodeDecodeError):
        ler_mapa(caminho)


@pytest.mark.parametrize(
    "grade, esperado",
    [
        pytest.param(["SG"], (0, 0), id="origem"),
        pytest.param(["G...", "..S."], (1, 2), id="linha-e-coluna-distintas"),
        pytest.param(["G.", ".S"], (1, 1), id="ultima-posicao"),
    ],
)
def test_encontrar_inicio_devolve_linha_e_coluna(grade, esperado):
    assert encontrar_inicio(grade) == esperado


@pytest.mark.parametrize("grade", [[".G"], []], ids=["sem-S", "grade-vazia"])
def test_encontrar_inicio_sem_inicio_levanta_erro(grade):
    # Caso defensivo: estas entradas não atendem à precondição de grade validada.
    with pytest.raises(ValueError, match="início 'S'"):
        encontrar_inicio(grade)


@pytest.mark.parametrize(
    "grade, esperado",
    [
        pytest.param(["SG"], [(0, 1)], id="uma-saida"),
        pytest.param(
            ["G..G", "..S.", ".G.G"],
            [(0, 0), (0, 3), (2, 1), (2, 3)],
            id="varias-saidas-em-ordem-de-leitura",
        ),
        pytest.param(["S."], [], id="sem-saida-defensivo"),
        pytest.param([], [], id="grade-vazia-defensivo"),
    ],
)
def test_encontrar_saidas_devolve_todas_em_ordem_de_leitura(grade, esperado):
    assert encontrar_saidas(grade) == esperado


@pytest.mark.parametrize(
    "grade, esperado",
    [
        pytest.param(["SG"], {}, id="sem-bonus"),
        pytest.param(["S+G"], {(0, 1): 0}, id="um-bonus"),
        pytest.param(
            ["G.+G", "..S.", "+G*+"],
            {(0, 2): 0, (2, 0): 1, (2, 3): 2},
            id="varios-bonus-em-ordem-ignorando-fonte",
        ),
        pytest.param(["S*G"], {}, id="somente-fonte"),
    ],
)
def test_enumerar_bonus_atribui_ids_desde_zero_em_ordem_de_leitura(grade, esperado):
    assert enumerar_bonus(grade) == esperado
