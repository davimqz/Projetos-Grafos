"""Contratos da orquestração e das entregas da Parte 1 (P3).

As análises foram escritas pelo integrante. Este módulo reutiliza a leitura,
a construção dos grafos e os algoritmos existentes em src.graphs.
As visualizações pertencem a src.viz e src.visualizar_parte1.

As funções de cálculo não gravam arquivos nem modificam os grafos recebidos.
ALVO participa das buscas, mas ele e seus arcos não entram nas métricas
físicas. A Parte 2 continua nos seus módulos específicos.
"""

# [IA] Codex - boilerplate original de tipos, assinaturas e contratos.
from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict

from src.graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
from src.graphs.estados import (
    Estado, construir_grafo_estados, construir_grafo_posicoes,
    rotular_estado, rotular_posicao,
)
from src.graphs.graph import Grafo
from src.graphs.io import encontrar_inicio, encontrar_saidas, ler_mapa
from src.viz import reconstruir_percurso

from src.parte1.modelos import AlgoritmoCaminho, StatusSolucao, DadosMapa, GrauEstado, Solucao

from src.parte1.carga import carregar_mapa

from src.parte1.exportacao import exportar_arestas

from src.parte1.exportacao import exportar_csv, exportar_json

# [IA] Codex - otimização das análises e da integração, preservando a lógica do integrante; algoritmos e construção dos grafos permanecem em src.graphs.

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


def resolver_mapa(dados: DadosMapa, algoritmo: AlgoritmoCaminho) -> Solucao:
    """Normaliza o resultado de um algoritmo existente até ALVO.

    BFS procura menos passos; Dijkstra e Bellman-Ford procuram menor custo.
    O caminho com status OK contém os rótulos desde a origem até ALVO.
    passos conta movimentos físicos, sem o arco virtual; custo representa
    a soma dos pesos do caminho, inclusive quando a busca usada é BFS.

    Registra RECUSA para Dijkstra com peso negativo, CICLO_NEGATIVO quando
    Bellman-Ford o detectar e SEM_SOLUCAO para ALVO inalcançável.
    Não implementa novamente os algoritmos e não grava arquivos.
    """
    return _resolver_mapa(dados, algoritmo, {})


def _resultado_busca(dados: DadosMapa, algoritmo: AlgoritmoCaminho, resultados: dict[str, dict]) -> dict:
    """Executa cada busca no máximo uma vez por mapa na orquestração."""
    if algoritmo not in resultados:
        buscar = {"BFS": bfs, "DIJKSTRA": dijkstra, "BELLMAN_FORD": bellman_ford}[algoritmo]
        resultados[algoritmo] = buscar(dados.grafo_estados, dados.origem)
    return resultados[algoritmo]


def _resolver_mapa(dados: DadosMapa, algoritmo: AlgoritmoCaminho, resultados: dict[str, dict]) -> Solucao:
    """Normaliza buscas existentes, com reutilização local dos resultados."""

    grafo = dados.grafo_estados
    inicio = dados.origem

    if inicio not in grafo.nos():
        raise ValueError(f"Origem '{inicio}' não existe no grafo.")

    if algoritmo not in ("BFS", "DIJKSTRA", "BELLMAN_FORD"):
        raise ValueError(f"Algoritmo desconhecido: {algoritmo}")

    caminho: list[str] = []
    custo: float | None = None
    try:
        resultado = _resultado_busca(dados, algoritmo, resultados)
        status = "OK" if algoritmo == "BFS" else resultado["status"]
        if status == "OK":
            caminho = reconstruir_percurso(resultado, inicio, "ALVO")
            if algoritmo == "BFS":
                custo = 0.0
                for origem, destino in zip(caminho, caminho[1:]):
                    for vizinho, peso in grafo.vizinhos(origem):
                        if vizinho == destino:
                            custo += peso
                            break
            else:
                custo = resultado["distancia"]["ALVO"]
    except ValueError as erro:
        status = "RECUSA" if algoritmo == "DIJKSTRA" and "negativo" in str(erro) else "SEM_SOLUCAO"

    if status != "OK":
        passos = None
        custo = None
        caminho = []
    else:
        passos = len(caminho) - 2

    return Solucao(
        mapa=dados.nome,
        algoritmo=algoritmo,
        passos=passos,
        custo=custo,
        status=status,
        caminho=caminho
    )

