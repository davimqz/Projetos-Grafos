// [IA] Claude Code – tela da Parte 2 (pedidos R5/R6 da reunião de 19/11): fontes e pares com os resultados já
// calculados pelo código do grupo (parte2.json) e desenho do subgrafo de cada caso com a cor da classe da carteira
import { useEffect, useMemo, useRef, useState } from 'react'
import { BarraZoom, Cy } from './CyGrafo.jsx'
import P2 from '../parte2.json'
import { NOME_CLASSE, corClasse, fmt, fmtInt } from '../util.js'
// [IA] Claude Code – cores dos grafos no design system brutalista (fundo claro, contornos pretos)

const CASOS = [
  ['buscas', 'BFS e DFS', '3 fontes'],
  ['dijkstra', 'Dijkstra', '5 pares origem–destino'],
  ['bellman_ford', 'Bellman-Ford', '2 origens'],
]

const classe = (no) => P2.classe[no] || 'desconhecido'
const curto = (no) => (no.length > 12 ? `${no.slice(0, 6)}…${no.slice(-4)}` : no)
const fmtBtc = (v) => v.toLocaleString('pt-BR', { maximumFractionDigits: 4 })

function rotuloCaso(tipo, c) {
  if (tipo === 'dijkstra') return `${curto(c.origem)} → ${curto(c.destino)}`
  return `${curto(c.origem)} (${NOME_CLASSE[classe(c.origem)]})`
}

// [IA] Claude Code – grafos da Parte 2 com Cytoscape.js: amostra da rede em várias camadas, caminhos e ciclos interativos
const corHex = (c) => getComputedStyle(document.documentElement).getPropertyValue(`--${c}`).trim() || '#A3A29C'
const FONTE_MONO = 'IBM Plex Mono, ui-monospace, monospace'

const ESTILO_P2 = [
  { selector: 'node', style: {
    width: 16, height: 16, 'background-color': 'data(cor)', 'border-width': 1.5, 'border-color': '#080808',
    label: 'data(rotulo)', 'font-family': FONTE_MONO, 'font-size': 8, 'font-weight': 600, color: '#080808',
    'text-valign': 'bottom', 'text-margin-y': 4, 'min-zoomed-font-size': 11,
    'text-background-color': '#FFFFFF', 'text-background-opacity': 0.9, 'text-background-padding': 2,
  } },
  { selector: 'node.origem', style: { width: 32, height: 32, shape: 'diamond', 'border-width': 3, 'font-size': 10, 'min-zoomed-font-size': 0 } },
  { selector: 'node.extremo', style: { width: 26, height: 26, 'border-width': 3, 'font-size': 10, 'min-zoomed-font-size': 0 } },
  { selector: 'edge', style: {
    width: 1.5, 'line-color': '#353535', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle',
    'target-arrow-color': '#353535', 'arrow-scale': 0.8, opacity: 0.85,
  } },
  { selector: 'edge.outro', style: { 'line-style': 'dashed', 'line-color': '#9A9993', 'target-arrow-color': '#9A9993', width: 1.2 } },
  { selector: 'edge.peso', style: {
    width: 3, 'line-color': '#080808', 'target-arrow-color': '#080808', opacity: 1, label: 'data(peso)',
    'font-family': FONTE_MONO, 'font-size': 11, 'font-weight': 700, 'text-background-color': '#FFFFFF',
    'text-background-opacity': 1, 'text-background-padding': 3, 'text-border-width': 1, 'text-border-color': '#080808', 'text-border-opacity': 1,
  } },
  { selector: 'edge.negativo', style: { 'line-color': '#E0412F', 'target-arrow-color': '#E0412F' } },
  { selector: '.apagado', style: { opacity: 0.15 } },
  { selector: 'node.foco', style: { 'overlay-color': '#D4F500', 'overlay-opacity': 0.6, 'overlay-padding': 7, 'min-zoomed-font-size': 0, 'z-index': 20 } },
  { selector: 'edge.foco', style: { width: 3, 'line-color': '#080808', 'target-arrow-color': '#080808', opacity: 1, 'z-index': 19 } },
]

function noCy(no, classes = '') {
  return { group: 'nodes', data: { id: no, rotulo: curto(no), cor: corHex(classe(no)) }, classes }
}

