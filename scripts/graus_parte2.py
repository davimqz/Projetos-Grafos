"""Graus de entrada e de saída das carteiras do recorte da Parte 2.

Uso: python -m scripts.graus_parte2 [--dataset data/dataset_parte2] [--out out/parte2]

Gera em --out:
- graus_parte2.csv: endereco, classe, grau_entrada, grau_saida (uma linha por carteira, inclusive grau 0)
- graus_frequencia.csv: direcao, grau, carteiras (quantas carteiras têm cada grau)
- graus_resumo.json: estatísticas por direção, no total e por classe, e as 5 carteiras de maior grau
- graus_zero.csv: quantidade e proporção de carteiras com grau zero por classe e direção
- graus_histograma.png e graus_ccdf.png: figuras da distribuição (tipo e elementos definidos pelo Davi)

Só contagem com pandas sobre arestas.csv e nos.csv; não usa os algoritmos nem interpreta os números.
"""
# [IA] Claude Code – contagem dos graus com pandas e exportação para CSV/JSON

import argparse
import json
from pathlib import Path

import pandas as pd

DIRECOES = {"entrada": "grau_entrada", "saida": "grau_saida"}


def calcular_graus(arestas: pd.DataFrame, nos: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por carteira de nos.csv com os graus de entrada e saída (0 quando não aparece nas arestas)."""
    saida = arestas["origem"].value_counts()
    entrada = arestas["destino"].value_counts()
    graus = nos[["endereco", "classe"]].copy()
    graus["grau_entrada"] = graus["endereco"].map(entrada).fillna(0).astype(int)
    graus["grau_saida"] = graus["endereco"].map(saida).fillna(0).astype(int)
    return graus


def frequencia(graus: pd.DataFrame) -> pd.DataFrame:
    """Quantas carteiras têm cada valor de grau, por direção."""
    partes = []
    for direcao, coluna in DIRECOES.items():
        contagem = graus[coluna].value_counts().sort_index()
        partes.append(pd.DataFrame({"direcao": direcao, "grau": contagem.index, "carteiras": contagem.values}))
    return pd.concat(partes, ignore_index=True)


def _estatisticas(serie: pd.Series) -> dict:
    return {
        "carteiras": int(serie.size),
        "minimo": int(serie.min()),
        "q1": float(serie.quantile(0.25)),
        "mediana": float(serie.median()),
        "media": round(float(serie.mean()), 4),
        "q3": float(serie.quantile(0.75)),
        "maximo": int(serie.max()),
        "desvio_padrao": round(float(serie.std()), 4),
        "com_grau_zero": int((serie == 0).sum()),
    }


def resumo(graus: pd.DataFrame, n_arestas: int, top: int = 5) -> dict:
    saida = {"nos": int(len(graus)), "arestas": int(n_arestas)}
    for direcao, coluna in DIRECOES.items():
        maiores = graus.sort_values([coluna, "endereco"], ascending=[False, True]).head(top)
        saida[direcao] = {
            "total": _estatisticas(graus[coluna]),
            "por_classe": {classe: _estatisticas(g[coluna]) for classe, g in graus.groupby("classe")},
            "maiores": maiores[["endereco", "classe", coluna]].rename(columns={coluna: "grau"}).to_dict("records"),
        }
    return saida


# Figuras: tipo, escalas e elementos definidos pelo Davi (histograma log-log com faixas logarítmicas, barras das
# classes lado a lado em cada faixa e proporção
# dentro da classe; CCDF log-log; um painel por direção; tabela dos graus zero abaixo do histograma).
# Cores e ordem das classes iguais às do notebook da AVD.
ORDEM = ["ilicito", "desconhecido", "licito"]
CORES = {"ilicito": "#c0392b", "desconhecido": "#95a5a6", "licito": "#2e8b57"}
NOMES = {"ilicito": "Ilícita", "desconhecido": "Desconhecida", "licito": "Lícita"}
TITULOS = {"entrada": "Grau de entrada", "saida": "Grau de saída"}


def faixas_log(grau_maximo: int) -> list[int]:
    """Limites das faixas logarítmicas de base 2: [1, 2), [2, 4), [4, 8), ... até cobrir o grau máximo."""
    limites = [1]
    while limites[-1] <= grau_maximo:
        limites.append(limites[-1] * 2)
    return limites


def tabela_grau_zero(graus: pd.DataFrame) -> pd.DataFrame:
    """Quantidade e proporção de carteiras com grau zero por classe e direção."""
    linhas = []
    for classe in ORDEM:
        g = graus[graus["classe"] == classe]
        linha = {"classe": NOMES[classe], "carteiras": len(g)}
        for direcao, coluna in DIRECOES.items():
            zeros = int((g[coluna] == 0).sum())
            linha[f"zero_{direcao}"] = zeros
            linha[f"prop_zero_{direcao}"] = zeros / len(g)
        linhas.append(linha)
    return pd.DataFrame(linhas)


def ccdf(serie: pd.Series) -> tuple[list[int], list[float]]:
    """Para cada grau k >= 1 presente, a proporção de carteiras (da classe inteira) com grau >= k."""
    total = len(serie)
    valores = serie[serie > 0].value_counts().sort_index()
    acumulado = valores[::-1].cumsum()[::-1]
    return list(valores.index), list(acumulado / total)


def figura_histograma(graus: pd.DataFrame, caminho: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    import numpy as np

    limites = faixas_log(int(graus[list(DIRECOES.values())].max().max()))
    inicio = np.array(limites[:-1], dtype=float)
    n = len(ORDEM)
    fig, eixos = plt.subplots(1, 2, figsize=(13, 6.5), sharey=True)
    for eixo, (direcao, coluna) in zip(eixos, DIRECOES.items()):
        for i, classe in enumerate(ORDEM):
            serie = graus.loc[graus["classe"] == classe, coluna]
            contagem, _ = np.histogram(serie[serie > 0], bins=limites)
            # proporção em relação à classe inteira (inclui as carteiras de grau zero, que vão para a tabela)
            proporcao = contagem / len(serie)
            # barras lado a lado: cada faixa [a, 2a) é dividida em n partes iguais na escala log
            esquerda = inicio * 2 ** (i / n)
            largura = inicio * 2 ** ((i + 1) / n) - esquerda
            mostrar = proporcao > 0
            eixo.bar(esquerda[mostrar], proporcao[mostrar], width=largura[mostrar], align="edge",
                     color=CORES[classe], edgecolor="white", linewidth=0.5, label=NOMES[classe])
        for limite in limites:
            eixo.axvline(limite, color="#cccccc", linewidth=0.6, zorder=0)
        eixo.set_xscale("log", base=2)
        eixo.set_yscale("log")
        eixo.set_title(TITULOS[direcao])
        eixo.set_xlabel("Grau (faixas logarítmicas de base 2)")
        eixo.grid(True, which="major", alpha=0.3)
    eixos[0].set_ylabel("Proporção das carteiras da classe")
    eixos[0].legend(title="Classe")
    fig.suptitle("Distribuição dos graus de entrada e de saída por classe (carteiras com grau ≥ 1)", fontsize=13)

    zeros = tabela_grau_zero(graus)
    celulas = [[r["classe"], f"{r['carteiras']:,}".replace(",", "."),
                f"{r['zero_entrada']:,}".replace(",", ".") + f" ({r['prop_zero_entrada']:.1%})".replace(".", ","),
                f"{r['zero_saida']:,}".replace(",", ".") + f" ({r['prop_zero_saida']:.1%})".replace(".", ",")]
               for _, r in zeros.iterrows()]
    tabela = fig.add_axes([0.2, 0.02, 0.6, 0.16])
    tabela.axis("off")
    t = tabela.table(cellText=celulas, loc="center", cellLoc="center",
                     colLabels=["Classe", "Carteiras", "Grau de entrada zero", "Grau de saída zero"])
    t.auto_set_font_size(False)
    t.set_fontsize(10)
    tabela.set_title("Carteiras com grau zero (fora do gráfico, pois não cabem na escala log)", fontsize=10)
    fig.subplots_adjust(top=0.88, bottom=0.32, wspace=0.08)
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)


def figura_ccdf(graus: pd.DataFrame, caminho: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, eixos = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    for eixo, (direcao, coluna) in zip(eixos, DIRECOES.items()):
        for classe in ORDEM:
            x, y = ccdf(graus.loc[graus["classe"] == classe, coluna])
            eixo.step(x, y, where="post", color=CORES[classe], linewidth=1.8, label=NOMES[classe])
        eixo.set_xscale("log")
        eixo.set_yscale("log")
        eixo.set_title(TITULOS[direcao])
        eixo.set_xlabel("Grau k")
        eixo.grid(True, which="major", alpha=0.3)
    eixos[0].set_ylabel("Proporção das carteiras da classe com grau ≥ k")
    eixos[0].legend(title="Classe")
    fig.suptitle("Distribuição acumulada complementar (CCDF) dos graus por classe", fontsize=13)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dataset", default="data/dataset_parte2", help="pasta com arestas.csv e nos.csv")
    parser.add_argument("--out", default="out/parte2", help="pasta de saída")
    args = parser.parse_args()

    pasta = Path(args.dataset)
    arestas = pd.read_csv(pasta / "arestas.csv", usecols=["origem", "destino"], dtype=str)
    nos = pd.read_csv(pasta / "nos.csv", usecols=["endereco", "classe"], dtype=str)

    graus = calcular_graus(arestas, nos)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    graus.to_csv(out / "graus_parte2.csv", index=False)
    frequencia(graus).to_csv(out / "graus_frequencia.csv", index=False)
    (out / "graus_resumo.json").write_text(
        json.dumps(resumo(graus, len(arestas)), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    tabela_grau_zero(graus).to_csv(out / "graus_zero.csv", index=False)
    figura_histograma(graus, out / "graus_histograma.png")
    figura_ccdf(graus, out / "graus_ccdf.png")
    print(f"Graus de {len(graus)} carteiras gravados em {out}")


if __name__ == "__main__":
    main()
