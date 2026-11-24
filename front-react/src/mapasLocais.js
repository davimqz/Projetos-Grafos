// [IA] Codex – armazenamento dos resultados dos mapas adicionados neste navegador.
import { ALGORITMOS } from './util.js'

const CHAVE = 'grafos.labirintos.v1'

export function lerMapasLocais() {
  try {
    const mapas = JSON.parse(localStorage.getItem(CHAVE) || '{}')
    if (!mapas || typeof mapas !== 'object' || Array.isArray(mapas)) return {}
    return Object.fromEntries(Object.entries(mapas).filter(([id, mapa]) =>
      id.startsWith('__local_') && mapa && typeof mapa.nome === 'string' &&
      Array.isArray(mapa.grade) && mapa.grade.length > 0 && mapa.grade.every((linha) => typeof linha === 'string') &&
      ALGORITMOS.every((alg) => Array.isArray(mapa.percursos?.[alg]) && typeof mapa.status?.[alg] === 'string')))
  } catch { return {} }
}

export function salvarMapasLocais(mapas) {
  try { localStorage.setItem(CHAVE, JSON.stringify(mapas)) }
  catch { throw new Error('Não foi possível atualizar os labirintos neste navegador. Verifique o espaço e a permissão de armazenamento.') }
}
