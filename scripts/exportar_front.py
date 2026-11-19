"""Exporta os dados usados pelo projeto React (front-react/).

Uso: python -m scripts.exportar_front
Gera front-react/src/dados.json a partir dos mapas, do grafo de estados e dos algoritmos do grupo
(src/graphs) e do recorte da Parte 2. Nenhum algoritmo é implementado aqui.
"""
# [IA] Claude Code – exporta para JSON os resultados já calculados pelo código do grupo

import json
from pathlib import Path

import pandas as pd

from src.visualizar_parte1 import preparar_mapa
from src.viz import ler_rotulo

RAIZ = Path(__file__).resolve().parent.parent
ALGORITMOS = ("BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD")
ORDEM = ["ilicito", "desconhecido", "licito"]


def dados_parte1():
    mapas = {}
    arquivos = sorted((RAIZ / "data" / "mapas").glob("*.txt")) + sorted((RAIZ / "data" / "mapas_grupo").glob("*.txt"))
    for arquivo in arquivos:
        dados, grafo, _, resultados = preparar_mapa(arquivo, ALGORITMOS)
        mapa = {
            "grade": dados["grade"],
            "percursos": dados["algoritmos"],
            "custos": dados["custos"],
            "status": dados["status"],
            "n_estados": len([no for no in grafo.nos() if no != "ALVO"]),
            "n_arcos": grafo.tamanho(),
        }
        if arquivo.stem.startswith("m08"):
            contagem = {}
            for no in grafo.nos():
                rotulo = ler_rotulo(no)
                if rotulo:
                    chave = f"{rotulo[0]},{rotulo[1]}"
                    contagem[chave] = contagem.get(chave, 0) + 1
            mapa["multiplicidade"] = contagem
        if arquivo.stem.startswith("m02"):
            mapa["grafo"] = {
                "nos": [no for no in grafo.nos() if no != "ALVO"],
                "arcos": [[u, v, p] for u, v, p in grafo.arestas() if "ALVO" not in (u, v)],
            }
            bfs = resultados["BFS"]
            mapa["arvore_bfs"] = {
                "camadas": {str(k): [n for n in v if n != "ALVO"] for k, v in bfs["camadas"].items()},
                "arcos": [[u, v] for u, v in bfs["arvore"] if "ALVO" not in (u, v)],
            }
        mapas[arquivo.stem] = mapa
    return {"mapas": mapas}


def dados_avd():
    pasta = RAIZ / "data" / "dataset_parte2"
    nos = pd.read_csv(pasta / "nos.csv")
    arestas = pd.read_csv(pasta / "arestas.csv")
    classe = nos.set_index("endereco")["classe"]
    origem = arestas["origem"].map(classe)
    destino = arestas["destino"].map(classe)
    proporcao = pd.crosstab(origem, destino, normalize="index").reindex(index=ORDEM, columns=ORDEM)
    sinal = arestas["peso"].apply(lambda p: "negativo" if p < 0 else ("zero" if p == 0 else "positivo"))
    sinais = pd.crosstab(destino, sinal).reindex(ORDEM)[["negativo", "zero", "positivo"]]
    return {
        "ordem": ORDEM,
        "contagem": nos["classe"].value_counts().reindex(ORDEM).astype(int).to_dict(),
        "mediana_recebido": nos.groupby("classe")["btc_received_total"].median().reindex(ORDEM).round(6).to_dict(),
        "origem_destino": {o: {d: round(float(proporcao.loc[o, d]), 4) for d in ORDEM} for o in ORDEM},
        "sinal_peso": {c: {s: int(sinais.loc[c, s]) for s in sinais.columns} for c in ORDEM},
    }


def main():
    dados = {"parte1": dados_parte1(), "avd": dados_avd()}
    destino = RAIZ / "front-react" / "src" / "dados.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    print(f"Gerado {destino} ({destino.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
