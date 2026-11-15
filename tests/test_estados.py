"""Contratos da modelagem em mapas artificiais com resultados explícitos.

O mapa mínimo e sua contagem autoral para o PDF ainda devem ser conferidos
pelo grupo; os exemplos destes testes foram sugeridos com apoio de IA.
"""

# [IA] Codex - testes da modelagem escrita pelo integrante e regressões dos pesos.
import pytest

from src.graphs.estados import (
    Estado,
    Transicao,
    construir_grafo_estados,
    construir_grafo_posicoes,
    enumerar_consumiveis,
    gerar_transicoes,
    movimentos_possiveis,
    rotular_estado,
    rotular_posicao,
)
from src.graphs.io import validar_mapa


def _estado(linha, coluna, chaves="", bonus=()):
    return Estado(linha, coluna, frozenset(chaves), frozenset(bonus))


@pytest.mark.parametrize("posicao, esperado", [
    ((0, 0), "(0,0)"), ((1, 2), "(1,2)"), ((30, 70), "(30,70)"),
])
def test_rotular_posicao(posicao, esperado):
    assert rotular_posicao(posicao) == esperado


@pytest.mark.parametrize("estado, esperado", [
    (_estado(0, 0), "(0,0)|-|{}"),
    (_estado(3, 5, "ba", [2, 0]), "(3,5)|ab|{0,2}"),
    (_estado(1, 2, "dcba"), "(1,2)|abcd|{}"),
    (_estado(30, 70, bonus=[10, 2, 0]), "(30,70)|-|{0,2,10}"),
    (_estado(1, 1, "a", [0]), "(1,1)|a|{0}"),
])
def test_rotular_estado_ordena_conjuntos_e_trata_vazios(estado, esperado):
    assert rotular_estado(estado) == esperado


@pytest.mark.parametrize("grade, opcao, esperado", [
    (["S*+", ".+G"], False, {(0, 2): 0, (1, 1): 1}),
    (["S*+", ".+G"], True, {(0, 2): 0, (1, 1): 1, (0, 1): 2}),
    (["S.G"], False, {}),
    (["S.G"], True, {}),
    (["S*G"], False, {}),
    (["S*G"], True, {(0, 1): 0}),
    (["S*+", "*+G"], True, {(0, 2): 0, (1, 1): 1, (0, 1): 2, (1, 0): 3}),
    (["S++G"], True, {(0, 1): 0, (0, 2): 1}),
])
def test_enumerar_consumiveis_preserva_ids_dos_bonus(grade, opcao, esperado):
    validar_mapa(grade)
    original = grade.copy()
    assert enumerar_consumiveis(grade, fonte_consumivel=opcao) == esperado
    assert grade == original


def test_enumerar_consumiveis_ignora_fontes_por_padrao():
    assert enumerar_consumiveis(["S*+G"]) == {(0, 2): 0}


@pytest.mark.parametrize("grade, posicao, esperado", [
    (["S..", "...", "..G"], (1, 1),
     [("N", (0, 1)), ("L", (1, 2)), ("S", (2, 1)), ("O", (1, 0))]),
    (["S..", "..G"], (0, 0), [("L", (0, 1)), ("S", (1, 0))]),
    (["S.G", "..."], (1, 2), [("N", (0, 2)), ("O", (1, 1))]),
    (["S#G", "#.#", ".#."], (1, 1), []),
    (["S#.", "...", ".#G"], (1, 1), [("L", (1, 2)), ("O", (1, 0))]),
    (["S..", ".G.", "..."], (1, 1), []),
    (["SAG"], (0, 0), [("L", (0, 1))]),
    (["S^G"], (0, 0), [("L", (0, 1))]),
    (["S..", ".^.", "..G"], (1, 1), [("N", (0, 1))]),
    (["S..", ".>.", "..G"], (1, 1), [("L", (1, 2))]),
    (["S..", ".v.", "..G"], (1, 1), [("S", (2, 1))]),
    (["S..", ".<.", "..G"], (1, 1), [("O", (1, 0))]),
    (["S#.", ".^.", "..G"], (1, 1), []),
    (["S..", ".>#", "..G"], (1, 1), []),
    (["S..", ".v.", ".#G"], (1, 1), []),
    (["S..", "#<.", "..G"], (1, 1), []),
    (["^SG"], (0, 0), []),
    (["SG>"], (0, 2), []),
    (["S", "G", "v"], (2, 0), []),
    (["<SG"], (0, 0), []),
])
def test_movimentos_respeitam_geometria_e_ordem(grade, posicao, esperado):
    validar_mapa(grade)
    original = grade.copy()
    assert movimentos_possiveis(grade, posicao) == esperado
    assert grade == original


