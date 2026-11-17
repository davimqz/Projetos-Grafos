// [IA] Claude Code – labirinto interativo: escolha de mapa/algoritmo e animação passo a passo
import { useEffect, useState } from 'react'
import { ALGORITMOS, MAPAS, NOME_ALG, fmtInt, lerRotulo } from '../util.js'
import { Grade, LegendaCasas } from './Grade.jsx'

export function Labirinto() {
  const nomes = Object.keys(MAPAS)
  const [mapa, setMapa] = useState(nomes.includes('m03_tres_chaves') ? 'm03_tres_chaves' : nomes[0])
  const [alg, setAlg] = useState('DIJKSTRA')
  const [passo, setPasso] = useState(0)
  const [tocando, setTocando] = useState(false)
  const [vel, setVel] = useState(5)

  const M = MAPAS[mapa]
  const caminho = M.percursos[alg] || []
  const custos = (M.custos || {})[alg] || []
  const temCaminho = caminho.length > 0
  const fim = caminho.length - 1

  useEffect(() => { setPasso(0); setTocando(false) }, [mapa, alg])
  useEffect(() => {
    if (!tocando) return undefined
    const t = setInterval(() => {
      setPasso((p) => {
        if (p >= fim) { setTocando(false); return p }
        return p + 1
      })
    }, 1000 / vel)
    return () => clearInterval(t)
  }, [tocando, vel, fim])

  const e = temCaminho ? lerRotulo(caminho[Math.min(passo, fim)]) : null
  const rotuloBotao = tocando ? 'Pausar' : passo >= fim && passo > 0 ? 'Recomeçar' : 'Animar'

  return (
    <section className="panel">
      <header>
        <h2>Labirinto interativo</h2>
        <p className="note">Escolha o mapa e o algoritmo e acompanhe o percurso passo a passo. A cor do caminho muda a cada chave coletada.</p>
      </header>
      <div className="lab">
        <div className="side">
          <label className="field">Mapa
            <select id="sel-mapa" value={mapa} onChange={(ev) => setMapa(ev.target.value)}>
              {nomes.map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
          </label>
          <label className="field">Algoritmo
            <select id="sel-alg" value={alg} onChange={(ev) => setAlg(ev.target.value)}>
              {ALGORITMOS.map((a) => <option key={a} value={a}>{NOME_ALG[a]}</option>)}
            </select>
          </label>
          <p className={temCaminho ? 'status' : 'status alerta'}>{M.status[alg]}</p>
          <div className="btns">
            <button className="btn" disabled={!temCaminho} aria-label="Passo anterior"
              onClick={() => { setTocando(false); setPasso((p) => Math.max(0, p - 1)) }}>◀</button>
            <button className="btn primary" disabled={!temCaminho}
              onClick={() => { if (passo >= fim) setPasso(0); setTocando(!tocando) }}>{rotuloBotao}</button>
            <button className="btn" disabled={!temCaminho} aria-label="Próximo passo"
              onClick={() => { setTocando(false); setPasso((p) => Math.min(fim, p + 1)) }}>▶</button>
          </div>
          <label className="field">Velocidade: {vel} passos/s
            <input id="vel" type="range" min="1" max="20" value={vel} onChange={(ev) => setVel(Number(ev.target.value))} />
          </label>
          {e && (
            <dl className="state">
              <div><dt>Passo</dt><dd>{passo} / {fim}</dd></div>
              <div><dt>Custo</dt><dd>{custos[passo] ?? '—'}</dd></div>
              <div><dt>Posição</dt><dd>({e.l}, {e.c})</dd></div>
              <div><dt>Chaves</dt><dd>{e.chaves || 'nenhuma'}</dd></div>
              <div className="wide"><dt>Bônus usados</dt><dd>{e.bonus.length ? e.bonus.join(', ') : 'nenhum'}</dd></div>
            </dl>
          )}
          <p className="note">{fmtInt(M.n_estados)} estados e {fmtInt(M.n_arcos)} arcos no grafo de estados.</p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, minWidth: 0 }}>
          <Grade grade={M.grade} caminho={caminho} passo={temCaminho ? passo : null} />
          <LegendaCasas />
        </div>
      </div>
    </section>
  )
}
