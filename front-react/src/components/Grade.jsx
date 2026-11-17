// [IA] Claude Code – desenho da grade do labirinto, do percurso e do heatmap
import { PALETA, corCasa, lerRotulo } from '../util.js'

export function Grade({ grade, caminho = [], passo = null, heat = null, tam }) {
  const L = grade.length
  const C = Math.max(...grade.map((r) => r.length))
  const s = tam || Math.max(10, Math.min(36, Math.floor(760 / C)))
  const pts = caminho.map(lerRotulo).filter(Boolean)
  const camadas = [...new Set(pts.map((p) => p.chaves))]
  const segs = []
  for (let i = 1; i < pts.length; i++) segs.push([pts[i - 1], pts[i], camadas.indexOf(pts[i].chaves)])
  const atual = passo != null && pts.length ? pts[Math.min(passo, pts.length - 1)] : null
  const maxH = heat ? Math.max(...Object.values(heat)) : 1

  return (
    <div className="scroll">
      <svg width={C * s} height={L * s} viewBox={`0 0 ${C * s} ${L * s}`} role="img" aria-label="Mapa do labirinto">
        {grade.map((row, l) =>
          [...row].map((ch, c) => {
            const q = heat ? heat[`${l},${c}`] || 0 : 0
            let fill = corCasa(ch)
            if (heat && ch !== '#') fill = q ? `hsl(${190 - 170 * (q / maxH)} 65% ${72 - 32 * (q / maxH)}%)` : 'var(--floor)'
            return (
              <g key={`${l}-${c}`}>
                <rect x={c * s} y={l * s} width={s} height={s} fill={fill} stroke="var(--line)" strokeWidth="0.5" />
                {s >= 18 && !heat && !'#.'.includes(ch) && (
                  <text x={c * s + s / 2} y={l * s + s / 2 + s * 0.15} textAnchor="middle" fontSize={s * 0.42}
                    style={{ fill: 'var(--cell-ink)', fontFamily: 'var(--mono)' }}>{ch}</text>
                )}
                {heat && s >= 16 && q > 0 && (
                  <text x={c * s + s / 2} y={l * s + s / 2 + 4} textAnchor="middle" fontSize={s * 0.4} style={{ fill: 'var(--cell-ink)' }}>{q}</text>
                )}
              </g>
            )
          }),
        )}
        {segs.slice(0, passo == null ? segs.length : passo).map(([a, b, k], i) => (
          <line key={`s${i}`} x1={a.c * s + s / 2} y1={a.l * s + s / 2} x2={b.c * s + s / 2} y2={b.l * s + s / 2}
            stroke={PALETA[k % 8]} strokeWidth={Math.max(2.5, s * 0.24)} strokeLinecap="round" />
        ))}
        {atual && (
          <circle cx={atual.c * s + s / 2} cy={atual.l * s + s / 2} r={s * 0.36} fill="var(--accent)" stroke="var(--surface)" strokeWidth="2.5" />
        )}
      </svg>
    </div>
  )
}

export function LegendaCasas() {
  const itens = [['parede', '#'], ['chão (1)', '.'], ['início', 'S'], ['saída', 'G'], ['lama (3)', ','], ['água (5)', '~'],
    ['chave', 'a'], ['porta', 'A'], ['esteira', '>'], ['bônus (−4)', '+'], ['fonte (−2)', '*']]
  return (
    <div className="legend">
      {itens.map(([nome, ch]) => (
        <span key={nome}><i style={{ background: corCasa(ch) }}></i>{nome}</span>
      ))}
    </div>
  )
}