def classificar_arcos(dados: DadosMapa) -> dict[str, object]:
    """Prepara a linha de um mapa para dfs_classificacao.csv.

    Usa a DFS existente a partir da origem, preservando a ordem N, L, S, O.
    A linha contém mapa, arvore, retorno, avanco e cruzamento.
    Também disponibiliza a indicação de ciclo para o relatório, separada
    das colunas obrigatórias. A busca inclui ALVO e seus arcos alcançáveis.
    """

    grafo = dados.grafo_estados
    inicio = dados.origem

    resultado = dfs(grafo, inicio)

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


def comparar_modelagens(dados: DadosMapa) -> list[dict[str, object]]:
    """Prepara as três linhas de um mapa para comparacao_modelagem.csv.

    Compara BFS com portas como chão, portas como parede e G_est correto.
    Colunas: mapa,abordagem,passos,caminho_valido,observacao.
    Os passos são movimentos físicos até uma saída; ausência de caminho
    deve ser representada explicitamente. Não compara os pesos dos caminhos.

    A validade considera as regras originais de chaves e portas.
    As observações interpretativas devem ser escritas pelo integrante.
    Os casos obrigatórios são m02, m03 e m04.
    """
    return _comparar_modelagens(dados, {})


def _comparar_modelagens(dados: DadosMapa, resultados_buscas: dict[str, dict]) -> list[dict[str, object]]:
    """Compara as modelagens aproveitando a BFS de estados quando disponível."""

    inicio_pos = rotular_posicao(encontrar_inicio(dados.grade))
    saidas_pos = {rotular_posicao(pos) for pos in encontrar_saidas(dados.grade)}

    grafos_posicoes = [
        ("portas_como_chao", dados.grafo_posicoes, "Ignora chaves e atravessa portas diretamente."),
        ("portas_como_parede", construir_grafo_posicoes(dados.grade, portas="parede"), "Bloqueia portas mesmo quando há chave disponível."),
    ]

    resultados: list[dict[str, object]] = []

    for abordagem, grafo, obs in grafos_posicoes:
        res = bfs(grafo, inicio_pos)
        destino = next((no for no in res["ordem"] if no in saidas_pos), None)

        if destino is None:
            passos = None
            valido = False
        else:
            caminho = reconstruir_percurso(res, inicio_pos, destino)

            passos = len(caminho) - 1
            chaves: set[str] = set()
            valido = True
            for no in caminho:
                linha, coluna = map(int, no.strip("()").split(","))
                casa = dados.grade[linha][coluna]
                if casa in "abcd":
                    chaves.add(casa)
                elif casa in "ABCD" and casa.lower() not in chaves:
                    valido = False
                    break

        resultados.append({
            "mapa": dados.nome,
            "abordagem": abordagem,
            "passos": passos,
            "caminho_valido": valido,
            "observacao": obs,
        })

    dist_est = _resultado_busca(dados, "BFS", resultados_buscas)["distancia"]["ALVO"]
    passos_est = None if dist_est == float("inf") else int(dist_est) - 1

    resultados.append({
        "mapa": dados.nome,
        "abordagem": "grafo_estados",
        "passos": passos_est,
        "caminho_valido": passos_est is not None,
        "observacao": "Modelagem exata com memória de chaves coletadas.",
    })

    return resultados

