"""Bellman-Ford (P2):
(i) pesos negativos sem ciclo negativo -> distâncias corretas;
(ii) com ciclo negativo -> flag levantada e ciclo retornado."""

# [IA] ChatGPT - casos de teste sugeridos e escritos para o Bellman-Ford.

import pytest

from src.graphs.graph import Grafo
from src.graphs.algorithms import bellman_ford


def test_pesos_negativos_sem_ciclo():
    grafo = Grafo()
    for vi, vj, peso in (
        ("A", "B", 3), ("B", "C", -5), ("A", "C", 4),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = bellman_ford(grafo, "A")

    assert resultado["distancia"] == {"A": 0, "B": 3, "C": -2}
    assert resultado["pai"] == {"A": None, "B": "A", "C": "B"}
    assert resultado["tem_ciclo_negativo"] is False
    assert resultado["ciclo_negativo"] == []
    assert resultado["custo_ciclo"] is None


def test_exemplo_aula_06():
    grafo = Grafo()
    for vi, vj, peso in (
        ("A", "B", 5), ("A", "C", -2), ("C", "B", 2),
        ("B", "D", 1), ("D", "C", 2), ("C", "E", 3),
        ("D", "E", 7), ("D", "F", 3), ("E", "F", 10),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = bellman_ford(grafo, "A")
    assert resultado["distancia"]["F"] == 4
    assert [resultado["pai"][no] for no in ("F", "D", "B", "C")] == [
        "D", "B", "C", "A"
    ]
    assert resultado["status"] == "OK"


def test_ciclo_negativo_alcancavel():
    grafo = Grafo()
    for vi, vj, peso in (
        ("A", "B", 1), ("B", "C", -2), ("C", "B", 0),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = bellman_ford(grafo, "A")

    assert resultado["status"] == "CICLO_NEGATIVO"
    assert resultado["tem_ciclo_negativo"] is True
    assert resultado["ciclo_negativo"][0] == resultado["ciclo_negativo"][-1]
    assert set(resultado["ciclo_negativo"]) == {"B", "C"}
    assert resultado["custo_ciclo"] == -2


def test_ciclo_negativo_inacessivel():
    grafo = Grafo()
    for vi, vj, peso in (
        ("A", "B", 1), ("X", "Y", -2), ("Y", "X", 1),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = bellman_ford(grafo, "A")

    assert resultado["tem_ciclo_negativo"] is False
    assert resultado["distancia"]["X"] == float("inf")
    assert resultado["distancia"]["Y"] == float("inf")


def test_laco_negativo():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "A", -1)
    grafo.adicionar_aresta("A", "B", 2)

    resultado = bellman_ford(grafo, "A")

    assert resultado["ciclo_negativo"] == ["A", "A"]
    assert resultado["custo_ciclo"] == -1


def test_no_isolado():
    grafo = Grafo()
    grafo.adicionar_no("A")
    grafo.adicionar_no("B")

    resultado = bellman_ford(grafo, "A")

    assert resultado["distancia"] == {"A": 0, "B": float("inf")}
    assert resultado["pai"] == {"A": None, "B": None}


@pytest.mark.parametrize("origem_invalida", ["X", "B"])
def test_origem_invalida(origem_invalida):
    grafo = Grafo()
    grafo.adicionar_no("A")

    with pytest.raises(ValueError, match="não existe"):
        bellman_ford(grafo, origem_invalida)


def test_grafo_vazio():
    with pytest.raises(ValueError, match="não existe"):
        bellman_ford(Grafo(), "A")
