"""Gera o recorte do grafo de carteiras (addr -> addr) do Elliptic++ usado na Parte 2.

Uso:
    python scripts/baixar_dataset.py
    python scripts/amostrar_dataset.py [--arestas 25000] [--sementes 50] [--seed 42]

Decisões aplicadas (ver docs/PARTE2_DATASET.md):
- laços (A -> A, troco) removidos;
- arestas duplicadas do mesmo par agregadas em um arco (valor_btc = soma, n_txs = contagem);
- atributos das carteiras somados em todos os time steps;
- transação sem valor: preenche com in_BTC_total - fees; se ainda faltar, valor_faltante = True;
- peso (Bellman-Ford) = saldo líquido da carteira de DESTINO = btc_received_total - btc_sent_total;
- peso do Dijkstra = valor_btc (soma do total_BTC das transações do par, sempre >= 0);
- recorte em bola de neve a partir de carteiras ilícitas, até atingir o número de arestas pedido.

Saídas em data/dataset_parte2/: arestas.csv, nos.csv, recorte_info.json.
"""
# [IA] Claude Code – manipulação de dados com pandas (limpeza, agregação e recorte do dataset)
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "dataset_parte2" / "raw"
SAIDA = RAIZ / "data" / "dataset_parte2"

COLS_SOMA = ["btc_received_total", "btc_sent_total", "total_txs", "fees_total"]
COLS_MAX = ["lifetime_in_blocks", "num_timesteps_appeared_in"]


def carregar_arestas() -> tuple[pd.DataFrame, dict]:
    at = pd.read_csv(RAW / "AddrTx_edgelist.csv")
    ta = pd.read_csv(RAW / "TxAddr_edgelist.csv")
    tx = pd.read_csv(RAW / "txs_features.csv", usecols=["txId", "total_BTC", "in_BTC_total", "fees"])

    tx["valor"] = tx["total_BTC"].fillna(tx["in_BTC_total"] - tx["fees"])
    trios = at.merge(ta, on="txId").merge(tx[["txId", "valor"]], on="txId", how="left")
    trios = trios.rename(columns={"input_address": "origem", "output_address": "destino"})

    info = {"arestas_brutas": len(trios)}
    lacos = trios["origem"] == trios["destino"]
    info["lacos_removidos"] = int(lacos.sum())
    trios = trios[~lacos]

    por_par = trios.groupby(["origem", "destino"])
    arestas = pd.DataFrame({
        "valor_btc": por_par["valor"].sum(min_count=1),
        "n_txs": por_par["txId"].nunique(),
    }).reset_index()
    info["duplicatas_agregadas"] = len(trios) - len(arestas)
    arestas["valor_faltante"] = arestas["valor_btc"].isna()
    return arestas, info


def carregar_carteiras() -> pd.DataFrame:
    feats = pd.read_csv(RAW / "wallets_features.csv", usecols=["address"] + COLS_SOMA + COLS_MAX)
    agg = {c: "sum" for c in COLS_SOMA} | {c: "max" for c in COLS_MAX}
    nos = feats.groupby("address").agg(agg)
    nos["saldo_btc"] = nos["btc_received_total"] - nos["btc_sent_total"]
    classes = pd.read_csv(RAW / "wallets_classes.csv").set_index("address")["class"]
    nos["classe"] = classes.map({1: "ilicito", 2: "licito", 3: "desconhecido"})
    return nos.reset_index().rename(columns={"address": "endereco"})


def bola_de_neve(arestas: pd.DataFrame, sementes: list[str], alvo: int, rng: np.random.Generator,
                 lote: int) -> set[str]:
    """Expande o conjunto de nós por vizinhança (entrada e saída) até o subgrafo induzido ter >= alvo arestas."""
    selecionados = set(sementes)
    fronteira = list(sementes)
    while fronteira:
        viz = arestas.loc[arestas["origem"].isin(fronteira), "destino"]
        viz = pd.concat([viz, arestas.loc[arestas["destino"].isin(fronteira), "origem"]]).unique()
        novos = [n for n in viz if n not in selecionados]
        rng.shuffle(novos)
        fronteira = []
        for i in range(0, len(novos), lote):
            bloco = novos[i:i + lote]
            selecionados.update(bloco)
            fronteira.extend(bloco)
            induzidas = arestas["origem"].isin(selecionados) & arestas["destino"].isin(selecionados)
            if induzidas.sum() >= alvo:
                return selecionados
    return selecionados


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--arestas", type=int, default=25_000, help="mínimo de arestas do recorte")
    parser.add_argument("--sementes", type=int, default=50, help="nº de carteiras ilícitas iniciais")
    parser.add_argument("--lote", type=int, default=100, help="nós adicionados por vez na expansão")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    rng = np.random.default_rng(args.seed)

    print("carregando arestas e transações...")
    arestas, info = carregar_arestas()
    print("carregando carteiras...")
    nos = carregar_carteiras()

    ilicitas = nos.loc[nos["classe"] == "ilicito", "endereco"]
    ilicitas = ilicitas[ilicitas.isin(arestas["origem"]) | ilicitas.isin(arestas["destino"])]
    sementes = list(rng.choice(ilicitas.to_numpy(), size=args.sementes, replace=False))

    print("expandindo o recorte...")
    sel = bola_de_neve(arestas, sementes, args.arestas, rng, args.lote)
    rec = arestas[arestas["origem"].isin(sel) & arestas["destino"].isin(sel)].copy()

    saldo = nos.set_index("endereco")["saldo_btc"]
    rec["peso"] = rec["destino"].map(saldo)
    rec = rec[["origem", "destino", "peso", "valor_btc", "n_txs", "valor_faltante"]]
    rec_nos = nos[nos["endereco"].isin(sel)]

    rec.to_csv(SAIDA / "arestas.csv", index=False)
    rec_nos.to_csv(SAIDA / "nos.csv", index=False)

    info |= {
        "parametros": vars(args),
        "sementes": sementes,
        "nos": len(rec_nos),
        "arestas": len(rec),
        "arestas_peso_negativo": int((rec["peso"] < 0).sum()),
        "arestas_peso_zero": int((rec["peso"] == 0).sum()),
        "arestas_valor_faltante": int(rec["valor_faltante"].sum()),
        "nos_sem_features": int(len(sel) - len(rec_nos)),
        "nos_por_classe": rec_nos["classe"].value_counts().to_dict(),
    }
    (SAIDA / "recorte_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in info.items() if k != "sementes"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