@pytest.mark.parametrize("grade, portas, nos, arcos", [
    (["SG"], "chao", {"(0,0)", "(0,1)"},
     {("(0,0)", "(0,1)", 1)}),
    (["SAG"], "chao", {"(0,0)", "(0,1)", "(0,2)"},
     {("(0,0)", "(0,1)", 1), ("(0,1)", "(0,0)", 1),
      ("(0,1)", "(0,2)", 1)}),
    (["SAG"], "parede", {"(0,0)", "(0,2)"}, set()),
    (["S>G"], "chao", {"(0,0)", "(0,1)", "(0,2)"},
     {("(0,0)", "(0,1)", 1), ("(0,1)", "(0,2)", 1)}),
    (["S#G", "###", "..#"], "chao",
     {"(0,0)", "(0,2)", "(2,0)", "(2,1)"},
     {("(2,0)", "(2,1)", 1), ("(2,1)", "(2,0)", 1)}),
])
def test_grafo_posicoes_inclui_isolados_e_respeita_variante(grade, portas, nos, arcos):
    validar_mapa(grade)
    original = grade.copy()
    grafo = construir_grafo_posicoes(grade, portas=portas)
    assert set(grafo.nos()) == nos
    assert set(grafo.arestas()) == arcos
    assert grafo.tamanho() == len(arcos)
    assert grade == original


def test_grafo_posicoes_custos_sao_da_casa_destino():
    grafo = construir_grafo_posicoes(["S.,~+*G"])
    assert grafo.vizinhos("(0,2)") == [("(0,3)", 5), ("(0,1)", 1)]
    assert grafo.vizinhos("(0,3)") == [("(0,4)", -4), ("(0,2)", 3)]
    assert grafo.vizinhos("(0,4)") == [("(0,5)", -2), ("(0,3)", 5)]
    assert grafo.vizinhos("(0,5)") == [("(0,6)", 1), ("(0,4)", -4)]
    assert grafo.vizinhos("(0,6)") == []


def test_grafo_posicoes_exclui_todas_as_portas_sem_excluir_chaves():
    grafo = construir_grafo_posicoes(["SabcdABCDG"], portas="parede")
    assert set(grafo.nos()) == {
        "(0,0)", "(0,1)", "(0,2)", "(0,3)", "(0,4)", "(0,9)",
    }
    assert grafo.vizinhos("(0,4)") == [("(0,3)", 1)]


def test_grafo_posicoes_recusa_variante_invalida():
    with pytest.raises(ValueError, match="chao.*parede"):
        construir_grafo_posicoes(["SG"], portas="invalida")


@pytest.mark.parametrize("grade, estado, opcao, esperado", [
    (["S.G"], _estado(0, 0), False, [Transicao(_estado(0, 1), "L", ".", 1)]),
    (["S~G"], _estado(0, 0), False, [Transicao(_estado(0, 1), "L", "~", 5)]),
    (["S,G"], _estado(0, 0), False, [Transicao(_estado(0, 1), "L", ",", 3)]),
    (["SaG"], _estado(0, 0), False, [Transicao(_estado(0, 1, "a"), "L", "a", 1)]),
    (["SaG"], _estado(0, 0, "a"), False,
     [Transicao(_estado(0, 1, "a"), "L", "a", 1)]),
    (["SAaG"], _estado(0, 0), False, []),
    (["SaAG"], _estado(0, 1, "a"), False,
     [Transicao(_estado(0, 2, "a"), "L", "A", 1),
      Transicao(_estado(0, 0, "a"), "O", "S", 1)]),
    (["S+G"], _estado(0, 0), False,
     [Transicao(_estado(0, 1, bonus=[0]), "L", "+", -4)]),
    (["S+G"], _estado(0, 0, bonus=[0]), False,
     [Transicao(_estado(0, 1, bonus=[0]), "L", "+", 1)]),
    (["S*G"], _estado(0, 0), False,
     [Transicao(_estado(0, 1), "L", "*", -2)]),
    (["S*G"], _estado(0, 0), True,
     [Transicao(_estado(0, 1, bonus=[0]), "L", "*", -2)]),
    (["S*G"], _estado(0, 0, bonus=[0]), True,
     [Transicao(_estado(0, 1, bonus=[0]), "L", "*", 1)]),
    (["SG"], _estado(0, 1), False, []),
    (["S^G"], _estado(0, 1), False, []),
    (["S>G"], _estado(0, 1), False, [Transicao(_estado(0, 2), "L", "G", 1)]),
])
def test_transicoes_aplicam_coletas_e_pesos(grade, estado, opcao, esperado):
    validar_mapa(grade)
    original = grade.copy()
    estado_original = (estado.linha, estado.coluna, estado.chaves, estado.bonus)
    consumiveis = enumerar_consumiveis(grade, fonte_consumivel=opcao)
    consumiveis_original = consumiveis.copy()
    assert gerar_transicoes(
        grade, estado, consumiveis, fonte_consumivel=opcao
    ) == esperado
    assert grade == original
    assert consumiveis == consumiveis_original
    assert (estado.linha, estado.coluna, estado.chaves, estado.bonus) == estado_original


