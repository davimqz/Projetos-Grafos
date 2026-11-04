"""BFS, DFS, Dijkstra e Bellman-Ford — implementação própria do grupo.

Pacote P2 — Algoritmos e testes. Proibido usar networkx/igraph aqui (só em tests/).

A implementar pelo grupo:
- BFS: distâncias em passos, níveis, árvore BFS
- DFS: classificação de arcos (árvore, retorno, avanço, cruzamento) e detecção de ciclo - Ok
- Dijkstra (heapq): recusa com mensagem clara se houver arco de peso negativo
- Bellman-Ford: distâncias + detecção e reconstrução do ciclo negativo
"""

from src.graphs.graph import Grafo

def dfs(grafo: Grafo, origem: str | None = None) -> dict:
    """Executa a busca em profundidade em um grafo dirigido.

    Se origem for informada, visita somente os nós alcançáveis a partir dela.
    Se origem for None, percorre todos os nós, formando floresta.
    """
    nos = grafo.nos()

    if origem is not None and origem not in nos:
        raise ValueError(f"Nó '{origem}' não existe.")

    estado = {no: "NAO_VISITADO" for no in nos}
    pai = {no: None for no in nos}
    descoberta = {no: None for no in nos}
    termino = {no: None for no in nos}
    ordem = []
    arcos = {
        "arvore": [],
        "retorno": [],
        "avanco": [],
        "cruzamento": [],
    }
    tempo = -1

    def visitar(vi: str) -> None:
        nonlocal tempo
        tempo += 1
        estado[vi] = "VISITADO"
        descoberta[vi] = tempo
        ordem.append(vi)

        for vj, _peso in grafo.vizinhos(vi):
            if estado[vj] == "NAO_VISITADO":
                pai[vj] = vi
                arcos["arvore"].append((vi, vj))
                visitar(vj)
            elif estado[vj] == "VISITADO":
                arcos["retorno"].append((vi, vj))
            elif descoberta[vi] < descoberta[vj]:
                arcos["avanco"].append((vi, vj))
            else:
                arcos["cruzamento"].append((vi, vj))

        estado[vi] = "ENCERRADO"
        tempo += 1
        termino[vi] = tempo

    if origem is not None:
        visitar(origem)
    else:
        for no in nos:
            if estado[no] == "NAO_VISITADO":
                visitar(no)

    contagem_arcos = {tipo: len(lista) for tipo, lista in arcos.items()}
    return {
        "ordem": ordem,
        "pai": pai,
        "descoberta": descoberta,
        "termino": termino,
        "estado": estado,
        "arcos": arcos,
        "contagem_arcos": contagem_arcos,
        "tem_ciclo": bool(arcos["retorno"]),
    }
