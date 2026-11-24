// [IA] Codex – formulário para validar e adicionar o conteúdo de um TXT.
import { useState } from 'react'

export function AdicionarLabirinto({ adicionar, enviando }) {
  const [aberto, setAberto] = useState(false)
  const [nome, setNome] = useState('')
  const [texto, setTexto] = useState('')
  const [erro, setErro] = useState('')

  async function confirmar(evento) {
    evento.preventDefault()
    setErro('')
    try {
      await adicionar(texto, nome.trim())
      setAberto(false); setTexto(''); setNome('')
    } catch (falha) {
      setErro(falha.message || 'Não foi possível adicionar o labirinto.')
    }
  }

  return <div className="adicionar-labirinto">
    <button type="button" className="btn destaque" disabled={enviando} aria-expanded={aberto}
      aria-controls="novo-labirinto" onClick={() => { setAberto(!aberto); setErro('') }}>Adicionar labirinto</button>
    {aberto && <form id="novo-labirinto" className="novo-labirinto" onSubmit={confirmar} aria-busy={enviando}>
      <label className="field">Nome do labirinto (opcional)
        <input value={nome} onChange={(ev) => setNome(ev.target.value)} maxLength={80} disabled={enviando} />
      </label>
      <label className="field">Conteúdo do TXT
        <textarea autoFocus rows={8} value={texto} onChange={(ev) => setTexto(ev.target.value)}
          placeholder={'#####\n#S.G#\n#####'} spellCheck={false} autoCapitalize="off" autoCorrect="off"
          wrap="off" required disabled={enviando} aria-describedby="instrucoes-labirinto" />
      </label>
      <p id="instrucoes-labirinto" className="note">Cole o mapa completo, com linhas de mesma largura, um S e pelo menos um G.
        Limites: 16 KiB, 2.500 casas e 8 bônus. Os quatro algoritmos serão processados.</p>
      <div className="acoes-labirinto">
        <button type="submit" className="btn primary" disabled={enviando || !texto.trim()} aria-busy={enviando}>
          {enviando ? 'Processando…' : 'Validar e adicionar'}
        </button>
        <button type="button" className="btn" disabled={enviando} onClick={() => { setAberto(false); setErro('') }}>Cancelar</button>
      </div>
      {erro && <p className="status alerta" role="alert">{erro}</p>}
    </form>}
  </div>
}
