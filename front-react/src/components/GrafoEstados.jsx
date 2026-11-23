// [IA] Claude Code – visualização interativa do grafo de estados com Cytoscape.js (zoom, arrastar, layouts e
// destaque do percurso). Só desenha os nós e arcos que o código do grupo exportou em dados.json; nada é calculado aqui.
import { useEffect, useMemo, useRef, useState } from 'react'
import { ALGORITMOS, MAPAS, NOME_ALG, PALETA, fmtInt, lerRotulo } from '../util.js'
import { BarraZoom, Cy } from './CyGrafo.jsx'

const NOMES_MAPAS = {
  m01_terreno: 'M01 · Terreno', m02_uma_chave: 'M02 · Uma chave', m03_tres_chaves: 'M03 · Três chaves',
  m04_esteiras: 'M04 · Esteiras', m05_bonus: 'M05 · Bônus', m06_fonte: 'M06 · Fonte', m07_impossivel: 'M07 · Impossível',
  g01_tres_depositos: 'G01 · Três depósitos', g02_poco_lateral: 'G02 · Poço lateral',
}
const LAYOUTS = [
  ['camadas', 'Camadas por chave'],
  ['arvore', 'Níveis a partir do início'],
  ['forca', 'Força (cose)'],
]
const PASSO = 34
const reduzMovimento = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

const ESTILO_BASE = [
  { selector: 'node', style: {
    width: 14, height: 14, 'background-color': 'data(cor)', 'border-width': 1.5, 'border-color': '#080808',
    label: 'data(rotulo)', 'font-family': 'IBM Plex Mono, ui-monospace, monospace', 'font-size': 7, 'font-weight': 600,
    color: '#080808', 'text-valign': 'bottom', 'text-margin-y': 3, 'min-zoomed-font-size': 9,
    'text-background-color': '#FFFFFF', 'text-background-opacity': 0.85, 'text-background-padding': 1,
  } },
  { selector: 'node.inicio', style: { width: 24, height: 24, shape: 'diamond', 'background-color': '#D4F500', 'border-width': 3, 'font-size': 9, 'min-zoomed-font-size': 0 } },
  { selector: 'node.saida', style: { width: 20, height: 20, shape: 'square', 'border-width': 3, 'font-size': 9, 'min-zoomed-font-size': 0 } },
  { selector: 'edge', style: {
    width: 1, 'line-color': '#BDBCB5', 'curve-style': 'straight', 'target-arrow-shape': 'triangle',
    'target-arrow-color': '#9A9993', 'arrow-scale': 0.6, opacity: 0.9,
  } },
  { selector: 'edge.muda', style: { 'line-color': '#E0412F', 'target-arrow-color': '#E0412F', width: 1.6 } },
  { selector: '.apagado', style: { opacity: 0.18 } },
  { selector: 'edge.rota', style: { width: 4, 'line-color': '#080808', 'target-arrow-color': '#080808', 'arrow-scale': 1, 'z-index': 10, opacity: 1 } },
  { selector: 'node.rota', style: { 'border-width': 3, 'z-index': 10, opacity: 1, 'min-zoomed-font-size': 0 } },
  { selector: 'node:selected', style: { 'overlay-color': '#D4F500', 'overlay-opacity': 0.5, 'overlay-padding': 6 } },
  { selector: 'edge.vizinho', style: { width: 2.5, 'line-color': '#353535', 'target-arrow-color': '#353535', opacity: 1, 'z-index': 9, label: 'data(peso)', 'font-size': 8, 'text-background-color': '#FFFFFF', 'text-background-opacity': 1, 'font-family': 'IBM Plex Mono, monospace' } },
]

