"""Visualizações e UX.

Parte 1 (P5a): percursos m03 e m08, grafo de estados do m02 em camadas,
árvore BFS do m02, heatmap de multiplicidade do m08 e labirinto interativo.
Parte 2 (P5b/AVD): comparação dos algoritmos e visualizações em out/parte2/.

Este módulo NÃO constrói G_pos/G_est, calcula soluções, armadilhas ou
interpreta resultados. Ele apenas representa informações recebidas.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
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
    for indice in range(len(estados) - 1):
        l1, c1, chaves, _ = estados[indice]
        l2, c2, _, _ = estados[indice + 1]
        ax.plot([c1, c2], [l1, l2], color=cores[chaves], linewidth=3.4,
                alpha=.87, zorder=7, solid_capstyle="round")
    for l, c, chaves, _ in estados:
        ax.scatter(c, l, s=18, color=[cores[chaves]], zorder=8)
    ax.scatter(estados[0][1], estados[0][0], s=110, marker="o",
               facecolors="white", edgecolors="#125E6A", linewidths=2, zorder=9)
    ax.scatter(estados[-1][1], estados[-1][0], s=110, marker="s",
               facecolors="white", edgecolors="#9B4D5F", linewidths=2, zorder=9)
    from matplotlib.lines import Line2D
    itens = [Line2D([0], [0], color=cores[chaves], lw=3,
                    label=f"Chaves: {chaves or 'nenhuma'}") for chaves in conjuntos]
    ax.legend(handles=itens, loc="upper center", bbox_to_anchor=(.5, -.02),
              ncol=min(4, len(itens)), frameon=False, fontsize=9)
    ax.set_title(titulo, fontsize=13, color="#233143", pad=14)
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
                                     mutation_scale=8, lw=1.3 if mudou else .75,
                                     color=cor, alpha=.8, zorder=1,
                                     connectionstyle="arc3,rad=.08"))
    for nome, (x, y) in layout.items():
        ax.scatter(x, y, s=170 if mostrar_nomes else 45, color="#2b7866", edgecolors="white", linewidths=1, zorder=3)
        if mostrar_nomes:
            try:
                dados = ler_rotulo(nome)
                # [IA] Codex – distingue estados da mesma posição por seus bônus.
                rotulo = f"({dados[0]},{dados[1]})" if dados else nome
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
    return _salvar(fig, arquivo)


def desenhar_camadas(grafo: Any, arquivo: str | Path,
                      max_nos: int = 250) -> Path:
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
                         "Grafo de estados por conjunto de chaves", True,
                         mostrar_nomes=len(nos) <= 100)


def desenhar_arvore_bfs(resultado_bfs: dict, arquivo: str | Path,
                        max_nos: int = 250) -> Path:
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
                         "Árvore BFS por nível", mostrar_nomes=quantidade <= 100)


def desenhar_heatmap(grade: list[str], grafo: Any, arquivo: str | Path) -> Path:
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
                ax.text(c, l, str(quantidades[l][c]), ha="center", va="center",
                        fontsize=8, color="#223448")
    ax.set_xticks(range(n_colunas)); ax.set_yticks(range(n_linhas))
    ax.set_xlabel("Coluna"); ax.set_ylabel("Linha")
    ax.set_title("Multiplicidade de estados por posição", fontsize=13, pad=14)
    fig.colorbar(imagem, ax=ax, fraction=.045, pad=.02, label="Estados distintos")
    return _salvar(fig, arquivo)


def gerar_html_interativo(mapas: dict[str, dict], arquivo: str | Path) -> Path:
    """Cria visualizador HTML sem bibliotecas externas.

    Formato de entrada:
    {
      "m03": {
        "grade": ["#####", "#S.G#", "#####"],
        "algoritmos": {"BFS": ["(1,1)|-|{}", "(1,2)|-|{}", ...]},
        "armadilhas": [[linha, coluna], ...]  # opcional, calculadas pelo grupo
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
        # [IA] Codex – correção da validação de mapas sem algoritmos.
        if not isinstance(dados.get("algoritmos"), dict) or not dados["algoritmos"]:
            raise ValueError(f"Mapa {nome} sem dicionário 'algoritmos'")
        for algoritmo, percurso in dados["algoritmos"].items():
            estados = _posicoes(percurso)
            # [IA] Claude Code – percurso vazio é aceito quando há mensagem de status (RECUSA, SEM_SOLUCAO...).
            if not estados and algoritmo not in dados.get("mensagens", {}):
                raise ValueError(f"Percurso vazio em {nome}/{algoritmo} (sem mensagem de status)")
            for l, c, _, _ in estados:
                if not (0 <= l < len(dados["grade"]) and 0 <= c < len(dados["grade"][0])):
                    raise ValueError(f"Posição fora da grade em {nome}/{algoritmo}")
    # Evita que nomes importados dos dados possam encerrar a tag <script>.
    dados_json = json.dumps(mapas, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    # [IA] Codex – revisão visual e acessibilidade do visualizador.
    # [IA] Claude Code – custo acumulado, troca de camadas, armadilhas por estado, mensagens e teclado.
    html = r'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Labirinto interativo — Grafos</title>
<style>
 :root{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#203b3b;background:#f4f3ed;--ink:#203b3b;--green:#126c5b;--line:#dce3d9}
*{box-sizing:border-box}body{max-width:1180px;margin:0 auto;padding:40px 28px 60px}header{margin-bottom:28px;border-bottom:1px solid #cbd7cb;padding-bottom:24px}header:before{content:"PROJETO DE GRAFOS  /  EXPLORADOR";display:block;color:#69877a;font-size:11px;font-weight:800;letter-spacing:.16em;margin-bottom:12px}h1{font-family:Georgia,serif;font-size:clamp(30px,4vw,46px);font-weight:normal;letter-spacing:-.035em;margin:0 0 8px}p{color:#62766e;margin:0;line-height:1.5}.panel{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px;margin:14px 0;box-shadow:0 6px 24px #24473508}
.controls{display:flex;flex-wrap:wrap;gap:18px;align-items:end}.group{display:flex;flex-direction:column;gap:7px;min-width:145px}label{font-size:12px;color:#587066;font-weight:700}select,input,button{font:inherit}select{padding:10px 34px 10px 12px;border:1px solid #cad8cc;border-radius:7px;background:#fff;color:var(--ink)}button{padding:10px 17px;border:1px solid #cad8cc;border-radius:7px;background:#fff;color:var(--ink);cursor:pointer;font-weight:650}button:hover:not(:disabled){border-color:var(--green)}button.primary{background:var(--green);color:white;border-color:var(--green)}button:disabled{opacity:.4;cursor:default}:focus-visible{outline:3px solid #e6ad52;outline-offset:3px}input{accent-color:var(--green)}.layout{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:24px;align-items:center}.map-wrap{overflow:auto;padding:20px;background:#edf2eb;border-radius:9px;min-width:0}
#grade{display:grid;gap:2px;width:max-content;margin:auto;--cell:34px}.cell{width:var(--cell);height:var(--cell);display:flex;align-items:center;justify-content:center;border-radius:3px;font-size:12px;font-weight:750;position:relative}.wall{background:#294940}.floor{background:#fff}.visited{background:#b9ded1}.outside{background:#e4e7e1;color:#9aa69f}.trap{outline:2px solid #c76b4b;outline-offset:-3px}.current{background:#d89c42!important;color:#172f2b!important;border-radius:50%;outline:3px solid #fff;outline-offset:-4px;z-index:1}.start{color:#087960}.goal{color:#a64d37}
.readout{font-size:13px}.readout:before{content:"ESTADO ATUAL";display:block;color:#82988a;font-size:10px;font-weight:800;letter-spacing:.14em;margin-bottom:8px}.readout div{display:flex;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px solid #edf1ec}.readout strong{color:#60786b;font-weight:500}.readout span{font-weight:700;text-align:right;font-variant-numeric:tabular-nums}#custo{color:var(--green);font-size:15px}.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center}#steps{flex:1;min-width:130px}#indice{font-size:12px;color:#60786b;min-width:20px}.legend{display:flex;flex-wrap:wrap;gap:16px;color:#60786b;font-size:12px;margin:12px 0 0}.legend span:before{content:"";display:inline-block;width:10px;height:10px;margin-right:6px;border-radius:2px;background:#b9ded1}.legend span:nth-child(2):before{background:#d89c42;border-radius:50%}.legend span:nth-child(3):before{background:transparent;border:2px solid #c76b4b}.legend span:nth-child(4):before{background:#e4e7e1}
#aviso{display:none;margin-top:12px;padding:12px 14px;border-radius:8px;background:#fbefe6;color:#7c3d22;font-size:13px;font-weight:600}.dica{font-size:12px;color:#82988a;margin-top:10px}
@media(max-width:740px){body{padding:24px 16px 40px}.layout{grid-template-columns:1fr}#grade{--cell:28px}.panel{padding:16px}.map-wrap{padding:14px}.group{flex:1 1 130px}}
</style></head><body>
<header><h1>Labirinto interativo</h1><p>Visualização de percursos calculados pelo projeto. Não executa algoritmos no navegador.</p></header>
<div class="panel controls"><div class="group"><label for="mapa">Mapa</label><select id="mapa"></select></div>
<div class="group"><label for="algoritmo">Algoritmo</label><select id="algoritmo"></select></div>
<div class="group"><label for="camadaSel">Camada exibida</label><select id="camadaSel"></select></div>
<div class="group"><label for="velocidade">Velocidade</label><select id="velocidade"><option value="1000">Lenta</option><option selected value="550">Normal</option><option value="200">Rápida</option></select></div>
<label><input type="checkbox" id="mostrarArmadilhas" checked> Mostrar armadilhas</label></div>
<div class="panel layout"><div><div class="map-wrap"><div id="grade" aria-label="Mapa do labirinto"></div></div><div class="legend"><span>Percorrido</span><span>Posição atual</span><span>Armadilha</span><span>Sem estado nesta camada</span></div><div id="aviso" role="status"></div></div><div class="readout">
<div><strong>Passo:</strong> <span id="passo"></span></div><div><strong>Posição:</strong> <span id="posicao"></span></div>
<div><strong>Chaves:</strong> <span id="chaves"></span></div><div><strong>Bônus consumidos:</strong> <span id="bonus"></span></div>
<div><strong>Custo acumulado:</strong> <span id="custo"></span></div>
<div><strong>Camada do estado:</strong> <span id="camada"></span></div>
<div><strong>Camada exibida:</strong> <span id="exibida"></span></div>
<div><strong>Estados no percurso:</strong> <span id="total"></span></div></div></div>
<div class="panel toolbar"><button id="anterior">Anterior</button><button class="primary" id="reproduzir">Reproduzir</button><button id="proximo">Próximo</button><input id="steps" aria-label="Selecionar passo do percurso" type="range" min="0" max="0" value="0"><span id="indice"></span></div>
<p class="dica">Teclado: ← e → avançam um passo; espaço reproduz ou pausa.</p>
<script>
const MAPAS = __DATA__;
const $ = id => document.getElementById(id);
let passoAtual=0, relogio=null;
function parseEstado(texto){if(texto==='ALVO')return null;const m=/^\((\d+)\s*,\s*(\d+)\)\|([a-d]*|-)\|\{([0-9,]*)\}$/.exec(texto);if(!m)throw Error('Estado inválido: '+texto);return {l:+m[1],c:+m[2],chaves:m[3]==='-'?'':m[3],bonus:m[4]};}
function nomeCamada(ch){return ch===''?'sem chaves':'chaves '+ch;}
function dados(){return MAPAS[$('mapa').value];}
function percurso(){return (dados().algoritmos[$('algoritmo').value]||[]).map(parseEstado).filter(x=>x!==null);}
function custos(){return (dados().custos||{})[$('algoritmo').value]||null;}
function estadosMapa(){const m=dados();const lista=(m.estados&&m.estados.length?m.estados:Object.values(m.algoritmos).flat());return lista.map(parseEstado).filter(x=>x!==null);}
function camadas(){const s=new Set(estadosMapa().map(e=>e.chaves));return Array.from(s).sort((a,b)=>a.length-b.length||a.localeCompare(b));}
function parar(){if(relogio!==null){clearInterval(relogio);relogio=null;} $('reproduzir').textContent='Reproduzir';}
function reiniciar(){parar();passoAtual=0;atualizar();}
function trocarMapa(){const m=dados();$('algoritmo').replaceChildren();Object.keys(m.algoritmos).forEach(nome=>{$('algoritmo').add(new Option(nome,nome));});
$('camadaSel').replaceChildren();$('camadaSel').add(new Option('Seguir o percurso','__auto'));camadas().forEach(ch=>$('camadaSel').add(new Option(nomeCamada(ch),ch)));reiniciar();}
function atualizar(){const m=dados(), p=percurso(), aviso=$('aviso'), msg=(m.mensagens||{})[$('algoritmo').value];
const grid=$('grade');grid.replaceChildren();grid.style.gridTemplateColumns='repeat('+m.grade[0].length+',var(--cell))';
if(!p.length){parar();aviso.style.display='block';aviso.textContent=msg||'Sem percurso para este algoritmo.';}else if(msg){aviso.style.display='block';aviso.textContent=msg;}else{aviso.style.display='none';}
passoAtual=Math.min(Math.max(passoAtual,0),Math.max(p.length-1,0));const atual=p[passoAtual]||null;
const sel=$('camadaSel').value, exibida=sel==='__auto'?(atual?atual.chaves:''):sel;
const temEstados=!!(m.estados&&m.estados.length), naCamada=new Set(estadosMapa().filter(e=>e.chaves===exibida).map(e=>e.l+','+e.c));
const vistos=new Set(p.slice(0,passoAtual+1).filter(s=>s.chaves===exibida||sel==='__auto').map(s=>s.l+','+s.c));
const armadilhas=new Set((m.armadilhas||[]).map(s=>s[0]+','+s[1]));((m.armadilhas_estados||[]).map(parseEstado).filter(e=>e&&e.chaves===exibida)).forEach(e=>armadilhas.add(e.l+','+e.c));
m.grade.forEach((linha,l)=>Array.from(linha).forEach((ch,c)=>{const cell=document.createElement('div');const key=l+','+c;cell.className='cell '+(ch==='#'?'wall':'floor');
if(ch!=='#'&&temEstados&&!naCamada.has(key))cell.classList.add('outside');if(vistos.has(key)&&ch!=='#')cell.classList.add('visited');if($('mostrarArmadilhas').checked&&armadilhas.has(key))cell.classList.add('trap');
if(atual&&atual.l===l&&atual.c===c&&(sel==='__auto'||atual.chaves===exibida))cell.classList.add('current');if(ch==='S')cell.classList.add('start');if(ch==='G')cell.classList.add('goal');cell.textContent=ch==='.'||ch==='#'?'':ch;cell.title='('+l+','+c+') '+ch;grid.appendChild(cell);}));
const cs=custos();$('passo').textContent=p.length?(passoAtual+1)+' / '+p.length:'—';$('posicao').textContent=atual?'('+atual.l+','+atual.c+')':'—';$('chaves').textContent=atual?(atual.chaves||'nenhuma'):'—';$('bonus').textContent=atual?(atual.bonus||'nenhum'):'—';
$('custo').textContent=cs&&p.length?String(+cs[passoAtual].toFixed(2)):'—';$('camada').textContent=atual?nomeCamada(atual.chaves):'—';$('exibida').textContent=nomeCamada(exibida);$('total').textContent=p.length;
$('steps').max=String(Math.max(p.length-1,0));$('steps').value=String(passoAtual);$('indice').textContent=String(passoAtual);$('anterior').disabled=passoAtual===0||!p.length;$('proximo').disabled=passoAtual>=p.length-1;$('reproduzir').disabled=p.length<2;
if(p.length&&passoAtual===p.length-1)parar();}
$('mapa').addEventListener('change',trocarMapa);$('algoritmo').addEventListener('change',reiniciar);$('camadaSel').addEventListener('change',atualizar);$('mostrarArmadilhas').addEventListener('change',atualizar);
$('anterior').addEventListener('click',()=>{parar();passoAtual--;atualizar();});$('proximo').addEventListener('click',()=>{parar();passoAtual++;atualizar();});
$('steps').addEventListener('input',e=>{parar();passoAtual=+e.target.value;atualizar();});$('velocidade').addEventListener('change',()=>{if(relogio!==null){parar();iniciar();}});
function iniciar(){if(percurso().length<2)return;if(passoAtual===percurso().length-1)passoAtual=0;relogio=setInterval(()=>{if(passoAtual<percurso().length-1){passoAtual++;atualizar();}else parar();},+$('velocidade').value);$('reproduzir').textContent='Pausar';atualizar();}
$('reproduzir').addEventListener('click',()=>{if(relogio!==null)parar();else iniciar();});
document.addEventListener('keydown',e=>{if(e.target.tagName==='SELECT'||e.target.tagName==='INPUT')return;if(e.key==='ArrowRight'){parar();passoAtual++;atualizar();}else if(e.key==='ArrowLeft'){parar();passoAtual--;atualizar();}else if(e.key===' '){e.preventDefault();$('reproduzir').click();}});
Object.keys(MAPAS).forEach(nome=>$('mapa').add(new Option(nome,nome)));trocarMapa();
</script></body></html>'''
    html = html.replace("__DATA__", dados_json)
    caminho = Path(arquivo)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(html, encoding="utf-8")
    return caminho
