// [IA] Codex – capitalização de títulos, legendas e valores apresentados na interface.
// [IA] Claude Code – figuras da Parte 1: percursos, camadas do m02, árvore BFS e heatmap do m08
// [IA] Codex – ampliação, contraste e legendas das figuras existentes
import { MAPAS } from '../util.js'
import { Grade, LegendaCasas } from './Grade.jsx'
// [IA] Claude Code – grafo de estados e árvore BFS desenhados com Cytoscape.js (interativos)
import { ArvoreBfsCy, GrafoEstados } from './GrafoEstados.jsx'

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

function Heatmap() {
  const M = MAPAS.m08_grande
  if (!M) return null
  const max = Math.max(...Object.values(M.multiplicidade))
  return (
    <section className="panel">
      <header>
        <h2>Heatmap de multiplicidade do M08</h2>
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
      <GrafoEstados />
      <ArvoreBfsCy />
      <Percurso nome="m03_tres_chaves" titulo="Percurso de menor custo no M03" />
      <Percurso nome="m08_grande" titulo="Percurso de menor custo no M08" />
      <Heatmap />
    </div>
  )
}
