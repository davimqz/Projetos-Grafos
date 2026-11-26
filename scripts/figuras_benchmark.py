"""Recria as três figuras complementares da seção 5.6 a partir dos resultados salvos.

Na raiz do projeto: python -m scripts.figuras_benchmark
"""
# [IA] Codex – leitura das saídas e desenho das figuras da seção 5.6.

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter

from src.carga_parte2 import ler_arestas
from src.casos_parte2 import _caminho_ate


PASTA = Path(__file__).resolve().parents[1] / "out" / "parte2"
ORIGEM_ILICITA = "39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K"
DESTINO_ILICITO = "17uQbqBGYLGjHtX8eJHoonfY4iUf8ixCwe"
# Mesmos pares, na ordem da tabela da seção 5.4.
PARES = [
    ("Ilícita → Ilícita", ORIGEM_ILICITA, DESTINO_ILICITO),
    ("Ilícita → Lícita", ORIGEM_ILICITA, "16PaWFJttSe54KviUNjyzP459DuQTiB8rT"),
    ("Lícita → Ilícita", "3MTTgd2BaPndUYkmGjiacaPLkuWsiPUzM3", "17tqJV8U98Q7zin186LbR2pYq4fncJuyLw"),
    ("Desconhecida → Ilícita", "1MFXYK1XucKFfhPhW9HDHD3vsM9BKey4qm", "1GeFfWdvjZ3HNd99e3WVwWcnCN63GQYrG6"),
    ("Ilícita → Desconhecida", ORIGEM_ILICITA, "1J5U1rN5dBzxK2g6imJZzcimPrDTPYaz7N"),
]


def ler_resultado(nome):
    return json.loads((PASTA / nome).read_text(encoding="utf-8"))


def inteiro(n):
    return f"{n:,.0f}".replace(",", ".")


def grafico_alcance(resultados):
    fracoes = sorted({r["fracao"] for r in resultados})
    contagem = {(r["algoritmo"], r["fracao"]): r["alcancados"] for r in resultados}
    fig, ax = plt.subplots(figsize=(10.5, 5.2), layout="constrained")
    algoritmos = ["BFS", "DFS", "Dijkstra", "Bellman-Ford"]
    cores = ["#2563a3", "#23795f", "#995404", "#795391"]
    for i, (nome, cor) in enumerate(zip(algoritmos, cores)):
        quantidades = [contagem[nome, f] for f in fracoes]
        posicoes = [j + (i - 1.5) * .19 for j in range(len(fracoes))]
        barras = ax.bar(posicoes, [n - 1 for n in quantidades], bottom=1,
                        width=.17, label=nome, color=cor)
        ax.bar_label(barras, labels=[inteiro(n) for n in quantidades], padding=4)
    ax.set_yscale("log")
    ax.set_ylim(1, 2.4 * max(contagem.values()))
    ax.yaxis.set_major_locator(FixedLocator([1, 10, 100, 1000, 10000]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda valor, _: inteiro(valor)))
    ax.set_xticks(range(len(fracoes)), [f"{f:.0%}" for f in fracoes])
    ax.set(xlabel="Fração dos vértices do recorte",
           ylabel="Carteiras alcançadas (escala logarítmica)")
    ax.set_title("Carteiras alcançadas por algoritmo", loc="left", pad=38)
    ax.legend(loc="lower center", bbox_to_anchor=(.5, 1), ncol=4, frameon=False)
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=.25)
    fig.savefig(PASTA / "benchmark_comportamento.png", dpi=160)
    plt.close(fig)


def diagrama(titulo, rotas, arquivo, alinhar_destinos=False):
    fig, eixos = plt.subplots(len(rotas), 1, figsize=(11, 1.2 * len(rotas) + 1.7))
    fig.subplots_adjust(left=.045, right=.97, top=1 - .85 / fig.get_figheight(),
                        bottom=.48 / fig.get_figheight(), hspace=.25)
    fig.suptitle(titulo, x=.045, ha="left", fontsize=18, weight="bold")
    maior = max(len(pesos) for _, _, pesos in rotas)
    for ax, (legenda, caminho, pesos) in zip(eixos, rotas):
        passos = len(pesos)
        espacamento = maior / passos if alinhar_destinos else 1
        total = f"{sum(pesos):.2f}".replace(".", ",")
        ax.set(xlim=(-.45, maior + .5), ylim=(0, 1))
        ax.axis("off")
        ax.text(-.42, .88, legenda, weight="bold", va="center")
        ax.text(maior + .44, .88, f"{passos} arcos  ·  {total} BTC", ha="right", va="center")
        for i, peso in enumerate(pesos):
            inicio = i * espacamento
            fim = inicio + espacamento
            ax.annotate("", (fim - .30, .3), (inicio + .30, .3),
                        arrowprops={"arrowstyle": "-|>", "color": "#32689a"})
            ax.text((inicio + fim) / 2, .50, f"{peso:.4f}".replace(".", ","),
                    ha="center", va="bottom", fontsize=9)
        for i, carteira in enumerate(caminho):
            ax.text(i * espacamento, .3, carteira[:8], ha="center", va="center",
                    family="monospace", bbox={"boxstyle": "round,pad=.3",
                                              "fc": "#edf4fc", "ec": "#9ab7d3"})
    fig.text(.045, .035, "Pesos dos arcos em BTC. Endereços abreviados e valores arredondados.",
             fontsize=9)
    fig.savefig(PASTA / arquivo, dpi=160)
    plt.close(fig)


def main():
    resultados = ler_resultado("parte2_report.json")["escalabilidade"]  # [IA] Claude Code – report novo (V1)
    rotas = []
    for legenda, origem, destino in PARES:
        caso = ler_resultado(f"dijkstra_{origem}_{destino}.json")
        rotas.append((legenda, caso["caminho"], [peso for _, _, peso in caso["arcos"]]))

    bfs = ler_resultado(f"bfs_{ORIGEM_ILICITA}.json")
    caminho_bfs = _caminho_ate(bfs["pai"], DESTINO_ILICITO)
    pesos_btc = {(u, v): peso for u, v, peso in ler_arestas(coluna_peso="valor_btc")}
    pesos_bfs = [pesos_btc[u, v] for u, v in zip(caminho_bfs, caminho_bfs[1:])]
    _, caminho_dijkstra, pesos_dijkstra = rotas[0]
    comparacao = [
        ("BFS  ·  Menor número de arcos", caminho_bfs, pesos_bfs),
        ("Dijkstra  ·  Menor soma de pesos", caminho_dijkstra, pesos_dijkstra),
    ]

    grafico_alcance(resultados)
    diagrama("Cinco caminhos de menor custo", rotas, "benchmark_caminhos_dijkstra.png")
    diagrama("BFS e Dijkstra no mesmo par de carteiras", comparacao,
             "benchmark_caminhos_bfs_dijkstra.png", alinhar_destinos=True)
    print(f"Três figuras complementares gravadas em {PASTA}")


if __name__ == "__main__":
    main()
