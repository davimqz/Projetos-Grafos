"""Visualizações e UX.

Parte 1 (P5a): percursos m03 e m08, grafo de estados do m02 em camadas,
árvore BFS do m02, heatmap de multiplicidade do m08 e labirinto interativo.
Parte 2 (P5b/AVD): comparação dos algoritmos e visualizações em out/parte2/.

Este módulo NÃO constrói G_pos/G_est, calcula soluções, armadilhas ou
interpreta resultados. Ele apenas representa informações recebidas.
"""

from __future__ import annotations

import base64
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import ListedColormap


ESTADO = re.compile(r"^\((\d+)\s*,\s*(\d+)\)\|([a-d]*|-)\|\{([0-9,]*)\}$")


def ler_rotulo(rotulo: str) -> tuple[int, int, str, tuple[int, ...]] | None:
    """Extrai posição, chaves e bônus de um rótulo de G_est; ignora ALVO.
    """
    if rotulo == "ALVO":
        return None
    achado = ESTADO.fullmatch(str(rotulo))
    if not achado:
        raise ValueError(f"Rótulo de estado não reconhecido: {rotulo!r}")
    linha, coluna, chaves, bonus = achado.groups()
    indices = tuple(int(numero) for numero in bonus.split(",") if numero)
    return int(linha), int(coluna), "" if chaves == "-" else chaves, indices


def _posicoes(percurso: list[str]) -> list[tuple[int, int, str, tuple[int, ...]]]:
    saida = []
    for rotulo in percurso:
        estado = ler_rotulo(rotulo)
        if estado is not None:
            saida.append(estado)
    return saida


def _verificar_grade(grade: list[str]) -> tuple[int, int]:
    if not grade or not grade[0] or any(len(linha) != len(grade[0]) for linha in grade):
        raise ValueError("A grade deve ser retangular e não vazia")
    return len(grade), len(grade[0])


def _salvar(fig: Any, arquivo: str | Path) -> Path:
    caminho = Path(arquivo)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return caminho


def _base_mapa(ax: Any, grade: list[str]) -> None:
    n_linhas, n_colunas = _verificar_grade(grade)
    cores = ListedColormap(["#F8F9FB", "#233143"])
    matriz = [[1 if casa == "#" else 0 for casa in linha] for linha in grade]
    ax.imshow(matriz, cmap=cores, vmin=0, vmax=1, interpolation="nearest")
    ax.set_xticks([i - 0.5 for i in range(n_colunas + 1)], minor=True)
    ax.set_yticks([i - 0.5 for i in range(n_linhas + 1)], minor=True)
    ax.grid(which="minor", color="#D4DAE0", linewidth=0.6)
    ax.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)
    for eixo in ax.spines.values():
        eixo.set_visible(False)
    for l, linha in enumerate(grade):
        for c, casa in enumerate(linha):
            if casa not in ("#", ".", ",", "~"):
                ax.text(c, l, casa, ha="center", va="center", fontsize=8,
                        color="#25384C", weight="bold", zorder=5)
    ax.set_xlim(-0.5, n_colunas - 0.5)
    ax.set_ylim(n_linhas - 0.5, -0.5)
    ax.set_aspect("equal")


def reconstruir_percurso(resultado: dict, origem: str, destino: str) -> list[str]:
    """Obtém um caminho do dicionário pai retornado por BFS ou Dijkstra.

    Não escolhe destino nem caminho — usa os parâmetros enviados pelo grupo.
    """
    pais = resultado.get("pai", {})
    if origem not in pais or destino not in pais:
        raise ValueError("Origem ou destino não está no resultado do algoritmo")
    caminho = []
    atual = destino
    vistos = set()
    while atual is not None and atual not in vistos:
        caminho.append(atual)
        if atual == origem:
            return list(reversed(caminho))
        vistos.add(atual)
        atual = pais.get(atual)
    raise ValueError(f"Não há percurso de {origem} até {destino}")


def desenhar_percurso(grade: list[str], percurso: list[str], arquivo: str | Path,
                      titulo: str = "Percurso pelo labirinto") -> Path:
    """Desenha o percurso; a cor muda quando o conjunto de chaves muda."""
    _verificar_grade(grade)
    estados = _posicoes(percurso)
    if not estados:
        raise ValueError("O percurso não contém estados de posição")
    for l, c, _, _ in estados:
        if not (0 <= l < len(grade) and 0 <= c < len(grade[0])):
            raise ValueError(f"Posição {(l,c)} está fora da grade")
    conjuntos = list(dict.fromkeys(chaves for _, _, chaves, _ in estados))
    cores = {chaves: plt.cm.viridis(i / max(len(conjuntos) - 1, 1))
             for i, chaves in enumerate(conjuntos)}
    fig, ax = plt.subplots(figsize=(max(7, len(grade[0]) * .5), max(5, len(grade) * .5)))
    _base_mapa(ax, grade)
    # [IA] Codex – traços encaixados preservam as cores nos corredores repetidos.
    for camada, conjunto in enumerate(conjuntos):
        for primeiro, segundo in zip(estados, estados[1:]):
            l1, c1, chaves, _ = primeiro
            l2, c2, _, _ = segundo
            if chaves == conjunto:
                ax.plot([c1, c2], [l1, l2], color=cores[chaves],
                        linewidth=3 + 2.4 * (len(conjuntos) - camada - 1),
                        zorder=7 + camada, solid_capstyle="round")
    ax.scatter(estados[0][1], estados[0][0], s=110, marker="o",
               facecolors="white", edgecolors="#125E6A", linewidths=2, zorder=20)
    ax.scatter(estados[-1][1], estados[-1][0], s=110, marker="s",
               facecolors="white", edgecolors="#9B4D5F", linewidths=2, zorder=20)
    from matplotlib.lines import Line2D
    itens = [Line2D([0], [0], color=cores[chaves], lw=3,
                    label=f"Chaves: {chaves or 'nenhuma'}") for chaves in conjuntos]
    itens.extend([Line2D([0], [0], marker="o", color="none", markerfacecolor="white",
                         markeredgecolor="#125E6A", markersize=8, label="Início"),
                  Line2D([0], [0], marker="s", color="none", markerfacecolor="white",
                         markeredgecolor="#9B4D5F", markersize=8, label="Fim do percurso")])
    ax.legend(handles=itens, loc="upper center", bbox_to_anchor=(.5, -.02),
              ncol=min(4, len(itens)), frameon=False, fontsize=9)
    ax.set_title(titulo, fontsize=13, color="#233143", pad=14)
    ax.set_xlabel("Coluna")
    ax.set_ylabel("Linha")
    return _salvar(fig, arquivo)


def _layout_camadas(nos: list[str], grupos: dict) -> dict[str, tuple[float, float]]:
    layout = {}
    for numero, (_, nomes) in enumerate(grupos.items()):
        total = len(nomes)
        for i, nome in enumerate(nomes):
            layout[nome] = (i - (total - 1) / 2, -numero * 2.5)
    return layout


