"""Exportação dos arcos e resultados já calculados da Parte 1."""

# [IA] Codex - separação das exportações existentes, sem alterar os resultados.
from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from .modelos import DadosMapa


def exportar_arestas(dados: DadosMapa, caminho: str | Path) -> None:
    """Grava os arcos de G_est em arestas_<mapa>.csv.

    Cabeçalho: origem,destino,movimento,casa_destino,peso.
    Uma linha por arco dirigido existente, sem espelhamento, preservando
    a ordem dos nós e dos vizinhos. Os metadados descrevem o movimento
    físico e o símbolo original do destino; os pesos vêm do grafo.

    Para os arcos virtuais até ALVO, movimento e casa_destino ficam vazios.
    Usa CSV com escape correto dos rótulos que contêm vírgulas.
    Não constrói novas transições nem altera as regras do mapa.
    """

    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)

        escritor.writerow([
            "origem",
            "destino",
            "movimento",
            "casa_destino",
            "peso",
        ])

        arcos = (
            (origem, destino, peso)
            for origem in dados.grafo_estados.nos()
            for destino, peso in dados.grafo_estados.vizinhos(origem)
        )
        for origem, destino, peso in arcos:

            if destino == "ALVO":
                escritor.writerow([origem, destino, "", "", peso])
                continue

            estado_origem = dados.estados[origem]
            estado_destino = dados.estados[destino]

            diffx = estado_origem.linha - estado_destino.linha
            diffy = estado_origem.coluna - estado_destino.coluna

            if diffx == 1 and diffy == 0:
                movimento = "N"
            elif diffx == -1 and diffy == 0:
                movimento = "S"
            elif diffx == 0 and diffy == 1:
                movimento = "O"
            else:
                movimento = "L"

            escritor.writerow([
                origem,
                destino,
                movimento,
                dados.grade[estado_destino.linha][estado_destino.coluna],
                peso
            ])
