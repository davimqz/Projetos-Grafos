// [IA] Codex – exercita a reprodução do HTML sem depender de servidor ou navegador.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const vm = require('node:vm')

class Elemento {
  constructor(id = '') { this.id = id; this.children = []; this.listeners = {}; this.value = ''; this.checked = false; this.dataset = {}; this.style = { setProperty() {} }; this.classList = { toggle() {} }; this.attributes = {}; this.clientWidth = 800; this.offsetWidth = 500; this.offsetHeight = 250 }
  addEventListener(evento, fn) { this.listeners[evento] = fn }
  disparar(evento) { this.listeners[evento]?.({ target: this }) }
  add(opcao) { this.children.push(opcao); if (this.children.length === 1) this.value = opcao.value }
  appendChild(filho) { this.children.push(filho); return filho }
  append(...filhos) { this.children.push(...filhos) }
  replaceChildren(...filhos) { this.children = [...filhos]; if (this.id === 'algoritmo' || this.id === 'camadaSel') this.value = '' }
  setAttribute(nome, valor) { this.attributes[nome] = String(valor) }
  click() { this.disparar('click') }
}
const ids = new Map()
const get = (id) => { if (!ids.has(id)) ids.set(id, new Elemento(id)); return ids.get(id) }
get('mostrarArmadilhas').checked = true
get('velocidade').value = '20'
const layout = new Elemento('layout')
let tick = null
const contexto = {
  document: { getElementById: get, createElement: () => new Elemento(), createElementNS: () => new Elemento(), querySelector: () => layout, addEventListener() {} },
  window: { addEventListener() {} },
  Option: class { constructor(text, value) { this.text = text; this.value = value } },
  getComputedStyle: () => ({ getPropertyValue: () => '24', columnGap: '1', paddingLeft: '2' }),
  setInterval: (fn) => { tick = fn; return 1 },
  clearInterval: () => { tick = null },
  console,
}
const html = fs.readFileSync(process.argv[2], 'utf8')
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1]
vm.runInNewContext(script, contexto)

get('comparar').checked = true
get('comparar').disparar('change')
assert.equal(get('indice').textContent, '0 de 14')
get('reproduzir').click()
for (let i = 0; i < 10; i++) { assert.ok(tick); tick() }
assert.equal(get('indice').textContent, '10 de 14')
const paineis = get('comparacao').children.filter((c) => c.attributes['aria-label'])
assert.equal(paineis.length, 4)
assert.equal(paineis[0].children[1].textContent, 'Percurso concluído.')
assert.equal(paineis[2].children[1].textContent, 'Em andamento.')
for (let i = 0; i < 4; i++) { assert.ok(tick); tick() }
assert.equal(get('indice').textContent, '14 de 14')
assert.equal(tick, null)
assert.equal(get('reproduzir').textContent, 'Recomeçar')
get('reproduzir').click()
assert.ok(tick)
tick()
assert.equal(get('indice').textContent, '1 de 14')

get('mapa').value = 'm07_impossivel'
get('mapa').disparar('change')
assert.equal(get('indice').textContent, 'indisponível')
assert.equal(get('reproduzir').disabled, true)
assert.equal(tick, null)
console.log('Reprodução sincronizada, conclusão, reinício e mapa sem solução: OK')
