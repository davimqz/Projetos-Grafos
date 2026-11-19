// [IA] Claude Code – desenho da grade do labirinto, do percurso e do heatmap
// [IA] Codex – desempenho do desenho, animação, ampliação e legendas
import { useMemo, useState } from 'react'
import { PALETA, corCasa, lerRotulo } from '../util.js'
import './legendas.css'

export function Grade({ grade, caminho = [], passo = null, heat = null, tam, duracao = 0 }) {
  const [ampliado, setAmpliado] = useState(false)
  const L = grade.length
  const C = Math.max(...grade.map((r) => r.length))
  const s = tam || Math.max(10, Math.min(36, Math.floor(760 / C)))
  const pts = useMemo(() => caminho.map(lerRotulo).filter(Boolean), [caminho])
  const camadas = useMemo(() => [...new Set(pts.map((p) => p.chaves))], [pts])
  const segs = useMemo(() => {
    const grupos = camadas.map(() => [])
    const limite = passo == null ? pts.length - 1 : Math.min(Math.max(0, passo - (duracao > 0 ? 1 : 0)), pts.length - 1)
    for (let i = 1; i <= limite; i++) {
      const a = pts[i - 1], b = pts[i]
      grupos[camadas.indexOf(b.chaves)].push(`M${a.c * s + s / 2} ${a.l * s + s / 2}L${b.c * s + s / 2} ${b.l * s + s / 2}`)
    }
    return grupos.map((g) => g.join(''))
  }, [pts, camadas, passo, s, duracao])
  const atual = passo != null && pts.length ? pts[Math.min(passo, pts.length - 1)] : null
  const anterior = duracao > 0 && passo > 0 ? pts[Math.min(passo - 1, pts.length - 1)] : null
  const maxH = heat ? Math.max(...Object.values(heat)) : 1
  const casas = useMemo(() => {
    const formas = new Map()
    const textos = []
    grade.forEach((row, l) =>
          [...row].forEach((ch, c) => {
            const q = heat ? heat[`${l},${c}`] || 0 : 0
            let fill = corCasa(ch)
            if (heat && ch !== '#') fill = q ? `hsl(${190 - 170 * (q / maxH)} 65% ${72 - 32 * (q / maxH)}%)` : 'var(--floor)'
            if (!formas.has(fill)) formas.set(fill, [])
            formas.get(fill).push(`M${c * s} ${l * s}h${s}v${s}h-${s}z`)
            if ((s >= 18 && !heat && !'#.'.includes(ch)) || (heat && s >= 16 && q > 0)) {
              textos.push(<text key={`${l}-${c}`} x={c * s + s / 2} y={l * s + s / 2 + s * 0.15} textAnchor="middle" fontSize={s * 0.42} style={{ fill: 'var(--cell-ink)', fontFamily: 'var(--mono)' }}>{heat ? q : ch}</text>)
            }
          }),
        )
    return { fundos: [...formas].map(([fill, partes]) => <path key={fill} d={partes.join('')} fill={fill} stroke="var(--cell-line)" strokeWidth="0.5" />), textos }
  }, [grade, heat, s, maxH])

  return (
    <div className="grade-view">
      <div className="view-actions"><button className="btn zoom-btn" type="button" onClick={() => setAmpliado((v) => !v)} aria-pressed={ampliado}>{ampliado ? 'Ajustar à tela' : 'Ampliar mapa'}</button>{ampliado && <span>Role para explorar o mapa ampliado.</span>}</div>
    <div className={`grade-container${ampliado ? ' ampliado' : ''}`} tabIndex={ampliado ? 0 : undefined}>
      <svg className="grade-svg" width={C * s} height={L * s} viewBox={`0 0 ${C * s} ${L * s}`} role="img" aria-label="Mapa do labirinto">
        {casas.fundos}
        {segs.map((d, i) => d && <path key={i} d={d} fill="none" stroke={PALETA[i % PALETA.length]} strokeWidth={Math.max(2.5, s * 0.24)} strokeLinecap="round" strokeLinejoin="round" />)}
        {anterior && atual && <line key={passo} x1={anterior.c * s + s / 2} y1={anterior.l * s + s / 2} x2={atual.c * s + s / 2} y2={atual.l * s + s / 2} stroke={PALETA[camadas.indexOf(atual.chaves) % PALETA.length]} strokeWidth={Math.max(2.5, s * 0.24)} strokeLinecap="round" pathLength="1" className="trecho-animado" style={{ animationDuration: `${duracao}ms` }} />}
        <g className="map-labels">{casas.textos}</g>
        {atual && (
          <circle cx={atual.c * s + s / 2} cy={atual.l * s + s / 2} r={s * 0.34} fill="#172333" stroke="#fff" strokeWidth="3" style={{ transition: `cx ${duracao}ms linear, cy ${duracao}ms linear` }} />
        )}
      </svg>
    </div>
      {passo == null && camadas.length > 0 && <div className="legenda-percurso" aria-label="Cores do percurso"><strong>Percurso</strong>{camadas.map((chaves, i) => <span key={chaves || 'sem-chave'}><i style={{ background: PALETA[i % PALETA.length] }} />{chaves ? `Chaves: ${chaves}` : 'Sem chaves'}</span>)}</div>}
    </div>
  )
}

export function LegendaCasas() {
  const grupos = [
    ['Mapa', [['Parede', '#'], ['Chão · custo 1', '.'], ['Início', 'S'], ['Saída', 'G']]],
    ['Terreno', [['Lama · custo 3', ','], ['Água · custo 5', '~'], ['Esteira', '>']]],
    ['Elementos', [['Chave', 'a'], ['Porta', 'A'], ['Bônus · −4', '+'], ['Fonte · −2', '*']]],
  ]
  return (
    <section className="map-key" aria-label="Legenda do mapa">
      <h3 className="map-key__title">Como ler o mapa</h3>
      <div className="map-key__groups">{grupos.map(([titulo, itens]) => <div className="map-key__group" key={titulo}><h4>{titulo}</h4><ul>{itens.map(([nome, ch]) => <li key={nome}><span className="map-key__symbol" style={{ background: corCasa(ch) }} aria-hidden="true">{ch === '#' ? '' : ch}</span><span>{nome}</span></li>)}</ul></div>)}</div>
    </section>
  )
}
