# Projeto Final — Teoria dos Grafos + AVD (2026.2)

<!-- [IA] Claude Code – organização do README a partir dos comandos e arquivos do repositório -->

**Parte 1:** Labirinto com Chaves (grafo de estados) · **Parte 2:** dataset Elliptic++ (rede de transações Bitcoin)

Status de cada pacote e próximos passos em [`docs/PROXIMOS_PASSOS.md`](docs/PROXIMOS_PASSOS.md).

## Equipe

| Integrante | Pacotes |
|---|---|
| Matheus | P1 (modelagem e grafo de estados), P3 (análises da Parte 1) |
| Thomaz | P2 (grafo e algoritmos), P5a (visualização da Parte 1) |
| Davi | P4a (dados e casos da Parte 2), P5c (README, PDF e declaração de IA) |
| Vagner | P4b (benchmark e escalabilidade), P5b (AVD) |

Dono e revisor de cada pacote em [`docs/PLANO_DE_TRABALHO.md`](docs/PLANO_DE_TRABALHO.md).

## Instalação

Python 3.11 ou mais novo.

```bash
git clone https://github.com/davimqz/Projetos-Grafos.git
cd Projetos-Grafos
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest
```

O recorte da Parte 2 já está em `data/dataset_parte2/`, então não é preciso baixar o dataset para rodar o projeto.

## Implementação

Os quatro algoritmos foram escritos pelo grupo em `src/graphs/algorithms.py`, sobre a lista de adjacência dirigida de
`src/graphs/graph.py` (vizinhos na ordem N, L, S, O). As mesmas funções são usadas nas duas partes.

| Algoritmo | O que devolve |
|---|---|
| BFS | ordem de visita, nível de cada nó e árvore de busca |
| DFS | ordem de visita, classificação dos arcos (árvore, retorno, avanço, cruzamento) e ciclo, se houver |
| Dijkstra | distâncias e caminho com `heapq`; recusa grafo com peso negativo |
| Bellman-Ford | distâncias e caminho; detecta ciclo negativo e reconstrói o ciclo |

O `networkx` aparece só em `tests/`, como oráculo para conferir os resultados.

## Parte 1 — Labirinto com Chaves

O mapa é lido e validado por `src/graphs/io.py`. Em `src/graphs/estados.py` saem dois grafos:

- **G_pos**: um nó por casa livre, com paredes e esteiras;
- **G_est**: um nó por estado `(l,c)|chaves|{bônus}`, explorado a partir de `S`, com um nó virtual `ALVO` (custo 0 a partir de cada `G`).

Variantes suportadas: portas como chão, portas como parede, `+` fixo em −4 e `--fonte-consumivel` (o `*` vale −2 só na primeira vez).

### Como executar

```bash
# percurso de um algoritmo em um mapa
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg BFS --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg DIJKSTRA --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m05_bonus.txt --alg BELLMAN_FORD --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/

# labirinto interativo de um mapa (gera out/parte1/labirinto_<mapa>.html)
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --interactive --out ./out/parte1/

# estados-armadilha a partir de um JSON com a lista de rótulos
python -m src.cli --mapa ./data/mapas/m04_esteiras.txt --armadilhas --arquivo-armadilhas ./out/parte1/armadilhas_m04.json --interactive --out ./out/parte1/

# figuras do P5a e o HTML conjunto (m02, m03 e m08)
python -m src.visualizar_parte1 --out ./out/parte1/
```

Sem `--alg`, a CLI usa Dijkstra. Se o algoritmo não se aplica ao mapa (por exemplo, Dijkstra com peso negativo) ou não
existe percurso até a saída, o motivo aparece no terminal e no HTML.

### Saídas em `out/parte1/`

| Arquivo | Conteúdo |
|---|---|
| `percurso_m03.png`, `percurso_m08.png` | percurso de menor custo (Dijkstra); a cor muda a cada chave pega |
| `camadas_m02.png` | G_est do m02 por conjunto de chaves, com os arcos entre camadas em destaque |
| `arvore_bfs_m02.png` | árvore da BFS no m02, com os níveis |
| `heatmap_m08.png` | quantos estados existem em cada casa do m08 |
| `labirinto_interativo.html` | mapa + algoritmo, passo a passo, estado atual, custo acumulado, camadas e armadilhas, com controle de velocidade |

