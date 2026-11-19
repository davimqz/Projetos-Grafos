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


def calcular_camadas(dados: DadosMapa) -> dict[str, object]:
    """Devolve os dados de um mapa para camadas.json.

    Uma camada corresponde a um conjunto de chaves, incluindo todos os
    conjuntos de bônus que aparecem com essas chaves. Registra ordem,
    tamanho e densidade de cada subgrafo induzido, sem ALVO.
    Também registra a quantidade de arcos entre camadas e as posições
    e símbolos das casas que os geram. Não inclui interpretações textuais.
    """

    nos_por_camada: dict[str, list[str]] = {}
    for rotulo, estado in dados.estados.items():
        camada = "".join(sorted(estado.chaves)) or "-"
        nos_por_camada.setdefault(camada, []).append(rotulo)

    tamanhos = dict.fromkeys(nos_por_camada, 0)
    camada_por_no = {no: camada for camada, nos in nos_por_camada.items() for no in nos}
    arcos_entre_camadas = 0
    casas_geradoras_dict: dict[tuple[int, int], str] = {}

    for origem, camada in camada_por_no.items():
        for destino, _ in dados.grafo_estados.vizinhos(origem):
            if destino not in camada_por_no:
                continue
            if camada == camada_por_no[destino]:
                tamanhos[camada] += 1
            else:
                arcos_entre_camadas += 1
                est_dest = dados.estados[destino]
                casas_geradoras_dict[(est_dest.linha, est_dest.coluna)] = dados.grade[est_dest.linha][est_dest.coluna]

    camadas = [
        {
            "camada": camada,
            "ordem": len(nos),
            "tamanho": tamanhos[camada],
            "densidade": _densidade(len(nos), tamanhos[camada]),
        }
        for camada, nos in sorted(
            nos_por_camada.items(), key=lambda item: (0 if item[0] == "-" else len(item[0]), item[0])
        )
    ]

    casas_geradoras = [
        {"linha": linha, "coluna": coluna, "simbolo": simbolo}
        for (linha, coluna), simbolo in sorted(casas_geradoras_dict.items())
    ]

    return {
        "camadas": camadas,
        "arcos_entre_camadas": arcos_entre_camadas,
        "casas_geradoras": casas_geradoras,
    }