def _desenhar_rede(grupos: dict[str, list[str]], arcos: list[tuple[str, str]],
                    arquivo: str | Path, titulo: str, destacar_transicao: bool = False,
                    mostrar_nomes: bool = True) -> Path:
    nos = [no for grupo in grupos.values() for no in grupo]
    # [IA] Codex – acabamento visual dos diagramas de rede.
    layout = _layout_camadas(nos, grupos)
    grupos_no = {no: camada for camada, membros in grupos.items() for no in membros}
    largura = max(6, min(22, max((len(g) for g in grupos.values()), default=1) * .7 + 3))
    altura = max(5, min(20, len(grupos) * 1.5 + 1))
    fig, ax = plt.subplots(figsize=(largura, altura))
    fig.patch.set_facecolor("#f6f7f2")
    ax.set_facecolor("#f6f7f2")
    for u, v in arcos:
        if u not in layout or v not in layout:
            continue
        x1, y1 = layout[u]
        x2, y2 = layout[v]
        mudou = grupos_no[u] != grupos_no[v]
        cor = "#c27d43" if destacar_transicao and mudou else "#9aafa5"
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=11, lw=1.5 if mudou else .85,
                                     color=cor, alpha=.8, zorder=1,
                                     shrinkA=8, shrinkB=11,
                                     connectionstyle="arc3,rad=.13"))
    for nome, (x, y) in layout.items():
        ax.scatter(x, y, s=170 if mostrar_nomes else 45, color="#2b7866", edgecolors="white", linewidths=1, zorder=3)
        if mostrar_nomes:
            try:
                dados = ler_rotulo(nome)
                # [IA] Codex – distingue estados da mesma posição por seus bônus.
                rotulo = f"({dados[0]},{dados[1]})|{dados[2] or '-'}" if dados else nome
                if dados and dados[3]:
                    rotulo += " {" + ",".join(map(str, dados[3])) + "}"
            except ValueError:
                rotulo = str(nome)[:14]
            ax.annotate(rotulo, (x, y), xytext=(0, -13), textcoords="offset points",
                        ha="center", fontsize=6.5, color="#233143")
    for camada, membros in grupos.items():
        y = layout[membros[0]][1] if membros else 0
        x_min = min((p[0] for p in layout.values()), default=0)
        ax.text(x_min - 1, y, str(camada), ha="right", va="center",
                fontsize=9, color="#426659", weight="bold")
    if layout:
        xs = [p[0] for p in layout.values()]
        ys = [p[1] for p in layout.values()]
        ax.set_xlim(min(xs) - 2, max(xs) + 1.5)
        ax.set_ylim(min(ys) - 1, max(ys) + 1)
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_title(titulo, fontsize=13, color="#233143", pad=16)
    if destacar_transicao:
        from matplotlib.lines import Line2D
        ax.legend(handles=[Line2D([0], [0], color="#9aafa5", label="Mesma camada"),
                           Line2D([0], [0], color="#c27d43", label="Mudança de camada")],
                  loc="lower center", bbox_to_anchor=(.5, -.08), ncol=2, frameon=False)
    return _salvar(fig, arquivo)


def desenhar_camadas(grafo: Any, arquivo: str | Path,
                      max_nos: int = 250, titulo: str = "Grafo de estados por conjunto de chaves") -> Path:
    """Desenha G_est agrupado por conjunto de chaves; destaca troca de camada.

    Erra explicitamente se o grafo for grande demais para um diagrama legível.
    Não remove ou amostra nós sem autorização.
    """
    nos = [no for no in grafo.nos() if no != "ALVO"]
    if len(nos) > max_nos:
        raise ValueError(f"Grafo com {len(nos)} nós: aumente max_nos ou faça um recorte explícito")
    grupos = defaultdict(list)
    for no in nos:
        dados = ler_rotulo(no)
        grupos[dados[2] or "sem chaves"].append(no)
    ordenado = dict(sorted(grupos.items(), key=lambda x: (0 if x[0] == "sem chaves" else len(x[0]), x[0])))
    arcos = [(u, v) for u, v, _ in grafo.arestas() if u != "ALVO" and v != "ALVO"]
    return _desenhar_rede(ordenado, arcos, arquivo,
                         titulo, True,
                         mostrar_nomes=len(nos) <= 100)


def desenhar_arvore_bfs(resultado_bfs: dict, arquivo: str | Path,
                        max_nos: int = 250, titulo: str = "Árvore BFS por nível") -> Path:
    """Desenha a árvore BFS a partir de camadas e arestas já calculadas."""
    camadas = resultado_bfs.get("camadas")
    arcos = resultado_bfs.get("arvore")
    if not isinstance(camadas, dict) or not isinstance(arcos, list):
        raise ValueError("Resultado BFS precisa incluir 'camadas' e 'arvore'")
    grupos = {f"nível {nivel}": list(nos) for nivel, nos in sorted(camadas.items())}
    quantidade = sum(len(nos) for nos in grupos.values())
    if quantidade > max_nos:
        raise ValueError(f"Árvore com {quantidade} nós: aumente max_nos ou use um recorte explícito")
    return _desenhar_rede(grupos, arcos, arquivo,
                         titulo, mostrar_nomes=quantidade <= 100)


def desenhar_heatmap(grade: list[str], grafo: Any, arquivo: str | Path,
                     titulo: str = "Multiplicidade de estados por posição") -> Path:
    """Exibe quantidade de estados distintos de G_est por posição física."""
    n_linhas, n_colunas = _verificar_grade(grade)
    quantidades = [[0] * n_colunas for _ in range(n_linhas)]
    for no in grafo.nos():
        dados = ler_rotulo(no)
        if dados is None:
            continue
        l, c, _, _ = dados
        if not (0 <= l < n_linhas and 0 <= c < n_colunas):
            raise ValueError(f"Posição {(l,c)} está fora da grade")
        quantidades[l][c] += 1
    valores = [[float("nan") if grade[l][c] == "#" else quantidades[l][c]
                for c in range(n_colunas)] for l in range(n_linhas)]
    fig, ax = plt.subplots(figsize=(max(7, n_colunas * .5), max(5, n_linhas * .5)))
    imagem = ax.imshow(valores, cmap="Blues", interpolation="nearest", vmin=0)
    for l in range(n_linhas):
        for c in range(n_colunas):
            if grade[l][c] != "#":
                valor = quantidades[l][c]
                cor = "white" if imagem.norm(valor) > .55 else "#223448"
                ax.text(c, l, str(valor), ha="center", va="center",
                        fontsize=8, color=cor)
    ax.set_xticks(range(n_colunas)); ax.set_yticks(range(n_linhas))
    ax.set_xlabel("Coluna"); ax.set_ylabel("Linha")
    ax.set_title(titulo, fontsize=13, pad=14)
    fig.colorbar(imagem, ax=ax, fraction=.045, pad=.02, label="Estados distintos")
    return _salvar(fig, arquivo)