def test_transicoes_nao_compartilham_coleta_entre_vizinhos():
    grade = ["S+a", "*.,", ".~G"]
    transicoes = gerar_transicoes(grade, _estado(1, 1), enumerar_consumiveis(grade))
    assert transicoes == [
        Transicao(_estado(0, 1, bonus=[0]), "N", "+", -4),
        Transicao(_estado(1, 2), "L", ",", 3),
        Transicao(_estado(2, 1), "S", "~", 5),
        Transicao(_estado(1, 0), "O", "*", -2),
    ]


def test_transicoes_fonte_tem_id_distinto_e_preserva_bonus_anterior():
    grade = ["S+G", ".*."]
    consumiveis = enumerar_consumiveis(grade, fonte_consumivel=True)
    assert gerar_transicoes(
        grade, _estado(1, 0, bonus=[0]), consumiveis, fonte_consumivel=True
    ) == [
        Transicao(_estado(0, 0, bonus=[0]), "N", "S", 1),
        Transicao(_estado(1, 1, bonus=[0, 1]), "L", "*", -2),
    ]


@pytest.mark.parametrize("grade, opcao, nos, arcos", [
    (["SG"], False, {"(0,0)|-|{}", "(0,1)|-|{}"},
     {("(0,0)|-|{}", "(0,1)|-|{}", 1), ("(0,1)|-|{}", "ALVO", 0)}),
    (["S.G"], False, {"(0,0)|-|{}", "(0,1)|-|{}", "(0,2)|-|{}"},
     {("(0,0)|-|{}", "(0,1)|-|{}", 1), ("(0,1)|-|{}", "(0,0)|-|{}", 1),
      ("(0,1)|-|{}", "(0,2)|-|{}", 1), ("(0,2)|-|{}", "ALVO", 0)}),
    (["S#G"], False, {"(0,0)|-|{}"}, set()),
    (["SG."], False, {"(0,0)|-|{}", "(0,1)|-|{}"},
     {("(0,0)|-|{}", "(0,1)|-|{}", 1), ("(0,1)|-|{}", "ALVO", 0)}),
    (["S^G"], False, {"(0,0)|-|{}", "(0,1)|-|{}"},
     {("(0,0)|-|{}", "(0,1)|-|{}", 1)}),
    (["GSG"], False, {"(0,0)|-|{}", "(0,1)|-|{}", "(0,2)|-|{}"},
     {("(0,1)|-|{}", "(0,2)|-|{}", 1), ("(0,1)|-|{}", "(0,0)|-|{}", 1),
      ("(0,0)|-|{}", "ALVO", 0), ("(0,2)|-|{}", "ALVO", 0)}),
    (["S+G"], False,
     {"(0,0)|-|{}", "(0,1)|-|{0}", "(0,0)|-|{0}", "(0,2)|-|{0}"},
     {("(0,0)|-|{}", "(0,1)|-|{0}", -4),
      ("(0,1)|-|{0}", "(0,0)|-|{0}", 1),
      ("(0,1)|-|{0}", "(0,2)|-|{0}", 1),
      ("(0,0)|-|{0}", "(0,1)|-|{0}", 1), ("(0,2)|-|{0}", "ALVO", 0)}),
    (["S*G"], False, {"(0,0)|-|{}", "(0,1)|-|{}", "(0,2)|-|{}"},
     {("(0,0)|-|{}", "(0,1)|-|{}", -2), ("(0,1)|-|{}", "(0,0)|-|{}", 1),
      ("(0,1)|-|{}", "(0,2)|-|{}", 1), ("(0,2)|-|{}", "ALVO", 0)}),
    (["S*G"], True,
     {"(0,0)|-|{}", "(0,1)|-|{0}", "(0,0)|-|{0}", "(0,2)|-|{0}"},
     {("(0,0)|-|{}", "(0,1)|-|{0}", -2),
      ("(0,1)|-|{0}", "(0,0)|-|{0}", 1),
      ("(0,1)|-|{0}", "(0,2)|-|{0}", 1),
      ("(0,0)|-|{0}", "(0,1)|-|{0}", 1), ("(0,2)|-|{0}", "ALVO", 0)}),
])
def test_grafo_estados_tem_exatamente_os_nos_e_arcos_esperados(grade, opcao, nos, arcos):
    validar_mapa(grade)
    original = grade.copy()
    grafo, estados = construir_grafo_estados(grade, fonte_consumivel=opcao)
    assert set(estados) == nos
    assert set(grafo.nos()) == nos | {"ALVO"}
    assert set(grafo.arestas()) == arcos
    assert grafo.ordem() == len(nos) + 1
    assert grafo.tamanho() == len(arcos)
    assert grafo.vizinhos("ALVO") == []
    assert all(rotular_estado(estado) == rotulo for rotulo, estado in estados.items())
    assert grade == original