/* Destaca o nó em foco e seus arcos; o resto do grafo fica apagado. */
function useFoco(cyRef, deps, onFoco) {
  useEffect(() => {
    const cy = cyRef.current
    if (!cy || !onFoco) return undefined
    const limpar = () => cy.elements().removeClass('foco apagado')
    const focar = (e) => {
      limpar()
      const no = e.target
      cy.elements().addClass('apagado')
      no.closedNeighborhood().removeClass('apagado')
      no.addClass('foco'); no.connectedEdges().addClass('foco')
      onFoco(no.id())
    }
    cy.on('mouseover tap', 'node', focar)
    cy.on('mouseout', 'node', limpar)
    cy.on('tap', (e) => { if (e.target === cy) { limpar(); onFoco(null) } })
    return () => cy.removeListener('mouseover tap mouseout tap')
  }, deps) // eslint-disable-line react-hooks/exhaustive-deps
}

function GrafoRede({ origem, nos, arvore, outros = [], onFoco, layoutInicial = 'forca' }) {
  const cyRef = useRef(null)
  const [modo, setModo] = useState(layoutInicial)
  const elementos = useMemo(() => [
    ...nos.map((n) => noCy(n, n === origem ? 'origem' : '')),
    ...arvore.map(([u, v], i) => ({ group: 'edges', data: { id: `a${i}`, source: u, target: v } })),
    ...outros.map(([u, v], i) => ({ group: 'edges', data: { id: `o${i}`, source: u, target: v }, classes: 'outro' })),
  ], [nos, arvore, outros, origem])
  const layout = useMemo(() => (modo === 'arvore'
    ? { name: 'breadthfirst', directed: true, roots: [origem], spacingFactor: 1.1, fit: true, padding: 30, animate: false }
    : { name: 'cose', animate: !window.matchMedia?.('(prefers-reduced-motion: reduce)').matches, animationDuration: 600, nodeRepulsion: () => 12000, idealEdgeLength: () => 60, fit: true, padding: 30 }), [modo, origem])
  useFoco(cyRef, [elementos, layout], onFoco)
  return (
    <div className="cy-palco">
      <BarraZoom cyRef={cyRef} />
      <div className="cy-modos" role="group" aria-label="Disposição do grafo">
        {[['forca', 'Força'], ['arvore', 'Árvore']].map(([id, nome]) => (
          <button key={id} type="button" className="btn zoom-btn" aria-pressed={modo === id} onClick={() => setModo(id)}>{nome}</button>
        ))}
      </div>
      <Cy cyRef={cyRef} elementos={elementos} layout={layout} estilo={ESTILO_P2} altura={540} rotulo={`Rede de carteiras a partir de ${origem}`} />
    </div>
  )
}

function GrafoCaminho({ caminho, arcos, ciclo }) {
  const cyRef = useRef(null)
  const elementos = useMemo(() => {
    const unicos = [...new Set(caminho)]
    const els = unicos.map((no, i) => ({
      ...noCy(no, ciclo ? '' : (i === 0 ? 'origem' : i === unicos.length - 1 ? 'extremo' : '')),
      position: ciclo
        ? { x: 200 * Math.cos(Math.PI + (2 * Math.PI * i) / unicos.length), y: 200 * Math.sin(Math.PI + (2 * Math.PI * i) / unicos.length) }
        : { x: i * 170, y: 0 },
    }))
    arcos.forEach(([u, v, w], i) => els.push({ group: 'edges', data: { id: `c${i}`, source: u, target: v, peso: fmtBtc(w) }, classes: `peso${w < 0 ? ' negativo' : ''}` }))
    return els
  }, [caminho, arcos, ciclo])
  const layout = useMemo(() => ({ name: 'preset', fit: true, padding: 60 }), [])
  return (
    <div className="cy-palco">
      <BarraZoom cyRef={cyRef} />
      <Cy cyRef={cyRef} elementos={elementos} layout={layout} estilo={ESTILO_P2} altura={ciclo ? 420 : 300} rotulo={ciclo ? 'Ciclo negativo' : 'Caminho mínimo'} />
    </div>
  )
}

function Legenda() {
  return (
    <div className="chart-legend">
      <strong>Classe da carteira</strong>
      {['ilicito', 'licito', 'desconhecido'].map((c) => (
        <span key={c}><i style={{ background: corClasse(c) }} />{NOME_CLASSE[c]}</span>
      ))}
      <span><i className="leg-inicio" />origem</span>
      <span><i className="leg-arco" />arco da árvore / caminho</span>
      <span><i className="leg-arco tracejado" />outro arco do dataset</span>
    </div>
  )
}

function Dados({ itens }) {
  return (
    <dl className="state">
      {itens.map(([k, v, largo]) => (
        <div key={k} className={largo ? 'wide' : undefined}><dt>{k}</dt><dd>{v}</dd></div>
      ))}
    </dl>
  )
}