def comparar_bonus(dados: DadosMapa) -> dict[str, object]:
    """Reúne as execuções de Bellman-Ford do experimento do m05.

    Compara G_pos com bônus de custo fixo e G_est com memória de consumo.
    Disponibiliza os resultados, incluindo ciclo e custo quando retornados
    pelo algoritmo existente. Recebe o m05 na variante padrão.
    Não escreve a prova nem a interpretação exigida no PDF.
    """
    return _comparar_bonus(dados, {})


def _comparar_bonus(dados: DadosMapa, resultados_buscas: dict[str, dict]) -> dict[str, object]:
    """Reaproveita o Bellman-Ford de estados sem alterar o experimento."""

    grafo_pos = dados.grafo_posicoes

    resultado_estados = _resultado_busca(dados, "BELLMAN_FORD", resultados_buscas)
    resultado_pos = bellman_ford(grafo_pos, rotular_posicao(encontrar_inicio(dados.grade)))

    return{
        "mapa": dados.nome,
        "grafo_posicoes": {
            "status":resultado_pos["status"],
            "tem_ciclo_negativo": resultado_pos["tem_ciclo_negativo"],
            "ciclo_negativo":resultado_pos["ciclo_negativo"],
            "custo_ciclo":resultado_pos["custo_ciclo"]
        },
        "grafo_estados": {
            "status":resultado_estados["status"],
            "tem_ciclo_negativo": resultado_estados["tem_ciclo_negativo"],
            "ciclo_negativo":resultado_estados["ciclo_negativo"],
            "custo_ciclo":resultado_estados["custo_ciclo"],
            "custo_ate_alvo":resultado_estados["distancia"]["ALVO"]
        }
    }

