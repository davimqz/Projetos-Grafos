"""Coordena as saídas da Parte 1 e imprime o resumo após as exportações."""

# [IA] Codex - integração da CLI com os resultados e exportadores existentes.
import json
import sys
from pathlib import Path

from matplotlib import pyplot as plt

from src.solve import executar_parte1
from src.visualizar_parte1 import exportar_figuras, preparar_apresentacao
from src.viz import gerar_html_interativo
from .saidas import RegistroSaidas


ALGORITMOS = ("BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD")


def executar_interface(
    mapas, saida, *, algoritmo=None, interactive=False, fonte_consumivel=False,
    mostrar_armadilhas=False, arquivo_armadilhas=None, lote=False,
):
    """Exporta todas as análises; --alg seleciona o resumo e o percurso visual."""
    plt.switch_backend("Agg")
    mapas = [Path(mapa) for mapa in mapas]
    saida = Path(saida)
    if fonte_consumivel:
        saida /= "fonte_consumivel"
    algoritmos = (algoritmo,) if algoritmo else ALGORITMOS
    registro = RegistroSaidas()
    apresentacoes, resumos = {}, []
    codigo = 0

    def apresentar(execucao):
        dados = preparar_apresentacao(execucao, algoritmos)
        if fornecidas is not None:
            if any(estado not in execucao.dados.estados for estado in fornecidas):
                raise ValueError("Armadilhas devem ser estados existentes no grafo deste mapa")
            dados["armadilhas_estados"] = fornecidas
        nome = mapas[len(resumos)].stem
        apresentacoes[nome] = dados
        bf = execucao.buscas.get("BELLMAN_FORD", {})
        resumos.append({
            "nome": nome,
            "solucoes": execucao.solucoes,
            "dfs": execucao.classificacao,
            "armadilhas": dados["armadilhas_estados"],
            "ciclo": bf.get("ciclo_negativo", []),
            "custo_ciclo": bf.get("custo_ciclo"),
        })
        exportar_figuras(execucao, dados, saida, registro.gravar)

    try:
        if not mapas:
            raise ValueError("Nenhum mapa foi encontrado para executar.")
        fornecidas = None
        if arquivo_armadilhas:
            if len(mapas) != 1:
                raise ValueError("--arquivo-armadilhas só pode ser usado com um mapa.")
            fornecidas = json.loads(Path(arquivo_armadilhas).read_text(encoding="utf-8"))
            if not isinstance(fornecidas, list) or any(not isinstance(s, str) for s in fornecidas):
                raise ValueError("O arquivo de armadilhas deve conter uma lista de rótulos.")
        executar_parte1(
            mapas, saida, fonte_consumivel=fonte_consumivel,
            ao_processar=apresentar, gravar=registro.gravar,
        )
    except (ValueError, OSError) as erro:
        registro.erros.append(f"Entrada ou processamento: {erro}")
        codigo = 2

    if interactive and apresentacoes:
        nome_html = "labirinto_interativo.html" if lote else f"labirinto_{mapas[0].stem}.html"
        registro.gravar(gerar_html_interativo, apresentacoes, saida / nome_html)
    imprimir_resumo(resumos, apresentacoes, algoritmos, registro, mostrar_armadilhas)
    return codigo or (1 if registro.erros else 0)


def imprimir_resumo(resumos, apresentacoes, algoritmos, registro, mostrar_armadilhas):
    """Usa somente os dados já preparados e os arquivos efetivamente concluídos."""
    print("Resumo da execução:")
    for resumo in resumos:
        dados = apresentacoes[resumo["nome"]]
        print(f"\nMapa: {resumo['nome']} | Estados alcançáveis: {len(dados['estados'])}")
        for algoritmo in algoritmos:
            if algoritmo == "DFS":
                percurso = dados["algoritmos"][algoritmo]
                caminho = percurso + ["ALVO"] if percurso else []
                passos = len(percurso) - 1 if percurso else None
                custo = dados["custos"][algoritmo][-1] if percurso else None
                status = "OK" if percurso else "SEM_SOLUCAO"
            else:
                solucao = resumo["solucoes"][algoritmo]
                caminho, passos, custo, status = (solucao[k] for k in ("caminho", "passos", "custo", "status"))
            print(f"  {algoritmo}: status={status}; passos={passos}; custo={custo}")
            print(f"    {dados['status'][algoritmo]}")
            print("    Caminho:", " -> ".join(caminho) if caminho else "indisponível")
            if algoritmo == "DFS":
                print("    Classificação DFS:", resumo["dfs"])
            if algoritmo == "BELLMAN_FORD" and resumo["ciclo"]:
                print(f"    Ciclo negativo no grafo (custo {resumo['custo_ciclo']}):", " -> ".join(resumo["ciclo"]))
        print(f"  Estados-armadilha: {len(resumo['armadilhas'])}")
        if mostrar_armadilhas:
            for estado in resumo["armadilhas"]:
                print(f"    {estado}")
    print(f"\nArquivos gerados ({len(registro.arquivos)}):")
    for arquivo in registro.arquivos:
        print(f"  {arquivo}")
    if registro.erros:
        print("Falhas na execução:", file=sys.stderr)
        for erro in registro.erros:
            print(f"  {erro}", file=sys.stderr)
