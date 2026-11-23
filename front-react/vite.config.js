// [IA] Claude Code – configuração do Vite para o projeto React
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { spawn } from 'node:child_process'
import { existsSync, readFile } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

// [IA] Codex – geração local pelo mesmo Python que produz os arquivos em out.
// [IA] Codex - leitura e identificação dos HTML na nova subpasta de saída.
const raiz = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const pythonLocal = process.platform === 'win32' ? join(raiz, '.venv', 'Scripts', 'python.exe') : join(raiz, '.venv', 'bin', 'python')
const python = existsSync(pythonLocal) ? pythonLocal : (process.platform === 'win32' ? 'python' : 'python3')
const prefixo = '/__grafos__/html/'
const nomeValido = (nome) => /^[a-z0-9_]+$/.test(nome)
const algoritmos = new Set(['BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD'])

function gerarHtmlLocal() {
  function instalar(server) {
    server.middlewares.use((req, res, next) => {
      const caminho = new URL(req.url, 'http://localhost').pathname
      // [IA] Codex – recebe o conteúdo do mapa e usa a validação Python do projeto.
      if (caminho === '/__grafos__/mapa') {
        const responder = (status, mensagem) => { if (!res.writableEnded) { res.statusCode = status; res.setHeader('Content-Type', 'application/json; charset=utf-8'); res.end(JSON.stringify({ erro: mensagem })) } }
        if (req.method !== 'POST') return responder(405, 'Método não permitido.')
        if (!req.headers.origin || req.headers.origin !== `http://${req.headers.host}` || !(req.headers['content-type'] || '').startsWith('text/plain')) return responder(403, 'Origem não autorizada.')
        let partes = [], tamanho = 0, excedeu = false
        req.on('data', (parte) => { tamanho += parte.length; if (tamanho > 16384) excedeu = true; else partes.push(parte) })
        req.on('end', () => {
          if (excedeu) return responder(413, 'O arquivo deve ter no máximo 16 KiB.')
          const processo = spawn(python, ['-X', 'utf8', '-m', 'scripts.mapa_front'], { cwd: raiz, windowsHide: true, env: { ...process.env, PYTHONIOENCODING: 'utf-8' } })
          let saida = '', erro = '', expirou = false
          const limite = setTimeout(() => { expirou = true; processo.kill() }, 30000)
          processo.stdout.setEncoding('utf8'); processo.stderr.setEncoding('utf8')
          processo.stdout.on('data', (p) => { saida += p })
          processo.stderr.on('data', (p) => { erro += p.slice(0, 4000) })
          processo.on('error', () => { clearTimeout(limite); responder(500, 'Não foi possível iniciar o Python.') })
          processo.on('close', (codigo) => {
            clearTimeout(limite)
            if (expirou) return responder(408, 'O cálculo excedeu 30 segundos; tente um mapa menor.')
            if (codigo !== 0) return responder(400, erro.trim() || 'Não foi possível processar o mapa.')
            res.setHeader('Content-Type', 'application/json; charset=utf-8'); res.end(saida)
          })
          processo.stdin.on('error', () => {})
          processo.stdin.end(Buffer.concat(partes))
        })
        return
      }
      if (!caminho.startsWith(prefixo)) return next()
      const nome = caminho.slice(prefixo.length)
      const responder = (status, mensagem) => { res.statusCode = status; res.setHeader('Content-Type', 'application/json; charset=utf-8'); res.end(JSON.stringify({ erro: mensagem })) }
      if (!nomeValido(nome)) return responder(400, 'Mapa inválido.')
      const arquivo = nome === 'conjunto' ? 'labirinto_interativo.html' : `labirinto_${nome}.html`
      if (req.method === 'GET') {
        return readFile(join(raiz, 'out', 'parte1', 'html', arquivo), (erro, html) => {
          if (erro) return responder(404, 'Gere o HTML antes de abri-lo.')
          res.setHeader('Content-Type', 'text/html; charset=utf-8'); res.setHeader('Cache-Control', 'no-store'); res.end(html)
        })
      }
      if (req.method !== 'POST') return responder(405, 'Método não permitido.')
      if (!req.headers.origin || req.headers.origin !== `http://${req.headers.host}` || !(req.headers['content-type'] || '').startsWith('application/json')) return responder(403, 'Origem não autorizada.')
      let corpo = ''
      req.on('data', (parte) => { corpo += parte; if (corpo.length > 2048) req.destroy() })
      req.on('end', () => {
        let algoritmo
        try { algoritmo = JSON.parse(corpo).algoritmo } catch { return responder(400, 'Dados inválidos.') }
        if (!algoritmos.has(algoritmo)) return responder(400, 'Algoritmo inválido.')
        const processo = spawn(python, ['-m', 'scripts.gerar_html_front', nome, algoritmo], { cwd: raiz, windowsHide: true })
        let erro = ''
        processo.stderr.on('data', (parte) => { erro += parte.toString().slice(0, 4000) })
        processo.on('error', () => responder(500, 'Não foi possível iniciar o Python. Confira o ambiente do projeto.'))
        processo.on('close', (codigo) => {
          if (res.writableEnded) return
          if (codigo !== 0) return responder(500, erro.trim() || 'Não foi possível gerar o HTML.')
          res.setHeader('Content-Type', 'application/json; charset=utf-8')
          res.end(JSON.stringify({ arquivo: `out/parte1/html/${arquivo}`, url: `${prefixo}${nome}` }))
        })
      })
    })
  }
  return { name: 'gerar-html-local', configureServer: instalar, configurePreviewServer: instalar }
}

export default defineConfig({
  plugins: [react(), gerarHtmlLocal()],
  base: './',
})
