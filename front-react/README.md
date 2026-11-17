# Grafos em React

<!-- [IA] Claude Code – instruções do projeto React -->

Projeto React (Vite) com o labirinto interativo, as figuras da Parte 1 e os 4 gráficos exploratórios da AVD.
É uma versão extra, fora dos requisitos do enunciado. Os dados vêm do código do grupo.

## Como rodar

```bash
# 1. Gerar os dados (na raiz do repositório)
python -m scripts.exportar_front

# 2. Instalar e abrir o projeto
cd front-react
npm install
npm run dev
```

Para gerar a versão final: `npm run build` (sai em `front-react/dist/`).

## Estrutura

- `src/dados.json`: dados gerados por `scripts/exportar_front.py` (não editar à mão)
- `src/util.js`: leitura dos rótulos de estado e formatação
- `src/components/Grade.jsx`: grade do labirinto, percurso e heatmap
- `src/components/Labirinto.jsx`: labirinto interativo com animação
- `src/components/Parte1.jsx`: percursos, camadas do m02, árvore BFS e heatmap do m08
- `src/components/Avd.jsx`: os 4 gráficos exploratórios
- `src/App.jsx`: cabeçalho e abas

O `package.json` troca o Rollup pela versão em WebAssembly (`overrides`), porque em algumas máquinas Windows o binário nativo é bloqueado.