def test_grafo_estados_chave_muda_camada_e_permanece_no_retorno():
    grafo, estados = construir_grafo_estados(["SaAG"])
    # Cinco estados fisicos e sete arcos contando a ligacao virtual.
    assert estados == {
        "(0,0)|-|{}": _estado(0, 0),
        "(0,1)|a|{}": _estado(0, 1, "a"),
        "(0,2)|a|{}": _estado(0, 2, "a"),
        "(0,0)|a|{}": _estado(0, 0, "a"),
        "(0,3)|a|{}": _estado(0, 3, "a"),
    }
    assert grafo.ordem() == 6
    assert grafo.tamanho() == 7
    assert grafo.vizinhos("(0,0)|-|{}") == [("(0,1)|a|{}", 1)]
    assert grafo.vizinhos("(0,1)|a|{}") == [
        ("(0,2)|a|{}", 1), ("(0,0)|a|{}", 1),
    ]
    assert grafo.vizinhos("(0,2)|a|{}") == [
        ("(0,3)|a|{}", 1), ("(0,1)|a|{}", 1),
    ]
    assert grafo.vizinhos("(0,0)|a|{}") == [("(0,1)|a|{}", 1)]
    assert grafo.vizinhos("(0,3)|a|{}") == [("ALVO", 0)]


@pytest.mark.parametrize("construir", [construir_grafo_posicoes, construir_grafo_estados])
def test_construcao_preserva_ordem_dos_vizinhos(construir):
    resultado = construir(["S..", "...", "..G"])
    if construir is construir_grafo_estados:
        grafo, _ = resultado
        assert grafo.vizinhos("(1,1)|-|{}") == [
            ("(0,1)|-|{}", 1), ("(1,2)|-|{}", 1),
            ("(2,1)|-|{}", 1), ("(1,0)|-|{}", 1),
        ]
    else:
        assert resultado.vizinhos("(1,1)") == [
            ("(0,1)", 1), ("(1,2)", 1), ("(2,1)", 1), ("(1,0)", 1),
        ]


def test_grafo_estados_inicio_fora_da_origem_e_caminhos_convergentes():
    grafo, estados = construir_grafo_estados(["G.", ".S"])
    assert estados["(1,1)|-|{}"] == _estado(1, 1)
    assert len(estados) == 4
    assert grafo.ordem() == 5
    assert grafo.tamanho() == 7
    assert grafo.vizinhos("(0,1)|-|{}") == [
        ("(1,1)|-|{}", 1), ("(0,0)|-|{}", 1),
    ]
    assert grafo.vizinhos("(1,0)|-|{}") == [
        ("(0,0)|-|{}", 1), ("(1,1)|-|{}", 1),
    ]
