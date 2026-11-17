// [IA] Claude Code – os 4 gráficos exploratórios da AVD (tipos escolhidos pelo Vagner no notebook)
import { DADOS_AVD as A, NOME_CLASSE, ORDEM, corClasse, fmt, fmtInt } from '../util.js'

function Barras({ dados, rotulo, yLabel, fmtV, fmtEixo }) {
  const W = 520
  const H = 290
  const m = { l: 64, r: 16, t: 22, b: 42 }
  const max = Math.max(...dados.map((d) => d.v)) * 1.2 || 1
  const bw = (W - m.l - m.r) / dados.length
  return (
    <div className="scroll">
      <svg className="fit" width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={rotulo}>
        {[0, 0.25, 0.5, 0.75, 1].map((t, i) => {
          const y = H - m.b - t * (H - m.t - m.b)
          return (
            <g key={i}>
              <line x1={m.l} x2={W - m.r} y1={y} y2={y} stroke="var(--line)" />
              <text x={m.l - 8} y={y + 4} textAnchor="end" fontSize="11" className="muted">{fmtEixo(t * max)}</text>
            </g>
          )
        })}
        {dados.map((d, i) => {
          const h = (d.v / max) * (H - m.t - m.b)
          const x = m.l + i * bw + bw * 0.2
          return (
            <g key={d.k}>
              <rect x={x} y={H - m.b - h} width={bw * 0.6} height={Math.max(h, 0)} fill={corClasse(d.k)} rx="4" />
              <text x={x + bw * 0.3} y={H - m.b - h - 8} textAnchor="middle" fontSize="12" fontWeight="600">{fmtV(d.v)}</text>
              <text x={x + bw * 0.3} y={H - m.b + 18} textAnchor="middle" fontSize="12">{NOME_CLASSE[d.k]}</text>
            </g>
          )
        })}
        <text x="14" y={H / 2} transform={`rotate(-90 14 ${H / 2})`} textAnchor="middle" fontSize="11" className="muted">{yLabel}</text>
      </svg>
    </div>
  )
}

function LegendaClasses() {
  return (
    <div className="legend">
      {ORDEM.map((c) => <span key={c}><i style={{ background: corClasse(c) }}></i>{NOME_CLASSE[c]}</span>)}
    </div>
  )
}

const SINAIS = ['negativo', 'zero', 'positivo']
const COR_SINAL = { negativo: 'var(--neg)', zero: 'var(--zero)', positivo: 'var(--pos)' }

export function Avd() {
  const total = ORDEM.reduce((s, c) => s + A.contagem[c], 0)
  const maxS = Math.max(...ORDEM.flatMap((c) => SINAIS.map((s) => A.sinal_peso[c][s]))) * 1.08
  return (
    <div className="grid">
      <section className="panel">
        <header><h2>1. Número de carteiras por classe</h2><p className="note">Recorte de {fmtInt(total)} carteiras do Elliptic++.</p></header>
        <Barras rotulo="Carteiras por classe" yLabel="Número de carteiras" dados={ORDEM.map((k) => ({ k, v: A.contagem[k] }))} fmtV={fmtInt} fmtEixo={fmtInt} />
        <LegendaClasses />
      </section>

      <section className="panel">
        <header><h2>2. Mediana do BTC total recebido por classe</h2><p className="note">Valor típico recebido por carteira, em BTC.</p></header>
        <Barras rotulo="Mediana do BTC recebido" yLabel="Mediana do BTC recebido" dados={ORDEM.map((k) => ({ k, v: A.mediana_recebido[k] }))}
          fmtV={(v) => fmt(v, 4)} fmtEixo={(v) => fmt(v, 3)} />
        <LegendaClasses />
      </section>

      <section className="panel">
        <header><h2>3. Para qual classe vão as arestas de cada classe</h2><p className="note">Cada linha soma 100%: proporção das arestas que saem da classe de origem.</p></header>
        <div className="scroll">
          <svg className="fit" width="520" height="300" viewBox="0 0 520 300" role="img" aria-label="Origem por destino">
            {ORDEM.map((o, i) => ORDEM.map((d, j) => {
              const v = A.origem_destino[o][d]
              return (
                <g key={o + d}>
                  <rect x={130 + j * 122} y={34 + i * 78} width="118" height="74" fill={`rgba(23,107,87,${0.1 + 0.85 * v})`} rx="6" />
                  <text x={189 + j * 122} y={76 + i * 78} textAnchor="middle" fontSize="15" fontWeight="600" style={{ fill: v > 0.5 ? '#ffffff' : 'var(--ink)' }}>{fmt(100 * v)}%</text>
                </g>
              )
            }))}
            {ORDEM.map((o, i) => <text key={`r${o}`} x="120" y={76 + i * 78} textAnchor="end" fontSize="12">{NOME_CLASSE[o]}</text>)}
            {ORDEM.map((d, j) => <text key={`c${d}`} x={189 + j * 122} y="24" textAnchor="middle" fontSize="12">{NOME_CLASSE[d]}</text>)}
            <text x="312" y="292" textAnchor="middle" fontSize="11" className="muted">Classe do destino</text>
            <text x="14" y="150" transform="rotate(-90 14 150)" textAnchor="middle" fontSize="11" className="muted">Classe da origem</text>
          </svg>
        </div>
      </section>

      <section className="panel">
        <header><h2>4. Sinal do peso das arestas, pela classe do destino</h2><p className="note">Número de arestas com peso negativo, zero ou positivo que chegam em cada classe.</p></header>
        <div className="scroll">
          <svg className="fit" width="520" height="290" viewBox="0 0 520 290" role="img" aria-label="Sinal do peso">
            {[0, 0.25, 0.5, 0.75, 1].map((t, i) => {
              const y = 248 - t * 220
              return (
                <g key={i}>
                  <line x1="64" x2="504" y1={y} y2={y} stroke="var(--line)" />
                  <text x="56" y={y + 4} textAnchor="end" fontSize="11" className="muted">{fmtInt(t * maxS)}</text>
                </g>
              )
            })}
            {ORDEM.map((c, i) => SINAIS.map((s, j) => {
              const v = A.sinal_peso[c][s]
              const h = (v / maxS) * 220
              const x = 80 + i * 146 + j * 40
              return (
                <g key={c + s}>
                  <rect x={x} y={248 - h} width="36" height={h} fill={COR_SINAL[s]} rx="3" />
                  <text x={x + 18} y={244 - h} textAnchor="middle" fontSize="10" className="muted">{fmtInt(v)}</text>
                </g>
              )
            }))}
            {ORDEM.map((c, i) => <text key={`l${c}`} x={138 + i * 146} y="268" textAnchor="middle" fontSize="12">{NOME_CLASSE[c]}</text>)}
            <text x="14" y="140" transform="rotate(-90 14 140)" textAnchor="middle" fontSize="11" className="muted">Número de arestas</text>
          </svg>
        </div>
        <div className="legend">
          {SINAIS.map((s) => <span key={s}><i style={{ background: COR_SINAL[s] }}></i>peso {s}</span>)}
        </div>
      </section>
    </div>
  )
}
