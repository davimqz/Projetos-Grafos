"""Carga do recorte da Parte 2 (data/dataset_parte2/) para o grafo do grupo.

Pacote P4a — Dados.

- ler_arestas: arestas.csv -> lista de (origem, destino, peso), na ordem do arquivo
- ler_nos: nos.csv -> {endereco: {atributos}} (classe, saldo etc.), para as análises
- carregar_grafo: insere as arestas em um grafo que tenha adicionar_arco(u, v, peso)

O nome do método adicionar_arco ainda precisa ser confirmado com o Thomaz (P2, graph.py).
Os nós são os endereços das carteiras (str).
"""
# [IA] Claude Code – leitura e validação dos CSVs do recorte com pandas (IO)
from pathlib import Path

import pandas as pd

PASTA_PADRAO = Path(__file__).resolve().parent.parent / "data" / "dataset_parte2"
COLUNAS_ARESTAS = ["origem", "destino", "peso"]
COLUNAS_NOS = ["endereco", "classe"]


def _ler_csv(caminho: Path, obrigatorias: list[str]) -> pd.DataFrame:
    if not caminho.exists():
        raise FileNotFoundError(f"arquivo não encontrado: {caminho}")
    df = pd.read_csv(caminho, dtype={c: str for c in obrigatorias if c != "peso"})
    faltando = [c for c in obrigatorias if c not in df.columns]
    if faltando:
        raise ValueError(f"{caminho.name}: faltam as colunas {faltando}")
    vazios = df[obrigatorias].isna().any(axis=1)
    if vazios.any():
        linha = int(vazios.idxmax()) + 2  # +1 do cabeçalho, +1 por começar em 1
        raise ValueError(f"{caminho.name}: valor vazio na linha {linha}")
    return df


def ler_arestas(pasta: str | Path = PASTA_PADRAO) -> list[tuple[str, str, float]]:
    """Devolve as arestas (origem, destino, peso) na ordem em que aparecem no CSV."""
    df = _ler_csv(Path(pasta) / "arestas.csv", COLUNAS_ARESTAS)
    return list(zip(df["origem"], df["destino"], df["peso"].astype(float)))


def ler_nos(pasta: str | Path = PASTA_PADRAO) -> dict[str, dict]:
    """Devolve {endereco: {coluna: valor}} com todos os atributos de nos.csv."""
    df = _ler_csv(Path(pasta) / "nos.csv", COLUNAS_NOS)
    if not df["endereco"].is_unique:
        raise ValueError("nos.csv: endereço repetido")
    return df.set_index("endereco").to_dict(orient="index")


def carregar_grafo(grafo, pasta: str | Path = PASTA_PADRAO):
    """Insere em `grafo` todas as arestas do recorte e devolve o próprio grafo."""
    for origem, destino, peso in ler_arestas(pasta):
        grafo.adicionar_arco(origem, destino, peso)
    return grafo
