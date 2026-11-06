"""BFS, DFS, Dijkstra e Bellman-Ford — implementação própria do grupo.

Pacote P2 — Algoritmos e testes. Proibido usar networkx/igraph aqui (só em tests/).

A implementar pelo grupo:
- BFS: distâncias em passos, níveis, árvore BFS
- DFS: classificação de arcos (árvore, retorno, avanço, cruzamento) e detecção de ciclo - Ok
- Dijkstra (heapq): recusa com mensagem clara se houver arco de peso negativo
- Bellman-Ford: distâncias + detecção e reconstrução do ciclo negativo
"""

from collections import deque
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

            vj, _peso = vizinhos[posicao]
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

def bfs(grafo: Grafo, origem: str) -> dict:
    """Os pesos das arestas nao sao utilizados.
    """
    nos = grafo.nos()

    if origem not in nos:
        raise ValueError(f"Nó '{origem}' não existe no grafo.")

    estado = {no: "NAO_VISITADO" for no in nos}
    pai = {no: None for no in nos}
    distancia = {no: float("inf") for no in nos}
    nivel = {no: None for no in nos}
    ordem = []
    arvore = []
    camadas = {0: [origem]}

    estado[origem] = "VISITADO"
    distancia[origem] = 0
    nivel[origem] = 0
    fila = deque([origem])

    while fila:
        vi = fila.popleft()
        ordem.append(vi)

        for aresta in grafo.vizinhos(vi):
            vj = aresta[0]

            if estado[vj] == "NAO_VISITADO":
                estado[vj] = "VISITADO"
                distancia[vj] = distancia[vi] + 1
                nivel[vj] = distancia[vj]
                pai[vj] = vi
                arvore.append((vi, vj))
                camadas.setdefault(nivel[vj], []).append(vj)
                fila.append(vj)

        estado[vi] = "ENCERRADO"

    return {
        "ordem": ordem,
        "pai": pai,
        "distancia": distancia,
        "nivel": nivel,
        "camadas": camadas,
        "arvore": arvore,
        "estado": estado,
    }

def bellman_ford(grafo: Grafo, origem: str) -> dict:
    nos = grafo.nos()

    if origem not in nos:
        raise ValueError(f"Nó '{origem}' não existe.")

    distancia = {no: float("inf") for no in nos}
    pai = {no: None for no in nos}
    peso_pai = {no: None for no in nos}
    distancia[origem] = 0

    arestas = [
        (vi, vj, peso)
        for vi in nos
        for vj, peso in grafo.vizinhos(vi)
    ]

    for _ in range(len(nos) - 1):
        alterou = False

        for vi, vj, peso in arestas:
            if distancia[vi] == float("inf"):
                continue

            novo_custo = distancia[vi] + peso
            if novo_custo < distancia[vj]:
                distancia[vj] = novo_custo
                pai[vj] = vi
                peso_pai[vj] = peso
                alterou = True

        if not alterou:
            break

    ultimo_atualizado = None
    for vi, vj, peso in arestas:
        if distancia[vi] == float("inf"):
            continue

        novo_custo = distancia[vi] + peso
        if novo_custo < distancia[vj]:
            distancia[vj] = novo_custo
            pai[vj] = vi
            peso_pai[vj] = peso
            ultimo_atualizado = vj

    ciclo_negativo = []
    custo_ciclo = None

    if ultimo_atualizado is not None:
        atual = ultimo_atualizado
        for _ in range(len(nos)):
            atual = pai[atual]

        inicio_ciclo = atual
        ciclo_inverso = [inicio_ciclo]
        atual = pai[inicio_ciclo]

        while atual != inicio_ciclo:
            ciclo_inverso.append(atual)
            atual = pai[atual]

        ciclo_inverso.append(inicio_ciclo)
        ciclo_negativo = list(reversed(ciclo_inverso))
        custo_ciclo = sum(peso_pai[vj] for vj in ciclo_negativo[1:])

    tem_ciclo_negativo = bool(ciclo_negativo)

    return {
        "distancia": distancia,
        "pai": pai,
        "tem_ciclo_negativo": tem_ciclo_negativo,
        "ciclo_negativo": ciclo_negativo,
        "custo_ciclo": custo_ciclo,
        "status": "CICLO_NEGATIVO" if tem_ciclo_negativo else "OK",
    }
