"""Contratos do grafo dirigido, incluindo cópias, ordem e transformações."""

# [IA] Codex - testes de regressão da revisão dos métodos existentes de Grafo.
from random import Random
from typing import get_type_hints

import networkx as nx
import pytest

from src.graphs.graph import Grafo


@pytest.fixture
def grafo():
    grafo = Grafo()
    for no in ("a", "b", "isolado", "c"):
        grafo.adicionar_no(no)
    for origem, destino, peso in (
        ("a", "b", 2), ("a", "c", 0), ("c", "b", -3), ("c", "c", 1)
    ):
        grafo.adicionar_aresta(origem, destino, peso)
    return grafo


def test_anotacoes_podem_ser_resolvidas():
    assert get_type_hints(Grafo.transposto)["return"] is Grafo
    assert get_type_hints(Grafo.subgrafo_induzido)["return"] is Grafo


def test_insercao_preserva_ordem_e_pesos(grafo):
    grafo.adicionar_no("a")
    grafo.adicionar_aresta("a", "b", 2)
    assert grafo.nos() == ["a", "b", "isolado", "c"]
    assert grafo.vizinhos("a") == [("b", 2), ("c", 0)]
    assert grafo.arestas() == [
        ("a", "b", 2), ("a", "c", 0), ("c", "b", -3), ("c", "c", 1)
    ]
    assert grafo.vizinhos("b") == []


def test_aresta_cria_extremos_e_rejeita_peso_conflitante():
    grafo = Grafo()
    grafo.adicionar_aresta("origem", "destino", 1.5)
    assert grafo.nos() == ["origem", "destino"]
    with pytest.raises(ValueError, match="peso diferente"):
        grafo.adicionar_aresta("origem", "destino", 2)
    assert grafo.arestas() == [("origem", "destino", 1.5)]


def test_consultas_devolvem_listas_independentes(grafo):
    grafo.nos().clear()
    grafo.arestas().clear()
    grafo.vizinhos("a").clear()
    assert grafo.ordem() == 4
    assert grafo.tamanho() == 4
    assert grafo.vizinhos("a") == [("b", 2), ("c", 0)]


def test_metricas(grafo):
    assert grafo.ordem() == 4
    assert grafo.tamanho() == 4
    assert grafo.densidade() == pytest.approx(1 / 3)
    assert [grafo.grau_entrada(no) for no in grafo.nos()] == [0, 2, 0, 2]
    assert [grafo.grau_saida(no) for no in grafo.nos()] == [2, 0, 0, 2]


@pytest.mark.parametrize("nos", [[], ["isolado"]])
def test_grafo_sem_arestas(nos):
    grafo = Grafo()
    for no in nos:
        grafo.adicionar_no(no)
    assert grafo.nos() == nos
    assert grafo.arestas() == []
    assert grafo.tamanho() == 0
    assert grafo.densidade() == 0.0
    assert grafo.transposto().nos() == nos
    assert grafo.subgrafo_induzido(nos).nos() == nos


def test_laco_e_duplicata():
    grafo = Grafo()
    grafo.adicionar_aresta("a", "a", -1)
    grafo.adicionar_aresta("a", "a", -1)
    assert grafo.ordem() == 1
    assert grafo.tamanho() == 1
    assert grafo.grau_entrada("a") == grafo.grau_saida("a") == 1
    assert grafo.densidade() == 0.0
    assert grafo.transposto().arestas() == [("a", "a", -1)]


@pytest.mark.parametrize("metodo", ["vizinhos", "grau_entrada", "grau_saida"])
def test_consulta_no_inexistente(grafo, metodo):
    with pytest.raises(ValueError, match="Nó 'ausente' não existe no grafo"):
        getattr(grafo, metodo)("ausente")
    assert grafo.ordem() == 4


def test_transposto_preserva_ordem_pesos_e_isolados(grafo):
    transposto = grafo.transposto()
    assert transposto.nos() == ["b", "a", "c", "isolado"]
    assert transposto.vizinhos("b") == [("a", 2), ("c", -3)]
    assert transposto.vizinhos("c") == [("a", 0), ("c", 1)]
    assert transposto.vizinhos("isolado") == []
    transposto.adicionar_aresta("a", "isolado", 4)
    assert grafo.vizinhos("a") == [("b", 2), ("c", 0)]


@pytest.mark.parametrize("tipo", [list, tuple, iter, set])
def test_subgrafo_aceita_iteraveis_e_remove_repeticoes(grafo, tipo):
    subgrafo = grafo.subgrafo_induzido(tipo(["a", "c", "isolado", "a"]))
    assert set(subgrafo.nos()) == {"a", "c", "isolado"}
    assert set(subgrafo.arestas()) == {("a", "c", 0), ("c", "c", 1)}
    assert subgrafo.vizinhos("isolado") == []
    subgrafo.adicionar_aresta("isolado", "a", 4)
    assert grafo.vizinhos("isolado") == []
    assert grafo.vizinhos("a") == [("b", 2), ("c", 0)]


def test_subgrafo_preserva_ordem_existente(grafo):
    subgrafo = grafo.subgrafo_induzido(iter(["c", "a", "isolado", "b", "a"]))
    assert subgrafo.nos() == ["c", "b", "a", "isolado"]
    assert subgrafo.vizinhos("c") == [("b", -3), ("c", 1)]
    assert subgrafo.vizinhos("a") == [("b", 2), ("c", 0)]


def test_subgrafo_vazio_e_no_inexistente(grafo):
    assert grafo.subgrafo_induzido([]).nos() == []
    with pytest.raises(ValueError, match="Nó 'ausente' não existe no grafo"):
        grafo.subgrafo_induzido(iter(["a", "ausente"]))
    assert grafo.nos() == ["a", "b", "isolado", "c"]


@pytest.mark.parametrize("semente", range(5))
def test_metricas_e_transformacoes_conferem_com_networkx(semente):
    random = Random(semente)
    grafo = Grafo()
    referencia = nx.DiGraph()
    nos = [str(i) for i in range(20)]
    referencia.add_nodes_from(nos)
    for no in nos:
        grafo.adicionar_no(no)
    for origem in nos[:-1]:
        for destino in nos[:-1]:
            if random.random() < 0.3:
                peso = random.randint(-5, 5)
                grafo.adicionar_aresta(origem, destino, peso)
                referencia.add_edge(origem, destino, weight=peso)

    assert grafo.ordem() == referencia.number_of_nodes()
    assert grafo.tamanho() == referencia.number_of_edges()
    assert grafo.densidade() == pytest.approx(nx.density(referencia))
    for no in nos:
        assert grafo.grau_entrada(no) == referencia.in_degree(no)
        assert grafo.grau_saida(no) == referencia.out_degree(no)

    for resultado, esperado in (
        (grafo.transposto(), referencia.reverse()),
        (grafo.subgrafo_induzido(nos[::2]), referencia.subgraph(nos[::2])),
        (grafo.transposto().transposto(), referencia),
    ):
        assert set(resultado.nos()) == set(esperado.nodes)
        assert set(resultado.arestas()) == set(esperado.edges(data="weight"))