function Busca({ c }) {
  const [foco, setFoco] = useState(null)
  const arcosDfs = c.dfs.contagem_arcos
  const rede = c.rede
  return (
    <div className="p2-corpo">
      <div className="mapa-area">
        {rede
          ? <GrafoRede key={c.origem} origem={c.origem} nos={rede.nos} arvore={rede.arvore} outros={rede.outros} onFoco={setFoco} />
          : <GrafoRede key={c.origem} origem={c.origem} nos={c.recorte.nos} arvore={c.recorte.arcos} onFoco={setFoco} />}
        <p className="note" style={{ marginTop: 14 }}>
          {rede
            ? <>Amostra da árvore BFS com {fmtInt(rede.nos.length)} das {fmtInt(c.alcancados)} carteiras alcançadas, em {fmtInt(Math.max(...Object.values(rede.nivel)))} camadas: linha cheia são arcos da árvore BFS e tracejado são os outros {fmtInt(rede.outros.length)} arcos do dataset entre essas carteiras. </>
            : <>Recorte com a origem e {fmtInt(c.recorte.nos.length - 1)} carteiras da camada 1 da BFS. </>}
          Passe o mouse ou toque num nó para ver o endereço e as conexões.
        </p>
      </div>
      <aside className="reproducao">
        <h3>BFS a partir da origem</h3>
        <Dados itens={[
          ['Origem', `${curto(c.origem)} · ${NOME_CLASSE[classe(c.origem)]}`, true],
          ['Alcançadas', `${fmtInt(c.alcancados)} de ${fmtInt(c.total_nos)}`],
          ['Camadas', fmtInt(c.tamanho_camadas.length - 1)],
          ['Nó em foco', foco ? `${curto(foco)} · ${NOME_CLASSE[classe(foco)]}` : '—', true],
        ]} />
        <table className="p2-tabela">
          <caption>Carteiras por camada</caption>
          <thead><tr><th>Camada</th><th>Carteiras</th></tr></thead>
          <tbody>{c.tamanho_camadas.map((t, i) => <tr key={i}><th scope="row">{i}</th><td>{fmtInt(t)}</td></tr>)}</tbody>
        </table>
        <h3>DFS a partir da origem</h3>
        <Dados itens={[
          ['Árvore', fmtInt(arcosDfs.arvore)], ['Retorno', fmtInt(arcosDfs.retorno)],
          ['Avanço', fmtInt(arcosDfs.avanco)], ['Cruzamento', fmtInt(arcosDfs.cruzamento)],
          ['Ciclo alcançável', c.dfs.tem_ciclo ? 'sim (há arco de retorno)' : 'não', true],
        ]} />
      </aside>
    </div>
  )
}

function Dijkstra({ c }) {
  return (
    <div className="p2-corpo">
      <div className="mapa-area">
        <GrafoCaminho caminho={c.caminho} arcos={c.arcos} />
        <p className="note" style={{ marginTop: 10 }}>Peso de cada arco: valor em BTC transferido entre as carteiras (sempre ≥ 0, por isso o Dijkstra se aplica).</p>
      </div>
      <aside className="reproducao">
        <h3>Caminho mínimo</h3>
        <Dados itens={[
          ['Origem', `${curto(c.origem)} · ${NOME_CLASSE[classe(c.origem)]}`, true],
          ['Destino', `${curto(c.destino)} · ${NOME_CLASSE[classe(c.destino)]}`, true],
          ['Custo', `${fmtBtc(c.custo)} BTC`], ['Arcos', fmtInt(c.passos)],
        ]} />
        <ol className="p2-lista">{c.caminho.map((n) => <li key={n}><i style={{ background: corClasse(classe(n)) }} />{curto(n)}</li>)}</ol>
      </aside>
    </div>
  )
}

