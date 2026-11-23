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

No labirinto, **Comparar os quatro algoritmos** mostra os percursos e resultados lado a lado;
DFS mostra o caminho da árvore de busca, não necessariamente o mínimo. **Carregar mapa .txt**
valida o arquivo com o Python do projeto e calcula os quatro resultados. São aceitos até 16 KiB,
2.500 casas e 8 bônus; o cálculo tem limite de 30 segundos. O mapa enviado fica apenas na
sessão e não integra o HTML conjunto. Estas funções de envio exigem `npm run dev` ou
`npm run preview` com Python e dependências instalados; não funcionam em hospedagem estática.
Para publicar o site estático (Vercel), gere com `VITE_SITE_ESTATICO=1 npm run build`: o upload e os
botões de gerar HTML somem da tela.

No labirinto, **Gerar HTML deste mapa** usa o mapa e o algoritmo selecionados e grava
`out/parte1/html/labirinto_<mapa>.html`; o botão também oferece um link para abri-lo.
**Gerar HTML conjunto** reúne todos os mapas de `data/mapas/` e
`data/mapas_grupo/` com os quatro algoritmos em
`out/parte1/html/labirinto_interativo.html`. Gerar novamente substitui o arquivo
correspondente. O arquivo é independente
e pode ser aberto fora do servidor. A geração é oferecida pelos comandos locais
`npm run dev` e `npm run preview`: ela precisa do Python e das dependências do
projeto instaladas na raiz (prefere `.venv`). Uma hospedagem estática de `dist/`
não executa o gerador Python. O HTML incorpora JetBrains Mono e sua licença,
sem depender de instalação da fonte ou acesso à rede.

## Estrutura

- `src/dados.json`: dados gerados por `scripts/exportar_front.py` (não editar à mão)
- `src/util.js`: leitura dos rótulos de estado e formatação
- `src/components/Grade.jsx`: grade do labirinto, percurso e heatmap
- `src/components/Labirinto.jsx`: labirinto interativo com animação
- `src/components/Parte1.jsx`: percursos, grafo de estados interativo, árvore BFS e heatmap do m08
- `src/components/GrafoEstados.jsx`: grafo de estados e árvore BFS com [Cytoscape.js](https://js.cytoscape.org/) (zoom, arrastar, layouts e destaque do percurso)
- `src/components/Avd.jsx`: os 4 gráficos exploratórios
- `src/App.jsx`: cabeçalho e abas

O `package.json` troca o Rollup pela versão em WebAssembly (`overrides`), porque em algumas máquinas Windows o binário nativo é bloqueado.
