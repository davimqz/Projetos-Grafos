"""Casos obrigatórios da Parte 2 (P4a): exporta a BFS e a DFS de uma fonte para JSON.

Os algoritmos são os do grupo (src/graphs/algorithms.py); aqui só há carga e exportação.
Os resultados trazem apenas os nós alcançados: `total_nos - alcancados` dá os demais,
e assim o JSON não precisa representar distância infinita.
"""
# [IA] Claude Code – exportação dos resultados de BFS/DFS para JSON (IO)

import json
from pathlib import Path

from src.carga_parte2 import carregar_grafo
from src.graphs.algorithms import bfs, dfs
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


def executar_busca(algoritmo, pasta, origem, saida):
    """Roda o algoritmo a partir da origem e grava <algoritmo>_<origem>.json em `saida`."""
    grafo = carregar_grafo(Grafo(), pasta)
    resultado = RESUMOS[algoritmo](grafo, origem)
    Path(saida).mkdir(parents=True, exist_ok=True)
    caminho = Path(saida) / f"{algoritmo.lower()}_{origem}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2, allow_nan=False)
    return caminho
