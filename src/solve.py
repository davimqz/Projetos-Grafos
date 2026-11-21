"""Orquestração das entregas da Parte 1 e interface pública existente.

As responsabilidades estão distribuídas em src.parte1. Os imports abaixo
mantêm disponíveis os tipos e as funções antes definidos neste módulo.
As visualizações pertencem a src.viz e src.visualizar_parte1.
"""

# [IA] Codex - separação por responsabilidade, preservando a lógica existente.
# [IA] Codex - integração das exportações e compartilhamento de resultados com a CLI.
from __future__ import annotations

from collections.abc import Callable, Iterable
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
from src.parte1.modelos import ExecucaoMapa

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
    ao_processar: Callable[[ExecucaoMapa], None] | None = None,
    gravar: Callable | None = None,
) -> None:
    """Orquestra as entregas dos mapas informados, incluindo mapas do grupo.

    Prepara os mapas e reúne métricas globais, camadas, graus, rankings,
    multiplicidades, becos, soluções e classificação DFS. Exporta os arcos
    de todos os mapas, inclusive m08 quando estiver entre as entradas.

    Saídas: metricas_global.json, camadas.json, graus_<mapa>.csv,
    arestas_<mapa>.csv, solucoes.csv e dfs_classificacao.csv.
    Para os mapas correspondentes, inclui comparacao_modelagem.csv,
    percurso_m03.json (menor custo, estado a estado), ciclo_negativo_m06.json
    (sequência de estados e custo). Para cada mapa, exporta armadilhas_<mapa>.csv
    e armadilhas_<mapa>.json, incluindo os mapas do grupo.
    Reúne ainda o experimento padrão em comparacao_bonus_m05.json.
    Os mapas fornecidos usam identificadores m01 a m08; mapas próprios
    mantêm o nome do arquivo sem extensão. Identificadores repetidos são erro.

    Os resultados da variante fonte_consumivel devem ir para uma pasta
    de saída diferente da execução padrão, escolhida pelo chamador.
    ao_processar recebe os resultados para apresentação, antes de liberar as buscas.
    gravar permite registrar exportações concluídas e tratar falhas de escrita.
    Sem esses parâmetros, preserva o retorno None e a propagação de erros.
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
    if gravar is None:
        gravar = lambda exportador, *args: exportador(*args)
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
        classificacao = classificar_arcos(dados, resultados_buscas)
        classificacoes.append(classificacao)
        metricas[nome] = {
            **calcular_metricas_globais(dados),
            **_analisar_graus(dados, graus),
            "tem_ciclo_dfs": classificacao["tem_ciclo"],
            "fonte_consumivel": fonte_consumivel,
        }
        camadas[nome] = calcular_camadas(dados)
        gravar(exportar_arestas, dados, saida / f"arestas_{nome}.csv")
        gravar(exportar_csv,
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
            if not reutilizar and ao_processar is None:
                resultados_buscas.pop(algoritmo, None)

        if nome in ("m02", "m03", "m04"):
            comparacoes.extend(_comparar_modelagens(dados, resultados_buscas))
        if nome == "m03" or ao_processar is not None:
            percurso = solucoes_mapa["DIJKSTRA"]
            if percurso["status"] == "RECUSA":
                percurso = solucoes_mapa["BELLMAN_FORD"]
            gravar(exportar_json, percurso, saida / f"percurso_{nome}.json")
        if nome == "m05" and not fonte_consumivel:
            gravar(exportar_json, _comparar_bonus(dados, resultados_buscas), saida / "comparacao_bonus_m05.json")
        if nome == "m06" or (
            ao_processar is not None and resultados_buscas["BELLMAN_FORD"]["tem_ciclo_negativo"]
        ):
            resultado = _resultado_busca(dados, "BELLMAN_FORD", resultados_buscas)
            gravar(exportar_json,
                {
                    "mapa": nome,
                    "fonte_consumivel": fonte_consumivel,
                    "status": solucoes_mapa["BELLMAN_FORD"]["status"],
                    "tem_ciclo_negativo": resultado["tem_ciclo_negativo"],
                    "ciclo_negativo": resultado["ciclo_negativo"],
                    "custo_ciclo": resultado["custo_ciclo"],
                },
                saida / f"ciclo_negativo_{nome}.json",
            )
            del resultado
        # [IA] Codex - exporta o resultado existente também para mapas próprios.
        armadilhas = encontrar_armadilhas(dados)
        gravar(exportar_csv,
            ({"estado": rotulo} for rotulo in armadilhas),
            ("estado",),
            saida / f"armadilhas_{nome}.csv",
        )
        gravar(exportar_json, armadilhas, saida / f"armadilhas_{nome}.json")
        if ao_processar is not None:
            ao_processar(ExecucaoMapa(dados, solucoes_mapa, classificacao, dict(resultados_buscas), armadilhas))
        resultados_buscas.clear()

    gravar(exportar_json, metricas, saida / "metricas_global.json")
    gravar(exportar_json, camadas, saida / "camadas.json")
    gravar(exportar_csv,
        solucoes,
        ("mapa", "algoritmo", "passos", "custo", "status", "caminho"),
        saida / "solucoes.csv",
    )
    gravar(exportar_csv,
        classificacoes,
        ("mapa", "arvore", "retorno", "avanco", "cruzamento"),
        saida / "dfs_classificacao.csv",
    )
    gravar(exportar_csv,
        comparacoes,
        ("mapa", "abordagem", "passos", "caminho_valido", "observacao"),
        saida / "comparacao_modelagem.csv",
    )
