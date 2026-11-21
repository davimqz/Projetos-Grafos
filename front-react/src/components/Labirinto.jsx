// [IA] Claude Code – labirinto interativo: escolha de mapa/algoritmo e animação passo a passo
// [IA] Codex – organização dos controles, navegação pelo percurso e apresentação
// [IA] Codex - indicação da pasta organizada de saída do HTML.
import { useEffect, useState } from 'react'
import { ALGORITMOS, MAPAS, NOME_ALG, fmtInt, lerRotulo } from '../util.js'
import { Grade, LegendaCasas } from './Grade.jsx'

const NOMES_MAPAS = {
  m01_terreno: 'M01 · Terreno',
  m02_uma_chave: 'M02 · Uma chave',
  m03_tres_chaves: 'M03 · Três chaves',
  m04_esteiras: 'M04 · Esteiras',
  m05_bonus: 'M05 · Bônus',
  m06_fonte: 'M06 · Fonte',
  m07_impossivel: 'M07 · Impossível',
  m08_grande: 'M08 · Grande',
  g01_tres_depositos: 'G01 · Três depósitos',
  g02_poco_lateral: 'G02 · Poço lateral',
}

export function Labirinto() {
  const nomes = Object.keys(MAPAS)
  const [mapa, setMapa] = useState(nomes.includes('m03_tres_chaves') ? 'm03_tres_chaves' : nomes[0])
  const [alg, setAlg] = useState('DIJKSTRA')
  const [passo, setPasso] = useState(0)
  const [tocando, setTocando] = useState(false)
  const [vel, setVel] = useState(5)
  const [gerando, setGerando] = useState(false)
  const [htmlGerado, setHtmlGerado] = useState(null)
  const [erroHtml, setErroHtml] = useState('')

  const M = MAPAS[mapa]
  const caminho = M.percursos[alg] || []
  const custos = (M.custos || {})[alg] || []
  const temCaminho = caminho.length > 0
  const fim = caminho.length - 1

  useEffect(() => { setPasso(0); setTocando(false); setHtmlGerado(null); setErroHtml('') }, [mapa, alg])
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

  async function gerarHtml(conjunto = false) {
    setGerando(true)
    setErroHtml('')
    setHtmlGerado(null)
    try {
      const resposta = await fetch(`/__grafos__/html/${conjunto ? 'conjunto' : mapa}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ algoritmo: alg }),
      })
      const dados = await resposta.json()
      if (!resposta.ok) throw new Error(dados.erro || 'Não foi possível gerar o HTML.')
      setHtmlGerado(dados)
    } catch (erro) {
      setErroHtml(erro.message || 'Não foi possível conectar ao gerador local.')
    } finally { setGerando(false) }
  }

  return (
    <section className="panel">
      <header>
        <span className="section-label">PARTE 1</span><h2>Labirinto interativo</h2>
        <p className="note">Escolha o mapa e o algoritmo e acompanhe o percurso passo a passo. A cor do caminho muda a cada chave coletada.</p>
      </header>
      <div className="lab">
        <div className="side">
          <div className="selecao">
          <label className="field">Mapa
            <select id="sel-mapa" value={mapa} disabled={gerando} onChange={(ev) => setMapa(ev.target.value)}>
              {nomes.map((n) => <option key={n} value={n}>{NOMES_MAPAS[n] || n}</option>)}
            </select>
          </label>
          <label className="field">Algoritmo
            <select id="sel-alg" value={alg} disabled={gerando} onChange={(ev) => setAlg(ev.target.value)}>
              {ALGORITMOS.map((a) => <option key={a} value={a}>{NOME_ALG[a]}</option>)}
            </select>
          </label>
          <p className={temCaminho ? 'status' : 'status alerta'}>{M.status[alg]}</p>
          </div>
          <div className="reproducao">
          <h3>Acompanhar percurso</h3>
          <div className="btns">
            <button className="btn" disabled={!temCaminho || passo === 0}
              onClick={() => { setTocando(false); setPasso((p) => Math.max(0, p - 1)) }}>Anterior</button>
            <button className="btn primary" disabled={!temCaminho}
              onClick={() => { if (passo >= fim) setPasso(0); setTocando(!tocando) }}>{rotuloBotao}</button>
            <button className="btn" disabled={!temCaminho || passo === fim}
              onClick={() => { setTocando(false); setPasso((p) => Math.min(fim, p + 1)) }}>Próximo</button>
          </div>
          <label className="field">Posição no percurso: {temCaminho ? `${passo} de ${fim}` : 'indisponível'}
            <input className="controle-faixa" type="range" min="0" max={Math.max(0, fim)} value={Math.min(passo, Math.max(0, fim))} disabled={!temCaminho} style={{ '--progresso': `${fim > 0 ? (passo / fim) * 100 : 0}%` }} onChange={(ev) => { setTocando(false); setPasso(Number(ev.target.value)) }} />
          </label>
          <label className="field">Velocidade: {vel} passos/s
            <input className="controle-faixa" id="vel" type="range" min="1" max="20" value={vel} style={{ '--progresso': `${((vel - 1) / 19) * 100}%` }} onChange={(ev) => setVel(Number(ev.target.value))} />
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
        </div>
        <div className="mapa-area" style={{ display: 'flex', flexDirection: 'column', gap: 10, minWidth: 0 }}>
          <Grade grade={M.grade} caminho={caminho} passo={temCaminho ? passo : null} duracao={tocando && passo > 0 ? 1000 / vel : 0} />
          <div className="path-legend"><span><i className="current-marker" /> posição atual</span><span><i className="path-marker" /> caminho percorrido</span></div>
          <LegendaCasas />
        </div>
      </div>
      <div className="exportar-html"><button type="button" className="btn" onClick={() => gerarHtml(false)} disabled={gerando}>Gerar HTML deste mapa</button><button type="button" className="btn" onClick={() => gerarHtml(true)} disabled={gerando}>Gerar HTML conjunto</button><span className="note">O conjunto reúne todos os mapas disponíveis; os arquivos são salvos em out/parte1/html.</span>{gerando && <p role="status">Gerando HTML…</p>}{htmlGerado && <p role="status">Gerado: <code>{htmlGerado.arquivo}</code> · <a href={htmlGerado.url} target="_blank" rel="noreferrer">Abrir HTML</a></p>}{erroHtml && <p role="alert">{erroHtml}</p>}</div>
    </section>
  )
}
