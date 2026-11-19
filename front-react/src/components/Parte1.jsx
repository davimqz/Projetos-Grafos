// [IA] Claude Code – figuras da Parte 1: percursos, camadas do m02, árvore BFS e heatmap do m08
// [IA] Codex – ampliação, contraste e legendas das figuras existentes
import { useState } from 'react'
import { MAPAS, lerRotulo } from '../util.js'
import { Grade, LegendaCasas } from './Grade.jsx'

const CORES_ESTADO = ['#81aaff', '#ff8e81']

function GrafoVisual({ children }) {
  const [ampliado, setAmpliado] = useState(false)
  return <div className="grafo-view"><div className="view-actions"><button type="button" className="btn zoom-btn" aria-pressed={ampliado} onClick={() => setAmpliado((v) => !v)}>{ampliado ? 'Ajustar à tela' : 'Ampliar grafo'}</button>{ampliado && <span>Role para explorar o grafo ampliado.</span>}</div><div className={`grafo-frame${ampliado ? ' ampliado' : ''}`} tabIndex={ampliado ? 0 : undefined}>{children}</div></div>
}

function Percurso({ nome, titulo }) {
  const M = MAPAS[nome]
  if (!M) return null
  const cam = M.percursos.DIJKSTRA
  const c = M.custos.DIJKSTRA
  return (
    <section className="panel">
      <header>
        <h2>{titulo}</h2>
        <p className="note">Dijkstra: {cam.length - 1} passos, custo {c[c.length - 1]}. A cor muda a cada chave coletada.</p>
      </header>
      <Grade grade={M.grade} caminho={cam} tam={nome.startsWith('m08') ? 11 : 30} />
      <LegendaCasas />
    </section>
  )
}

function Camadas() {
  const M = MAPAS.m02_uma_chave
  if (!M) return null
  const G = M.grafo
  const nos = G.nos.map((n) => ({ n, ...lerRotulo(n) }))
  const grupos = [...new Set(nos.map((x) => x.chaves))].sort()
  const W = 860
  const colW = W / grupos.length
  const pos = {}
  grupos.forEach((g, gi) => {
    nos.filter((x) => x.chaves === g).forEach((x) => { pos[x.n] = [gi * colW + 34 + x.c * ((colW - 68) / 12), 46 + x.l * 62] })
  })
  const H = Math.max(...Object.values(pos).map((p) => p[1])) + 30
  return (
    <section className="panel">
      <header>
        <h2>Grafo de estados do m02 em camadas</h2>
        <p className="note">Uma camada por conjunto de chaves; em vermelho, os arcos que mudam de camada.</p>
      </header>
      <GrafoVisual>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Camadas do m02">
          <defs>
            <marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0L10,5L0,10z" fill="var(--muted)" /></marker>
            <marker id="seta2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0L10,5L0,10z" fill="#ff8e81" /></marker>
          </defs>
          {grupos.map((g, gi) => (
            <g key={`t${g}`}>
              <rect x={gi * colW + 6} y="4" width={colW - 12} height={H - 8} rx="10" fill="var(--chip)" />
              <text x={gi * colW + colW / 2} y="26" textAnchor="middle" fontWeight="600">chaves: {g || 'nenhuma'}</text>
            </g>
          ))}
          {G.arcos.map(([u, v], i) => {
            const a = pos[u]
            const b = pos[v]
            if (!a || !b) return null
            const muda = lerRotulo(u).chaves !== lerRotulo(v).chaves
            return (
              <line key={`a${i}`} x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={muda ? '#ff8e81' : 'var(--muted)'}
                strokeWidth={muda ? 2.5 : 1} opacity={muda ? 1 : 0.8} markerEnd={muda ? 'url(#seta2)' : 'url(#seta)'} />
            )
          })}
          {nos.map((x) => (
            <circle key={x.n} cx={pos[x.n][0]} cy={pos[x.n][1]} r="5.5" fill={CORES_ESTADO[grupos.indexOf(x.chaves) % CORES_ESTADO.length]} stroke="var(--surface)" strokeWidth="1.5" />
          ))}
        </svg>
      </GrafoVisual>
    </section>
  )
}

function ArvoreBFS() {
  const M = MAPAS.m02_uma_chave
  if (!M) return null
  const A = M.arvore_bfs
  const niveis = Object.keys(A.camadas).map(Number).sort((a, b) => a - b)
  const W = 860
  const pos = {}
  niveis.forEach((k) => {
    const ns = A.camadas[k]
    ns.forEach((n, i) => { pos[n] = [((i + 1) * W) / (ns.length + 1), 28 + k * 24] })
  })
  const H = 28 + niveis.length * 24 + 16
  return (
    <section className="panel">
      <header>
        <h2>Árvore BFS de estados do m02</h2>
        <p className="note">Um nível por linha: a distância, em passos, a partir do início.</p>
      </header>
      <GrafoVisual>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Árvore BFS">
          {niveis.filter((k) => k % 5 === 0).map((k) => (
            <g key={`n${k}`}>
              <line x1="0" x2={W} y1={28 + k * 24} y2={28 + k * 24} stroke="var(--line)" strokeDasharray="3 4" />
              <text x="4" y={24 + k * 24} fontSize="11" className="muted">nível {k}</text>
            </g>
          ))}
          {A.arcos.map(([u, v], i) => (pos[u] && pos[v] ? (
            <line key={i} x1={pos[u][0]} y1={pos[u][1]} x2={pos[v][0]} y2={pos[v][1]} stroke="var(--muted)" strokeWidth="1.2" />
          ) : null))}
          {niveis.map((k) => A.camadas[k].map((n) => (
            <circle key={n} cx={pos[n][0]} cy={pos[n][1]} r="5" fill={CORES_ESTADO[lerRotulo(n).chaves ? 1 : 0]} stroke="var(--surface)" strokeWidth="1.5" />
          )))}
        </svg>
      </GrafoVisual>
      <div className="legend">
        <span><i style={{ background: CORES_ESTADO[0] }}></i>sem chave</span>
        <span><i style={{ background: CORES_ESTADO[1] }}></i>com a chave a</span>
      </div>
    </section>
  )
}

function Heatmap() {
  const M = MAPAS.m08_grande
  if (!M) return null
  const max = Math.max(...Object.values(M.multiplicidade))
  return (
    <section className="panel">
      <header>
        <h2>Heatmap de multiplicidade do m08</h2>
        <p className="note">Número de estados associados a cada casa. A escala vai de azul (menos) a vermelho (mais).</p>
      </header>
      <Grade grade={M.grade} heat={M.multiplicidade} tam={13} />
      <div className="heat-scale"><span>1 estado</span><i /><span>{max} estados</span></div>
    </section>
  )
}

export function Parte1() {
  return (
    <div className="figuras">
      <Percurso nome="m03_tres_chaves" titulo="Percurso de menor custo no m03" />
      <Camadas />
      <ArvoreBFS />
      <Percurso nome="m08_grande" titulo="Percurso de menor custo no m08" />
      <Heatmap />
    </div>
  )
}
