"""BFS (P2) — níveis corretos em grafo pequeno."""
import random

import networkx as nx
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

# [IA] ChatGPT - casos de teste para validar a BFS.

def test_laco_na_origem_nao_redescobre_inicio():
    """O laço A->A não deve alterar o pai ou o nível da origem."""
    grafo = Grafo()
    grafo.adicionar_aresta("A", "A", 1)
    grafo.adicionar_aresta("A", "B", 1)

    resultado = bfs(grafo, "A")

    assert resultado["ordem"] == ["A", "B"]
    assert resultado["pai"] == {"A": None, "B": "A"}
    assert resultado["distancia"] == {"A": 0, "B": 1}
    assert resultado["nivel"] == {"A": 0, "B": 1}
    assert resultado["camadas"] == {0: ["A"], 1: ["B"]}
    assert resultado["arvore"] == [("A", "B")]


@pytest.mark.parametrize("semente", range(10))
def test_bfs_com_networkx_como_oraculo(semente):
    """Confere distâncias e árvore BFS em grafos dirigidos reproduzíveis."""
    aleatorio = random.Random(semente)
    grafo = Grafo()
    referencia = nx.DiGraph()
    nos = [str(i) for i in range(9)]

    for no in nos:
        grafo.adicionar_no(no)
        referencia.add_node(no)

    for inicio in nos:
        for fim in nos:
            if aleatorio.random() < 0.2:
                peso = aleatorio.choice([-3, 0, 1, 5])
                grafo.adicionar_aresta(inicio, fim, peso)
                referencia.add_edge(inicio, fim, weight=peso)

    for origem in ("0", "4", "8"):
        resultado = bfs(grafo, origem)
        distancias = nx.single_source_shortest_path_length(referencia, origem)
        arestas_arvore = list(nx.bfs_edges(referencia, origem))

        esperado_distancia = {
            no: distancias.get(no, float("inf")) for no in nos
        }
        esperado_pai = {no: None for no in nos}
        for pai, filho in arestas_arvore:
            esperado_pai[filho] = pai

        assert resultado["distancia"] == esperado_distancia
        assert resultado["nivel"] == {no: distancias.get(no) for no in nos}
        assert resultado["pai"] == esperado_pai
        assert resultado["arvore"] == arestas_arvore
