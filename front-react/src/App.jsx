// [IA] Codex – capitalização de títulos, legendas e valores apresentados na interface.
// [IA] Claude Code – estrutura da página: cabeçalho, abas e conteúdo de cada aba
// [IA] Codex – revisão da identidade visual e navegação
// [IA] Claude Code – layout brutalista: sidebar preta com navegação numerada e masthead editorial por seção
import { Suspense, lazy, useEffect, useState } from 'react'
import { Labirinto } from './components/Labirinto.jsx'
import { Avd } from './components/Avd.jsx'
// [IA] Claude Code – aba com Cytoscape carregada sob demanda para não pesar as outras abas
const Parte1 = lazy(() => import('./components/Parte1.jsx').then((m) => ({ default: m.Parte1 })))
// [IA] Claude Code – aba da Parte 2 (R5/R6), também com Cytoscape
const Parte2 = lazy(() => import('./components/Parte2.jsx').then((m) => ({ default: m.Parte2 })))

// [id, nome, descrição curta na navegação, contexto no masthead, texto de abertura]
const ABAS = [
  ['labirinto', 'Labirinto', 'Explore os percursos', ['Parte 1', 'Grafo de estados'],
    'Mapas com chaves, portas, terrenos e esteiras. Escolha um algoritmo e siga o percurso casa a casa.'],
  ['parte1', 'Grafos e mapas', 'Figuras da Parte 1', ['Parte 1', 'Figuras'],
    'Percursos de menor custo, o grafo de estados em camadas, a árvore BFS e a multiplicidade de estados por casa.'],
  ['parte2', 'Rede de carteiras', 'Algoritmos · Parte 2', ['Parte 2', 'Elliptic++'],
    'BFS, DFS, Dijkstra e Bellman-Ford executados sobre a rede de transações entre carteiras Bitcoin.'],
  ['avd', 'Análise de dados', 'AVD · Parte 2', ['Parte 2', 'AVD'],
    'Gráficos exploratórios e explanatórios do recorte de carteiras do Elliptic++, como estão no notebook e no relatório.'],
]

function lerAba() {
  const h = window.location.hash.slice(1)
  return ABAS.some((a) => a[0] === h) ? h : 'labirinto'
}

const num = (i) => String(i + 1).padStart(2, '0')

export default function App() {
  const [aba, setAba] = useState(lerAba)
  useEffect(() => {
    const f = () => setAba(lerAba())
    window.addEventListener('hashchange', f)
    return () => window.removeEventListener('hashchange', f)
  }, [])

  const indice = ABAS.findIndex((a) => a[0] === aba)
  const [, nomeAtual, , contexto, abertura] = ABAS[indice]

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <svg className="brand-mark" viewBox="0 0 48 48" aria-hidden="true"><path d="M12 30 22 13l14 8-4 15-20-6 10-17 10 23M12 30l24-9" fill="none" strokeWidth="2" strokeLinejoin="miter"/><g><circle cx="12" cy="30" r="3"/><circle cx="22" cy="13" r="3"/><circle cx="36" cy="21" r="3"/><circle cx="32" cy="36" r="3"/></g></svg>
          <div><span className="brand-name">Grafos</span><span className="brand-kicker">Teoria e visualização</span></div>
        </div>
        <nav className="tabs" aria-label="Seções do projeto">
          <span className="nav-group">Seções</span>
          {ABAS.map(([id, nome, descricao], i) => (
            <button key={id} className="tab" aria-current={aba === id ? 'page' : undefined}
              onClick={() => { setAba(id); window.history.replaceState(null, '', `#${id}`) }}>
              <span className="tab-num" aria-hidden="true">{num(i)}</span>
              <span className="tab-copy"><span>{nome}</span><small>{descricao}</small></span>
            </button>
          ))}
        </nav>
        <div className="sidebar-foot"><strong>Teoria dos grafos + AVD</strong>Projeto final · 2026.2</div>
      </aside>
      <main className="conteudo">
        <header className="masthead">
          <div>
            <div className="masthead-meta"><span>{num(indice)} / {num(ABAS.length - 1)}</span>{contexto.map((c) => <span key={c}>{c}</span>)}</div>
            <h1>{nomeAtual}</h1>
            <p>{abertura}</p>
          </div>
          <div className="masthead-num" aria-hidden="true">{num(indice)}</div>
        </header>
        {aba === 'labirinto' && <Labirinto />}
        {aba === 'parte1' && <Suspense fallback={<p className="status" role="status">Carregando grafos…</p>}><Parte1 /></Suspense>}
        {aba === 'parte2' && <Suspense fallback={<p className="status" role="status">Carregando grafos…</p>}><Parte2 /></Suspense>}
        {aba === 'avd' && <Avd />}
      </main>
    </div>
  )
}