# [IA] Codex - escrita genérica de CSV com resultados já calculados.
# [IA] Codex - escrita genérica de JSON com dados já preparados.
# [IA] Codex - integração das análises do integrante e exportação dos resultados.
def executar_parte1(
    mapas: Iterable[str | Path], saida: str | Path, *, fonte_consumivel: bool = False,
) -> None:
    """Orquestra as entregas dos mapas informados, incluindo mapas do grupo.

    Prepara os mapas e reúne métricas globais, camadas, graus, rankings,
    multiplicidades, becos, soluções e classificação DFS. Exporta os arcos
    de todos os mapas, inclusive m08 quando estiver entre as entradas.

    Saídas: metricas_global.json, camadas.json, graus_<mapa>.csv,
    arestas_<mapa>.csv, solucoes.csv e dfs_classificacao.csv.
    Para os mapas correspondentes, inclui comparacao_modelagem.csv,
    percurso_m03.json (menor custo, estado a estado), ciclo_negativo_m06.json
    (sequência de estados e custo), armadilhas_m04.csv e armadilhas_m07.csv.
    Reúne ainda o experimento padrão em comparacao_bonus_m05.json e listas
    armadilhas_m04.json/armadilhas_m07.json compatíveis com a CLI existente.
    Os mapas fornecidos usam identificadores m01 a m08; mapas próprios
    mantêm o nome do arquivo sem extensão. Identificadores repetidos são erro.

    Os resultados da variante fonte_consumivel devem ir para uma pasta
    de saída diferente da execução padrão, escolhida pelo chamador.
    Não implementa algoritmos, desenha figuras nem redige análises do PDF.
    Erros de entrada e escrita são propagados para tratamento pela CLI.
    """

    nomes_fornecidos = {
        "m01_terreno": "m01",
        "m02_uma_chave": "m02",
        "m03_tres_chaves": "m03",
        "m04_esteiras": "m04",
        "m05_bonus": "m05",
        "m06_fonte": "m06",
        "m07_impossivel": "m07",
        "m08_grande": "m08",
    }
    entradas: list[tuple[Path, str]] = []
    for mapa in mapas:
        arquivo = Path(mapa)
        nome = nomes_fornecidos.get(arquivo.stem, arquivo.stem)
        entradas.append((arquivo, nome))
    nomes = [nome for _, nome in entradas]
    if len(nomes) != len(set(nomes)):
        raise ValueError("Os mapas devem ter identificadores distintos na mesma execução.")

    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    metricas: dict[str, object] = {}
    camadas: dict[str, object] = {}
    solucoes: list[Solucao] = []
    classificacoes: list[dict[str, object]] = []
    comparacoes: list[dict[str, object]] = []
    algoritmos: tuple[AlgoritmoCaminho, ...] = ("BFS", "DIJKSTRA", "BELLMAN_FORD")

    for arquivo, nome in entradas:
        dados = carregar_mapa(arquivo, nome=nome, fonte_consumivel=fonte_consumivel)
        graus = calcular_graus(dados)
        resultados_buscas: dict[str, dict] = {}
        classificacao = classificar_arcos(dados)
        classificacoes.append(classificacao)
        metricas[nome] = {
            **calcular_metricas_globais(dados),
            **_analisar_graus(dados, graus),
            "tem_ciclo_dfs": classificacao["tem_ciclo"],
            "fonte_consumivel": fonte_consumivel,
        }
        camadas[nome] = calcular_camadas(dados)
        exportar_arestas(dados, saida / f"arestas_{nome}.csv")
        exportar_csv(
            graus,
            ("estado", "grau_entrada", "grau_saida"),
            saida / f"graus_{nome}.csv",
        )

        solucoes_mapa = {}
        for algoritmo in algoritmos:
            solucao = _resolver_mapa(dados, algoritmo, resultados_buscas)
            solucoes.append(solucao)
            solucoes_mapa[algoritmo] = solucao
            reutilizar = (
                algoritmo == "BFS" and nome in ("m02", "m03", "m04")
                or algoritmo == "BELLMAN_FORD" and (
                    nome == "m06" or nome == "m05" and not fonte_consumivel
                )
            )
            if not reutilizar:
                resultados_buscas.pop(algoritmo, None)

        if nome in ("m02", "m03", "m04"):
            comparacoes.extend(_comparar_modelagens(dados, resultados_buscas))
        if nome == "m03":
            percurso = solucoes_mapa["DIJKSTRA"]
            if percurso["status"] == "RECUSA":
                percurso = solucoes_mapa["BELLMAN_FORD"]
            exportar_json(percurso, saida / "percurso_m03.json")
        if nome == "m05" and not fonte_consumivel:
            exportar_json(_comparar_bonus(dados, resultados_buscas), saida / "comparacao_bonus_m05.json")
        if nome == "m06":
            resultado = _resultado_busca(dados, "BELLMAN_FORD", resultados_buscas)
            exportar_json(
                {
                    "mapa": nome,
                    "fonte_consumivel": fonte_consumivel,
                    "status": solucoes_mapa["BELLMAN_FORD"]["status"],
                    "tem_ciclo_negativo": resultado["tem_ciclo_negativo"],
                    "ciclo_negativo": resultado["ciclo_negativo"],
                    "custo_ciclo": resultado["custo_ciclo"],
                },
                saida / "ciclo_negativo_m06.json",
            )
            del resultado
        resultados_buscas.clear()
        if nome in ("m04", "m07"):
            armadilhas = encontrar_armadilhas(dados)
            exportar_csv(
                ({"estado": rotulo} for rotulo in armadilhas),
                ("estado",),
                saida / f"armadilhas_{nome}.csv",
            )
            exportar_json(armadilhas, saida / f"armadilhas_{nome}.json")

    exportar_json(metricas, saida / "metricas_global.json")
    exportar_json(camadas, saida / "camadas.json")
    exportar_csv(
        solucoes,
        ("mapa", "algoritmo", "passos", "custo", "status", "caminho"),
        saida / "solucoes.csv",
    )
    exportar_csv(
        classificacoes,
        ("mapa", "arvore", "retorno", "avanco", "cruzamento"),
        saida / "dfs_classificacao.csv",
    )
    exportar_csv(
        comparacoes,
        ("mapa", "abordagem", "passos", "caminho_valido", "observacao"),
        saida / "comparacao_modelagem.csv",
    )
