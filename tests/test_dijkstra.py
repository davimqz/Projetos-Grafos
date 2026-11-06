"""Dijkstra (P2) — caminhos corretos com pesos >= 0; recusa grafo com peso negativo."""

# [IA] ChatGPT - casos de teste de regressão e comparação com NetworkX.

import random

import pytest

from src.graphs.algorithms import dijkstra
from src.graphs.graph import Grafo


def test_menor_caminho_pode_ter_mais_arestas():
    grafo = Grafo()
    for vi, vj, peso in (
        ("A", "B", 20), ("A", "C", 2), ("C", "D", 1),
        ("D", "B", 2), ("B", "E", 3), ("C", "E", 30),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = dijkstra(grafo, "A")

    assert resultado["distancia"] == {"A": 0, "B": 5, "C": 2, "D": 3, "E": 8}
    assert resultado["pai"] == {"A": None, "B": "D", "C": "A", "D": "C", "E": "B"}
    assert resultado["ordem"] == ["A", "C", "D", "B", "E"]
    assert resultado["status"] == "OK"


def test_exemplo_aula_06_dijkstra():
    grafo = Grafo()
    for vi, vj, peso in (
        ("A", "B", 2), ("A", "C", 4), ("B", "C", 1),
        ("B", "D", 4), ("B", "E", 3), ("C", "E", 1),
        ("E", "D", 3), ("D", "F", 2), ("E", "F", 1),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = dijkstra(grafo, "A")
    assert resultado["distancia"]["F"] == 5
    assert resultado["pai"]["F"] == "E"
    assert resultado["pai"]["E"] == "C"
    assert resultado["pai"]["C"] == "B"


def test_peso_zero_e_laco_na_origem():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "A", 0)
    grafo.adicionar_aresta("A", "B", 0)
    grafo.adicionar_aresta("B", "C", 2)
    resultado = dijkstra(grafo, "A")

    assert resultado["distancia"] == {"A": 0, "B": 0, "C": 2}
    assert resultado["pai"] == {"A": None, "B": "A", "C": "B"}
    assert resultado["ordem"] == ["A", "B", "C"]


def test_no_inacessivel_e_grafo_dirigido():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 5)
    grafo.adicionar_no("C")
    resultado = dijkstra(grafo, "B")
    assert resultado["distancia"]["A"] == float("inf")
    assert resultado["distancia"]["C"] == float("inf")
    assert resultado["distancia"]["B"] == 0
    assert resultado["pai"]["A"] is None
    assert resultado["ordem"] == ["B"]


@pytest.mark.parametrize("arestas", [
    [("A", "B", -1)],
    [("A", "B", 2), ("X", "Y", -1)],
])
def test_recusa_peso_negativo_mesmo_se_inacessivel(arestas):
    grafo = Grafo()
    for vi, vj, peso in arestas:
        grafo.adicionar_aresta(vi, vj, peso)

    with pytest.raises(ValueError, match="peso negativo"):
        dijkstra(grafo, "A")


def test_origem_invalida():
    grafo = Grafo()
    grafo.adicionar_no("A")
    with pytest.raises(ValueError, match="não existe"):
        dijkstra(grafo, "X")


def test_grafo_vazio():
    with pytest.raises(ValueError, match="não existe"):
        dijkstra(Grafo(), "A")


def test_atualizacao_de_prioridade():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 9)
    grafo.adicionar_aresta("A", "C", 1)
    grafo.adicionar_aresta("C", "B", 2)
    grafo.adicionar_aresta("B", "D", 1)
    grafo.adicionar_aresta("C", "D", 20)
    resultado = dijkstra(grafo, "A")
    assert resultado["distancia"]["B"] == 3
    assert resultado["distancia"]["D"] == 4
    assert resultado["ordem"] == ["A", "C", "B", "D"]
    assert resultado["ordem"].count("B") == 1


@pytest.mark.parametrize("semente", range(30))
def test_distancias_com_networkx(semente):
    """Confere distâncias e validade dos predecessores com um oráculo independente."""
    nx = pytest.importorskip("networkx")
    sorteio = random.Random(semente)
    grafo = Grafo()
    oraculo = nx.DiGraph()
    nos = [f"N{i}" for i in range(12)]
    for no in nos:
        grafo.adicionar_no(no)
        oraculo.add_node(no)

    for vi in nos:
        for vj in nos:
            if sorteio.random() < 0.18:
                peso = sorteio.randint(0, 25)
                grafo.adicionar_aresta(vi, vj, peso)
                oraculo.add_edge(vi, vj, weight=peso)

    origem = nos[semente % len(nos)]
    resultado = dijkstra(grafo, origem)
    esperado = nx.single_source_dijkstra_path_length(oraculo, origem)

    for no in nos:
        assert resultado["distancia"][no] == esperado.get(no, float("inf"))
        if no == origem or no not in esperado:
            assert resultado["pai"][no] is None
        else:
            pai = resultado["pai"][no]
            assert pai is not None
            assert oraculo.has_edge(pai, no)
            assert resultado["distancia"][pai] + oraculo[pai][no]["weight"] == resultado["distancia"][no]

    assert set(resultado["ordem"]) == set(esperado)
    assert len(resultado["ordem"]) == len(set(resultado["ordem"]))


# [IA] Codex - regressões para desempate, ciclo zero e pesos fracionários.
def test_empate_preserva_ordem_de_insercao_e_primeiro_pai():
    grafo = Grafo()
    for vi, vj, peso in (
        ("A", "Z", 1), ("A", "B", 1), ("Z", "F", 2), ("B", "F", 2),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = dijkstra(grafo, "A")

    assert resultado["ordem"] == ["A", "Z", "B", "F"]
    assert resultado["pai"]["F"] == "Z"
    assert resultado["distancia"]["F"] == 3


def test_ciclo_zero_nao_cria_ciclo_nos_predecessores():
    grafo = Grafo()
    for vi, vj, peso in (
        ("A", "B", 0), ("B", "C", 0), ("C", "A", 0), ("C", "D", 2),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = dijkstra(grafo, "A")

    assert resultado["distancia"] == {"A": 0, "B": 0, "C": 0, "D": 2}
    assert resultado["pai"] == {"A": None, "B": "A", "C": "B", "D": "C"}
    assert resultado["ordem"] == ["A", "B", "C", "D"]


def test_pesos_fracionarios():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 0.9)
    grafo.adicionar_aresta("A", "C", 0.1)
    grafo.adicionar_aresta("C", "B", 0.2)

    resultado = dijkstra(grafo, "A")

    assert resultado["distancia"]["B"] == pytest.approx(0.3)
    assert resultado["pai"]["B"] == "C"
