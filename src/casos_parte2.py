"""Casos obrigatórios da Parte 2 (P4a): exporta BFS, DFS, Dijkstra e Bellman-Ford para JSON.

Os algoritmos são os do grupo (src/graphs/algorithms.py); aqui só há carga e exportação.
Os resultados trazem apenas os nós alcançados: `total_nos - alcancados` dá os demais,
e assim o JSON não precisa representar distância infinita.
"""
# [IA] Claude Code – exportação dos resultados de BFS/DFS/Dijkstra/Bellman-Ford para JSON (IO)

import json
from pathlib import Path

from src.carga_parte2 import carregar_grafo
from src.graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
from src.graphs.graph import Grafo


def resumir_bfs(grafo, origem):
    """Devolve ordem, camadas (o índice é o nível), distância, pai e árvore da BFS."""
    r = bfs(grafo, origem)
    alcancados = r["ordem"]
    return {
        "algoritmo": "BFS",
        "origem": origem,
        "total_nos": grafo.ordem(),
        "alcancados": len(alcancados),
        "ordem": alcancados,
        "camadas": [r["camadas"][nivel] for nivel in sorted(r["camadas"])],
        "distancia": {no: r["distancia"][no] for no in alcancados},
        "pai": {no: r["pai"][no] for no in alcancados},
        "arvore": r["arvore"],
    }


def resumir_dfs(grafo, origem):
    """Devolve ordem, pai, arcos classificados e ciclo da DFS a partir da origem."""
    r = dfs(grafo, origem)
    alcancados = r["ordem"]
    return {
        "algoritmo": "DFS",
        "origem": origem,
        "total_nos": grafo.ordem(),
        "alcancados": len(alcancados),
        "ordem": alcancados,
        "pai": {no: r["pai"][no] for no in alcancados},
        "contagem_arcos": r["contagem_arcos"],
        "arcos": r["arcos"],
        "tem_ciclo": r["tem_ciclo"],
        "escopo_ciclo": r["escopo_ciclo"],
    }


RESUMOS = {"BFS": resumir_bfs, "DFS": resumir_dfs}


def _gravar(resultado, saida, nome):
    Path(saida).mkdir(parents=True, exist_ok=True)
    caminho = Path(saida) / nome
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2, allow_nan=False)
    return caminho


def executar_busca(algoritmo, pasta, origem, saida):
    """Roda o algoritmo a partir da origem e grava <algoritmo>_<origem>.json em `saida`."""
    grafo = carregar_grafo(Grafo(), pasta)
    resultado = RESUMOS[algoritmo](grafo, origem)
    return _gravar(resultado, saida, f"{algoritmo.lower()}_{origem}.json")


def _caminho_ate(pai, destino):
    """Reconstrói o caminho origem → destino seguindo os pais."""
    caminho = [destino]
    while pai[caminho[-1]] is not None:
        caminho.append(pai[caminho[-1]])
    return caminho[::-1]


def _pesos_do_caminho(grafo, caminho):
    """Peso de cada arco do caminho, na ordem (u, v, peso)."""
    arcos = []
    for u, v in zip(caminho, caminho[1:]):
        peso = min(p for vizinho, p in grafo.vizinhos(u) if vizinho == v)
        arcos.append([u, v, peso])
    return arcos


def resumir_dijkstra(grafo, origem, destino):
    """Custo mínimo e caminho origem → destino; peso = valor_btc (sempre ≥ 0)."""
    if destino not in grafo.nos():
        raise ValueError(f"Nó '{destino}' não existe.")
    r = dijkstra(grafo, origem)
    if r["distancia"][destino] == float("inf"):
        raise ValueError(f"'{destino}' não é alcançável a partir de '{origem}'.")
    caminho = _caminho_ate(r["pai"], destino)
    return {
        "algoritmo": "DIJKSTRA",
        "peso": "valor_btc",
        "origem": origem,
        "destino": destino,
        "custo": r["distancia"][destino],
        "passos": len(caminho) - 1,
        "caminho": caminho,
        "arcos": _pesos_do_caminho(grafo, caminho),
    }


def resumir_bellman_ford(grafo, origem):
    """Distâncias a partir da origem (peso = saldo) ou o ciclo negativo encontrado.

    Com ciclo negativo alcançável as distâncias não são definidas (dá para baixar sem
    limite), então o JSON traz só o ciclo e o custo dele.
    """
    r = bellman_ford(grafo, origem)
    alcancados = [no for no, d in r["distancia"].items() if d != float("inf")]
    resultado = {
        "algoritmo": "BELLMAN_FORD",
        "peso": "peso",
        "origem": origem,
        "total_nos": grafo.ordem(),
        "alcancados": len(alcancados),
        "status": r["status"],
        "tem_ciclo_negativo": r["tem_ciclo_negativo"],
    }
    if r["tem_ciclo_negativo"]:
        ciclo = r["ciclo_negativo"]
        resultado["ciclo_negativo"] = ciclo
        resultado["arcos_ciclo"] = _pesos_do_caminho(grafo, ciclo)
        resultado["custo_ciclo"] = r["custo_ciclo"]
    else:
        resultado["arcos_negativos_alcancaveis"] = sum(
            1 for u in alcancados for _, p in grafo.vizinhos(u) if p < 0
        )
        resultado["distancia"] = {no: r["distancia"][no] for no in alcancados}
        resultado["pai"] = {no: r["pai"][no] for no in alcancados}
    return resultado


def executar_dijkstra(pasta, origem, destino, saida):
    """Grava dijkstra_<origem>_<destino>.json em `saida`."""
    grafo = carregar_grafo(Grafo(), pasta, coluna_peso="valor_btc")
    resultado = resumir_dijkstra(grafo, origem, destino)
    return _gravar(resultado, saida, f"dijkstra_{origem}_{destino}.json")


def executar_bellman_ford(pasta, origem, saida):
    """Grava bellman_ford_<origem>.json em `saida`."""
    grafo = carregar_grafo(Grafo(), pasta)
    resultado = resumir_bellman_ford(grafo, origem)
    return _gravar(resultado, saida, f"bellman_ford_{origem}.json")
