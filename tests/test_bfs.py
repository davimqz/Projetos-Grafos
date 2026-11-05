"""BFS (P2) — níveis corretos em grafo pequeno."""

import pytest

from src.graphs.graph import Grafo
from src.graphs.algorithms import bfs


def test_ordem_visita():
    grafo = Grafo()
    for inicio, fim in (
        ("A", "B"), ("A", "C"), ("A", "D"),
        ("B", "E"), ("C", "E"), ("C", "F"),
        ("D", "F"), ("F", "G"),
    ):
        grafo.adicionar_aresta(inicio, fim, 1)

    resultado = bfs(grafo, "A")

    assert resultado["ordem"] == ["A", "B", "C", "D", "E", "F", "G"]
    assert resultado["distancia"] == {
        "A": 0, "B": 1, "C": 1, "D": 1,
        "E": 2, "F": 2, "G": 3,
    }
    assert resultado["camadas"] == {
        0: ["A"], 1: ["B", "C", "D"], 2: ["E", "F"], 3: ["G"]
    }
    assert resultado["arvore"] == [
        ("A", "B"), ("A", "C"), ("A", "D"),
        ("B", "E"), ("C", "F"), ("F", "G"),
    ]
    assert resultado["pai"] == {
        "A": None, "B": "A", "C": "A", "D": "A",
        "E": "B", "F": "C", "G": "F",
    }
    assert resultado["nivel"] == resultado["distancia"]


def test_no_isolado():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_no("C")

    resultado = bfs(grafo, "A")

    assert resultado["ordem"] == ["A", "B"]
    assert resultado["distancia"]["C"] == float("inf")
    assert resultado["nivel"]["C"] is None
    assert resultado["pai"]["C"] is None
    assert resultado["estado"]["C"] == "NAO_VISITADO"


def test_ciclo():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_aresta("B", "C", 1)
    grafo.adicionar_aresta("C", "A", 1)

    resultado = bfs(grafo, "A")

    assert resultado["ordem"] == ["A", "B", "C"]
    assert len(resultado["arvore"]) == 2
    assert all(estado == "ENCERRADO" for estado in resultado["estado"].values())


def test_grafo_dirigido():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 1)

    resultado = bfs(grafo, "B")

    assert resultado["ordem"] == ["B"]
    assert resultado["distancia"]["A"] == float("inf")


def test_pesos():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 100)
    grafo.adicionar_aresta("A", "C", 1)
    grafo.adicionar_aresta("C", "B", -5)

    resultado = bfs(grafo, "A")

    assert resultado["distancia"]["B"] == 1
    assert resultado["pai"]["B"] == "A"
    assert resultado["distancia"]["C"] == 1


def test_origem_isolada():
    grafo = Grafo()
    grafo.adicionar_no("A")
    grafo.adicionar_no("B")

    resultado = bfs(grafo, "A")

    assert resultado["ordem"] == ["A"]
    assert resultado["camadas"] == {0: ["A"]}
    assert resultado["arvore"] == []
    assert resultado["estado"]["B"] == "NAO_VISITADO"


def test_origem_invalida():
    grafo = Grafo()
    grafo.adicionar_no("A")

    with pytest.raises(ValueError, match="não existe"):
        bfs(grafo, "B")


def test_grafo_vazio():
    with pytest.raises(ValueError, match="não existe"):
        bfs(Grafo(), "A")


def test_caminho_longo():
    grafo = Grafo()
    for i in range(2500):
        grafo.adicionar_aresta(str(i), str(i + 1), 1)

    resultado = bfs(grafo, "0")

    assert len(resultado["ordem"]) == 2501
    assert resultado["distancia"]["2500"] == 2500
    assert resultado["pai"]["2500"] == "2499"
    assert resultado["estado"]["2500"] == "ENCERRADO"