As análises do P3 (`metricas_global.json`, `camadas.json`, `graus_<mapa>.csv`, `arestas_<mapa>.csv`,
`comparacao_modelagem.csv`, `solucoes.csv`, armadilhas do m04 e do m07 e comparações do m05) estão implementadas em
`src/parte1/`, com orquestração por `src.solve.executar_parte1` para os mapas informados, inclusive os do grupo.
A integração dessa orquestração com a CLI permanece pendente.

## Parte 2 — Elliptic++ (rede de carteiras Bitcoin)

Usamos o grafo de carteiras (endereço → endereço), porque o grafo de transações não tem ciclos. O grafo completo tem
2,87 milhões de arestas, então trabalhamos com um recorte em bola de neve a partir de 50 carteiras ilícitas (seed 42):
**14.182 carteiras e 25.111 arcos**.

| Peso | Usado em | Definição |
|---|---|---|
| `valor_btc` | BFS (ignorado), DFS (ignorado), Dijkstra | soma do `total_BTC` das transações do par A → B (sempre ≥ 0) |
| saldo do destino | Bellman-Ford | `btc_received_total − btc_sent_total` da carteira B (pode ser negativo) |

**Pergunta de pesquisa:** carteiras ilícitas participam mais de ciclos de repasse (ciclos negativos) do que as lícitas?

Decisões de limpeza (laços, arestas repetidas, uma linha por carteira) e limitações do recorte em
[`docs/PARTE2_DATASET.md`](docs/PARTE2_DATASET.md). Resultados e interpretação em
[`docs/relatorio/parte2.md`](docs/relatorio/parte2.md).

### Como executar

```bash
# BFS e DFS a partir de uma carteira
python -m src.cli --dataset ./data/dataset_parte2/ --alg BFS --source 39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --alg DFS --source 39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K --out ./out/parte2/

# Dijkstra entre duas carteiras
python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source 39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K --target 16PaWFJttSe54KviUNjyzP459DuQTiB8rT --out ./out/parte2/

# Bellman-Ford a partir de uma carteira
python -m src.cli --dataset ./data/dataset_parte2/ --alg BELLMAN_FORD --source 1MFXYK1XucKFfhPhW9HDHD3vsM9BKey4qm --out ./out/parte2/

# benchmark (média de 5 execuções) e escalabilidade em 10%, 50% e 100%
python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/

# graus de entrada e saída por carteira, histograma e CCDF por classe
python -m scripts.graus_parte2
```

Para refazer o recorte do zero (baixa os CSVs brutos do Google Drive para `data/dataset_parte2/raw/`):

```bash
python scripts/baixar_dataset.py
python scripts/amostrar_dataset.py --arestas 25000 --sementes 50 --seed 42
```

### Saídas em `out/parte2/`

| Arquivo | Conteúdo |
|---|---|
| `bfs_<carteira>.json`, `dfs_<carteira>.json` | 3 fontes (uma ilícita, uma lícita, uma desconhecida): ordem, camadas e ciclos |
| `dijkstra_<origem>_<destino>.json` | 5 pares: caminho e custo |
| `bellman_ford_<carteira>.json` | 1 caso com peso negativo sem ciclo e 1 com ciclo negativo detectado |
| `parte2_report.json` | tempos médios e escalabilidade por algoritmo |
| `benchmark_escalabilidade.png` | tempo × tamanho do grafo |
| `graus_histograma.png`, `graus_ccdf.png` | distribuição dos graus de entrada e saída por classe |
| `graus_parte2.csv`, `graus_resumo.json`, `graus_zero.csv` | graus por carteira, estatísticas por classe e carteiras com grau zero |

## AVD

A análise exploratória do recorte está em [`notebooks/avd/01_exploratoria.ipynb`](notebooks/avd/01_exploratoria.ipynb):
estrutura, distribuições, dados faltantes (a classe "desconhecido" é tratada como ausência de rótulo e não é apagada),
relações entre atributos e outliers, com 4 gráficos exploratórios e 2 explanatórios. As figuras são salvas em
`out/parte2/avd/` quando o notebook é executado.

