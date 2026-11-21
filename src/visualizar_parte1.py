"""Geração das visualizações da Parte 1 com os componentes do projeto."""

# [IA] Codex – integração das visualizações com mapas e algoritmos existentes.
# [IA] Codex - apresentação dos resultados compartilhados pela orquestração.
from pathlib import Path

from src.parte1.analises import classificar_arcos, encontrar_armadilhas
from src.parte1.buscas import _resolver_mapa
from src.parte1.carga import carregar_mapa
from src.parte1.modelos import ExecucaoMapa
from src.viz import (desenhar_arvore_bfs, desenhar_camadas, desenhar_heatmap,
                     desenhar_percurso, gerar_html_interativo, reconstruir_percurso)


def preparar_mapa(arquivo, algoritmos=("BFS",), *, fonte_consumivel=False):
    """Entrada independente; a CLI usa preparar_apresentacao com seus resultados."""
    dados = carregar_mapa(arquivo, fonte_consumivel=fonte_consumivel)
    resultados = {}
    solucoes = {nome: _resolver_mapa(dados, nome, resultados) for nome in algoritmos if nome != "DFS"}
    classificacao = classificar_arcos(dados, resultados) if "DFS" in algoritmos else {}
    execucao = ExecucaoMapa(dados, solucoes, classificacao, resultados, encontrar_armadilhas(dados))
    return preparar_apresentacao(execucao, algoritmos), dados.grafo_estados, dados.estados, resultados


def preparar_apresentacao(execucao, algoritmos):
    """Formata caminhos existentes para figuras/HTML, sem executar buscas."""
    dados = execucao.dados
    grafo = dados.grafo_estados
    solucoes = dict(execucao.solucoes)
    if "DFS" in algoritmos:
        try:
            caminho = reconstruir_percurso(execucao.buscas["DFS"], dados.origem, "ALVO")
        except ValueError:
            caminho = []
        solucoes["DFS"] = {"caminho": caminho, "status": "OK" if caminho else "SEM_SOLUCAO"}
    mensagens_status = {
        "OK": "Percurso encontrado.",
        "RECUSA": "Dijkstra recusa grafo com peso negativo.",
        "SEM_SOLUCAO": "Saída não alcançável.",
        "CICLO_NEGATIVO": "Ciclo negativo detectado; caminho mínimo não definido.",
    }
    percursos = {nome: solucoes[nome]["caminho"][:-1] for nome in algoritmos}
    status = {nome: mensagens_status[solucoes[nome]["status"]] for nome in algoritmos}
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
    return {"grade": dados.grade, "algoritmos": percursos, "status": status,
            "mensagens": {nome: texto for nome, texto in status.items() if not percursos[nome]},
            "estados": list(dados.estados), "custos": custos,
            "armadilhas_estados": execucao.armadilhas}


def exportar_figuras(execucao, apresentacao, saida, gravar):
    """Desenha os resultados recebidos e registra cada arquivo concluído."""
    dados = execucao.dados
    saida = Path(saida)
    preferidos = ("DIJKSTRA", "BELLMAN_FORD", "BFS", "DFS")
    algoritmo = next((nome for nome in preferidos if apresentacao["algoritmos"].get(nome)), None)
    if algoritmo:
        gravar(desenhar_percurso, dados.grade, apresentacao["algoritmos"][algoritmo],
               saida / f"percurso_{dados.nome}.png", titulo=f"{dados.nome} — {algoritmo}")
    if dados.nome == "m02":
        gravar(desenhar_camadas, dados.grafo_estados, saida / "camadas_m02.png")
        gravar(desenhar_arvore_bfs, execucao.buscas["BFS"], saida / "arvore_bfs_m02.png")
    if dados.nome == "m08":
        gravar(desenhar_heatmap, dados.grade, dados.grafo_estados, saida / "heatmap_m08.png")


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
