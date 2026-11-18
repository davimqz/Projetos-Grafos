"""Graus de entrada e de saída das carteiras do recorte da Parte 2.

Uso: python -m scripts.graus_parte2 [--dataset data/dataset_parte2] [--out out/parte2]

Gera em --out:
- graus_parte2.csv: endereco, classe, grau_entrada, grau_saida (uma linha por carteira, inclusive grau 0)
- graus_frequencia.csv: direcao, grau, carteiras (quantas carteiras têm cada grau)
- graus_resumo.json: estatísticas por direção, no total e por classe, e as 5 carteiras de maior grau

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
    print(f"Graus de {len(graus)} carteiras gravados em {out}")


if __name__ == "__main__":
    main()
