// [IA] Codex – capitalização de títulos, legendas e valores apresentados na interface.
// [IA] Codex – reprodução individual ou sincronizada dos quatro algoritmos.
import { useEffect, useState } from 'react'
import { ALGORITMOS, NOME_ALG, fmtInt, lerRotulo } from '../util.js'
import { Grade, LegendaCasas } from './Grade.jsx'
import { Icone } from './Icone.jsx'

export function PercursoLabirinto({ M, alg, comparacao = false }) {
  const [passo, setPasso] = useState(0)
  const [tocando, setTocando] = useState(false)
  const [vel, setVel] = useState(5)
  const caminho = M.percursos[alg] || []
  const custos = (M.custos || {})[alg] || []
  const fim = comparacao ? Math.max(...ALGORITMOS.map((nome) => (M.percursos[nome] || []).length - 1)) : caminho.length - 1
  const temCaminho = fim >= 0

  useEffect(() => { setPasso(0); setTocando(false) }, [M, alg])
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

  const rotuloBotao = tocando ? 'Pausar' : passo >= fim && passo > 0 ? 'Recomeçar' : 'Animar'

  return <section className={`percurso-labirinto${comparacao ? ' comparando' : ''}`} aria-label={comparacao ? 'Comparação dos quatro algoritmos' : `Percurso ${NOME_ALG[alg]}`}>
    {!comparacao && <p className={temCaminho ? 'status' : 'status alerta'}>{M.status[alg]}</p>}
    <div className="lab">
        <div className="mapa-area" style={{ display: 'flex', flexDirection: 'column', gap: 10, minWidth: 0 }}>
          {comparacao ? <div className="comparacao-algoritmos">
            {ALGORITMOS.map((nome) => {
              const percurso = M.percursos[nome] || []
              const atual = Math.min(passo, Math.max(0, percurso.length - 1))
              return <article key={nome} aria-label={`Percurso ${NOME_ALG[nome]}`}>
                <h3>{NOME_ALG[nome]}</h3>
                <p className={percurso.length ? 'status' : 'status alerta'}>{M.status[nome]}</p>
                <Grade grade={M.grade} caminho={percurso} passo={percurso.length ? atual : null}
                  duracao={tocando && passo > 0 && passo < percurso.length ? 1000 / vel : 0} />
                <EstadoPercurso caminho={percurso} custos={M.custos?.[nome] || []} passo={atual} />
              </article>
            })}
          </div> : <Grade grade={M.grade} caminho={caminho} passo={temCaminho ? passo : null} duracao={tocando && passo > 0 ? 1000 / vel : 0} />}
          <div className="path-legend"><span><i className="current-marker" /> Posição atual</span><span><i className="path-marker" /> Caminho percorrido</span></div>
          <LegendaCasas />
        </div>
        <div className="reproducao">
          <h3>Acompanhar percurso</h3>
          <div className="btns">
            <button className="btn" disabled={!temCaminho || passo === 0}
              onClick={() => { setTocando(false); setPasso((p) => Math.max(0, p - 1)) }}><Icone nome="anterior" />Anterior</button>
            <button className="btn primary" disabled={!temCaminho}
              onClick={() => { if (passo >= fim) setPasso(0); setTocando(!tocando) }}><Icone nome={tocando ? 'pause' : passo >= fim && passo > 0 ? 'reiniciar' : 'play'} />{rotuloBotao}</button>
            <button className="btn" disabled={!temCaminho || passo === fim}
              onClick={() => { setTocando(false); setPasso((p) => Math.min(fim, p + 1)) }}>Próximo<Icone nome="proximo" /></button>
          </div>
          <label className="field">Posição no percurso: {temCaminho ? `${passo} de ${fim}` : 'indisponível'}
            <input className="controle-faixa" type="range" min="0" max={Math.max(0, fim)} value={Math.min(passo, Math.max(0, fim))} disabled={!temCaminho} style={{ '--progresso': `${fim > 0 ? (passo / fim) * 100 : 0}%` }} onChange={(ev) => { setTocando(false); setPasso(Number(ev.target.value)) }} />
          </label>
          <label className="field">Velocidade: {vel} passos/s
            <input className="controle-faixa" type="range" min="1" max="20" value={vel} style={{ '--progresso': `${((vel - 1) / 19) * 100}%` }} onChange={(ev) => setVel(Number(ev.target.value))} />
          </label>
          {!comparacao && <EstadoPercurso caminho={caminho} custos={custos} passo={passo} />}
          <p className="note">{fmtInt(M.n_estados)} estados e {fmtInt(M.n_arcos)} arcos no grafo de estados.</p>
        </div>
    </div>
  </section>
}

// [IA] Codex – estado de cada percurso no passo compartilhado, limitado ao próprio fim.
function EstadoPercurso({ caminho, custos, passo }) {
  if (!caminho.length) return null
  passo = Math.min(passo, caminho.length - 1)
  const fim = caminho.length - 1
  const e = lerRotulo(caminho[passo])
  if (!e) return null
  return (
    <dl className="state">
      <div><dt>Passo</dt><dd>{passo} / {fim}</dd></div>
      <div><dt>Custo</dt><dd>{custos[passo] ?? '—'}</dd></div>
      <div><dt>Posição</dt><dd>({e.l}, {e.c})</dd></div>
      <div><dt>Chaves</dt><dd>{e.chaves || 'Nenhuma'}</dd></div>
      <div className="wide"><dt>Bônus usados</dt><dd>{e.bonus.length ? e.bonus.join(', ') : 'Nenhum'}</dd></div>
    </dl>
  )
}
