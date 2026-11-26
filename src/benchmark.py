"""Benchmark da Parte 2 (P4b): tempo médio, escalabilidade e parte2_report.json.

- tempo médio de 5 execuções de cada algoritmo
- escalabilidade em 10% / 50% / 100% dos nós, comparada com a complexidade teórica
  pela coluna tempo_por_custo_teorico_ms = tempo / custo do caso medido
- a DFS percorre o grafo inteiro (floresta); BFS, Dijkstra e Bellman-Ford partem da carteira com
  mais arcos de saída de cada amostra, então não fazem a mesma tarefa que a DFS
- status OK no Bellman-Ford significa parada antecipada: o tempo não mede V * E
- latência: tempo de uma execução isolada; o JSON guarda a menor e a maior das 5
- memória: pico alocado pelo algoritmo (tracemalloc), sem contar o grafo, que já existia
- casos obrigatórios: as mesmas fontes e pares dos JSONs de out/parte2/ (seção 5), cada um com 5 execuções
"""
# [IA] Claude Code – benchmark da Parte 2
# [IA] Claude Code – casos obrigatórios e repetições no parte2_report.json (V1), a pedido do Vagner

import json
import math
import random
import timeit
import tracemalloc
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # só grava o arquivo, sem abrir janela
import matplotlib.pyplot as plt

from src.carga_parte2 import carregar_grafo
from src.graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
from src.graphs.graph import Grafo

SEED = 42
FRACOES = [0.1, 0.5, 1.0]
REPETICOES = 5

# Casos obrigatórios da seção 5 (mesmos nomes dos JSONs em out/parte2/)
FONTES_BUSCA = [
    "1MFXYK1XucKFfhPhW9HDHD3vsM9BKey4qm",
    "35fNF5Uwbsoa5ABPCUvKZNyuAV7S9sJTou",
    "39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K",
]
PARES_DIJKSTRA = [
    ("39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K", "17uQbqBGYLGjHtX8eJHoonfY4iUf8ixCwe"),
    ("39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K", "16PaWFJttSe54KviUNjyzP459DuQTiB8rT"),
    ("3MTTgd2BaPndUYkmGjiacaPLkuWsiPUzM3", "17tqJV8U98Q7zin186LbR2pYq4fncJuyLw"),
    ("1MFXYK1XucKFfhPhW9HDHD3vsM9BKey4qm", "1GeFfWdvjZ3HNd99e3WVwWcnCN63GQYrG6"),
    ("39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K", "1J5U1rN5dBzxK2g6imJZzcimPrDTPYaz7N"),
]
FONTES_BELLMAN_FORD = [
    "3Fzzji5nFaSptmYL8bNsm3KcpYm3qnxqBS",  # caso sem ciclo negativo
    "1MFXYK1XucKFfhPhW9HDHD3vsM9BKey4qm",  # caso com ciclo negativo
]


def custo_busca(grafo, retorno):
    """V + arcos percorridos: a DFS percorre todos; a BFS, só os dos nós alcançados."""
    return grafo.ordem() + sum(grafo.grau_saida(no) for no in retorno["ordem"])


def custo_bellman_ford(grafo, retorno):
    """V * E, que só vale com ciclo negativo; sem ele o algoritmo para antes (None)."""
    if retorno["status"] == "CICLO_NEGATIVO":
        return grafo.ordem() * grafo.tamanho()
    return None


def custo_dijkstra(grafo, retorno):
    """Estima o custo da validação global e das operações de heap na região alcançada."""
    arcos_alcancados = sum(grafo.grau_saida(no) for no in retorno["ordem"])
    custo_validacao = grafo.ordem() + grafo.tamanho()
    return custo_validacao + arcos_alcancados * math.log2(max(2, grafo.ordem()))


# Cada novo algoritmo realizado, adiciona aqui:
# nome: (função, precisa de origem, complexidade, custo do caso medido)
ALGORITMOS = {
    "DFS": (dfs, False, "O(V + E)", custo_busca),
    "BFS": (bfs, True, "O(V + E)", custo_busca),
    "Dijkstra": (dijkstra, True, "O((V + E) log V)", custo_dijkstra),
    "Bellman-Ford": (bellman_ford, True, "O(V * E)", custo_bellman_ford),
}


def amostrar(grafo, fracao):
    """Sorteia uma fração dos nós e devolve o subgrafo induzido por eles."""
    k = round(fracao * grafo.ordem())
    nos = random.Random(SEED).sample(grafo.nos(), k)
    return grafo.subgrafo_induzido(nos)


def maior_grau_saida(grafo):
    """Origem usada por BFS, Dijkstra e Bellman-Ford: o nó com mais arcos de saída."""
    return max(grafo.nos(), key=grafo.grau_saida)


def medir_tempos(funcao, grafo, repeticoes=5):
    """Roda funcao(grafo) `repeticoes` vezes e devolve o tempo de cada execução, em segundos.

    O timeit desliga o coletor de lixo enquanto mede; sem isso ele às vezes roda no meio
    de uma execução e infla o tempo (o ponto de 50% saía com ~22 ms em vez de ~12 ms).
    """
    return timeit.repeat(lambda: funcao(grafo), number=1, repeat=repeticoes)


def tempo_medio(funcao, grafo, repeticoes=5):
    """Tempo médio de `repeticoes` execuções de funcao(grafo), em segundos."""
    return sum(medir_tempos(funcao, grafo, repeticoes)) / repeticoes