function montarElementos(M) {
  const nos = M.grafo.nos.map((id) => ({ id, ...lerRotulo(id) })).filter((n) => n.l != null)
  const camadas = [...new Set(nos.map((n) => n.chaves))].sort((a, b) => a.length - b.length || a.localeCompare(b))
  const C = Math.max(...M.grade.map((r) => r.length))
  const L = M.grade.length
  const colunas = camadas.length <= 2 ? camadas.length : 2 // camadas em grade para o desenho não ficar comprido demais
  const inicio = M.grade.flatMap((r, l) => [...r].map((ch, c) => (ch === 'S' ? [l, c] : null))).find(Boolean)
  const elementos = nos.map((n) => {
    const camada = camadas.indexOf(n.chaves)
    const ehInicio = inicio && n.l === inicio[0] && n.c === inicio[1] && !n.chaves && !n.bonus.length
    const ehSaida = M.grade[n.l]?.[n.c] === 'G'
    return {
      group: 'nodes',
      data: { id: n.id, rotulo: `${n.l},${n.c}`, cor: PALETA[camada % PALETA.length], camada, chaves: n.chaves, bonus: n.bonus.join(', ') },
      position: { x: ((camada % colunas) * (C + 2) + n.c) * PASSO, y: (Math.floor(camada / colunas) * (L + 2) + n.l) * PASSO + (n.bonus.length * PASSO) / 3 },
      classes: [ehInicio && 'inicio', ehSaida && 'saida'].filter(Boolean).join(' '),
    }
  })
  const ids = new Set(nos.map((n) => n.id))
  M.grafo.arcos.forEach(([u, v, p], i) => {
    if (!ids.has(u) || !ids.has(v)) return
    const muda = lerRotulo(u).chaves !== lerRotulo(v).chaves
    elementos.push({ group: 'edges', data: { id: `e${i}`, source: u, target: v, peso: p }, classes: muda ? 'muda' : '' })
  })
  return { elementos, camadas, raiz: elementos.find((e) => e.classes?.includes('inicio'))?.data.id }
}

export function GrafoEstados() {
  const nomes = Object.keys(MAPAS).filter((n) => MAPAS[n].grafo)
  const [mapa, setMapa] = useState(nomes.includes('m02_uma_chave') ? 'm02_uma_chave' : nomes[0])
  const [layout, setLayout] = useState('camadas')
  const [alg, setAlg] = useState('DIJKSTRA')
  const [sel, setSel] = useState(null)
  const cyRef = useRef(null)
  const M = MAPAS[mapa]

  const { elementos, camadas, raiz } = useMemo(() => montarElementos(M), [M])
  const opcoesLayout = useMemo(() => {
    const animar = !reduzMovimento()
    if (layout === 'camadas') return { name: 'preset', fit: true, padding: 30 }
    if (layout === 'arvore') return { name: 'breadthfirst', directed: true, roots: raiz ? [raiz] : undefined, spacingFactor: 0.9, fit: true, padding: 30, animate: false }
    return { name: 'cose', animate: animar, animationDuration: 600, nodeRepulsion: () => 9000, idealEdgeLength: () => 40, fit: true, padding: 30, randomize: false }
  }, [layout, raiz])

  // Destaque do percurso do algoritmo escolhido
  const caminho = useMemo(() => (alg ? (M.percursos[alg] || []) : []), [M, alg])
  useEffect(() => {
    const cy = cyRef.current
    if (!cy) return
    cy.elements().removeClass('rota apagado vizinho')
    setSel(null)
    const rota = caminho.filter((id) => cy.getElementById(id).nonempty())
    if (rota.length < 2) return
    cy.elements().addClass('apagado')
    rota.forEach((id, i) => {
      cy.getElementById(id).removeClass('apagado').addClass('rota')
      if (i > 0) cy.getElementById(rota[i - 1]).edgesTo(cy.getElementById(id)).removeClass('apagado').addClass('rota')
    })
  }, [caminho, elementos, opcoesLayout])

  function selecionar(no) {
    const cy = cyRef.current
    cy.edges().removeClass('vizinho')
    if (!no) { setSel(null); return }
    no.connectedEdges().addClass('vizinho')
    setSel({ id: no.id(), ...no.data(), saida: no.outgoers('edge').length, entrada: no.incomers('edge').length })
  }

  const custo = alg && M.custos?.[alg]?.length ? M.custos[alg].at(-1) : null
  return (
    <section className="panel">
      <header>
        <span className="section-label">GRAFO DE ESTADOS · CYTOSCAPE</span>
        <h2>Grafo de estados interativo</h2>
        <p className="note">Cada nó é um estado (posição, chaves e bônus) e cada arco é um movimento possível. Arraste para mover, use a roda do mouse para dar zoom e clique num estado para ver as conexões. Em vermelho, os arcos que mudam de camada (coleta de chave).</p>
      </header>
      <div className="selecao">
        <label className="field">Mapa
          <select value={mapa} onChange={(e) => setMapa(e.target.value)}>
            {nomes.map((n) => <option key={n} value={n}>{NOMES_MAPAS[n] || n} · {fmtInt(MAPAS[n].n_estados)} estados</option>)}
          </select>
        </label>
        <label className="field">Disposição
          <select value={layout} onChange={(e) => setLayout(e.target.value)}>
            {LAYOUTS.map(([id, nome]) => <option key={id} value={id}>{nome}</option>)}
          </select>
        </label>
        <label className="field">Destacar percurso
          <select value={alg} onChange={(e) => setAlg(e.target.value)}>
            <option value="">Nenhum</option>
            {ALGORITMOS.map((a) => <option key={a} value={a}>{NOME_ALG[a]}</option>)}
          </select>
        </label>
      </div>
      <div className="cy-corpo">
        <div className="cy-palco">
          <BarraZoom cyRef={cyRef} />
          <Cy cyRef={cyRef} elementos={elementos} layout={opcoesLayout} estilo={ESTILO_BASE} aoSelecionar={selecionar} rotulo={`Grafo de estados de ${NOMES_MAPAS[mapa] || mapa}`} />
        </div>
        <aside className="reproducao">
          <h3>Resumo</h3>
          <dl className="state">
            <div><dt>Estados</dt><dd>{fmtInt(M.n_estados)}</dd></div>
            <div><dt>Arcos</dt><dd>{fmtInt(M.n_arcos)}</dd></div>
            <div className="wide"><dt>Percurso destacado</dt><dd>{alg ? (caminho.length ? `${NOME_ALG[alg]} · ${caminho.length - 1} passos · custo ${custo ?? '—'}` : `${NOME_ALG[alg]} · sem percurso`) : 'nenhum'}</dd></div>
          </dl>
          <h3>Estado selecionado</h3>
          {sel ? (
            <dl className="state">
              <div className="wide"><dt>Rótulo</dt><dd>{sel.id}</dd></div>
              <div><dt>Chaves</dt><dd>{sel.chaves || 'nenhuma'}</dd></div>
              <div><dt>Bônus usados</dt><dd>{sel.bonus || 'nenhum'}</dd></div>
              <div><dt>Arcos de saída</dt><dd>{sel.saida}</dd></div>
              <div><dt>Arcos de entrada</dt><dd>{sel.entrada}</dd></div>
            </dl>
          ) : <p className="note">Clique num nó para ver o estado e destacar seus arcos, com o peso de cada um.</p>}
          <div className="chart-legend cy-legenda">
            <strong>Camadas</strong>
            {camadas.map((c, i) => <span key={c || '-'}><i style={{ background: PALETA[i % PALETA.length] }} />{c ? `chaves ${c}` : 'sem chave'}</span>)}
            <span><i className="leg-inicio" />início</span>
            <span><i className="leg-saida" />saída</span>
          </div>
        </aside>
      </div>
    </section>
  )
}

