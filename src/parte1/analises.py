"""Métricas, camadas, graus, classificação de arcos e estados-armadilha.

As análises preservam os grafos recebidos e não gravam arquivos.
ALVO participa das buscas, mas não das métricas físicas.
"""

# [IA] Codex - separação das análises existentes, preservando a lógica do integrante.
from __future__ import annotations

from collections import Counter

from src.graphs.algorithms import bfs, dfs
from .modelos import DadosMapa, GrauEstado


def calcular_metricas_globais(dados: DadosMapa) -> dict[str, object]:
    """Devolve as métricas de um mapa para metricas_global.json.

    Inclui ordem, tamanho e densidade de G_pos e G_est, teto teórico
    e taxa de ocupação. Não conta ALVO nem os arcos virtuais.
    O teto considera casas livres, chaves distintas e bônus consumíveis;
    na variante fonte_consumivel, inclui também as fontes consumíveis.
    Reutiliza as consultas de Grafo e não grava arquivos.
    """

    simbolos_livres = ".SG,~abcdABCD><^v+*"

    ordem_pos = dados.grafo_posicoes.ordem()
    tamanho_pos = dados.grafo_posicoes.tamanho()
    densidade_pos = _densidade(ordem_pos, tamanho_pos)

    ordem_est = len(dados.estados)
    tamanho_est = sum(
        destino in dados.estados
        for origem in dados.estados
        for destino, _ in dados.grafo_estados.vizinhos(origem)
    )
    densidade_est = _densidade(ordem_est, tamanho_est)

    contagem: Counter[str] = Counter()
    for linha in dados.grade:
        contagem.update(linha)
    casas_livres = sum(contagem[char] for char in simbolos_livres)
    chaves_distintas = sum(char in contagem for char in "abcd")
    bonus_consumiveis = contagem["+"]
    fontes_consumiveis = contagem["*"]

    teto_teorico = casas_livres * (2 ** chaves_distintas) * (2 ** bonus_consumiveis)
    if dados.fonte_consumivel:
        teto_teorico *= (2 ** fontes_consumiveis)

    taxa_ocupacao = ordem_est / teto_teorico if teto_teorico > 0 else 0

    return {
        "ordem_pos": ordem_pos,
        "tamanho_pos": tamanho_pos,
        "densidade_pos": densidade_pos,
        "ordem_est": ordem_est,
        "tamanho_est": tamanho_est,
        "densidade_est": densidade_est,
        "teto_teorico": teto_teorico,
        "taxa_ocupacao": taxa_ocupacao
    }


def _densidade(ordem: int, tamanho: int) -> float:
    """Calcula a mesma densidade dirigida sem copiar um subgrafo."""
    return tamanho / (ordem * (ordem - 1)) if ordem > 1 else 0.0
