// [IA] Claude Code – funções auxiliares de formatação e leitura dos rótulos de estado
// [IA] Codex – ajuste da paleta dos percursos
import dados from './dados.json'

export const MAPAS = dados.parte1.mapas
export const ALGORITMOS = ['BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD']
export const NOME_ALG = { BFS: 'BFS', DFS: 'DFS', DIJKSTRA: 'Dijkstra', BELLMAN_FORD: 'Bellman-Ford' }
export const NOME_CLASSE = { ilicito: 'ilícito', desconhecido: 'desconhecido', licito: 'lícito' }
// [IA] Codex – rótulos legíveis para códigos de status, sem alterar os dados de origem.
export const NOME_STATUS = { CICLO_NEGATIVO: 'Ciclo negativo', SEM_SOLUCAO: 'Sem solução', RECUSA: 'Recusa' }
// [IA] Codex – inicial maiúscula preservando a grafia de siglas e nomes no restante do texto.
export const capitalizarInicial = (texto) => texto.charAt(0).toLocaleUpperCase('pt-BR') + texto.slice(1)
export const PALETA = ['#2463eb', '#d04a36', '#a46300', '#00816d', '#8657ac', '#bd4c7d', '#537d19', '#5b6776']

export const corClasse = (c) => `var(--${c})`
export const fmt = (v, d = 1) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d })
export const fmtInt = (v) => Math.round(v).toLocaleString('pt-BR')

// Rótulo de estado no formato do enunciado: (linha,coluna)|chaves|{bônus}
export function lerRotulo(rotulo) {
  const m = /^\((\d+),(\d+)\)\|([^|]*)\|\{([^}]*)\}$/.exec(rotulo)
  if (!m) return null
  return {
    l: Number(m[1]),
    c: Number(m[2]),
    chaves: m[3] === '-' ? '' : m[3],
    bonus: m[4] ? m[4].split(',').filter(Boolean) : [],
  }
}

export function corCasa(ch) {
  if (ch === '#') return 'var(--wall)'
  if (ch === 'S') return 'var(--start)'
  if (ch === 'G') return 'var(--goal)'
  if (ch === ',') return 'var(--mud)'
  if (ch === '~') return 'var(--water)'
  if (/[a-d]/.test(ch)) return 'var(--key)'
  if (/[A-D]/.test(ch)) return 'var(--door)'
  if ('<>^v'.includes(ch)) return 'var(--belt)'
  if (ch === '+') return 'var(--bonus)'
  if (ch === '*') return 'var(--fonte)'
  return 'var(--floor)'
}
