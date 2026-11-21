"""Métricas, camadas, graus, classificação de arcos e estados-armadilha.

As análises preservam os grafos recebidos e não gravam arquivos.
ALVO participa das buscas, mas não das métricas físicas.
"""

# [IA] Codex - separação das análises existentes, preservando a lógica do integrante.
# [IA] Codex - reaproveitamento do resultado da DFS na orquestração e visualização.
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


def calcular_graus(dados: DadosMapa) -> list[GrauEstado]:
    """Devolve as linhas de graus_<mapa>.csv para os estados físicos.

    Os graus não contam arcos para ALVO. Mantém a ordem dos estados
    recebidos para permitir uma exportação reproduzível.
    """

    # Uma única passagem pelos arcos substitui uma varredura por estado.
    graus: dict[str, GrauEstado] = {
        rotulo: {"estado": rotulo, "grau_entrada": 0, "grau_saida": 0}
        for rotulo in dados.estados
    }
    for origem, grau in graus.items():
        for destino, _ in dados.grafo_estados.vizinhos(origem):
            if destino in graus:
                grau["grau_saida"] += 1
                graus[destino]["grau_entrada"] += 1
    return list(graus.values())


def analisar_graus(dados: DadosMapa) -> dict[str, object]:
    """Devolve rankings, multiplicidades por casa e estados de beco.

    Registra os estados de maior grau de entrada e saída, com desempate
    pela ordem de leitura do rótulo, e os respectivos graus físicos.
    Inclui a multiplicidade máxima, as casas que a atingem e sua quantidade.
    Becos são estados sem saída física que não estão em G.
    As explicações desses resultados ficam a cargo do grupo no PDF.
    """

    return _analisar_graus(dados, calcular_graus(dados))


def _analisar_graus(dados: DadosMapa, graus: list[GrauEstado]) -> dict[str, object]:
    """Reutiliza os graus já calculados durante a orquestração."""
    graus_entrada = {grau["estado"]: grau["grau_entrada"] for grau in graus}
    graus_saida = {grau["estado"]: grau["grau_saida"] for grau in graus}

    # Menor rótulo no empate, sem ordenar todos os estados.
    estado_maior_entrada = min(graus_entrada, key=lambda no: (-graus_entrada[no], no), default=None)
    estado_maior_saida = min(graus_saida, key=lambda no: (-graus_saida[no], no), default=None)

    multiplicidades: dict[tuple[int, int], int] = {}
    for estado in dados.estados.values():
        pos = (estado.linha, estado.coluna)
        multiplicidades[pos] = multiplicidades.get(pos, 0) + 1

    multiplicidade_maxima = max(multiplicidades.values(), default=0)
    casas_max = [
        {"linha": linha, "coluna": coluna, "simbolo": dados.grade[linha][coluna]}
        for (linha, coluna), qtd in sorted(multiplicidades.items())
        if qtd == multiplicidade_maxima
    ]

    becos = [
        rotulo
        for rotulo, estado in dados.estados.items()
        if graus_saida[rotulo] == 0 and dados.grade[estado.linha][estado.coluna] != "G"
    ]

    return {
        "estado_maior_grau_entrada": estado_maior_entrada,
        "maior_grau_entrada": graus_entrada.get(estado_maior_entrada, 0),
        "estado_maior_grau_saida": estado_maior_saida,
        "maior_grau_saida": graus_saida.get(estado_maior_saida, 0),
        "multiplicidade_maxima": multiplicidade_maxima,
        "casas_multiplicidade_maxima": casas_max,
        "quantidade_casas_multiplicidade_maxima": len(casas_max),
        "becos": becos,
        "quantidade_becos": len(becos),
    }


def classificar_arcos(dados: DadosMapa, resultados: dict[str, dict] | None = None) -> dict[str, object]:
    """Prepara a linha de um mapa para dfs_classificacao.csv.

    Usa a DFS existente a partir da origem, preservando a ordem N, L, S, O.
    A linha contém mapa, arvore, retorno, avanco e cruzamento.
    Também disponibiliza a indicação de ciclo para o relatório, separada
    das colunas obrigatórias. A busca inclui ALVO e seus arcos alcançáveis.
    """

    grafo = dados.grafo_estados
    inicio = dados.origem

    if resultados is None:
        resultados = {}
    if "DFS" not in resultados:
        resultados["DFS"] = dfs(grafo, inicio)
    resultado = resultados["DFS"]

    return {
        "mapa": dados.nome,
        "arvore": resultado["contagem_arcos"]["arvore"],
        "retorno": resultado["contagem_arcos"]["retorno"],
        "avanco": resultado["contagem_arcos"]["avanco"],
        "cruzamento": resultado["contagem_arcos"]["cruzamento"],
        "tem_ciclo": resultado["tem_ciclo"],
        }


def encontrar_armadilhas(dados: DadosMapa) -> list[str]:
    """Devolve os rótulos físicos alcançáveis sem caminho até ALVO.

    Reutiliza o transposto e uma busca já implementada pelo grupo.
    ALVO não pertence ao retorno. A lista mantém a ordem dos estados
    recebidos e serve tanto ao CSV obrigatório quanto à visualização.
    Não grava arquivos nem modifica o grafo original.
    """

    grafo = dados.grafo_estados.transposto()
    alcancaveis = set(bfs(grafo, "ALVO")["ordem"])

    out = []

    for rotulo in dados.estados:
        if rotulo not in alcancaveis:
            out.append(rotulo)

    return out
