// [IA] Claude Code – estrutura da página: cabeçalho, abas e conteúdo de cada aba
// [IA] Codex – revisão da identidade visual e navegação
import { useEffect, useState } from 'react'
import { Labirinto } from './components/Labirinto.jsx'
import { Parte1 } from './components/Parte1.jsx'
import { Avd } from './components/Avd.jsx'

const ABAS = [['labirinto', 'Labirinto', 'Explore os percursos'], ['parte1', 'Grafos e mapas', 'Figuras da Parte 1'], ['avd', 'Análise de dados', 'AVD · Parte 2']]

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


  return (
    <>
      <div className="topo">
        <div className="wrap topo-inner">
          <div className="brand"><svg className="brand-mark" viewBox="0 0 48 48" aria-hidden="true"><path d="M12 30 22 13l14 8-4 15-20-6 10-17 10 23M12 30l24-9" fill="none" stroke="white" strokeWidth="2" strokeLinejoin="round"/><g fill="white"><circle cx="12" cy="30" r="3"/><circle cx="22" cy="13" r="3"/><circle cx="36" cy="21" r="3"/><circle cx="32" cy="36" r="3"/></g></svg><div><h1>Grafos</h1><span className="brand-kicker">Teoria e visualização</span></div></div>
          <nav className="tabs" aria-label="Seções do projeto">
            {ABAS.map(([id, nome, descricao]) => (
              <button key={id} className="tab" aria-current={aba === id ? 'page' : undefined}
                onClick={() => { setAba(id); window.history.replaceState(null, '', `#${id}`) }}><span className="tab-node" aria-hidden="true"/><span className="tab-copy"><span>{nome}</span><small>{descricao}</small></span></button>
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
