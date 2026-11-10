"""DFS (P2) — detecção de ciclo e classificação de arcos em grafo dirigido:
árvore, retorno, avanço e cruzamento."""

import random

import networkx as nx
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
    resultado = dfs(Grafo())
    assert resultado["ordem"] == []
    assert resultado["tem_ciclo"] is False
    assert resultado["escopo_ciclo"] == "grafo_inteiro"


def test_origem_invalida():
    grafo = Grafo()
    grafo.adicionar_no("A")

    with pytest.raises(ValueError, match="não existe"):
        dfs(grafo, "B")

# [IA] ChatGPT - casos de regressão para a DFS com pilha explícita.
def test_caminho_longo():
    grafo = Grafo()
    for n in range(2500):
        grafo.adicionar_aresta(str(n), str(n + 1), 1)

    resultado = dfs(grafo, "0")

    assert len(resultado["ordem"]) == 2501
    assert resultado["ordem"][0] == "0"
    assert resultado["ordem"][-1] == "2500"
    assert resultado["termino"]["0"] == 5001
    assert resultado["tem_ciclo"] is False


def test_ciclo_fora_da_origem():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_aresta("X", "Y", 1)
    grafo.adicionar_aresta("Y", "X", 1)

    parcial = dfs(grafo, "A")
    completo = dfs(grafo)

    assert parcial["tem_ciclo"] is False
    assert parcial["escopo_ciclo"] == "alcancaveis_da_origem"
    assert parcial["estado"]["X"] == "NAO_VISITADO"
    assert completo["tem_ciclo"] is True
    assert completo["escopo_ciclo"] == "grafo_inteiro"
    assert completo["arcos"]["retorno"] == [("Y", "X")]


def test_outra_origem():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_aresta("B", "C", 1)
    grafo.adicionar_aresta("C", "B", 1)

    resultado = dfs(grafo, "B")

    assert resultado["ordem"] == ["B", "C"]
    assert resultado["tem_ciclo"] is True
    assert resultado["estado"]["A"] == "NAO_VISITADO"


# [IA] Codex - teste de cruzamento entre árvores da floresta DFS.
def test_arco_de_cruzamento_entre_arvores_da_floresta():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_aresta("C", "B", 1)

    resultado = dfs(grafo)

    assert resultado["ordem"] == ["A", "B", "C"]
    assert resultado["pai"] == {"A": None, "B": "A", "C": None}
    assert resultado["arcos"]["cruzamento"] == [("C", "B")]
    assert resultado["tem_ciclo"] is False


@pytest.mark.parametrize("semente", range(10))
def test_dfs_com_networkx_como_oraculo(semente):
    """Confere árvore DFS, descoberta e ciclos em grafos dirigidos."""
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
        resultado = dfs(grafo, origem)
        alcancaveis = nx.descendants(referencia, origem) | {origem}
        recorte = referencia.subgraph(alcancaveis)

        assert resultado["ordem"] == list(
            nx.dfs_preorder_nodes(referencia, source=origem)
        )
        assert resultado["arcos"]["arvore"] == list(
            nx.dfs_edges(referencia, source=origem)
        )
        assert resultado["tem_ciclo"] == (
            not nx.is_directed_acyclic_graph(recorte)
        )

    completo = dfs(grafo)
    assert completo["arcos"]["arvore"] == list(nx.dfs_edges(referencia))
    assert completo["tem_ciclo"] == (
        not nx.is_directed_acyclic_graph(referencia)
    )

    # [IA] Codex - invariantes de tempos e classificação de todos os arcos.
    for resultado in (dfs(grafo, "0"), completo):
        visitados = set(resultado["ordem"])
        descoberta = resultado["descoberta"]
        termino = resultado["termino"]
        tempos = [tempo for no in visitados for tempo in (descoberta[no], termino[no])]
        assert sorted(tempos) == list(range(2 * len(visitados)))
        for no in nos:
            if no in visitados:
                assert descoberta[no] < termino[no]
                assert resultado["estado"][no] == "ENCERRADO"
            else:
                assert descoberta[no] is None
                assert termino[no] is None
                assert resultado["pai"][no] is None
                assert resultado["estado"][no] == "NAO_VISITADO"

        classificados = [arco for arcos in resultado["arcos"].values() for arco in arcos]
        esperados = {(vi, vj) for vi, vj in referencia.edges if vi in visitados}
        assert set(classificados) == esperados
        assert len(classificados) == len(esperados)
        assert resultado["contagem_arcos"] == {
            tipo: len(arcos) for tipo, arcos in resultado["arcos"].items()
        }
        for tipo, arcos in resultado["arcos"].items():
            for vi, vj in arcos:
                if tipo == "arvore":
                    assert resultado["pai"][vj] == vi
                    assert descoberta[vi] < descoberta[vj] < termino[vj] < termino[vi]
                elif tipo == "retorno":
                    assert descoberta[vj] <= descoberta[vi] < termino[vi] <= termino[vj]
                elif tipo == "avanco":
                    assert resultado["pai"][vj] != vi
                    assert descoberta[vi] < descoberta[vj] < termino[vj] < termino[vi]
                else:
                    assert termino[vj] < descoberta[vi]
