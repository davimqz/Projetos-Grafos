// [IA] Claude Code – tela da Parte 2 (pedidos R5/R6 da reunião de 19/11): fontes e pares com os resultados já
// calculados pelo código do grupo (parte2.json) e desenho do subgrafo de cada caso com a cor da classe da carteira
import { useMemo, useState } from 'react'
import P2 from '../parte2.json'
import { NOME_CLASSE, corClasse, fmt, fmtInt } from '../util.js'

const CASOS = [
  ['buscas', 'BFS e DFS', '3 fontes'],
  ['dijkstra', 'Dijkstra', '5 pares origem–destino'],
  ['bellman_ford', 'Bellman-Ford', '2 origens'],
]

const classe = (no) => P2.classe[no] || 'desconhecido'
const curto = (no) => (no.length > 12 ? `${no.slice(0, 6)}…${no.slice(-4)}` : no)
const fmtBtc = (v) => v.toLocaleString('pt-BR', { maximumFractionDigits: 4 })

function rotuloCaso(tipo, c) {
  if (tipo === 'dijkstra') return `${curto(c.origem)} → ${curto(c.destino)}`
  return `${curto(c.origem)} (${NOME_CLASSE[classe(c.origem)]})`
}

/* Posições: origem no centro e as demais carteiras em anéis pela profundidade no recorte.
   Cada anel segue a ordem angular dos predecessores, para os arcos não se cruzarem. */
function layoutRadial(nos, nivel, W, H, arcos = []) {
  const pai = {}
  arcos.forEach(([u, v]) => { if (!(v in pai)) pai[v] = u })
  const porNivel = {}
  nos.forEach((n) => { (porNivel[nivel[n] ?? 1] ||= []).push(n) })
  const niveis = Object.keys(porNivel).map(Number).sort((a, b) => a - b)
  const maxNivel = Math.max(...niveis, 1)
  const raioMax = Math.min(W, H) / 2 - 46
  const pos = {}
  const angulo = {}
  niveis.forEach((nv) => {
    let lista = porNivel[nv]
    if (nv > 1) lista = [...lista].sort((a, b) => (angulo[pai[a]] ?? 0) - (angulo[pai[b]] ?? 0))
    const r = nv === 0 ? 0 : raioMax * Math.sqrt(nv / maxNivel)
    lista.forEach((n, i) => {
      const a = (2 * Math.PI * i) / lista.length - Math.PI / 2
      angulo[n] = a
      pos[n] = [W / 2 + r * Math.cos(a), H / 2 + r * Math.sin(a)]
    })
  })
  return pos
}

/* Profundidade de cada nó numa lista de arcos pai → filho (árvore de predecessores já calculada). */
function profundidades(origem, arcos) {
  const pai = {}
  arcos.forEach(([u, v]) => { pai[v] = u })
  const prof = { [origem]: 0 }
  const medir = (n, guarda = 0) => {
    if (prof[n] !== undefined) return prof[n]
    if (!(n in pai) || guarda > arcos.length) return 1
    prof[n] = medir(pai[n], guarda + 1) + 1
    return prof[n]
  }
  arcos.forEach(([, v]) => medir(v))
  return prof
}

function Seta({ id }) {
  return (
    <marker id={id} viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 0 10 5 0 10z" fill="#9db4d6" />
    </marker>
  )
}

function aparar([x1, y1], [x2, y2], r) {
  const dx = x2 - x1
  const dy = y2 - y1
  const d = Math.hypot(dx, dy) || 1
  return [x1 + (dx / d) * r, y1 + (dy / d) * r, x2 - (dx / d) * r, y2 - (dy / d) * r]
}

function No({ no, x, y, destaque, rotulo, onFoco }) {
  const r = destaque ? 13 : 8
  return (
    <g onMouseEnter={() => onFoco?.(no)} onFocus={() => onFoco?.(no)} tabIndex={0} style={{ cursor: 'default' }}>
      <title>{`${no} · ${NOME_CLASSE[classe(no)]}`}</title>
      {destaque && <circle cx={x} cy={y} r={r + 5} fill="none" stroke="#ffffff" strokeWidth="2" />}
      <circle cx={x} cy={y} r={r} fill={corClasse(classe(no))} stroke="#0b192f" strokeWidth="1.5" />
      {rotulo && <text x={x} y={y + r + 15} textAnchor="middle" fontSize="11" fontWeight="600">{curto(no)}</text>}
    </g>
  )
}

