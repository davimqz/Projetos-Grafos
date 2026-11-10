"""Bellman-Ford (P2):
(i) pesos negativos sem ciclo negativo -> distâncias corretas;
(ii) com ciclo negativo -> flag levantada e ciclo retornado."""

# [IA] ChatGPT - casos de teste sugeridos e escritos para o Bellman-Ford.

import random

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


def test_caminho_precisa_de_todas_as_n_menos_uma_passadas():
    grafo = Grafo()
    # A ordem dos nós faz cada passada alcançar apenas mais um nó do caminho.
    for no in ("E", "D", "C", "B", "A"):
        grafo.adicionar_no(no)
    for vi, vj, peso in (
        ("A", "B", 2), ("B", "C", -1), ("C", "D", 3), ("D", "E", -2),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = bellman_ford(grafo, "A")

    assert resultado["distancia"] == {"A": 0, "B": 2, "C": 1, "D": 4, "E": 2}
    assert resultado["pai"] == {"A": None, "B": "A", "C": "B", "D": "C", "E": "D"}
    assert resultado["status"] == "OK"
    assert resultado["tem_ciclo_negativo"] is False
    assert resultado["ciclo_negativo"] == []
    assert resultado["custo_ciclo"] is None


def test_ordem_do_ciclo_negativo_respeita_arcos_dirigidos():
    grafo = Grafo()
    # Três nós, sem arcos reversos: inverter o ciclo deve falhar neste teste.
    for vi, vj, peso in (
        ("A", "B", 1), ("B", "C", -4), ("C", "D", 1), ("D", "B", 1),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = bellman_ford(grafo, "A")
    ciclo = resultado["ciclo_negativo"]

    assert resultado["tem_ciclo_negativo"] is True
    assert len(ciclo) == 4
    assert ciclo[0] == ciclo[-1]
    assert set(ciclo[:-1]) == {"B", "C", "D"}
    for vi, vj in zip(ciclo, ciclo[1:]):
        assert vj in dict(grafo.vizinhos(vi))


def test_custo_do_ciclo_formado_antes_da_verificacao_final():
    grafo = Grafo()
    # B -> C -> D -> B já fecha o ciclo na primeira passada de relaxamento.
    # A cauda também permite que o último nó atualizado fique fora do ciclo.
    for vi, vj, peso in (
        ("A", "B", 2), ("B", "C", -5), ("C", "D", 1), ("D", "B", 1),
        ("D", "E", 4), ("E", "F", 1),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = bellman_ford(grafo, "A")
    ciclo = resultado["ciclo_negativo"]

    assert resultado["status"] == "CICLO_NEGATIVO"
    assert resultado["tem_ciclo_negativo"] is True
    assert len(ciclo) == 4
    assert ciclo[0] == ciclo[-1]
    assert set(ciclo[:-1]) == {"B", "C", "D"}
    custo_dos_arcos = sum(
        dict(grafo.vizinhos(vi))[vj] for vi, vj in zip(ciclo, ciclo[1:])
    )
    assert resultado["custo_ciclo"] == custo_dos_arcos == -3


def test_ciclo_de_custo_zero_nao_e_negativo():
    grafo = Grafo()
    for vi, vj, peso in (
        ("A", "B", 2), ("B", "C", -3), ("C", "D", 1), ("D", "B", 2),
    ):
        grafo.adicionar_aresta(vi, vj, peso)

    resultado = bellman_ford(grafo, "A")

    assert resultado["distancia"] == {"A": 0, "B": 2, "C": -1, "D": 0}
    assert resultado["status"] == "OK"
    assert resultado["tem_ciclo_negativo"] is False
    assert resultado["ciclo_negativo"] == []
    assert resultado["custo_ciclo"] is None


# [IA] Codex - regressões de nó único, frações e oráculo aleatório persistente.
@pytest.mark.parametrize("peso", [-1, 0, 1])
def test_no_unico_com_laco(peso):
    grafo = Grafo()
    grafo.adicionar_aresta("A", "A", peso)

    resultado = bellman_ford(grafo, "A")

    assert resultado["tem_ciclo_negativo"] is (peso < 0)
    assert resultado["status"] == ("CICLO_NEGATIVO" if peso < 0 else "OK")
    if peso < 0:
        assert resultado["ciclo_negativo"] == ["A", "A"]
        assert resultado["custo_ciclo"] == peso
    else:
        assert resultado["distancia"] == {"A": 0}
        assert resultado["pai"] == {"A": None}
        assert resultado["ciclo_negativo"] == []
        assert resultado["custo_ciclo"] is None


def test_pesos_fracionarios():
    grafo = Grafo()
    grafo.adicionar_aresta("A", "B", 0.9)
    grafo.adicionar_aresta("A", "C", 0.5)
    grafo.adicionar_aresta("C", "B", -0.2)

    resultado = bellman_ford(grafo, "A")

    assert resultado["status"] == "OK"
    assert resultado["distancia"]["B"] == pytest.approx(0.3)
    assert resultado["pai"]["B"] == "C"


@pytest.mark.parametrize("semente", range(20))
def test_bellman_ford_com_networkx_como_oraculo(semente):
    nx = pytest.importorskip("networkx")
    sorteio = random.Random(semente)
    grafo = Grafo()
    referencia = nx.DiGraph()
    nos = [f"N{i}" for i in range(6)]
    for no in nos:
        grafo.adicionar_no(no)
        referencia.add_node(no)
    for vi in nos:
        for vj in nos:
            if sorteio.random() < 0.2:
                peso = sorteio.randint(-3, 6)
                grafo.adicionar_aresta(vi, vj, peso)
                referencia.add_edge(vi, vj, weight=peso)

    for origem in nos:
        resultado = bellman_ford(grafo, origem)
        try:
            distancias = nx.single_source_bellman_ford_path_length(referencia, origem)
        except nx.NetworkXUnbounded:
            assert resultado["status"] == "CICLO_NEGATIVO"
            assert resultado["tem_ciclo_negativo"] is True
            ciclo = resultado["ciclo_negativo"]
            assert len(ciclo) >= 2
            assert ciclo[0] == ciclo[-1]
            assert len(ciclo[:-1]) == len(set(ciclo[:-1]))
            assert nx.has_path(referencia, origem, ciclo[0])
            assert all(referencia.has_edge(vi, vj) for vi, vj in zip(ciclo, ciclo[1:]))
            custo = sum(referencia[vi][vj]["weight"] for vi, vj in zip(ciclo, ciclo[1:]))
            assert resultado["custo_ciclo"] == custo
            assert custo < 0
        else:
            assert resultado["status"] == "OK"
            assert resultado["tem_ciclo_negativo"] is False
            assert resultado["ciclo_negativo"] == []
            assert resultado["custo_ciclo"] is None
            assert resultado["distancia"] == {
                no: distancias.get(no, float("inf")) for no in nos
            }
            for no in nos:
                if no not in distancias:
                    assert resultado["pai"][no] is None
                    continue
                # Percorrer até a origem detecta também ciclos indevidos nos pais.
                atual = no
                caminho = set()
                while atual != origem:
                    assert atual not in caminho
                    caminho.add(atual)
                    pai = resultado["pai"][atual]
                    assert referencia.has_edge(pai, atual)
                    assert distancias[atual] == distancias[pai] + referencia[pai][atual]["weight"]
                    atual = pai
                assert resultado["pai"][origem] is None
