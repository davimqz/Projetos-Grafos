"""Normalização, reutilização de buscas e comparação de modelagens da Parte 1.

Os algoritmos e a construção dos grafos são reutilizados de src.graphs.
"""

# [IA] Codex - separação do código existente, preservando os resultados e a lógica.
from __future__ import annotations

from src.graphs.algorithms import bellman_ford, bfs, dijkstra
from src.graphs.estados import construir_grafo_posicoes, rotular_posicao
from src.graphs.io import encontrar_inicio, encontrar_saidas
from src.viz import reconstruir_percurso
from .modelos import AlgoritmoCaminho, DadosMapa, Solucao


def resolver_mapa(dados: DadosMapa, algoritmo: AlgoritmoCaminho) -> Solucao:
    """Normaliza o resultado de um algoritmo existente até ALVO.

    BFS procura menos passos; Dijkstra e Bellman-Ford procuram menor custo.
    O caminho com status OK contém os rótulos desde a origem até ALVO.
    passos conta movimentos físicos, sem o arco virtual; custo representa
    a soma dos pesos do caminho, inclusive quando a busca usada é BFS.

    Registra RECUSA para Dijkstra com peso negativo, CICLO_NEGATIVO quando
    Bellman-Ford o detectar e SEM_SOLUCAO para ALVO inalcançável.
    Não implementa novamente os algoritmos e não grava arquivos.
    """
    return _resolver_mapa(dados, algoritmo, {})


def _resultado_busca(dados: DadosMapa, algoritmo: AlgoritmoCaminho, resultados: dict[str, dict]) -> dict:
    """Executa cada busca no máximo uma vez por mapa na orquestração."""
    if algoritmo not in resultados:
        buscar = {"BFS": bfs, "DIJKSTRA": dijkstra, "BELLMAN_FORD": bellman_ford}[algoritmo]
        resultados[algoritmo] = buscar(dados.grafo_estados, dados.origem)
    return resultados[algoritmo]


def _resolver_mapa(dados: DadosMapa, algoritmo: AlgoritmoCaminho, resultados: dict[str, dict]) -> Solucao:
    """Normaliza buscas existentes, com reutilização local dos resultados."""

    grafo = dados.grafo_estados
    inicio = dados.origem

    if inicio not in grafo.nos():
        raise ValueError(f"Origem '{inicio}' não existe no grafo.")

    if algoritmo not in ("BFS", "DIJKSTRA", "BELLMAN_FORD"):
        raise ValueError(f"Algoritmo desconhecido: {algoritmo}")

    caminho: list[str] = []
    custo: float | None = None
    try:
        resultado = _resultado_busca(dados, algoritmo, resultados)
        status = "OK" if algoritmo == "BFS" else resultado["status"]
        if status == "OK":
            caminho = reconstruir_percurso(resultado, inicio, "ALVO")
            if algoritmo == "BFS":
                custo = 0.0
                for origem, destino in zip(caminho, caminho[1:]):
                    for vizinho, peso in grafo.vizinhos(origem):
                        if vizinho == destino:
                            custo += peso
                            break
            else:
                custo = resultado["distancia"]["ALVO"]
    except ValueError as erro:
        status = "RECUSA" if algoritmo == "DIJKSTRA" and "negativo" in str(erro) else "SEM_SOLUCAO"

    if status != "OK":
        passos = None
        custo = None
        caminho = []
    else:
        passos = len(caminho) - 2

    return Solucao(
        mapa=dados.nome,
        algoritmo=algoritmo,
        passos=passos,
        custo=custo,
        status=status,
        caminho=caminho
    )
