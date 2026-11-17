// [IA] Claude Code – estrutura da página: cabeçalho, abas e conteúdo de cada aba
import { useEffect, useState } from 'react'
import { DADOS_AVD, MAPAS, ORDEM, fmtInt } from './util.js'
import { Labirinto } from './components/Labirinto.jsx'
import { Parte1 } from './components/Parte1.jsx'
import { Avd } from './components/Avd.jsx'

const ABAS = [['labirinto', 'Labirinto'], ['parte1', 'Figuras da Parte 1'], ['avd', 'AVD · Parte 2']]

function lerAba() {
  const h = window.location.hash.slice(1)
  return ABAS.some((a) => a[0] === h) ? h : 'labirinto'
}

export default function App() {
  const [aba, setAba] = useState(lerAba)
  useEffect(() => {
    const f = () => setAba(lerAba())
    window.addEventListener('hashchange', f)
    return () => window.removeEventListener('hashchange', f)
  }, [])

  const carteiras = ORDEM.reduce((s, c) => s + DADOS_AVD.contagem[c], 0)

  return (
    <>
      <div className="topo">
        <div className="wrap">
          <h1>Grafos em React</h1>
          <div className="chips">
            <span className="chip">{Object.keys(MAPAS).length} mapas</span>
            <span className="chip">4 algoritmos</span>
            <span className="chip">{fmtInt(carteiras)} carteiras</span>
          </div>
          <nav className="tabs" role="tablist">
            {ABAS.map(([id, nome]) => (
              <button key={id} className="tab" role="tab" aria-selected={aba === id}
                onClick={() => { setAba(id); window.history.replaceState(null, '', `#${id}`) }}>{nome}</button>
            ))}
          </nav>
        </div>
      </div>
      <main className="wrap">
        {aba === 'labirinto' && <Labirinto />}
        {aba === 'parte1' && <Parte1 />}
        {aba === 'avd' && <Avd />}
      </main>
    </>
  )
}
