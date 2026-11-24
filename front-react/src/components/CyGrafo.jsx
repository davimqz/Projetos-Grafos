// [IA] Claude Code – núcleo compartilhado dos grafos interativos (Cytoscape.js): ciclo de vida, redimensionamento e zoom
import { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'
import { Icone } from './Icone.jsx'

/* Componente genérico: recebe os elementos já montados e cuida do ciclo de vida do Cytoscape. */
export function Cy({ elementos, layout, estilo, aoSelecionar, rotulo, altura = 560, cyRef }) {
  const div = useRef(null)
  useEffect(() => {
    const cy = cytoscape({
      // cópia: o Cytoscape altera os objetos de posição recebidos, e o layout "camadas" precisa das posições originais
      container: div.current, elements: elementos.map((e) => ({ ...e, data: { ...e.data }, position: e.position && { ...e.position } })), style: estilo,
      minZoom: 0.1, maxZoom: 4, boxSelectionEnabled: false,
    })
    // layout rodado à parte para poder pará-lo antes de destruir o grafo (animação do cose)
    const disposicao = cy.layout(layout)
    disposicao.run()
    if (aoSelecionar) {
      cy.on('tap', 'node', (e) => aoSelecionar(e.target))
      cy.on('tap', (e) => { if (e.target === cy) aoSelecionar(null) })
    }
    if (cyRef) cyRef.current = cy
    // O container pode mudar de largura depois do primeiro desenho (fontes, barra de rolagem, responsivo)
    let largura = div.current.clientWidth
    const obs = new ResizeObserver(() => {
      const nova = div.current?.clientWidth
      if (!nova || nova === largura) return
      largura = nova
      cy.resize(); cy.fit(undefined, 30)
    })
    obs.observe(div.current)
    return () => { obs.disconnect(); disposicao.stop(); cy.destroy(); if (cyRef) cyRef.current = null }
  }, [elementos, layout, estilo]) // eslint-disable-line react-hooks/exhaustive-deps
  return <div ref={div} className="cy-area" style={{ height: altura }} role="img" aria-label={rotulo} />
}

export function BarraZoom({ cyRef }) {
  const zoom = (f) => { const cy = cyRef.current; if (cy) cy.zoom({ level: cy.zoom() * f, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }) }
  return (
    <div className="cy-zoom">
      <button type="button" className="btn zoom-btn" onClick={() => zoom(1.3)} aria-label="Aproximar">+</button>
      <button type="button" className="btn zoom-btn" onClick={() => zoom(1 / 1.3)} aria-label="Afastar">−</button>
      <button type="button" className="btn zoom-btn" onClick={() => cyRef.current?.fit(undefined, 30)}><Icone nome="reduzir" />Enquadrar</button>
    </div>
  )
}

