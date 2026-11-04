"""DFS (P2) — detecção de ciclo e classificação de arcos em grafo dirigido:
árvore, retorno, avanço e cruzamento."""

import pytest

from src.graphs.graph import Grafo
from src.graphs.algorithms import dfs


def test_tipos_arestas():
    grafo = Grafo()
    for origem, destino in (
        ("A", "B"), ("A", "C"), ("A", "D"),
        ("B", "C"), ("C", "A"), ("D", "C"),
    ):
        grafo.adicionar_aresta(origem, destino, 1)

    resultado = dfs(grafo, "A")

    assert resultado["ordem"] == ["A", "B", "C", "D"]
    assert resultado["arcos"]["arvore"] == [("A", "B"), ("B", "C"), ("A", "D")]
    assert resultado["arcos"]["retorno"] == [("C", "A")]
    assert resultado["arcos"]["avanco"] == [("A", "C")]
    assert resultado["arcos"]["cruzamento"] == [("D", "C")]
    assert resultado["contagem_arcos"] == {
        "arvore": 3, "retorno": 1, "avanco": 1, "cruzamento": 1
    }
    assert resultado["tem_ciclo"] is True
    assert resultado["pai"] == {"A": None, "B": "A", "C": "B", "D": "A"}
    assert resultado["descoberta"] == {"A": 0, "B": 1, "C": 2, "D": 5}
    assert resultado["termino"] == {"A": 7, "B": 4, "C": 3, "D": 6}


def test_sem_ciclo():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 2)
    grafo.adicionar_aresta("B", "C", -5)

    resultado = dfs(grafo, "A")

    assert resultado["tem_ciclo"] is False
    assert resultado["arcos"]["retorno"] == []
    assert resultado["ordem"] == ["A", "B", "C"]
    assert resultado["estado"] == {
        "A": "ENCERRADO", "B": "ENCERRADO", "C": "ENCERRADO"
    }


def test_no_isolado():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_no("isolado")

    resultado = dfs(grafo, "A")

    assert resultado["ordem"] == ["A", "B"]
    assert resultado["estado"]["isolado"] == "NAO_VISITADO"
    assert resultado["descoberta"]["isolado"] is None
    assert resultado["termino"]["isolado"] is None


def test_todos_os_nos():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_no("isolado")

    resultado = dfs(grafo)

    assert resultado["ordem"] == ["A", "B", "isolado"]
    assert resultado["pai"]["isolado"] is None
    assert all(estado == "ENCERRADO" for estado in resultado["estado"].values())


def test_laco():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "A", 1)

    resultado = dfs(grafo, "A")

    assert resultado["arcos"]["retorno"] == [("A", "A")]
    assert resultado["tem_ciclo"] is True


def test_vazio():
    assert dfs(Grafo())["ordem"] == []
    assert dfs(Grafo())["tem_ciclo"] is False


def test_origem_invalida():
    grafo = Grafo()
    grafo.adicionar_no("A")

    with pytest.raises(ValueError, match="não existe"):
        dfs(grafo, "B")


# [IA] Codex – testes de profundidade, alcance de ciclos e floresta DFS.
def test_caminho_profundo():
    grafo = Grafo()
    for i in range(2000):
        grafo.adicionar_aresta(str(i), str(i + 1), 1)

    resultado = dfs(grafo, "0")

    assert len(resultado["ordem"]) == 2001
    assert resultado["ordem"] == [str(i) for i in range(2001)]
    assert resultado["pai"]["2000"] == "1999"
    assert resultado["contagem_arcos"]["arvore"] == 2000
    assert resultado["tem_ciclo"] is False


def test_ciclo_fora_do_alcance_da_origem():
    grafo = Grafo()
    for origem, destino in (("A", "B"), ("C", "D"), ("D", "C")):
        grafo.adicionar_aresta(origem, destino, 1)

    a_partir_de_a = dfs(grafo, "A")
    floresta = dfs(grafo)

    assert a_partir_de_a["ordem"] == ["A", "B"]
    assert a_partir_de_a["tem_ciclo"] is False
    assert a_partir_de_a["estado"]["C"] == "NAO_VISITADO"
    assert floresta["tem_ciclo"] is True
    assert floresta["arcos"]["retorno"] == [("D", "C")]


def test_arco_de_cruzamento_entre_arvores_da_floresta():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_aresta("C", "B", 1)

    resultado = dfs(grafo)

    assert resultado["ordem"] == ["A", "B", "C"]
    assert resultado["pai"] == {"A": None, "B": "A", "C": None}
    assert resultado["arcos"]["cruzamento"] == [("C", "B")]
    assert resultado["tem_ciclo"] is False