function GrafoRecorte({ origem, nos, nivel, arcos, onFoco }) {
  const W = 620
  const H = 520
  const pos = useMemo(() => layoutRadial(nos, nivel, W, H, arcos), [nos, nivel, arcos])
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Subgrafo a partir de ${origem}`}>
      <defs><Seta id="seta-recorte" /></defs>
      {arcos.map(([u, v], i) => {
        if (!pos[u] || !pos[v]) return null
        const [x1, y1, x2, y2] = aparar(pos[u], pos[v], u === origem ? 15 : 10)
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#5d7aa3" strokeWidth="1.2" markerEnd="url(#seta-recorte)" />
      })}
      {nos.map((n) => <No key={n} no={n} x={pos[n][0]} y={pos[n][1]} destaque={n === origem} rotulo={n === origem} onFoco={onFoco} />)}
    </svg>
  )
}

function GrafoCaminho({ caminho, arcos, ciclo }) {
  const n = caminho.length
  const W = Math.max(620, 150 * n)
  const H = ciclo ? 300 : 220
  const pos = {}
  if (ciclo) {
    // Ciclo [v0, v1, ..., v0]: carteiras distintas num círculo, a partir da esquerda.
    const unicos = caminho.slice(0, -1)
    const raio = unicos.length === 2 ? 170 : Math.min(W, H) / 2 - 50
    unicos.forEach((no, i) => {
      const a = Math.PI + (2 * Math.PI * i) / unicos.length
      pos[no] = [W / 2 + raio * Math.cos(a), H / 2 + raio * Math.sin(a)]
    })
  } else {
    caminho.forEach((no, i) => { pos[no] = [70 + (i * (W - 140)) / Math.max(n - 1, 1), H / 2] })
  }
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={ciclo ? 'Ciclo negativo' : 'Caminho mínimo'}>
      <defs><Seta id="seta-caminho" /></defs>
      {arcos.map(([u, v, w], i) => {
        const [x1, y1, x2, y2] = aparar(pos[u], pos[v], 18)
        // Com 2 carteiras os arcos de ida e volta se sobrepõem; a curva os separa
        const curva = ciclo && arcos.length === 2 ? (i === 0 ? -80 : 80) : 0
        const mx = (x1 + x2) / 2
        const my = (y1 + y2) / 2 + curva
        return (
          <g key={i}>
            <path d={`M${x1} ${y1} Q${mx} ${my} ${x2} ${y2}`} fill="none" stroke={w < 0 ? '#f0837a' : '#81acfa'} strokeWidth="2.5" markerEnd="url(#seta-caminho)" />
            <text x={mx} y={(y1 + y2) / 2 + curva / 2 - 8} textAnchor="middle" fontSize="12" fontWeight="700">{fmtBtc(w)}</text>
          </g>
        )
      })}
      {Object.entries(pos).map(([no, [x, y]], i) => (
        <No key={no} no={no} x={x} y={y} destaque={i === 0 || i === Object.keys(pos).length - 1} rotulo />
      ))}
    </svg>
  )
}

function Legenda() {
  return (
    <div className="chart-legend">
      <strong>Classe da carteira</strong>
      {['ilicito', 'licito', 'desconhecido'].map((c) => (
        <span key={c}><i style={{ background: corClasse(c) }} />{NOME_CLASSE[c]}</span>
      ))}
      <span><i style={{ background: 'transparent', borderColor: '#fff', borderRadius: '50%' }} />origem / extremos</span>
    </div>
  )
}

function Dados({ itens }) {
  return (
    <dl className="state">
      {itens.map(([k, v, largo]) => (
        <div key={k} className={largo ? 'wide' : undefined}><dt>{k}</dt><dd>{v}</dd></div>
      ))}
    </dl>
  )
}

function Busca({ c }) {
  const [foco, setFoco] = useState(null)
  const arcosDfs = c.dfs.contagem_arcos
  return (
    <div className="p2-corpo">
      <div className="mapa-area">
        <div className="grafo-frame"><GrafoRecorte origem={c.origem} nos={c.recorte.nos} nivel={c.recorte.nivel} arcos={c.recorte.arcos} onFoco={setFoco} /></div>
        <p className="note" style={{ marginTop: 10 }}>
          Recorte com a origem e {fmtInt(c.recorte.nos.length - 1)} das {fmtInt(c.tamanho_camadas[1] ?? 0)} carteiras da camada 1 da BFS
          {c.recorte.completo ? '.' : ' (o grafo alcançado inteiro não cabe na tela).'} Passe o mouse sobre um nó para ver o endereço.
        </p>
      </div>
      <aside className="reproducao">
        <h3>BFS a partir da origem</h3>
        <Dados itens={[
          ['Origem', `${curto(c.origem)} · ${NOME_CLASSE[classe(c.origem)]}`, true],
          ['Alcançadas', `${fmtInt(c.alcancados)} de ${fmtInt(c.total_nos)}`],
          ['Camadas', fmtInt(c.tamanho_camadas.length - 1)],
          ['Nó em foco', foco ? `${curto(foco)} · ${NOME_CLASSE[classe(foco)]}` : '—', true],
        ]} />
        <table className="p2-tabela">
          <caption>Carteiras por camada</caption>
          <thead><tr><th>Camada</th><th>Carteiras</th></tr></thead>
          <tbody>{c.tamanho_camadas.map((t, i) => <tr key={i}><th scope="row">{i}</th><td>{fmtInt(t)}</td></tr>)}</tbody>
        </table>
        <h3>DFS a partir da origem</h3>
        <Dados itens={[
          ['Árvore', fmtInt(arcosDfs.arvore)], ['Retorno', fmtInt(arcosDfs.retorno)],
          ['Avanço', fmtInt(arcosDfs.avanco)], ['Cruzamento', fmtInt(arcosDfs.cruzamento)],
          ['Ciclo alcançável', c.dfs.tem_ciclo ? 'sim (há arco de retorno)' : 'não', true],
        ]} />
      </aside>
    </div>
  )
}

function Dijkstra({ c }) {
  return (
    <div className="p2-corpo">
      <div className="mapa-area">
        <div className="grafo-frame"><GrafoCaminho caminho={c.caminho} arcos={c.arcos} /></div>
        <p className="note" style={{ marginTop: 10 }}>Peso de cada arco: valor em BTC transferido entre as carteiras (sempre ≥ 0, por isso o Dijkstra se aplica).</p>
      </div>
      <aside className="reproducao">
        <h3>Caminho mínimo</h3>
        <Dados itens={[
          ['Origem', `${curto(c.origem)} · ${NOME_CLASSE[classe(c.origem)]}`, true],
          ['Destino', `${curto(c.destino)} · ${NOME_CLASSE[classe(c.destino)]}`, true],
          ['Custo', `${fmtBtc(c.custo)} BTC`], ['Arcos', fmtInt(c.passos)],
        ]} />
        <ol className="p2-lista">{c.caminho.map((n) => <li key={n}><i style={{ background: corClasse(classe(n)) }} />{curto(n)}</li>)}</ol>
      </aside>
    </div>
  )
}

function BellmanFord({ c }) {
  if (c.tem_ciclo_negativo) {
    return (
      <div className="p2-corpo">
        <div className="mapa-area">
          <div className="grafo-frame"><GrafoCaminho caminho={c.ciclo} arcos={c.arcos} ciclo /></div>
          <p className="note" style={{ marginTop: 10 }}>Ciclo negativo alcançável a partir da origem: dar uma volta no ciclo soma custo negativo, então o caminho mínimo não é definido.</p>
        </div>
        <aside className="reproducao">
          <h3>Resultado</h3>
          <Dados itens={[
            ['Origem', `${curto(c.origem)} · ${NOME_CLASSE[classe(c.origem)]}`, true],
            ['Status', c.status], ['Custo do ciclo', fmtBtc(c.custo_ciclo)],
            ['Alcançadas', `${fmtInt(c.alcancados)} de ${fmtInt(c.total_nos)}`, true],
          ]} />
          <ol className="p2-lista">{c.ciclo.map((n, i) => <li key={i}><i style={{ background: corClasse(classe(n)) }} />{curto(n)}</li>)}</ol>
        </aside>
      </div>
    )
  }
  const prof = profundidades(c.origem, c.arcos)
  const nos = Object.keys(prof)
  const negativas = Object.entries(c.distancia).filter(([, d]) => d < 0).sort((a, b) => a[1] - b[1])
  return (
    <div className="p2-corpo">
      <div className="mapa-area">
        <div className="grafo-frame"><GrafoRecorte origem={c.origem} nos={nos} nivel={prof} arcos={c.arcos} /></div>
        <p className="note" style={{ marginTop: 10 }}>Árvore de caminhos mínimos devolvida pelo Bellman-Ford: cada carteira aparece ligada ao seu predecessor.</p>
      </div>
      <aside className="reproducao">
        <h3>Resultado</h3>
        <Dados itens={[
          ['Origem', `${curto(c.origem)} · ${NOME_CLASSE[classe(c.origem)]}`, true],
          ['Status', c.status], ['Alcançadas', fmtInt(c.alcancados)],
          ['Arcos negativos alcançáveis', fmtInt(c.arcos_negativos_alcancaveis), true],
        ]} />
        <table className="p2-tabela">
          <caption>Carteiras com distância negativa</caption>
          <thead><tr><th>Carteira</th><th>Distância</th></tr></thead>
          <tbody>{negativas.map(([n, d]) => <tr key={n}><th scope="row"><i style={{ background: corClasse(classe(n)) }} />{curto(n)}</th><td>{fmtBtc(d)}</td></tr>)}</tbody>
        </table>
      </aside>
    </div>
  )
}

function Tempos() {
  return (
    <section className="panel">
      <header>
        <span className="section-label">DESEMPENHO NO GRAFO COMPLETO</span>
        <h2>Tempo e memória por algoritmo</h2>
        <p className="note">Média de 5 execuções no recorte inteiro ({fmtInt(P2.tempos[0].nos)} carteiras e {fmtInt(P2.tempos[0].arestas)} arcos), do <code>parte2_report.json</code>.</p>
      </header>
      <div className="scroll">
        <table className="p2-tabela larga">
          <thead><tr><th>Algoritmo</th><th>Complexidade</th><th>Tempo médio (ms)</th><th>Latência mín–máx (ms)</th><th>Pico de memória (KB)</th><th>Status</th></tr></thead>
          <tbody>{P2.tempos.map((t) => (
            <tr key={t.algoritmo}>
              <th scope="row">{t.algoritmo}</th><td>{t.complexidade}</td><td>{fmt(t.tempo_medio_ms, 2)}</td>
              <td>{fmt(t.latencia_min_ms, 2)} – {fmt(t.latencia_max_ms, 2)}</td><td>{fmt(t.memoria_pico_kb, 1)}</td><td>{t.status}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </section>
  )
}

function casoInicial() {
  const p = new URLSearchParams(window.location.search)
  const tipo = CASOS.some(([id]) => id === p.get('p2')) ? p.get('p2') : 'buscas'
  return [tipo, Math.max(0, Math.min(Number(p.get('caso')) || 0, P2[tipo].length - 1))]
}

export function Parte2() {
  const [tipo, setTipo] = useState(() => casoInicial()[0])
  const [indice, setIndice] = useState(() => casoInicial()[1])
  const casos = P2[tipo]
  const caso = casos[Math.min(indice, casos.length - 1)]
  return (
    <div className="figuras">
      <section className="panel">
        <header>
          <span className="section-label">PARTE 2 · ELLIPTIC++</span>
          <h2>Os algoritmos na rede de carteiras</h2>
          <p className="note">Cada nó é uma carteira Bitcoin e cada arco liga quem enviou a quem recebeu. Os resultados são os mesmos do relatório,
            calculados pelos algoritmos do grupo e lidos de <code>parte2.json</code>.</p>
        </header>
        <div className="selecao">
          <label className="field">Algoritmo
            <select value={tipo} onChange={(e) => { setTipo(e.target.value); setIndice(0) }}>
              {CASOS.map(([id, nome, desc]) => <option key={id} value={id}>{nome} · {desc}</option>)}
            </select>
          </label>
          <label className="field">{tipo === 'dijkstra' ? 'Par origem → destino' : 'Carteira de origem'}
            <select value={indice} onChange={(e) => setIndice(Number(e.target.value))}>
              {casos.map((c, i) => <option key={i} value={i}>{rotuloCaso(tipo, c)}</option>)}
            </select>
          </label>
        </div>
        <Legenda />
        {tipo === 'buscas' && <Busca key={indice} c={caso} />}
        {tipo === 'dijkstra' && <Dijkstra c={caso} />}
        {tipo === 'bellman_ford' && <BellmanFord c={caso} />}
      </section>
      <Tempos />
    </div>
  )
}
