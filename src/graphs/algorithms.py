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
    arcos = {"arvore": [], "retorno": [], "avanco": [], "cruzamento": []}
    tempo = -1

    def descobrir(no: str) -> list:
        """Registra a descoberta e cria uma posição na pilha."""
        nonlocal tempo
        tempo += 1
        estado[no] = "VISITADO"
        descoberta[no] = tempo
        ordem.append(no)
        return [no, grafo.vizinhos(no), 0]

    def percorrer(inicio: str) -> None:
        """Executa a DFS guardando o próximo vizinho de cada vértice."""
        nonlocal tempo
        pilha = [descobrir(inicio)]

        while pilha:
            vi, vizinhos, posicao = pilha[-1]

            if posicao == len(vizinhos):
                estado[vi] = "ENCERRADO"
                tempo += 1
                termino[vi] = tempo
                pilha.pop()
                continue

            vj = vizinhos[posicao][0]
            pilha[-1][2] += 1

            if estado[vj] == "NAO_VISITADO":
                pai[vj] = vi
                arcos["arvore"].append((vi, vj))
                pilha.append(descobrir(vj))
            elif estado[vj] == "VISITADO":
                arcos["retorno"].append((vi, vj))
            elif descoberta[vi] < descoberta[vj]:
                arcos["avanco"].append((vi, vj))
            else:
                arcos["cruzamento"].append((vi, vj))

    if origem is not None:
        percorrer(origem)
    else:
        for no in nos:
            if estado[no] == "NAO_VISITADO":
                percorrer(no)

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
        "escopo_ciclo": "alcancaveis_da_origem" if origem is not None else "grafo_inteiro",
    }
