// [IA] Codex – capitalização de títulos, legendas e valores apresentados na interface.
// [IA] Claude Code – aba da AVD: mostra as figuras oficiais do Vagner (out/parte2/avd/) com os textos das seções
// 6.4 e 6.6 do relatório, lidos direto dos arquivos no build. Tipo de gráfico, cores e análise são do Vagner;
// aqui nada é redesenhado nem escrito, só exibido, então a aba acompanha o notebook e o relatório.
import { capitalizarInicial } from '../util.js'
import relatorio from '../../../docs/relatorio/RELATORIO.md?raw'

const FIGURAS = import.meta.glob('../../../out/parte2/avd/*.png', { eager: true, query: '?url', import: 'default' })
const figura = (caminho) => FIGURAS[`../../../out/parte2/avd/${caminho.split('/').pop()}`]

/* Trecho do relatório entre um título "### ..." e o próximo título do mesmo nível (ou a linha ---). */
function secao(inicio) {
  const linhas = relatorio.replace(/\r/g, '').split('\n')
  const i = linhas.findIndex((l) => l.startsWith(inicio))
  if (i < 0) return []
  const fim = linhas.findIndex((l, j) => j > i && (l.startsWith('### ') || l.startsWith('## ') || l.trim() === '---'))
  return linhas.slice(i + 1, fim < 0 ? undefined : fim)
}

/* Cada "#### Título" vira um bloco com a imagem e os parágrafos que vêm depois dela. */
function blocos(linhas) {
  const lista = []
  for (const linha of linhas) {
    if (linha.startsWith('#### ')) { lista.push({ titulo: linha.slice(5).trim(), paragrafos: [] }); continue }
    const atual = lista.at(-1)
    if (!atual || !linha.trim()) continue
    const img = /^!\[(.*)\]\((.*)\)\s*$/.exec(linha.trim())
    if (img) { atual.alt = img[1]; atual.src = figura(img[2]); continue }
    atual.paragrafos.push(linha.trim())
  }
  return lista
}

/* Negrito do markdown (**texto**) sem interpretar HTML. */
function Texto({ children }) {
  return children.split(/(\*\*[^*]+\*\*)/).map((parte, i) => (
    parte.startsWith('**') && parte.endsWith('**') ? <strong key={i}>{parte.slice(2, -2)}</strong> : parte
  ))
}

function Figura({ titulo, alt, src, paragrafos }) {
  const [rotulo, ...resto] = titulo.split(':')
  return (
    <section className="panel avd-figura">
      <header>
        <span className="section-label">{rotulo}</span>
        <h2>{capitalizarInicial(resto.join(':').trim() || titulo)}</h2>
      </header>
      {src ? <img className="avd-img" src={src} alt={alt || titulo} loading="lazy" /> : <p className="status alerta">Figura não encontrada em out/parte2/avd/.</p>}
      <div className="avd-texto">{paragrafos.map((p, i) => <p key={i}><Texto>{p}</Texto></p>)}</div>
    </section>
  )
}

export function Avd() {
  const exploratorias = blocos(secao('### 6.4'))
  const explanatorias = blocos(secao('### 6.6'))
  return (
    <div className="figuras">
      <p className="note">Figuras geradas pelo notebook <code>notebooks/avd/01_exploratoria.ipynb</code>, com os textos das seções 6.4 e 6.6 do relatório.</p>
      <h2 className="avd-grupo">Exploratórias</h2>
      <div className="grid avd-grade">{exploratorias.map((b) => <Figura key={b.titulo} {...b} />)}</div>
      <h2 className="avd-grupo">Explanatórias</h2>
      <div className="figuras">{explanatorias.map((b) => <Figura key={b.titulo} {...b} />)}</div>
    </div>
  )
}