def gerar_html_interativo(mapas: dict[str, dict], arquivo: str | Path) -> Path:
    """Cria visualizador HTML sem bibliotecas externas.

    Formato de entrada:
    {
      "m03": {
        "grade": ["#####", "#S.G#", "#####"],
        "algoritmos": {"BFS": ["(1,1)|-|{}", "(1,2)|-|{}", ...]},
        "armadilhas": ["(linha,coluna)|chaves|{bonus}", ...]  # opcional
      },
      ...
    }

    Campos opcionais lidos pelo HTML (calculados pelo grupo):
      "custos": {"BFS": [0, 1, ...]}            custo acumulado por estado (sem ALVO)
      "mensagens": {"Dijkstra": "RECUSA: ..."}  aviso de status do algoritmo
      "estados": ["(1,1)|-|{}", ...]            estados de G_est, para a troca de camadas
      "armadilhas_estados": ["(2,3)|a|{}", ...] estados-armadilha, realçados por camada

    Os percursos e armadilhas devem ter sido calculados externamente.
    """
    if not mapas:
        raise ValueError("Forneça pelo menos um mapa")
    for nome, dados in mapas.items():
        _verificar_grade(dados["grade"])
        if "armadilhas" in dados:
            if not isinstance(dados["armadilhas"], list):
                raise ValueError(f"Armadilhas inválidas em {nome}")
            for rotulo in dados["armadilhas"]:
                if isinstance(rotulo, (list, tuple)) and len(rotulo) == 2:
                    continue
                estado = ler_rotulo(rotulo)
                if estado is None or not (0 <= estado[0] < len(dados["grade"]) and 0 <= estado[1] < len(dados["grade"][0])):
                    raise ValueError(f"Estado-armadilha inválido em {nome}: {rotulo!r}")
        # [IA] Codex – correção da validação de mapas sem algoritmos.
        if not isinstance(dados.get("algoritmos"), dict) or not dados["algoritmos"]:
            raise ValueError(f"Mapa {nome} sem dicionário 'algoritmos'")
        for algoritmo, percurso in dados["algoritmos"].items():
            estados = _posicoes(percurso)
            # [IA] Claude Code – percurso vazio é aceito quando há mensagem de status (RECUSA, SEM_SOLUCAO...).
            if not estados and not (dados.get("mensagens", {}).get(algoritmo) or dados.get("status", {}).get(algoritmo)):
                raise ValueError(f"Percurso vazio em {nome}/{algoritmo} (sem mensagem de status)")
            custos = dados.get("custos", {}).get(algoritmo)
            if custos is not None and (len(custos) != len(estados) or any(not isinstance(c, (int, float)) for c in custos)):
                raise ValueError(f"Custos incompatíveis com o percurso em {nome}/{algoritmo}")
            for l, c, _, _ in estados:
                if not (0 <= l < len(dados["grade"]) and 0 <= c < len(dados["grade"][0])):
                    raise ValueError(f"Posição fora da grade em {nome}/{algoritmo}")
    # Evita que nomes importados dos dados possam encerrar a tag <script>.
    dados_json = json.dumps(mapas, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    # [IA] Codex – revisão visual e acessibilidade do visualizador.
    # [IA] Claude Code – custo acumulado, troca de camadas, armadilhas por estado, mensagens e teclado.
    html = r'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Grafos · Teoria e visualização</title>
<!-- [IA] Codex – ícone incorporado para funcionar também ao abrir o arquivo localmente. -->
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Crect width='48' height='48' rx='11' fill='%232456d8'/%3E%3Cpath d='M12 30 22 13l14 8-4 15-20-6 10-17 10 23M12 30l24-9' fill='none' stroke='%23fff' stroke-width='2' stroke-linejoin='round' opacity='.8'/%3E%3Cg fill='%23fff'%3E%3Ccircle cx='12' cy='30' r='3'/%3E%3Ccircle cx='22' cy='13' r='3'/%3E%3Ccircle cx='36' cy='21' r='3'/%3E%3Ccircle cx='32' cy='36' r='3'/%3E%3C/g%3E%3C/svg%3E">
<style>
 :root{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#203b3b;background:#f4f3ed;--ink:#203b3b;--green:#126c5b;--line:#dce3d9}
*{box-sizing:border-box}body{max-width:1180px;margin:0 auto;padding:40px 28px 60px}header{margin-bottom:28px;border-bottom:1px solid #cbd7cb;padding-bottom:24px}header:before{content:"PROJETO DE GRAFOS  /  EXPLORADOR";display:block;color:#69877a;font-size:11px;font-weight:800;letter-spacing:.16em;margin-bottom:12px}h1{font-family:Georgia,serif;font-size:clamp(30px,4vw,46px);font-weight:normal;letter-spacing:-.035em;margin:0 0 8px}p{color:#62766e;margin:0;line-height:1.5}.panel{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px;margin:14px 0;box-shadow:0 6px 24px #24473508}
.controls{display:flex;flex-wrap:wrap;gap:18px;align-items:end}.group{display:flex;flex-direction:column;gap:7px;min-width:145px}label{font-size:12px;color:#587066;font-weight:700}select,input,button{font:inherit}select{padding:10px 34px 10px 12px;border:1px solid #cad8cc;border-radius:7px;background:#fff;color:var(--ink)}button{padding:10px 17px;border:1px solid #cad8cc;border-radius:7px;background:#fff;color:var(--ink);cursor:pointer;font-weight:650}button:hover:not(:disabled){border-color:var(--green)}button.primary{background:var(--green);color:white;border-color:var(--green)}button:disabled{opacity:.4;cursor:default}:focus-visible{outline:3px solid #e6ad52;outline-offset:3px}input{accent-color:var(--green)}.layout{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:24px;align-items:center}.map-wrap{overflow:auto;padding:20px;background:#edf2eb;border-radius:9px;min-width:0}
#grade{display:grid;gap:2px;width:max-content;margin:auto;--cell:34px}.cell{width:var(--cell);height:var(--cell);display:flex;align-items:center;justify-content:center;border-radius:3px;font-size:12px;font-weight:750;position:relative}.wall{background:#294940}.floor{background:#fff}.visited{background:#b9ded1}.outside{background:#e4e7e1;color:#9aa69f}.trap{outline:2px solid #c76b4b;outline-offset:-3px}.current{background:#d89c42!important;color:#172f2b!important;border-radius:50%;outline:3px solid #fff;outline-offset:-4px;z-index:1}.start{color:#087960}.goal{color:#a64d37}
.readout{font-size:13px}.readout:before{content:"ESTADO ATUAL";display:block;color:#82988a;font-size:10px;font-weight:800;letter-spacing:.14em;margin-bottom:8px}.readout div{display:flex;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px solid #edf1ec}.readout strong{color:#60786b;font-weight:500}.readout span{font-weight:700;text-align:right;font-variant-numeric:tabular-nums}#custo{color:var(--green);font-size:15px}.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center}#steps{flex:1;min-width:130px}#indice{font-size:12px;color:#60786b;min-width:20px}.legend{display:flex;flex-wrap:wrap;gap:16px;color:#60786b;font-size:12px;margin:12px 0 0}.legend span:before{content:"";display:inline-block;width:10px;height:10px;margin-right:6px;border-radius:2px;background:#b9ded1}.legend span:nth-child(2):before{background:#d89c42;border-radius:50%}.legend span:nth-child(3):before{background:transparent;border:2px solid #c76b4b}.legend span:nth-child(4):before{background:#e4e7e1}
#aviso{display:none;margin-top:12px;padding:12px 14px;border-radius:8px;background:#fbefe6;color:#7c3d22;font-size:13px;font-weight:600}.dica{font-size:12px;color:#82988a;margin-top:10px}
@media(max-width:740px){body{padding:24px 16px 40px}.layout{grid-template-columns:1fr}#grade{--cell:28px}.panel{padding:16px}.map-wrap{padding:14px}.group{flex:1 1 130px}}
/* [IA] Codex – apresentação inspirada em uma planta de navegação. */
:root{--ink:#142e43;--muted:#526b7a;--accent:#145e88;--line:#cbd9e0;color:var(--ink);background:#eaf0f2;font-family:"Trebuchet MS",system-ui,sans-serif}
body{max-width:1380px;padding:36px 32px 56px}header{display:grid;grid-template-columns:1fr auto;gap:12px;align-items:end;border-bottom:2px solid var(--ink);margin-bottom:18px;padding-bottom:18px}header:before{content:"TEORIA DOS GRAFOS  /  PARTE 1";grid-column:1/-1;color:var(--accent);font:700 11px/1.2 Consolas,monospace;letter-spacing:.15em;margin:0}h1{font-family:"Trebuchet MS",sans-serif;font-weight:800;letter-spacing:-.04em;font-size:clamp(29px,3.5vw,44px);margin:0}header p{max-width:365px;color:var(--muted);font-size:13px;text-align:right}.panel{border-color:var(--line);border-radius:6px;box-shadow:0 4px 20px #24475a0b;margin:12px 0;padding:20px}.controls{gap:16px;align-items:end}.group{min-width:155px;flex:1 1 155px}.controls label,.group label{color:#39576a;font-size:12px}select{width:100%;border-color:#b9cbd4;color:var(--ink);border-radius:4px}button{border-color:#b9cbd4;border-radius:4px;color:var(--ink)}button:hover:not(:disabled){border-color:var(--accent)}button.primary{background:var(--accent);border-color:var(--accent)}input{accent-color:var(--accent)}:focus-visible{outline:3px solid #db8d1a;outline-offset:3px}
.layout{grid-template-columns:minmax(0,1fr) 250px;gap:22px;align-items:start}.map-title{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin:0 0 10px}.map-title h2{font-size:15px;margin:0}.map-title small{color:var(--muted);font-size:12px}.map-wrap{background-color:#dce8ed;background-image:linear-gradient(#b8ccd83d 1px,transparent 1px),linear-gradient(90deg,#b8ccd83d 1px,transparent 1px);background-size:20px 20px;border:1px solid #ccdde5;border-radius:4px;padding:24px}.cell{border-radius:2px;font-family:Consolas,monospace}.wall{background:#244052}.floor{background:#fbfdfe}.visited{background:#9cdbd5}.trap{outline:2px solid #bd5434}.current{background:#f2b746!important;color:#172d3c!important}.start{color:#087060}.goal{color:#a64339}.cell.key{box-shadow:inset 0 0 0 2px #3e8a81;color:#205e55}.cell.door{box-shadow:inset 0 0 0 2px #8864a8;color:#60407f}.readout{background:#f3f7f8;border:1px solid #dae7eb;border-radius:4px;padding:16px;font-size:13px}.readout:before{color:var(--accent);font:700 11px Consolas,monospace;letter-spacing:.12em}.readout div{border-color:#dce8ec}.readout strong{color:#536d7b}.readout span{overflow-wrap:anywhere}.legend{color:#4a6371;gap:16px}.legend span:before{background:#9cdbd5}.legend span:nth-child(2):before{background:#f2b746}.legend span:nth-child(3):before{border-color:#bd5434}.legend span:nth-child(4):before{display:inline-block;background:#e4e7e1}.legend span:nth-child(5):before{display:none}.toolbar{gap:10px}.toolbar .progress{flex:1;display:flex;align-items:center;gap:12px;min-width:180px}.toolbar #steps{width:100%}#indice{font-family:Consolas,monospace;color:var(--muted)}
.cell.outside{background:#d5dcdd;color:#73838a}.legend span:nth-child(4):before{display:inline-block;background:#d5dcdd}.legend span:nth-child(5):before{display:none}
@media(max-width:740px){body{padding:22px 14px 40px}header{grid-template-columns:1fr}header p{text-align:left}.layout{grid-template-columns:minmax(0,1fr)}.layout>div{min-width:0}.panel{padding:16px}.map-wrap{padding:14px}#grade{--cell:28px}.toolbar .progress{flex-basis:100%}.group{min-width:0;flex:1 1 130px}.map-title{flex-wrap:wrap}}
/* [IA] Codex – JetBrains Mono incorporada para uso sem rede.
__FONT_LICENSE__
*/
@font-face{font-family:"JetBrains Mono";src:url(data:font/woff2;base64,__FONT_DATA__) format("woff2");font-style:normal;font-weight:400;font-display:swap}
:root,body,h1,header:before,.cell,.readout:before,#indice{font-family:"JetBrains Mono",Consolas,"Liberation Mono",monospace}
/* [IA] Codex – visual compatível com o front React, sem alterar os dados. */
:root{--ink:#eaf0ff;--muted:#c1cde0;--accent:#719bff;--line:#385171;color:var(--ink);background:#081225;color-scheme:dark}
body{background-color:#081225;background-image:radial-gradient(circle at 8% 25%,#719bff55 0 2px,transparent 2.5px),radial-gradient(circle at 27% 75%,#719bff44 0 2px,transparent 2.5px),radial-gradient(circle at 50% 22%,#719bff55 0 2px,transparent 2.5px),linear-gradient(155deg,transparent 25%,#28436c88 25.1%,transparent 25.25%),linear-gradient(23deg,transparent 47%,#28436c88 47.1%,transparent 47.25%);background-size:850px 550px;background-attachment:fixed}
header{border-color:#385171}header:before{color:#a7c2ff}header p,p{color:#c1cde0}h1{color:#fff}.panel{background:#101e36f2;border:1px solid #385171;border-radius:14px;box-shadow:0 18px 50px #02081466}
.controls label,.group label{color:#c1cde0}.group select{background:#162744;color:#f1f5ff;border:1px solid #6a82a6;border-radius:7px;min-height:44px}select option{background:#fff;color:#17243a}button{background:#192c49;color:#eaf0ff;border:1px solid #3a5275;border-radius:8px}button:hover:not(:disabled){background:#233a5e;border-color:#89aaff}button.primary{background:#376be7;color:#fff;border-color:#5c8fff}button.primary:hover:not(:disabled){background:#4a7af0}:focus-visible{outline:3px solid #a5c0ff;outline-offset:3px}input{accent-color:#8db0ff}
.map-title small{color:#c1cde0}.map-wrap{background:#536d8b;background-image:none;border:1px solid #839bb9;border-radius:8px;scrollbar-color:#7897c5 #12223a;scrollbar-width:thin}#grade{gap:1px;padding:2px;background:#899eb9;outline:2px solid #bccbe0}.cell{border-radius:0;color:#18243a}.wall{background:#26354a}.floor{background:#f7f9ff}.cell.start{background:#a8dab9;color:#142138}.cell.goal{background:#f2b5a1;color:#142138}.cell.key{background:#f2d46e;color:#142138;box-shadow:none}.cell.door{background:#c6b6dd;color:#142138;box-shadow:none}.cell.mud{background:#dbc49a}.cell.water{background:#a5c9e9}.cell.belt{background:#c9d5df}.cell.bonus{background:#e8b5ce}.cell.fonte{background:#9ed7d1}.cell.outside{background:#d1d9e4;color:#53657d}.cell.visited{background:#9bbcff;color:#142138}.cell.trap{outline:3px solid #d64b3e;outline-offset:-3px}.cell.current{background:#172333!important;color:#fff!important;border-radius:50%;outline:3px solid #fff;outline-offset:-4px}
.readout{background:#162744;border:1px solid #405a7e;border-radius:10px}.readout:before{color:#a7c2ff}.readout div{border-color:#40516a}.readout strong{color:#c1cde0}.readout span{color:#fff}#custo{color:#a7c2ff}#indice,.legend{color:#d6e1f3}.legend span:before{background:#9bbcff}.legend span:nth-child(2):before{background:#172333;border:1px solid #fff}.legend span:nth-child(3):before{border-color:#d64b3e}.legend span:nth-child(4):before{display:none}#aviso{background:#402a30;color:#ffd5c9}
/* [IA] Codex – percurso e marcador sincronizados com a reprodução. */
.map-stage{position:relative;width:max-content;margin:auto}#percursoSvg{position:absolute;inset:0;pointer-events:none;overflow:visible}.cell span{position:relative;z-index:1;text-shadow:0 0 3px #fff,0 0 3px #fff}#grade.pequena .cell span{display:none}.legend span:first-child:before{width:18px;height:4px;vertical-align:middle;background:#2463eb;border-radius:3px}.cell.visited{background:inherit}.cell.wall{background:#26354a}@keyframes revelar-trajeto{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}.trecho-animado{stroke-dasharray:1;animation:revelar-trajeto linear both}@media(prefers-reduced-motion:reduce){.trecho-animado{animation:none;stroke-dasharray:none}#marcador{transition:none!important}}
/* [IA] Codex – estrutura e controles alinhados ao front, preservando camadas e armadilhas. */
body{max-width:1380px;padding:24px 32px 56px}header{display:flex;align-items:center;gap:13px;margin:0 0 26px;padding:0 0 20px;border-bottom:1px solid #385171}header:before{display:none}.marca{width:46px;height:46px;flex:none;background:#2456d8;border-radius:11px;box-shadow:0 0 0 1px #719bff55,0 8px 24px #02081777}.marca-titulo{font:700 20px/1.2 "JetBrains Mono",monospace;color:#fff}.marca-subtitulo{font-size:12px;color:#b2c3dc;margin-top:3px}.principal{padding:28px}.intro{border-bottom:1px solid #385171;padding-bottom:22px;margin-bottom:24px}.intro small{display:block;color:#a7c2ff;font-size:11px;font-weight:700;letter-spacing:.1em;margin-bottom:8px}.intro h1{font-size:clamp(25px,3vw,34px);line-height:1.2;letter-spacing:-.035em}.intro p{margin-top:8px;font-size:13px}.controls{gap:14px 16px;margin:0 0 24px}.group{min-width:150px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:32px;margin:0;padding:0;border:0;border-radius:0;background:transparent;box-shadow:none}.mapa-area{min-width:0;padding:20px;background:#0a172bea;border:1px solid #385171;border-radius:12px}.map-title{margin-bottom:12px}.sidebar{min-width:0;border-left:1px solid #30415f;padding-left:26px}.sidebar h2{font-size:15px;margin:0 0 16px}.toolbar{display:flex;gap:6px;margin:0 0 18px;padding:0;border:0;background:none;box-shadow:none}.toolbar button{flex:1;min-width:0;padding:10px 7px}.toolbar .progress{display:block;flex:1 0 100%;min-width:0;margin-top:8px}.toolbar .progress label{display:block;margin-bottom:8px;color:#c1cde0;font-size:12px}.toolbar .progress input{width:100%;margin:0}.velocidade{margin:0 0 20px}.velocidade input{width:100%;margin:4px 0 0}.readout{background:transparent;border:0;border-radius:0;padding:0}.readout:before{margin-bottom:0}.readout div{padding:9px 0}.legend{padding:15px;background:#162744;border:1px solid #405a7e;border-radius:10px;line-height:1.5}#aviso{margin:16px 0 0}
@media(max-width:820px){body{padding:20px 16px 40px}.principal{padding:18px}.layout{grid-template-columns:minmax(0,1fr);gap:22px}.sidebar{border-left:0;border-top:1px solid #30415f;padding:22px 0 0}.mapa-area{padding:12px}.controls .group{flex:1 1 140px}}
/* [IA] Codex – impede que os rótulos de reprodução ultrapassem os botões. */
.toolbar{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr) minmax(0,1fr);gap:6px}.toolbar button{width:100%;min-width:0;padding:10px 4px;font-size:12px;white-space:nowrap}.toolbar .progress{grid-column:1/-1;margin-top:8px}
.map-key{padding:20px;margin-top:12px;border:1px solid #405a7e;border-radius:10px;background:#162744;color:#f1f5ff}.map-key h3{margin:0 0 16px;font-size:14px}.map-key-grupos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.map-key h4{margin:0 0 10px;color:#b9cbe4;font-size:12px}.map-key ul{display:grid;gap:9px;list-style:none;margin:0;padding:0}.map-key li{display:flex;align-items:center;gap:10px;font-size:12px}.map-key i{display:inline-flex;align-items:center;justify-content:center;flex:0 0 26px;width:26px;height:26px;border:1px solid #e0e8f4;border-radius:4px;color:#142138;font:700 14px/1 "JetBrains Mono",monospace;font-style:normal}@media(max-width:700px){.map-key-grupos{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:390px){.map-key-grupos{grid-template-columns:1fr}}
input[type=range]{appearance:none;-webkit-appearance:none;display:block;width:100%;height:28px;margin:0;background:transparent;cursor:pointer}input[type=range]::-webkit-slider-runnable-track{height:6px;border-radius:999px;background:linear-gradient(to right,#8db0ff 0 var(--progresso,0%),#354b6a var(--progresso,0%) 100%)}input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:18px;height:18px;margin-top:-6px;border:3px solid #eaf0ff;border-radius:50%;background:#4e80f0;box-shadow:0 0 0 2px #4e80f055}input[type=range]::-moz-range-track{height:6px;border-radius:999px;background:#354b6a}input[type=range]::-moz-range-progress{height:6px;border-radius:999px;background:#8db0ff}input[type=range]::-moz-range-thumb{width:12px;height:12px;border:3px solid #eaf0ff;border-radius:50%;background:#4e80f0}input[type=range]:disabled{opacity:.45;cursor:not-allowed}
/* [IA] Codex – identidade visual clara do front React, mantida offline. */
:root{color-scheme:light;--ink:#080808;--muted:#595955;--accent:#080808;--line:#bdbcb5;background:#f2f1ec;color:var(--ink)}
body{background:#f2f1ec;color:var(--ink);font:400 15px/1.5 Arial,Helvetica,sans-serif;max-width:1380px}
header{border-color:#080808}.marca{background:#d4f500;border:1px solid #080808;border-radius:0;box-shadow:4px 4px 0 #080808}.marca path{stroke:#080808}.marca g{fill:#080808}.marca-titulo{font:400 27px/1 Impact,'Arial Narrow',sans-serif;color:#080808}.marca-subtitulo{color:#595955}
.panel{background:#fff;border:1px solid #080808;border-radius:0;box-shadow:none}.principal{padding:32px}.intro{border-color:#bdbcb5}.intro small{color:#080808;font:700 11px/1.2 'JetBrains Mono',monospace;letter-spacing:.1em}.intro small:before{content:'';display:inline-block;width:10px;height:10px;margin-right:8px;background:#d4f500;border:1px solid #080808}.intro h1{font:400 clamp(30px,3vw,38px)/1.05 Impact,'Arial Narrow',sans-serif;color:#080808;letter-spacing:0}.intro p,p{color:#595955;font-family:Arial,Helvetica,sans-serif;font-size:14px}
.controls{padding-bottom:24px;border-bottom:1px solid #bdbcb5}.controls label,.group label{color:#080808;font:700 11px/1.2 'JetBrains Mono',monospace;letter-spacing:.04em}.group select{min-height:46px;background:#fff;color:#080808;border:2px solid #080808;border-radius:0;font:600 15px Arial,Helvetica,sans-serif}.group select:hover{background:#e9f7a3}select option{background:#fff;color:#080808}input[type=checkbox]{accent-color:#080808;width:18px;height:18px;vertical-align:middle}
button{min-height:44px;background:#fff;color:#080808;border:2px solid #080808;border-radius:0;font:700 12px Arial,Helvetica,sans-serif}button:hover:not(:disabled){background:#d4f500;border-color:#080808;box-shadow:4px 4px 0 #080808}button.primary,button.primary:hover:not(:disabled){background:#080808;border-color:#080808;color:#fff}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #080808;outline-offset:3px}
.layout{gap:24px}.mapa-area{padding:0;background:transparent;border:0;border-radius:0}.map-title h2,.sidebar h2{font:400 22px/1.1 Impact,'Arial Narrow',sans-serif;color:#080808}.sidebar{border-color:#080808}.map-wrap{min-height:260px;display:flex;align-items:center;justify-content:safe center;background-color:#f2f1ec;background-image:linear-gradient(#d5d4ce 1px,transparent 1px),linear-gradient(90deg,#d5d4ce 1px,transparent 1px);background-size:24px 24px;border:1px solid #080808;border-radius:0;scrollbar-color:#777 #f2f1ec}.map-stage{flex:none}#grade{background:#bdbcb5;outline:2px solid #080808;box-shadow:6px 6px 0 #080808}.cell.wall{background:#171717}.cell.floor{background:#fff}.cell.start{background:#d4f500}.cell.goal{background:#ff7a59}.cell.key{background:#f2c94c}.cell.door{background:#c7b5e0}.cell.mud{background:#d9bf8c}.cell.water{background:#9cc7e8}.cell.belt{background:#cfcfc8}.cell.bonus{background:#f0a8c8}.cell.fonte{background:#8fd6cc}.cell.outside{background:#d5d4ce;color:#595955}.cell.trap{outline-color:#b3261e}
.legend{padding:12px 16px;color:#080808;background:#fff;border:1px solid #080808;border-radius:0}.legend span:nth-child(3):before{border-color:#b3261e}.map-key{color:#080808;background:#fff;border:1px solid #080808;border-radius:0}.map-key h4{color:#595955}.map-key i{border:1px solid #080808;border-radius:0}.map-key li:first-child i{color:#080808}.map-key li i[style*='#26354a']{background:#171717!important}.map-key li i[style*='#a8dab9']{background:#d4f500!important}.map-key li i[style*='#f2b5a1']{background:#ff7a59!important}
.readout{background:#fff;color:#080808}.readout:before{color:#595955}.readout div{border-color:#bdbcb5}.readout strong{color:#595955}.readout span,#custo,#indice{color:#080808}.toolbar .progress label{color:#080808}#aviso{border:1px solid #b3261e;border-radius:0;background:#fff3ef;color:#8a261e}
input[type=range]::-webkit-slider-runnable-track{border-radius:0;background:linear-gradient(to right,#080808 0 var(--progresso,0%),#d5d4ce var(--progresso,0%) 100%)}input[type=range]::-webkit-slider-thumb{border:2px solid #080808;border-radius:0;background:#d4f500;box-shadow:none}input[type=range]::-moz-range-track{border-radius:0;background:#d5d4ce}input[type=range]::-moz-range-progress{border-radius:0;background:#080808}input[type=range]::-moz-range-thumb{border:2px solid #080808;border-radius:0;background:#d4f500}
@media(max-width:820px){.principal{padding:18px}.sidebar{border-color:#080808}.mapa-area{padding:0}.map-wrap{justify-content:flex-start}}
/* [IA] Codex – comparação offline com reprodução compartilhada. */
.comparacao{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:0 0 24px}.comparacao[hidden]{display:none}.comparacao article{min-width:0;border:1px solid #080808;padding:16px;background:#fff}.comparacao h3{font:400 22px/1.1 Impact,'Arial Narrow',sans-serif;margin:0 0 8px}.comparacao .resultado{min-height:22px;margin:0 0 10px;font-size:13px;color:#595955}.comparacao .resultado.erro{color:#b3261e}.comparacao .grade-comparacao{overflow:auto;min-height:160px;display:flex;align-items:center;justify-content:safe center;padding:12px;background:#f2f1ec;border:1px solid #080808}.comparacao svg{display:block;max-width:100%;height:auto;flex:none;outline:1px solid #080808}.comparacao .estado-comparacao{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));margin-top:12px;border-top:1px solid #080808;border-left:1px solid #080808}.comparacao .estado-comparacao div{padding:8px;border-right:1px solid #080808;border-bottom:1px solid #080808;overflow-wrap:anywhere;font-size:12px}.comparacao .estado-comparacao strong{display:block;font:700 10px 'JetBrains Mono',monospace;color:#595955}.comparacao .estado-comparacao span{display:block;margin-top:4px}.comparando .mapa-area,.comparando .readout{display:none}.comparando.layout{display:block}.comparando .sidebar{border:0;border-top:1px solid #080808;padding:20px 0 0}.comparando .toolbar{max-width:480px}.comparando .velocidade{max-width:480px}@media(max-width:700px){.comparacao{grid-template-columns:1fr}}
.principal:has(#comparar:checked){display:flex;flex-direction:column}.principal:has(#comparar:checked) .intro{order:0}.principal:has(#comparar:checked) .controls{order:1}.principal:has(#comparar:checked) .layout{order:2}.principal:has(#comparar:checked) .comparacao{order:3}.principal:has(#comparar:checked) #aviso{order:4}.comparando .sidebar{padding:0;border:0}.comparacao-info{grid-column:1/-1;color:#595955;font-size:13px}
</style></head><body>
<header><svg class="marca" viewBox="0 0 48 48" aria-hidden="true"><path d="M12 30 22 13l14 8-4 15-20-6 10-17 10 23M12 30l24-9" fill="none" stroke="white" stroke-width="2" stroke-linejoin="round"/><g fill="white"><circle cx="12" cy="30" r="3"/><circle cx="22" cy="13" r="3"/><circle cx="36" cy="21" r="3"/><circle cx="32" cy="36" r="3"/></g></svg><div><div class="marca-titulo">Grafos</div><div class="marca-subtitulo">Teoria e visualização</div></div></header>
<main class="panel principal"><div class="intro"><small>PARTE 1</small><h1>Labirinto interativo</h1><p>Escolha o mapa e o algoritmo e acompanhe o percurso passo a passo. A cor do caminho muda a cada chave coletada.</p></div>
<div class="controls"><div class="group"><label for="mapa">Mapa</label><select id="mapa"></select></div>
<div class="group"><label for="algoritmo">Algoritmo</label><select id="algoritmo"></select></div>
<div class="group"><label for="camadaSel">Camada exibida</label><select id="camadaSel"></select></div>
<label><input type="checkbox" id="mostrarArmadilhas" checked> Mostrar armadilhas</label><label><input type="checkbox" id="comparar"> Comparar os quatro algoritmos</label></div>
<section id="comparacao" class="comparacao" aria-label="Comparação dos quatro algoritmos" hidden></section>
<div class="layout"><div class="mapa-area"><div class="map-title"><h2>Mapa e percurso</h2><button id="ampliar" type="button" aria-pressed="false">Ampliar mapa</button></div><div id="mapaWrap" class="map-wrap" tabindex="0" aria-label="Mapa do labirinto; use a rolagem para navegar"><div class="map-stage"><div id="grade" aria-label="Mapa do labirinto"></div><svg id="percursoSvg" aria-hidden="true"><g id="tracos"></g><circle id="marcador" fill="#172333" stroke="#fff" stroke-width="2.5"/></svg></div></div><div class="legend"><span>Percurso (a cor muda com as chaves)</span><span>Posição atual</span><span>Armadilha</span></div><section class="map-key" aria-label="Legenda do mapa"><h3>Como ler o mapa</h3><div class="map-key-grupos"><div><h4>Mapa</h4><ul><li><i style="background:#26354a"></i>Parede</li><li><i style="background:#f7f9ff">.</i>Chão · custo 1</li><li><i style="background:#a8dab9">S</i>Início</li><li><i style="background:#f2b5a1">G</i>Saída</li></ul></div><div><h4>Terreno</h4><ul><li><i style="background:#dbc49a">,</i>Lama · custo 3</li><li><i style="background:#a5c9e9">~</i>Água · custo 5</li><li><i style="background:#c9d5df">&gt;</i>Esteira</li></ul></div><div><h4>Elementos</h4><ul><li><i style="background:#f2d46e">a</i>Chave</li><li><i style="background:#c6b6dd">A</i>Porta</li><li><i style="background:#e8b5ce">+</i>Bônus · −4</li><li><i style="background:#9ed7d1">*</i>Fonte · −2</li></ul></div></div></section></div><aside class="sidebar"><h2>Acompanhar percurso</h2><div class="toolbar" aria-label="Controles do percurso"><button id="anterior">Anterior</button><button class="primary" id="reproduzir">Animar</button><button id="proximo">Próximo</button><div class="progress"><label for="steps">Posição no percurso: <span id="indice"></span></label><input id="steps" aria-label="Selecionar passo do percurso" type="range" min="0" max="0" value="0"></div></div><div class="velocidade group"><label for="velocidade">Velocidade: <span id="valorVelocidade">5</span> passos/s</label><input id="velocidade" type="range" min="1" max="20" value="5"></div><div class="readout" aria-label="Estado atual">
<div><strong>Passo:</strong> <span id="passo"></span></div><div><strong>Posição:</strong> <span id="posicao"></span></div>
<div><strong>Chaves:</strong> <span id="chaves"></span></div><div><strong>Bônus consumidos:</strong> <span id="bonus"></span></div>
<div><strong>Custo acumulado:</strong> <span id="custo"></span></div><div><strong>Camada do estado:</strong> <span id="camada"></span></div><div><strong>Camada exibida:</strong> <span id="exibida"></span></div>
<div><strong>Estados no percurso:</strong> <span id="total"></span></div><div><strong>Resultado:</strong> <span id="status"></span></div><div><strong>Armadilhas:</strong> <span id="infoArmadilhas"></span></div></div></aside></div>
<div id="aviso" role="status"></div>
</main>
<script>
const MAPAS = __DATA__;
const $ = id => document.getElementById(id);
// [IA] Codex – os rótulos seguem o seletor do React; os identificadores continuam iguais.
const NOMES_MAPAS={m01_terreno:'M01 · Terreno',m02_uma_chave:'M02 · Uma chave',m02:'M02 · Uma chave',m03_tres_chaves:'M03 · Três chaves',m03:'M03 · Três chaves',m04_esteiras:'M04 · Esteiras',m05_bonus:'M05 · Bônus',m06_fonte:'M06 · Fonte',m07_impossivel:'M07 · Impossível',m08_grande:'M08 · Grande',m08:'M08 · Grande',g01_tres_depositos:'G01 · Três depósitos',g02_poco_lateral:'G02 · Poço lateral'};
const NOMES_ALGORITMOS={BFS:'BFS',DFS:'DFS',DIJKSTRA:'Dijkstra',BELLMAN_FORD:'Bellman-Ford'};
let passoAtual=0, relogio=null, ultimoPasso=-1, ultimoMapa='', ultimaCamada='', ampliado=false;
const coresPercurso=['#2463eb','#d04a36','#a46300','#00816d','#8657ac','#bd4c7d','#537d19','#5b6776'];
const cachePercursos=new WeakMap(), cacheEstados=new WeakMap();
function parseEstado(texto){if(texto==='ALVO')return null;const m=/^\((\d+)\s*,\s*(\d+)\)\|([a-d]*|-)\|\{([0-9,]*)\}$/.exec(texto);if(!m)throw Error('Estado inválido: '+texto);return {l:+m[1],c:+m[2],chaves:m[3]==='-'?'':m[3],bonus:m[4]};}
function nomeCamada(ch){return ch===''?'sem chaves':'chaves '+ch;}
function dados(){return MAPAS[$('mapa').value];}
function percurso(){const lista=dados().algoritmos[$('algoritmo').value];if(!lista)return [];if(!cachePercursos.has(lista))cachePercursos.set(lista,lista.map(parseEstado).filter(x=>x!==null));return cachePercursos.get(lista);}
function custos(){return (dados().custos||{})[$('algoritmo').value]||null;}
function estadosMapa(){const m=dados();if(!cacheEstados.has(m)){const lista=(m.estados&&m.estados.length?m.estados:Object.values(m.algoritmos).flat());cacheEstados.set(m,lista.map(parseEstado).filter(x=>x!==null));}return cacheEstados.get(m);}
function desenharPercurso(p,atual,sel,exibida){const grade=$('grade'),svg=$('percursoSvg'),tracos=$('tracos'),marcador=$('marcador'),estilo=getComputedStyle(grade),s=parseFloat(estilo.getPropertyValue('--cell')),gap=parseFloat(estilo.columnGap)||0,pad=parseFloat(estilo.paddingLeft)||0, largura=grade.offsetWidth,altura=grade.offsetHeight;
svg.setAttribute('width',largura);svg.setAttribute('height',altura);svg.setAttribute('viewBox','0 0 '+largura+' '+altura);tracos.replaceChildren();
const camadas=Array.from(new Set(p.map(e=>e.chaves))),animar=relogio!==null&&passoAtual===ultimoPasso+1&&ultimoMapa===$('mapa').value&&ultimaCamada===sel,limite=animar?passoAtual-1:passoAtual;
const visivel=e=>sel==='__auto'||e.chaves===exibida, ponto=e=>[pad+e.c*(s+gap)+s/2,pad+e.l*(s+gap)+s/2];
function segmento(a,b,animado){if(!visivel(a)||!visivel(b))return;const linha=document.createElementNS('http://www.w3.org/2000/svg','line'),[x1,y1]=ponto(a),[x2,y2]=ponto(b);for(const [k,v] of Object.entries({x1,y1,x2,y2,stroke:coresPercurso[camadas.indexOf(b.chaves)%coresPercurso.length],'stroke-width':Math.max(1,s*.24),'stroke-linecap':'round'}))linha.setAttribute(k,v);if(animado){linha.setAttribute('pathLength','1');linha.setAttribute('class','trecho-animado');linha.style.animationDuration=(1000/Number($('velocidade').value))+'ms';}tracos.appendChild(linha);}
for(let i=1;i<=limite;i++)segmento(p[i-1],p[i],false);if(animar&&passoAtual>0)segmento(p[passoAtual-1],p[passoAtual],true);
if(atual&&visivel(atual)){const [x,y]=ponto(atual),duracao=1000/Number($('velocidade').value);marcador.style.transition=animar?'cx '+duracao+'ms linear, cy '+duracao+'ms linear':'none';marcador.setAttribute('cx',x);marcador.setAttribute('cy',y);marcador.setAttribute('r',s*.34);marcador.setAttribute('stroke-width',Math.min(2.5,Math.max(.8,s*.25)));marcador.style.display='';}else marcador.style.display='none';ultimoPasso=passoAtual;ultimoMapa=$('mapa').value;ultimaCamada=sel;}
function camadas(){const s=new Set(estadosMapa().map(e=>e.chaves));return Array.from(s).sort((a,b)=>a.length-b.length||a.localeCompare(b));}
function fimReproducao(){return $('comparar').checked?Math.max(-1,...Object.values(dados().algoritmos).map(p=>p.length-1)):percurso().length-1;}
function parar(){if(relogio!==null){clearInterval(relogio);relogio=null;} $('reproduzir').textContent=passoAtual>0&&passoAtual>=fimReproducao()?'Recomeçar':'Animar';}
function reiniciar(){parar();passoAtual=0;atualizar();}
function trocarMapa(){const m=dados();$('algoritmo').replaceChildren();Object.keys(m.algoritmos).forEach(nome=>{$('algoritmo').add(new Option(NOMES_ALGORITMOS[nome]||nome,nome));});
$('camadaSel').replaceChildren();$('camadaSel').add(new Option('Seguir o percurso','__auto'));camadas().forEach(ch=>$('camadaSel').add(new Option(nomeCamada(ch),ch)));reiniciar();}
// [IA] Codex – quatro percursos e estados sincronizados, usando dados já incluídos no HTML.
let paineisComparacao=[], mapaComparado='';
const ORDEM_ALGORITMOS=['BFS','DFS','DIJKSTRA','BELLMAN_FORD'];
function elementoSvg(tag,atributos){const el=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(atributos))el.setAttribute(k,String(v));return el;}
function montarComparacao(){const m=dados(), secao=$('comparacao');secao.replaceChildren();paineisComparacao=[];mapaComparado=$('mapa').value;const info=document.createElement('p');info.className='comparacao-info';info.textContent='Os quatro percursos seguem os controles acima. Contorno vermelho: estado-armadilha.';secao.appendChild(info);
for(const nome of ORDEM_ALGORITMOS){const artigo=document.createElement('article'),titulo=document.createElement('h3'),resultado=document.createElement('p'),caixa=document.createElement('div'),estado=document.createElement('div');
titulo.textContent=NOMES_ALGORITMOS[nome];resultado.className='resultado';caixa.className='grade-comparacao';estado.className='estado-comparacao';artigo.setAttribute('aria-label','Percurso '+NOMES_ALGORITMOS[nome]);
const svg=elementoSvg('svg',{viewBox:'0 0 '+m.grade[0].length*24+' '+m.grade.length*24,role:'img','aria-label':'Mapa do percurso '+NOMES_ALGORITMOS[nome]});const celulas=[];
m.grade.forEach((linha,l)=>Array.from(linha).forEach((ch,c)=>{let cor=ch==='#'?'#171717':ch==='S'?'#d4f500':ch==='G'?'#ff7a59':/[a-d]/.test(ch)?'#f2c94c':/[A-D]/.test(ch)?'#c7b5e0':ch===','?'#d9bf8c':ch==='~'?'#9cc7e8':'<>^v'.includes(ch)?'#cfcfc8':ch==='+'?'#f0a8c8':ch==='*'?'#8fd6cc':'#ffffff';const rect=elementoSvg('rect',{x:c*24,y:l*24,width:24,height:24,fill:cor,stroke:'#bdbcb5','stroke-width':.5});svg.appendChild(rect);celulas.push(rect);if(ch!=='.'&&ch!=='#'&&m.grade[0].length<=40){const t=elementoSvg('text',{x:c*24+12,y:l*24+16,'text-anchor':'middle','font-size':12,'font-weight':'bold',fill:'#080808'});t.textContent=ch;svg.appendChild(t);}}));
const linhas=elementoSvg('g',{}),marcador=elementoSvg('circle',{r:7,fill:'#172333',stroke:'#fff','stroke-width':2});svg.append(linhas,marcador);caixa.appendChild(svg);artigo.append(titulo,resultado,caixa,estado);secao.appendChild(artigo);paineisComparacao.push({nome,resultado,estado,linhas,marcador,celulas,armadilhasAnteriores:[]});}}
function atualizarComparacao(){const m=dados(),fim=fimReproducao();if(mapaComparado!==$('mapa').value||!paineisComparacao.length)montarComparacao();passoAtual=Math.min(Math.max(passoAtual,0),Math.max(0,fim));
for(const painel of paineisComparacao){const lista=m.algoritmos[painel.nome]||[],p=lista.map(parseEstado).filter(Boolean),pos=Math.min(passoAtual,p.length-1),atual=p[pos],mensagem=(m.mensagens||{})[painel.nome]||(m.status||{})[painel.nome]||(p.length?'Percurso encontrado.':'Resultado indisponível.');painel.resultado.textContent=mensagem;painel.resultado.classList.toggle('erro',!p.length);painel.linhas.replaceChildren();
const sel=$('camadaSel').value,camada=sel==='__auto'?(atual?atual.chaves:''):sel,visivel=e=>sel==='__auto'||e.chaves===camada,cores=Array.from(new Set(p.map(e=>e.chaves)));for(let i=1;i<=pos;i++){const a=p[i-1],b=p[i];if(!visivel(a)||!visivel(b))continue;painel.linhas.appendChild(elementoSvg('line',{x1:a.c*24+12,y1:a.l*24+12,x2:b.c*24+12,y2:b.l*24+12,stroke:coresPercurso[cores.indexOf(b.chaves)%coresPercurso.length],'stroke-width':5,'stroke-linecap':'round'}));}
painel.marcador.style.display=atual&&visivel(atual)?'':'none';if(atual){painel.marcador.setAttribute('cx',atual.c*24+12);painel.marcador.setAttribute('cy',atual.l*24+12);}
for(const i of painel.armadilhasAnteriores){painel.celulas[i].setAttribute('stroke','#bdbcb5');painel.celulas[i].setAttribute('stroke-width','.5');}painel.armadilhasAnteriores=[];if($('mostrarArmadilhas').checked){for(const rotulo of (m.armadilhas_estados||m.armadilhas||[])){const e=Array.isArray(rotulo)?{l:rotulo[0],c:rotulo[1],chaves:camada}:parseEstado(rotulo);if(e&&e.chaves===camada){const i=e.l*m.grade[0].length+e.c,rect=painel.celulas[i];if(rect){rect.setAttribute('stroke','#b3261e');rect.setAttribute('stroke-width','3');painel.armadilhasAnteriores.push(i);}}}}
painel.estado.replaceChildren();if(atual){const custo=(m.custos||{})[painel.nome];for(const [rotulo,valor] of [['Passo',pos+' / '+(p.length-1)],['Custo',custo?custo[pos]:'—'],['Posição','('+atual.l+','+atual.c+')'],['Chaves',atual.chaves||'nenhuma'],['Bônus usados',atual.bonus||'nenhum']]){const div=document.createElement('div'),forte=document.createElement('strong'),span=document.createElement('span');forte.textContent=rotulo;span.textContent=valor;div.append(forte,span);painel.estado.appendChild(div);}}}
$('steps').max=String(Math.max(0,fim));$('steps').value=String(passoAtual);$('steps').style.setProperty('--progresso',(fim>0?100*passoAtual/fim:0)+'%');$('indice').textContent=fim>=0?passoAtual+' de '+fim:'indisponível';$('steps').disabled=fim<0;$('anterior').disabled=passoAtual===0||fim<0;$('proximo').disabled=passoAtual>=fim;$('reproduzir').disabled=fim<1;$('aviso').style.display='none';if(fim>=0&&passoAtual===fim)parar();}
function atualizar(){const comparando=$('comparar').checked;$('comparacao').hidden=!comparando;document.querySelector('.layout').classList.toggle('comparando',comparando);$('algoritmo').disabled=comparando;if(comparando){atualizarComparacao();return;}const m=dados(), p=percurso(), aviso=$('aviso'), msg=(m.mensagens||{})[$('algoritmo').value]||(m.status||{})[$('algoritmo').value];
const grid=$('grade');if(grid.dataset.mapa!==$('mapa').value){grid.replaceChildren();grid.dataset.mapa=$('mapa').value;grid.style.gridTemplateColumns='repeat('+m.grade[0].length+',var(--cell))';m.grade.forEach((linha,l)=>Array.from(linha).forEach((ch,c)=>{const cell=document.createElement('div'),texto=document.createElement('span');texto.textContent=ch==='.'||ch==='#'?'':ch;cell.appendChild(texto);cell.title='('+l+','+c+') '+ch;grid.appendChild(cell);}));}
const colunas=m.grade[0].length,espaco=Math.max(1,$('mapaWrap').clientWidth-52),tamanho=ampliado?34:Math.max(3,Math.min(36,Math.floor((espaco-colunas-3)/colunas)));grid.style.setProperty('--cell',tamanho+'px');grid.classList.toggle('pequena',tamanho<18);
if(!p.length){parar();aviso.style.display='block';aviso.textContent=msg||'Sem percurso para este algoritmo.';}else if(msg && msg !== 'OK' && msg !== 'Percurso encontrado.'){aviso.style.display='block';aviso.textContent=msg;}else{aviso.style.display='none';aviso.textContent='';}
passoAtual=Math.min(Math.max(passoAtual,0),Math.max(p.length-1,0));const atual=p[passoAtual]||null;
const sel=$('camadaSel').value, exibida=sel==='__auto'?(atual?atual.chaves:''):sel;
const temEstados=!!(m.estados&&m.estados.length), naCamada=new Set(estadosMapa().filter(e=>e.chaves===exibida).map(e=>e.l+','+e.c));
const armadilhas=new Set((m.armadilhas||[]).filter(Array.isArray).map(s=>s[0]+','+s[1]));(m.armadilhas||[]).filter(s=>typeof s==='string').map(parseEstado).filter(e=>e&&e.chaves===exibida).forEach(e=>armadilhas.add(e.l+','+e.c));((m.armadilhas_estados||[]).map(parseEstado).filter(e=>e&&e.chaves===exibida)).forEach(e=>armadilhas.add(e.l+','+e.c));
let indiceCelula=0;m.grade.forEach((linha,l)=>Array.from(linha).forEach((ch,c)=>{const cell=grid.children[indiceCelula++],key=l+','+c,classes=['cell',ch==='#'?'wall':'floor'];
if(ch!=='#'&&temEstados&&!naCamada.has(key))classes.push('outside');if($('mostrarArmadilhas').checked&&armadilhas.has(key))classes.push('trap');
if(ch==='S')classes.push('start');if(ch==='G')classes.push('goal');if(/[a-d]/.test(ch))classes.push('key');if(/[A-D]/.test(ch))classes.push('door');if(ch===',')classes.push('mud');if(ch==='~')classes.push('water');if('<>^v'.includes(ch))classes.push('belt');if(ch==='+')classes.push('bonus');if(ch==='*')classes.push('fonte');const valor=classes.join(' ');if(cell.className!==valor)cell.className=valor;}));
desenharPercurso(p,atual,sel,exibida);
$('status').textContent=msg||(m.status||{})[$('algoritmo').value]||(p.length?'Percurso encontrado.':'Sem percurso.');$('infoArmadilhas').textContent=(Array.isArray(m.armadilhas_estados)||Array.isArray(m.armadilhas))?'Dispon\u00edveis para a camada':'N\u00e3o fornecidas';const cs=custos();$('passo').textContent=p.length?(passoAtual+1)+' / '+p.length:'—';$('posicao').textContent=atual?'('+atual.l+','+atual.c+')':'—';$('chaves').textContent=atual?(atual.chaves||'nenhuma'):'—';$('bonus').textContent=atual?(atual.bonus||'nenhum'):'—';
$('custo').textContent=cs&&p.length?String(+cs[passoAtual].toFixed(2)):'—';$('camada').textContent=atual?nomeCamada(atual.chaves):'—';$('exibida').textContent=nomeCamada(exibida);$('total').textContent=p.length;
$('steps').max=String(Math.max(p.length-1,0));$('steps').value=String(passoAtual);$('steps').style.setProperty('--progresso',(p.length>1?100*passoAtual/(p.length-1):0)+'%');$('velocidade').style.setProperty('--progresso',((Number($('velocidade').value)-1)/19*100)+'%');$('indice').textContent=p.length?passoAtual+' de '+(p.length-1):'indisponível';$('steps').disabled=!p.length;$('anterior').disabled=passoAtual===0||!p.length;$('proximo').disabled=passoAtual>=p.length-1;$('reproduzir').disabled=p.length<2;
if(p.length&&passoAtual===p.length-1)parar();}
$('mapa').addEventListener('change',trocarMapa);$('algoritmo').addEventListener('change',reiniciar);$('camadaSel').addEventListener('change',atualizar);$('mostrarArmadilhas').addEventListener('change',atualizar);
$('comparar').addEventListener('change',reiniciar);
$('anterior').addEventListener('click',()=>{parar();passoAtual--;atualizar();});$('proximo').addEventListener('click',()=>{parar();passoAtual++;atualizar();});
$('steps').addEventListener('input',e=>{parar();passoAtual=+e.target.value;atualizar();});$('velocidade').addEventListener('input',()=>{$('valorVelocidade').textContent=$('velocidade').value;$('velocidade').style.setProperty('--progresso',((Number($('velocidade').value)-1)/19*100)+'%');if(relogio!==null){parar();iniciar();}});
function iniciar(){const fim=fimReproducao();if(fim<1)return;if(passoAtual>=fim)passoAtual=0;relogio=setInterval(()=>{if(passoAtual<fimReproducao()){passoAtual++;atualizar();}else parar();},1000/Number($('velocidade').value));$('reproduzir').textContent='Pausar';atualizar();}
$('reproduzir').addEventListener('click',()=>{if(relogio!==null)parar();else iniciar();});
$('ampliar').addEventListener('click',()=>{ampliado=!ampliado;$('ampliar').textContent=ampliado?'Ajustar à tela':'Ampliar mapa';$('ampliar').setAttribute('aria-pressed',String(ampliado));atualizar();});
document.addEventListener('keydown',e=>{if(e.target.tagName==='SELECT'||e.target.tagName==='INPUT')return;if(e.key==='ArrowRight'){parar();passoAtual++;atualizar();}else if(e.key==='ArrowLeft'){parar();passoAtual--;atualizar();}else if(e.key===' '){e.preventDefault();$('reproduzir').click();}});
window.addEventListener('resize',()=>atualizar());
Object.keys(MAPAS).forEach(nome=>$('mapa').add(new Option(NOMES_MAPAS[nome]||nome,nome)));trocarMapa();
</script></body></html>'''
    fonte = Path(__file__).resolve().parent / "assets" / "JetBrainsMono-Regular.woff2"
    licenca = fonte.with_name("JetBrainsMono-OFL.txt").read_text(encoding="utf-8")
    html = (html.replace("__DATA__", dados_json)
            .replace("__FONT_DATA__", base64.b64encode(fonte.read_bytes()).decode("ascii"))
            .replace("__FONT_LICENSE__", licenca.replace("*/", "* /")))
    caminho = Path(arquivo)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(html, encoding="utf-8")
    return caminho
