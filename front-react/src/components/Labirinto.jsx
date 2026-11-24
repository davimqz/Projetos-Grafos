// [IA] Claude Code – labirinto interativo: escolha de mapa/algoritmo e animação passo a passo
// [IA] Codex – organização dos controles, navegação pelo percurso e apresentação
// [IA] Codex - indicação da pasta organizada de saída do HTML.
import { useEffect, useState } from 'react'
import { ALGORITMOS, MAPAS, NOME_ALG } from '../util.js'
// [IA] Claude Code – ícones e estado de carregamento nos botões (design system brutalista)
import { Icone } from './Icone.jsx'
// [IA] Codex – inclusão por texto e coleção persistente de labirintos locais.
import { AdicionarLabirinto } from './AdicionarLabirinto.jsx'
import { PercursoLabirinto } from './PercursoLabirinto.jsx'
import { lerMapasLocais, salvarMapasLocais } from '../mapasLocais.js'

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

// [IA] Codex – inclusão por texto e geração de HTML dependem do Python local.
const COM_PYTHON = import.meta.env.VITE_SITE_ESTATICO !== '1'

export function Labirinto() {
  const nomes = Object.keys(MAPAS)
  const [mapa, setMapa] = useState(nomes.includes('m03_tres_chaves') ? 'm03_tres_chaves' : nomes[0])
  const [alg, setAlg] = useState('DIJKSTRA')
  const [gerando, setGerando] = useState(false)
  const [htmlGerado, setHtmlGerado] = useState(null)
  const [erroHtml, setErroHtml] = useState('')
  const [mapasAdicionados, setMapasAdicionados] = useState(lerMapasLocais)
  const [enviando, setEnviando] = useState(false)
  const [comparar, setComparar] = useState(false)

  const M = mapasAdicionados[mapa] || MAPAS[mapa]
  useEffect(() => { setHtmlGerado(null); setErroHtml('') }, [mapa, alg])

  // [IA] Codex – texto colado usa a validação e os quatro algoritmos existentes.
  async function adicionarMapa(texto, nome) {
    if (!texto.trim()) throw new Error('Cole o conteúdo do labirinto.')
    if (new TextEncoder().encode(texto).length > 16384) throw new Error('O conteúdo deve ter no máximo 16 KiB.')
    setEnviando(true)
    try {
      const resposta = await fetch('/__grafos__/mapa', { method: 'POST', headers: { 'Content-Type': 'text/plain; charset=utf-8' }, body: texto })
      const dados = await resposta.json()
      if (!resposta.ok) throw new Error(dados.erro || 'Não foi possível processar o mapa.')
      const id = `__local_${crypto.randomUUID()}`
      const novos = { ...mapasAdicionados, [id]: { ...dados, nome: nome || `Labirinto ${Object.keys(mapasAdicionados).length + 1}` } }
      salvarMapasLocais(novos)
      setMapasAdicionados(novos); setMapa(id)
    } finally { setEnviando(false) }
  }

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
      <div className="selecao">
          <label className="field">Mapa
            <select id="sel-mapa" value={mapa} disabled={gerando} onChange={(ev) => setMapa(ev.target.value)}>
              {nomes.map((n) => <option key={n} value={n}>{NOMES_MAPAS[n] || n}</option>)}
              {Object.entries(mapasAdicionados).map(([id, dados]) => <option key={id} value={id}>{dados.nome} · Adicionado</option>)}
            </select>
          </label>
          <label className="field">Algoritmo
            <select id="sel-alg" value={alg} disabled={gerando || comparar} onChange={(ev) => setAlg(ev.target.value)}>
              {ALGORITMOS.map((a) => <option key={a} value={a}>{NOME_ALG[a]}</option>)}
            </select>
          </label>
          <label className="check-comparar"><input type="checkbox" checked={comparar} onChange={(ev) => setComparar(ev.target.checked)} /> Comparar os quatro algoritmos</label>
          {COM_PYTHON && <AdicionarLabirinto adicionar={adicionarMapa} enviando={enviando} />}
          {enviando && <p className="status" role="status">Processando mapa…</p>}
      </div>
      <PercursoLabirinto key={`${mapa}-${comparar ? 'comparacao' : alg}`} M={M} alg={alg} comparacao={comparar} />
      {COM_PYTHON && <div className="exportar-html"><button type="button" className="btn primary" aria-busy={gerando} onClick={() => gerarHtml(false)} disabled={gerando || Boolean(mapasAdicionados[mapa])}>{!gerando && <Icone nome="baixar" />}Gerar HTML deste mapa</button><button type="button" className="btn" aria-busy={gerando} onClick={() => gerarHtml(true)} disabled={gerando}>{!gerando && <Icone nome="baixar" />}Gerar HTML conjunto</button><span className="note">O conjunto reúne os mapas do projeto; os arquivos são salvos em out/parte1/html.</span>{gerando && <p role="status">Gerando HTML…</p>}{htmlGerado && <p role="status">Gerado: <code>{htmlGerado.arquivo}</code> · <a href={htmlGerado.url} target="_blank" rel="noreferrer">Abrir HTML</a></p>}{erroHtml && <p role="alert">{erroHtml}</p>}</div>}
    </section>
  )
}
