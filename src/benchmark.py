"""Benchmark da Parte 2 (P4b): tempo médio, escalabilidade e parte2_report.json.

- tempo médio de 5 execuções de cada algoritmo
- escalabilidade em 10% / 50% / 100% dos nós, comparada com a complexidade teórica
  pela coluna tempo_por_custo_teorico_ms = tempo / custo do caso medido
- a DFS percorre o grafo inteiro (floresta); BFS e Bellman-Ford partem da carteira com
  mais arcos de saída de cada amostra, então não fazem a mesma tarefa que a DFS
- status OK no Bellman-Ford significa parada antecipada: o tempo não mede V * E
"""
# [IA] Claude Code – benchmark da Parte 2

import json
import random
import timeit
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # só grava o arquivo, sem abrir janela
import matplotlib.pyplot as plt

from src.carga_parte2 import carregar_grafo
from src.graphs.algorithms import bellman_ford, bfs, dfs
from src.graphs.graph import Grafo

SEED = 42
FRACOES = [0.1, 0.5, 1.0]


def custo_busca(grafo, retorno):
    """V + arcos percorridos: a DFS percorre todos; a BFS, só os dos nós alcançados."""
    return grafo.ordem() + sum(grafo.grau_saida(no) for no in retorno["ordem"])


def custo_bellman_ford(grafo, retorno):
    """V * E, que só vale com ciclo negativo; sem ele o algoritmo para antes (None)."""
    if retorno["status"] == "CICLO_NEGATIVO":
        return grafo.ordem() * grafo.tamanho()
    return None


# Cada novo algoritmo realizado, adiciona aqui:
# nome: (função, precisa de origem, complexidade, custo do caso medido)
ALGORITMOS = {
    "DFS": (dfs, False, "O(V + E)", custo_busca),
    "BFS": (bfs, True, "O(V + E)", custo_busca),
    "Bellman-Ford": (bellman_ford, True, "O(V * E)", custo_bellman_ford),
}


def amostrar(grafo, fracao):
    """Sorteia uma fração dos nós e devolve o subgrafo induzido por eles."""
    k = round(fracao * grafo.ordem())
    nos = random.Random(SEED).sample(grafo.nos(), k)
    return grafo.subgrafo_induzido(nos)


def maior_grau_saida(grafo):
    """Origem usada por BFS e Bellman-Ford: o nó com mais arcos de saída."""
    return max(grafo.nos(), key=grafo.grau_saida)


def tempo_medio(funcao, grafo, repeticoes=5):
    """Roda funcao(grafo) `repeticoes` vezes e devolve o tempo médio em segundos.

    O timeit desliga o coletor de lixo enquanto mede; sem isso ele às vezes roda no meio
    de uma execução e infla o tempo (o ponto de 50% saía com ~22 ms em vez de ~12 ms).
    """
    tempos = timeit.repeat(lambda: funcao(grafo), number=1, repeat=repeticoes)
    return sum(tempos) / repeticoes


def contar_alcancados(retorno):
    """Quantos nós o algoritmo alcançou (BFS e DFS têm `ordem`; o Bellman-Ford, distâncias)."""
    if "ordem" in retorno:
        return len(retorno["ordem"])
    return sum(d != float("inf") for d in retorno["distancia"].values())


def executar_benchmark(pasta, saida, fracoes=FRACOES):
    """Mede cada algoritmo em cada fração e grava parte2_report.json e o gráfico."""
    grafo = carregar_grafo(Grafo(), pasta)
    resultados = []
    for nome, (funcao, usa_origem, complexidade, custo) in ALGORITMOS.items():
        for fracao in fracoes:
            g = amostrar(grafo, fracao)
            origem = maior_grau_saida(g) if usa_origem else None
            ultimo = {}  # guarda o retorno da última execução, para o relatório
            t = tempo_medio(lambda gr: ultimo.update(funcao(gr, origem)), g)
            custo_caso = custo(g, ultimo)
            resultados.append({
                "algoritmo": nome, "fracao": fracao, "nos": g.ordem(), "arestas": g.tamanho(),
                "complexidade": complexidade,
                "origem": origem,
                "alcancados": contar_alcancados(ultimo),
                "status": ultimo.get("status", "-"),
                "tempo_medio_ms": round(t * 1000, 2),
                "tempo_por_custo_teorico_ms": round(t / custo_caso * 1000, 6) if custo_caso else None,
            })
    Path(saida).mkdir(parents=True, exist_ok=True)
    with open(Path(saida) / "parte2_report.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    gerar_grafico(resultados, saida)
    return resultados


def gerar_grafico(resultados, saida):
    """Gráfico de linha: tamanho do grafo (V + E) x tempo médio, uma linha por algoritmo."""
    plt.figure()
    for nome in ALGORITMOS:
        linhas = [r for r in resultados if r["algoritmo"] == nome]
        x = [r["nos"] + r["arestas"] for r in linhas]
        y = [r["tempo_medio_ms"] for r in linhas]
        plt.plot(x, y, "o-", label=nome)
    plt.xscale("log")  # a comparação com a teoria de cada algoritmo está na coluna de custo do JSON
    plt.yscale("log")  # o Bellman-Ford fica ordens de grandeza acima dos outros
    plt.minorticks_off()
    plt.xticks(x, [str(valor) for valor in x])  # só os três tamanhos medidos
    plt.title("Tempo médio x tamanho do grafo")
    plt.xlabel("|V| + |E| (escala log)")
    plt.ylabel("Tempo médio (ms, escala log)")
    plt.legend()
    plt.savefig(Path(saida) / "benchmark_escalabilidade.png", dpi=150)
    plt.close()
