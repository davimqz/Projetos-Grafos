"""Geração das visualizações da Parte 1 com os componentes do projeto."""

# [IA] Codex – integração das visualizações com mapas e algoritmos existentes.
from pathlib import Path

from src.graphs.algorithms import bfs, dfs, dijkstra, bellman_ford
from src.graphs.estados import Estado, construir_grafo_estados, rotular_estado
from src.graphs.io import encontrar_inicio, ler_mapa
from src.viz import (desenhar_arvore_bfs, desenhar_camadas, desenhar_heatmap,
                     desenhar_percurso, gerar_html_interativo, reconstruir_percurso)


def preparar_mapa(arquivo, algoritmos=("BFS",), *, fonte_consumivel=False):
    grade = ler_mapa(arquivo)
    grafo, estados = construir_grafo_estados(grade, fonte_consumivel=fonte_consumivel)
    linha, coluna = encontrar_inicio(grade)
    origem = rotular_estado(Estado(linha, coluna, frozenset(), frozenset()))
    funcoes = {"BFS": bfs, "DFS": dfs, "DIJKSTRA": dijkstra, "BELLMAN_FORD": bellman_ford}
    percursos, status, resultados = {}, {}, {}
    for nome in algoritmos:
        try:
            resultado = funcoes[nome](grafo, origem)
        except ValueError as erro:
            if nome != "DIJKSTRA" or "peso negativo" not in str(erro):
                raise
            percursos[nome], status[nome] = [], str(erro)
            continue
        resultados[nome] = resultado
        if resultado.get("tem_ciclo_negativo"):
            percursos[nome], status[nome] = [], "Ciclo negativo detectado; caminho mínimo não definido."
            continue
        try:
            percursos[nome] = reconstruir_percurso(resultado, origem, "ALVO")[:-1]
            status[nome] = "Percurso encontrado."
        except ValueError:
            percursos[nome], status[nome] = [], "Saída não alcançável."
    # [IA] Codex – prepara os dados de apresentação a partir dos arcos existentes.
    custos = {}
    for nome, caminho in percursos.items():
        if not caminho:
            continue
        acumulados = [0]
        for u, v in zip(caminho, caminho[1:]):
            peso = next(peso for destino, peso in grafo.vizinhos(u) if destino == v)
            acumulados.append(acumulados[-1] + peso)
        custos[nome] = acumulados
    return {"grade": grade, "algoritmos": percursos, "status": status,
            "mensagens": {nome: texto for nome, texto in status.items() if not percursos[nome]},
            "estados": list(estados), "custos": custos}, grafo, estados, resultados


def gerar_mapa(arquivo, saida, *, algoritmo="DIJKSTRA", interactive=False, fonte_consumivel=False,
               armadilhas_estados=None):
    saida = Path(saida)
    dados, grafo, estados, resultados = preparar_mapa(arquivo, (algoritmo,), fonte_consumivel=fonte_consumivel)
    if armadilhas_estados is not None:
        if not isinstance(armadilhas_estados, list) or any(
            not isinstance(rotulo, str) or rotulo not in estados for rotulo in armadilhas_estados
        ):
            raise ValueError("Armadilhas devem ser uma lista de estados existentes no grafo deste mapa")
        dados["armadilhas_estados"] = armadilhas_estados
    caminho = dados["algoritmos"][algoritmo]
    if caminho:
        nome_mapa = {"m03_tres_chaves": "m03", "m08_grande": "m08"}.get(Path(arquivo).stem, Path(arquivo).stem)
        desenhar_percurso(dados["grade"], caminho, saida / f"percurso_{nome_mapa}.png",
                          titulo=f"{Path(arquivo).stem} — {algoritmo}")
    if interactive:
        gerar_html_interativo({Path(arquivo).stem: dados}, saida / f"labirinto_{Path(arquivo).stem}.html")
    return dados["status"][algoritmo]


def gerar_figuras(arquivos, saida):
    """Gera as figuras P5a e inclui todos os mapas informados no HTML."""
    saida = Path(saida)
    mapas = {}
    for nome, arquivo in arquivos.items():
        dados, grafo, _, resultados = preparar_mapa(
            arquivo, ("BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD")
        )
        mapas[nome] = dados
        if nome in ("m03", "m08"):
            caminho = dados["algoritmos"]["DIJKSTRA"]
            if not caminho:
                raise ValueError(f"{nome}: {dados['status']['DIJKSTRA']}")
            desenhar_percurso(dados["grade"], caminho, saida / f"percurso_{nome}.png",
                              titulo=f"{nome} — Dijkstra (menor custo)")
        if nome == "m02":
            desenhar_camadas(grafo, saida / "camadas_m02.png")
            desenhar_arvore_bfs(resultados["BFS"], saida / "arvore_bfs_m02.png")
        if nome == "m08":
            desenhar_heatmap(dados["grade"], grafo, saida / "heatmap_m08.png")
    gerar_html_interativo(mapas, saida / "labirinto_interativo.html")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gerar figuras P5a com mapas reais")
    parser.add_argument("--mapas", default="data/mapas", help="diretório dos mapas")
    parser.add_argument("--mapas-grupo", default="data/mapas_grupo", help="diretório dos mapas do grupo")
    parser.add_argument("--out", default="out/parte1", help="diretório de saída")
    args = parser.parse_args()
    # [IA] Codex - inclui os mapas próprios sem manter uma lista fixa de arquivos.
    nomes_figuras = {"m02_uma_chave": "m02", "m03_tres_chaves": "m03", "m08_grande": "m08"}
    arquivos = {}
    for pasta in (args.mapas, args.mapas_grupo):
        for arquivo in sorted(Path(pasta).glob("*.txt")):
            nome = nomes_figuras.get(arquivo.stem, arquivo.stem)
            if nome in arquivos:
                parser.error(f"Há mapas com o mesmo identificador: {nome}")
            arquivos[nome] = arquivo
    gerar_figuras(arquivos, args.out)
