"""Leva o rótulo das transações do Elliptic++ (txs_classes.csv) para as arestas do recorte da Parte 2.

Uso:
    python scripts/rotular_transacoes.py

Precisa em data/dataset_parte2/raw/: AddrTx_edgelist.csv, TxAddr_edgelist.csv e txs_classes.csv
(IDs do Drive: AddrTx e TxAddr já estão em scripts/baixar_dataset.py; txs_classes.csv é o arquivo
1DiBxn8TXdbJqoSw58pYUeaqO3oOKhuQO da mesma pasta do Drive do EllipticPlusPlus).

Não altera arestas.csv nem nos.csv. Gera em data/dataset_parte2/:
- arestas_transacoes.csv: uma linha por aresta do recorte, com quantas das transações daquele par
  são ilícitas, lícitas ou desconhecidas (a soma bate com n_txs);
- transacoes_recorte.csv: uma linha por transação que gerou alguma aresta do recorte, com a classe
  e em quantas arestas do recorte ela aparece (uma transação com várias entradas e saídas vira
  vários arcos, então % de arestas e % de transações são números diferentes).
"""
# [IA] Claude Code – manipulação de dados com pandas (junção do rótulo das transações com as arestas do recorte)
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "dataset_parte2" / "raw"
PASTA = RAIZ / "data" / "dataset_parte2"

CLASSES = ["ilicito", "licito", "desconhecido"]
MAPA_CLASSE = {1: "ilicito", 2: "licito", 3: "desconhecido", "1": "ilicito", "2": "licito",
               "3": "desconhecido", "unknown": "desconhecido"}


def rotular(arestas: pd.DataFrame, addr_tx: pd.DataFrame, tx_addr: pd.DataFrame,
            classes_tx: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Liga cada aresta (origem, destino) do recorte às transações que a formaram e conta as classes.

    addr_tx: input_address, txId · tx_addr: txId, output_address · classes_tx: txId, class.
    Usa a mesma regra do amostrar_dataset.py: par (entrada, saída) da mesma transação, sem laços.
    """
    carteiras = set(arestas["origem"]) | set(arestas["destino"])
    entradas = addr_tx[addr_tx["input_address"].isin(carteiras)]
    saidas = tx_addr[tx_addr["output_address"].isin(carteiras)]
    trios = entradas.merge(saidas, on="txId").rename(
        columns={"input_address": "origem", "output_address": "destino"})
    trios = trios[trios["origem"] != trios["destino"]].drop_duplicates()
    trios = trios.merge(arestas[["origem", "destino"]], on=["origem", "destino"])

    classe = classes_tx.set_index("txId")["class"].map(MAPA_CLASSE)
    trios["classe"] = trios["txId"].map(classe)
    if trios["classe"].isna().any():
        raise ValueError("transação do recorte sem classe em txs_classes.csv")

    contagem = (trios.groupby(["origem", "destino", "classe"])["txId"].nunique()
                .unstack(fill_value=0).reindex(columns=CLASSES, fill_value=0)
                .add_prefix("n_tx_").reset_index())
    contagem.columns.name = None
    arestas_tx = arestas[["origem", "destino", "n_txs"]].merge(contagem, on=["origem", "destino"], how="left")
    cols = [f"n_tx_{c}" for c in CLASSES]
    arestas_tx[cols] = arestas_tx[cols].fillna(0).astype(int)
    if not (arestas_tx[cols].sum(axis=1) == arestas_tx["n_txs"]).all():
        raise ValueError("contagem por classe não bate com n_txs de alguma aresta")

    transacoes = (trios.groupby(["txId", "classe"]).size().rename("n_arestas").reset_index())
    return arestas_tx, transacoes


def resumo(arestas_tx: pd.DataFrame, transacoes: pd.DataFrame) -> None:
    n = len(arestas_tx)
    print(f"Arestas do recorte: {n}")
    for c in CLASSES:
        alguma = (arestas_tx[f"n_tx_{c}"] > 0).sum()
        print(f"  com pelo menos 1 transação {c}: {alguma} ({100 * alguma / n:.1f}%)")
    so_desc = (arestas_tx["n_tx_desconhecido"] == arestas_tx["n_txs"]).sum()
    print(f"  só com transações desconhecidas: {so_desc} ({100 * so_desc / n:.1f}%)")
    print(f"Transações distintas que formam o recorte: {len(transacoes)}")
    print(transacoes["classe"].value_counts().reindex(CLASSES, fill_value=0).to_string())
    print((100 * transacoes["classe"].value_counts(normalize=True)).reindex(CLASSES, fill_value=0)
          .round(1).to_string())


def main() -> None:
    arestas = pd.read_csv(PASTA / "arestas.csv")
    print("carregando edgelists e classes das transações...")
    addr_tx = pd.read_csv(RAW / "AddrTx_edgelist.csv")
    tx_addr = pd.read_csv(RAW / "TxAddr_edgelist.csv")
    classes_tx = pd.read_csv(RAW / "txs_classes.csv")

    arestas_tx, transacoes = rotular(arestas, addr_tx, tx_addr, classes_tx)
    arestas_tx.to_csv(PASTA / "arestas_transacoes.csv", index=False)
    transacoes.to_csv(PASTA / "transacoes_recorte.csv", index=False)
    resumo(arestas_tx, transacoes)


if __name__ == "__main__":
    main()