function BellmanFord({ c }) {
  if (c.tem_ciclo_negativo) {
    return (
      <div className="p2-corpo">
        <div className="mapa-area">
          <GrafoCaminho caminho={c.ciclo} arcos={c.arcos} ciclo />
          <p className="note" style={{ marginTop: 10 }}>Ciclo negativo alcançável a partir da origem: dar uma volta no ciclo soma custo negativo, então o caminho mínimo não é definido.</p>
        </div>
        <aside className="reproducao">
          <h3>Resultado</h3>
          <Dados itens={[
            ['Origem', `${curto(c.origem)} · ${NOME_CLASSE[classe(c.origem)]}`, true],
            ['Status', c.status], ['Custo do ciclo', fmtBtc(c.custo_ciclo)],
            ['Alcançadas', `${fmtInt(c.alcancados)} de ${fmtInt(c.total_nos)}`, true],
          ]} />
          <ol className="p2-lista">{c.ciclo.map((n, i) => <li key={i}><i style={{ background: corClasse(classe(n)) }} />{curto(n)}</li>)}</ol>
        </aside>
      </div>
    )
  }
  const nos = [...new Set([c.origem, ...c.arcos.flat()])]
  const negativas = Object.entries(c.distancia).filter(([, d]) => d < 0).sort((a, b) => a[1] - b[1])
  return (
    <div className="p2-corpo">
      <div className="mapa-area">
        <GrafoRede key={c.origem} origem={c.origem} nos={nos} arvore={c.arcos} layoutInicial="arvore" />
        <p className="note" style={{ marginTop: 10 }}>Árvore de caminhos mínimos devolvida pelo Bellman-Ford: cada carteira aparece ligada ao seu predecessor.</p>
      </div>
      <aside className="reproducao">
        <h3>Resultado</h3>
        <Dados itens={[
          ['Origem', `${curto(c.origem)} · ${NOME_CLASSE[classe(c.origem)]}`, true],
          ['Status', c.status], ['Alcançadas', fmtInt(c.alcancados)],
          ['Arcos negativos alcançáveis', fmtInt(c.arcos_negativos_alcancaveis), true],
        ]} />
        <table className="p2-tabela">
          <caption>Carteiras com distância negativa</caption>
          <thead><tr><th>Carteira</th><th>Distância</th></tr></thead>
          <tbody>{negativas.map(([n, d]) => <tr key={n}><th scope="row"><i style={{ background: corClasse(classe(n)) }} />{curto(n)}</th><td>{fmtBtc(d)}</td></tr>)}</tbody>
        </table>
      </aside>
    </div>
  )
}

function Tempos() {
  return (
    <section className="panel">
      <header>
        <span className="section-label">DESEMPENHO NO GRAFO COMPLETO</span>
        <h2>Tempo e memória por algoritmo</h2>
        <p className="note">Média de 5 execuções no recorte inteiro ({fmtInt(P2.tempos[0].nos)} carteiras e {fmtInt(P2.tempos[0].arestas)} arcos), do <code>parte2_report.json</code>.</p>
      </header>
      <div className="scroll">
        <table className="p2-tabela larga">
          <thead><tr><th>Algoritmo</th><th>Complexidade</th><th>Tempo médio (ms)</th><th>Latência mín–máx (ms)</th><th>Pico de memória (KB)</th><th>Status</th></tr></thead>
          <tbody>{P2.tempos.map((t) => (
            <tr key={t.algoritmo}>
              <th scope="row">{t.algoritmo}</th><td>{t.complexidade}</td><td>{fmt(t.tempo_medio_ms, 2)}</td>
              <td>{fmt(t.latencia_min_ms, 2)} – {fmt(t.latencia_max_ms, 2)}</td><td>{fmt(t.memoria_pico_kb, 1)}</td><td>{t.status}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </section>
  )
}

function casoInicial() {
  const p = new URLSearchParams(window.location.search)
  const tipo = CASOS.some(([id]) => id === p.get('p2')) ? p.get('p2') : 'buscas'
  return [tipo, Math.max(0, Math.min(Number(p.get('caso')) || 0, P2[tipo].length - 1))]
}

export function Parte2() {
  const [tipo, setTipo] = useState(() => casoInicial()[0])
  const [indice, setIndice] = useState(() => casoInicial()[1])
  const casos = P2[tipo]
  const caso = casos[Math.min(indice, casos.length - 1)]
  return (
    <div className="figuras">
      <section className="panel">
        <header>
          <span className="section-label">PARTE 2 · ELLIPTIC++</span>
          <h2>Os algoritmos na rede de carteiras</h2>
          <p className="note">Cada nó é uma carteira Bitcoin e cada arco liga quem enviou a quem recebeu. Os resultados são os mesmos do relatório,
            calculados pelos algoritmos do grupo e lidos de <code>parte2.json</code>.</p>
        </header>
        <div className="selecao">
          <label className="field">Algoritmo
            <select value={tipo} onChange={(e) => { setTipo(e.target.value); setIndice(0) }}>
              {CASOS.map(([id, nome, desc]) => <option key={id} value={id}>{nome} · {desc}</option>)}
            </select>
          </label>
          <label className="field">{tipo === 'dijkstra' ? 'Par origem → destino' : 'Carteira de origem'}
            <select value={indice} onChange={(e) => setIndice(Number(e.target.value))}>
              {casos.map((c, i) => <option key={i} value={i}>{rotuloCaso(tipo, c)}</option>)}
            </select>
          </label>
        </div>
        <Legenda />
        {tipo === 'buscas' && <Busca key={indice} c={caso} />}
        {tipo === 'dijkstra' && <Dijkstra c={caso} />}
        {tipo === 'bellman_ford' && <BellmanFord c={caso} />}
      </section>
      <Tempos />
    </div>
  )
}