/* Árvore BFS do m02 (arcos de árvore devolvidos pela BFS do grupo), desenhada em níveis. */
export function ArvoreBfsCy() {
  const M = MAPAS.m02_uma_chave
  const cyRef = useRef(null)
  const { elementos, raiz } = useMemo(() => {
    if (!M?.arvore_bfs) return { elementos: [] }
    const A = M.arvore_bfs
    const nivel = {}
    Object.entries(A.camadas).forEach(([k, ns]) => ns.forEach((n) => { nivel[n] = Number(k) }))
    const els = Object.keys(nivel).map((id) => {
      const r = lerRotulo(id)
      return { group: 'nodes', data: { id, rotulo: r ? `${r.l},${r.c}` : id, cor: r?.chaves ? PALETA[1] : PALETA[0] }, classes: nivel[id] === 0 ? 'inicio' : '' }
    })
    A.arcos.forEach(([u, v], i) => { if (u in nivel && v in nivel) els.push({ group: 'edges', data: { id: `t${i}`, source: u, target: v } }) })
    return { elementos: els, raiz: Object.keys(nivel).find((n) => nivel[n] === 0) }
  }, [M])
  const layout = useMemo(() => ({ name: 'breadthfirst', directed: true, roots: raiz ? [raiz] : undefined, spacingFactor: 0.75, fit: true, padding: 24, animate: false }), [raiz])
  if (!M?.arvore_bfs) return null
  return (
    <section className="panel">
      <header>
        <h2>Árvore BFS de estados do m02</h2>
        <p className="note">Arcos de árvore devolvidos pela BFS do grupo: cada nível é a distância, em passos, a partir do início (losango lime).</p>
      </header>
      <div className="cy-palco">
        <BarraZoom cyRef={cyRef} />
        <Cy cyRef={cyRef} elementos={elementos} layout={layout} estilo={ESTILO_BASE} altura={620} rotulo="Árvore BFS de estados do m02" />
      </div>
      <div className="legend">
        <span><i style={{ background: PALETA[0] }}></i>sem chave</span>
        <span><i style={{ background: PALETA[1] }}></i>com a chave a</span>
      </div>
    </section>
  )
}