def pico_memoria(funcao, grafo):
    """Roda funcao(grafo) uma vez e devolve o pico de memória alocada durante a execução, em bytes.

    Fica numa execução separada do timeit porque o tracemalloc deixa o código mais lento.
    O grafo foi criado antes do start, então só entram as estruturas do próprio algoritmo
    (visitados, fila, distâncias, predecessores) e o retorno.
    """
    tracemalloc.start()
    try:
        funcao(grafo)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return pico


def contar_alcancados(retorno):
    """Quantos nós o algoritmo alcançou (BFS e DFS têm `ordem`; o Bellman-Ford, distâncias)."""
    if "ordem" in retorno:
        return len(retorno["ordem"])
    return sum(d != float("inf") for d in retorno["distancia"].values())


def medir_caso(nome, funcao, grafo, origem, destino=None):
    """Mede um caso obrigatório: 5 execuções do algoritmo a partir da origem, no grafo inteiro."""
    ultimo = {}
    tempos = medir_tempos(lambda gr: ultimo.update(funcao(gr, origem)), grafo, REPETICOES)
    t = sum(tempos) / len(tempos)
    pico = pico_memoria(lambda gr: funcao(gr, origem), grafo)
    return {
        "algoritmo": nome, "origem": origem, "destino": destino,
        "alcancados": contar_alcancados(ultimo),
        "status": ultimo.get("status", "-"),
        "repeticoes": REPETICOES,
        "tempo_medio_ms": round(t * 1000, 2),
        "latencia_min_ms": round(min(tempos) * 1000, 2),
        "latencia_max_ms": round(max(tempos) * 1000, 2),
        "memoria_pico_kb": round(pico / 1024, 1),
    }


def medir_casos(grafo, grafo_dijkstra):
    """Casos obrigatórios: BFS e DFS nas 3 fontes, Dijkstra nos 5 pares e Bellman-Ford nos 2 casos."""
    casos = []
    for origem in FONTES_BUSCA:
        casos.append(medir_caso("BFS", bfs, grafo, origem))
        casos.append(medir_caso("DFS", dfs, grafo, origem))
    for origem, destino in PARES_DIJKSTRA:
        casos.append(medir_caso("Dijkstra", dijkstra, grafo_dijkstra, origem, destino))
    for origem in FONTES_BELLMAN_FORD:
        casos.append(medir_caso("Bellman-Ford", bellman_ford, grafo, origem))
    return casos


def executar_benchmark(pasta, saida, fracoes=FRACOES, com_casos=True):
    """Mede cada algoritmo em cada fração e os casos obrigatórios; grava parte2_report.json e o gráfico.

    O JSON tem duas listas: "escalabilidade" (algoritmo x fração) e "casos" (tarefas da seção 5).
    """
    grafo = carregar_grafo(Grafo(), pasta)
    grafo_dijkstra = carregar_grafo(Grafo(), pasta, coluna_peso="valor_btc")
    resultados = []
    for nome, (funcao, usa_origem, complexidade, custo) in ALGORITMOS.items():
        grafo_base = grafo_dijkstra if nome == "Dijkstra" else grafo
        for fracao in fracoes:
            g = amostrar(grafo_base, fracao)
            origem = maior_grau_saida(g) if usa_origem else None
            ultimo = {}  # guarda o retorno da última execução, para o relatório
            tempos = medir_tempos(lambda gr: ultimo.update(funcao(gr, origem)), g, REPETICOES)
            t = sum(tempos) / len(tempos)
            custo_caso = custo(g, ultimo)
            pico = pico_memoria(lambda gr: funcao(gr, origem), g)
            resultados.append({
                "algoritmo": nome, "fracao": fracao, "nos": g.ordem(), "arestas": g.tamanho(),
                "complexidade": complexidade,
                "origem": origem,
                "alcancados": contar_alcancados(ultimo),
                "status": ultimo.get("status", "-"),
                "repeticoes": REPETICOES,
                "tempo_medio_ms": round(t * 1000, 2),
                "latencia_min_ms": round(min(tempos) * 1000, 2),
                "latencia_max_ms": round(max(tempos) * 1000, 2),
                "tempo_por_custo_teorico_ms": round(t / custo_caso * 1000, 6) if custo_caso else None,
                "memoria_pico_kb": round(pico / 1024, 1),
            })
    relatorio = {
        "repeticoes": REPETICOES,
        "escalabilidade": resultados,
        "casos": medir_casos(grafo, grafo_dijkstra) if com_casos else [],
    }
    Path(saida).mkdir(parents=True, exist_ok=True)
    with open(Path(saida) / "parte2_report.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    gerar_grafico(resultados, saida)
    return relatorio


def gerar_grafico(resultados, saida):
    """Gráfico de linha: tamanho do grafo (V + E) x tempo médio, uma linha por algoritmo."""
    plt.figure()
    for nome in ALGORITMOS:
        linhas = [r for r in resultados if r["algoritmo"] == nome]
        x = [r["nos"] + r["arestas"] for r in linhas]
        y = [r["tempo_medio_ms"] for r in linhas]
        plt.plot(x, y, "o-", label=nome)
    plt.xscale("log")  # a comparação com a teoria de cada algoritmo está na coluna de custo do JSON
    plt.yscale("log")  # os tempos vão de menos de 1 ms (10%) a dezenas de ms (100%)
    plt.minorticks_off()
    tamanhos = sorted({r["nos"] + r["arestas"] for r in resultados})
    plt.xticks(tamanhos, [str(valor) for valor in tamanhos])  # só os tamanhos medidos
    plt.title("Tempo médio x tamanho do grafo")
    plt.xlabel("|V| + |E| (escala log)")
    plt.ylabel("Tempo médio (ms, escala log)")
    plt.legend()
    plt.savefig(Path(saida) / "benchmark_escalabilidade.png", dpi=150)
    plt.close()
