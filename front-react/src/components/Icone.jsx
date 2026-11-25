// [IA] Claude Code – ícones minimalistas (traços do Lucide, licença ISC) embutidos para não adicionar dependência
const TRACOS = {
  play: <polygon points="6 3 20 12 6 21 6 3" />,
  pause: <><rect x="14" y="4" width="4" height="16" /><rect x="6" y="4" width="4" height="16" /></>,
  reiniciar: <><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /><path d="M3 3v5h5" /></>,
  anterior: <path d="m15 18-6-6 6-6" />,
  proximo: <path d="m9 18 6-6-6-6" />,
  ampliar: <><polyline points="15 3 21 3 21 9" /><polyline points="9 21 3 21 3 15" /><line x1="21" x2="14" y1="3" y2="10" /><line x1="3" x2="10" y1="21" y2="14" /></>,
  reduzir: <><polyline points="4 14 10 14 10 20" /><polyline points="20 10 14 10 14 4" /><line x1="14" x2="21" y1="10" y2="3" /><line x1="3" x2="10" y1="21" y2="14" /></>,
  enviar: <><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" x2="12" y1="3" y2="15" /></>,
  baixar: <><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" x2="12" y1="15" y2="3" /></>,
}

export function Icone({ nome }) {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="square" strokeLinejoin="miter" aria-hidden="true" focusable="false">
      {TRACOS[nome]}
    </svg>
  )
}
