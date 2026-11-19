"""Orquestração das entregas da Parte 1 e interface pública existente.

As responsabilidades estão distribuídas em src.parte1. Os imports abaixo
mantêm disponíveis os tipos e as funções antes definidos neste módulo.
As visualizações pertencem a src.viz e src.visualizar_parte1.
"""

# [IA] Codex - separação por responsabilidade, preservando a lógica existente.
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from src.parte1.analises import (
    _analisar_graus,
    analisar_graus,
    calcular_camadas,
    calcular_graus,
    calcular_metricas_globais,
    classificar_arcos,
    encontrar_armadilhas,
)
from src.parte1.buscas import (
    _comparar_bonus,
    _comparar_modelagens,
    _resolver_mapa,
    _resultado_busca,
    comparar_bonus,
    comparar_modelagens,
    resolver_mapa,
)
from src.parte1.carga import carregar_mapa
from src.parte1.exportacao import exportar_arestas, exportar_csv, exportar_json
from src.parte1.modelos import AlgoritmoCaminho, DadosMapa, GrauEstado, Solucao, StatusSolucao

__all__ = [
    "AlgoritmoCaminho", "DadosMapa", "GrauEstado", "Solucao", "StatusSolucao",
    "analisar_graus", "calcular_camadas", "calcular_graus", "calcular_metricas_globais",
    "carregar_mapa", "classificar_arcos", "comparar_bonus", "comparar_modelagens",
    "encontrar_armadilhas", "executar_parte1", "exportar_arestas", "exportar_csv",
    "exportar_json", "resolver_mapa",
]


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