```bash
pip install jupyter
jupyter notebook notebooks/avd/01_exploratoria.ipynb
```

## Front-end em React (extra)

Versão extra, fora do que o enunciado pede, com o labirinto interativo, as figuras da Parte 1 e os gráficos
exploratórios da AVD. Precisa do Node.js.

```bash
python -m scripts.exportar_front   # gera front-react/src/dados.json com os resultados do código do grupo
cd front-react
npm install
npm run dev
```

Detalhes em [`front-react/README.md`](front-react/README.md).

## Relatório em PDF e matriz de contribuição

```bash
python -m scripts.gerar_pdf                         # docs/relatorio/RELATORIO.md -> docs/relatorio/RELATORIO.pdf
python -m scripts.matriz_contribuicao --revisoes    # tabelas da seção 10.2 (commits por pacote e PRs revisados)
```

O PDF é impresso pelo Chrome ou pelo Edge em modo headless, com as figuras embutidas. Se nenhum dos dois estiver no
caminho padrão, defina `NAVEGADOR_PDF` com o executável. O script avisa quando ainda há marcadores `[A ESCREVER]` ou
`[COMPLETAR]` no texto. A opção `--revisoes` precisa do `gh` autenticado.

## Estrutura

```
.
├─ README.md
├─ requirements.txt
├─ docs/
│  ├─ PLANO_DE_TRABALHO.md     # pacotes, donos e revisores
│  ├─ PROXIMOS_PASSOS.md       # status atual
│  ├─ PARTE2_DATASET.md        # decisões sobre o dataset da Parte 2
│  ├─ REGISTRO_IA.md           # registro de cada uso de IA
│  └─ relatorio/parte2.md      # resultados e interpretação da Parte 2
├─ data/
│  ├─ mapas/                   # mapas fornecidos (m01 a m08)
│  ├─ mapas_grupo/             # 2 mapas criados pelo grupo
│  └─ dataset_parte2/          # recorte (nos.csv, arestas.csv); o bruto fica em raw/, fora do git
├─ notebooks/avd/              # análise exploratória (AVD)
├─ scripts/                    # download e recorte do dataset, exportação para o front
├─ front-react/                # front-end extra em React (Vite)
├─ out/
│  ├─ parte1/
│  └─ parte2/
├─ src/
│  ├─ cli.py                   # ponto de entrada das duas partes
│  ├─ solve.py                 # orquestração da Parte 1 e interface pública
│  ├─ parte1/
│  │  ├─ modelos.py            # tipos compartilhados
│  │  ├─ carga.py              # preparo dos mapas
│  │  ├─ analises.py           # métricas, camadas, graus e armadilhas
│  │  ├─ buscas.py             # normalização das buscas e comparações
│  │  └─ exportacao.py         # escrita de CSV e JSON
│  ├─ viz.py                   # figuras e HTML interativo
│  ├─ visualizar_parte1.py     # gera as figuras do P5a
│  ├─ carga_parte2.py          # carrega o recorte como grafo
│  ├─ casos_parte2.py          # casos obrigatórios da Parte 2
│  ├─ benchmark.py             # tempos e escalabilidade
│  └─ graphs/
│     ├─ io.py                 # leitura e validação dos mapas
│     ├─ estados.py            # G_pos e G_est
│     ├─ graph.py              # lista de adjacência dirigida
│     └─ algorithms.py         # BFS, DFS, Dijkstra, Bellman-Ford
└─ tests/                      # pytest (networkx só como oráculo)
   ├─ test_solve.py            # compatibilidade da interface pública
   └─ parte1/                  # testes por responsabilidade e integração
```

As funções e os tipos da Parte 1 continuam disponíveis por `src.solve`.
Suas implementações ficam em `src/parte1/`, com a lógica existente preservada.
Os algoritmos e a construção dos grafos permanecem em `src/graphs/`.

## Uso de IA

Todo trecho feito com apoio de IA é marcado no código com `# [IA] <ferramenta> – <finalidade>` e registrado em
[`docs/REGISTRO_IA.md`](docs/REGISTRO_IA.md). A declaração assinada pelo grupo fica em `docs/DECLARACAO_IA.pdf`.
