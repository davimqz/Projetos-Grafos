"""Medições das funções do grupo no grafo de estados completo, a partir de S."""

# [IA] Codex - medição e exportação da Parte 1 usando os algoritmos existentes.
import hashlib
import platform
import sys
import timeit
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

from src.graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
from .caminhos import caminho_saida
from .carga import carregar_mapa
from .exportacao import exportar_csv, exportar_json
from .saidas import RegistroSaidas


ALGORITMOS = {"BFS": bfs, "DFS": dfs, "DIJKSTRA": dijkstra, "BELLMAN_FORD": bellman_ford}
COLUNAS = (
    "mapa", "arquivo", "sha256", "fonte_consumivel", "algoritmo", "origem",
    "nos", "arestas", "status", "alvo_alcancavel", "mensagem", "repeticoes",
    "tempo_medio_ms", "latencia_min_ms", "latencia_max_ms", "memoria_pico_bytes",
)


def executar_busca(funcao, dados):
    """Só a recusa de pesos negativos do Dijkstra é um resultado esperado."""
    try:
        return funcao(dados.grafo_estados, dados.origem)
    except ValueError as erro:
        if funcao is not ALGORITMOS["DIJKSTRA"] or "negativo" not in str(erro):
            raise
        return {"status": "RECUSA", "mensagem": str(erro)}


def medir_caso(dados, algoritmo, repeticoes):
    """Aquecimento, tempos sem tracemalloc e pico numa execução independente."""
    funcao = ALGORITMOS[algoritmo]
    resultado = executar_busca(funcao, dados)
    status = resultado.get("status", "OK")
    if status == "RECUSA":
        alcanca = None
    elif "ordem" in resultado:
        alcanca = "ALVO" in resultado["ordem"]
    else:
        alcanca = resultado["distancia"]["ALVO"] != float("inf")
    mensagem = resultado.get("mensagem", "")
    del resultado
    chamar = lambda: executar_busca(funcao, dados)
    tempos = [segundos * 1000 for segundos in timeit.repeat(chamar, number=1, repeat=repeticoes)]
    tracemalloc.start()
    try:
        chamar()
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return {
        "algoritmo": algoritmo, "origem": dados.origem,
        "status": status, "alvo_alcancavel": alcanca, "mensagem": mensagem,
        "repeticoes": repeticoes, "tempos_ms": tempos,
        "tempo_medio_ms": sum(tempos) / len(tempos),
        "latencia_min_ms": min(tempos), "latencia_max_ms": max(tempos),
        "memoria_pico_bytes": pico,
    }


def executar_benchmark(mapas, saida, *, fonte_consumivel=False, algoritmo=None, repeticoes=5):
    """Grava só benchmark.csv/json; não executa análises, desenhos ou normalização.

    V e E incluem ALVO. Status é o retorno global da busca, não o custo até ALVO.
    O pico inclui alocações Python da chamada e seu retorno; exclui o grafo pronto.
    O timeit desativa temporariamente o coletor de lixo nas medições de tempo.
    """
    if isinstance(repeticoes, bool) or not isinstance(repeticoes, int) or repeticoes < 1:
        raise ValueError("O número de repetições deve ser um inteiro positivo.")
    if algoritmo is not None and algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo desconhecido: {algoritmo}")
    if tracemalloc.is_tracing():
        raise ValueError("Desative o tracemalloc externo antes de medir tempo e memória.")
    mapas = [Path(mapa) for mapa in mapas]
    if not mapas:
        raise ValueError("Nenhum mapa foi encontrado para executar.")
    if len({mapa.stem for mapa in mapas}) != len(mapas):
        raise ValueError("Os mapas devem ter identificadores distintos na mesma execução.")
    linhas = []
    for mapa in mapas:
        dados = carregar_mapa(mapa, fonte_consumivel=fonte_consumivel)
        contexto = {
            "mapa": dados.nome, "arquivo": str(mapa),
            "sha256": hashlib.sha256(mapa.read_bytes()).hexdigest(),
            "fonte_consumivel": fonte_consumivel,
            "nos": dados.grafo_estados.ordem(), "arestas": dados.grafo_estados.tamanho(),
        }
        for nome in (algoritmo,) if algoritmo else ALGORITMOS:
            linhas.append({**contexto, **medir_caso(dados, nome, repeticoes)})
    saida = Path(saida) / "fonte_consumivel" if fonte_consumivel else Path(saida)
    relatorio = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
        "ambiente": {"python": sys.version, "plataforma": platform.platform(),
                     "processador": platform.processor()},
        "metodo": {"aquecimentos": 1, "repeticoes_tempo": repeticoes,
                   "execucoes_memoria": 1, "unidade_tempo": "ms", "unidade_memoria": "bytes",
                   "escopo": "Funções originais no G_est completo a partir de S; V/E incluem ALVO.",
                   "status": "Retorno global da busca; não normaliza ciclos para o caminho até ALVO.",
                   "tempo": "timeit, GC desativado, sem tracemalloc; sem IO, construção ou exportação.",
                   "memoria": "Pico de alocações Python da chamada e retorno; exclui o grafo pronto."},
        "resultados": linhas,
    }
    registro = RegistroSaidas()
    registro.gravar(exportar_csv, linhas, COLUNAS, caminho_saida(saida, "benchmark.csv"))
    registro.gravar(exportar_json, relatorio, caminho_saida(saida, "benchmark.json"))
    return relatorio, registro


def executar_interface(mapas, saida, **opcoes):
    """Mantém os códigos da CLI: 0 concluído, 1 falha de escrita, 2 entrada inválida."""
    try:
        relatorio, registro = executar_benchmark(mapas, saida, **opcoes)
    except (OSError, ValueError) as erro:
        print(f"Entrada ou processamento: {erro}", file=sys.stderr)
        return 2
    print("Resumo do benchmark (grafo completo; inclui tempo de recusa):")
    for linha in relatorio["resultados"]:
        print(f"  {linha['mapa']} / {linha['algoritmo']}: {linha['status']}; "
              f"média={linha['tempo_medio_ms']:.6f} ms; pico={linha['memoria_pico_bytes']} bytes")
    for arquivo in registro.arquivos:
        print(f"Arquivo gerado: {arquivo}")
    for erro in registro.erros:
        print(f"Falha de exportação: {erro}", file=sys.stderr)
    return 1 if registro.erros else 0
