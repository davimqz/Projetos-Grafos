"""Benchmark da Parte 2 (P4b): tempo médio, escalabilidade e parte2_report.json.

- tempo médio de 5 execuções de cada algoritmo
- escalabilidade em 10% / 50% / 100% dos nós, comparada com a complexidade teórica
  pela coluna tempo_por_elemento_us = tempo / (V + E), em microssegundos
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
from src.graphs.algorithms import dfs
from src.graphs.graph import Grafo

SEED = 42
FRACOES = [0.1, 0.5, 1.0]

# Cada novo algoritm realizado, adiciona aqui
ALGORITMOS = {"DFS": (dfs, "O(V + E)")}


def amostrar(grafo, fracao):
    """Sorteia uma fração dos nós e devolve o subgrafo induzido por eles."""
    k = round(fracao * grafo.ordem())
    nos = random.Random(SEED).sample(grafo.nos(), k)
    return grafo.subgrafo_induzido(nos)


def tempo_medio(funcao, grafo, repeticoes=5):
    """Roda funcao(grafo) `repeticoes` vezes e devolve o tempo médio em segundos.

    O timeit desliga o coletor de lixo enquanto mede; sem isso ele às vezes roda no meio
    de uma execução e infla o tempo (o ponto de 50% saía com ~22 ms em vez de ~12 ms).
    """
    tempos = timeit.repeat(lambda: funcao(grafo), number=1, repeat=repeticoes)
    return sum(tempos) / repeticoes


def executar_benchmark(pasta, saida):
    """Mede cada algoritmo em cada fração e grava parte2_report.json e o gráfico."""
    grafo = carregar_grafo(Grafo(), pasta)
    resultados = []
    for nome, (funcao, complexidade) in ALGORITMOS.items():
        for fracao in FRACOES:
            g = amostrar(grafo, fracao)
            v, e = g.ordem(), g.tamanho()
            t = tempo_medio(funcao, g)
            resultados.append({
                "algoritmo": nome, "fracao": fracao, "nos": v, "arestas": e,
                "complexidade": complexidade,
                "tempo_medio_ms": round(t * 1000, 2),
                "tempo_por_elemento_us": round(t / (v + e) * 1_000_000, 2),
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
    plt.title("Tempo médio x tamanho do grafo")
    plt.xlabel("|V| + |E|")
    plt.ylabel("Tempo médio (ms)")
    plt.legend()
    plt.savefig(Path(saida) / "benchmark_escalabilidade.png", dpi=150)
    plt.close()
