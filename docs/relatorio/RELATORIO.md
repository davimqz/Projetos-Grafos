<!-- [IA] Claude Code – esqueleto do relatório: seções tiradas do enunciado, partes factuais preenchidas a partir do repositório; análises, discussões, prova e conclusões ficam para o grupo -->

# Projeto Final — Teoria dos Grafos + AVD (2026.2)

**Labirinto com Chaves (Grafo de Estados) + Comparação de Algoritmos no Elliptic++**

Matheus Araujo · Thomaz Lima · Davi Marques Oliveira · Vagner Montenegro de Melo

Repositório: <https://github.com/davimqz/Projetos-Grafos> · Entrega: 26/11/2026

> **Como usar este esqueleto.** Cada bloco marcado com **[A ESCREVER]** diz o que o enunciado pede e quem é o dono.
> Pelas regras de IA, análises, discussões, conclusões, notas analíticas e a prova do m05 têm que ser escritas por
> nós; a IA só pode revisar ortografia e clareza depois. Apagar este aviso e os marcadores antes de gerar o PDF.

---

## Sumário

1. Introdução
2. Manual de uso
3. Implementação comum (grafo e algoritmos)
4. Parte 1 — Labirinto com Chaves
5. Parte 2 — Elliptic++
6. AVD — análise exploratória e explanatória
7. Testes
8. Limitações
9. Conclusões
10. Matriz de contribuição
11. Uso de IA

---

## 1. Introdução

> **[A ESCREVER — Davi]** Um ou dois parágrafos: o que o projeto faz nas duas partes, o que é o grafo de estados e qual é
> a pergunta de pesquisa da Parte 2.

---

## 2. Manual de uso

### 2.1 Instalação

Python 3.11 ou mais novo.

```bash
git clone https://github.com/davimqz/Projetos-Grafos.git
cd Projetos-Grafos
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest
```

O recorte da Parte 2 já está em `data/dataset_parte2/`; não é preciso baixar o dataset.

### 2.2 Parte 1

```bash
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg BFS --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg DIJKSTRA --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m05_bonus.txt --alg BELLMAN_FORD --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m04_esteiras.txt --armadilhas --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --interactive --out ./out/parte1/
python -m src.visualizar_parte1 --out ./out/parte1/
```

> **[COMPLETAR — Matheus]** Comando que gera as saídas do P3 (`solve.py`) quando entrar na main.

### 2.3 Parte 2

```bash
python -m src.cli --dataset ./data/dataset_parte2/ --alg BFS --source <carteira> --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --alg DFS --source <carteira> --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source <carteira> --target <carteira> --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --alg BELLMAN_FORD --source <carteira> --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/
```

### 2.4 Labirinto interativo

> **[A ESCREVER — Thomaz]** Como abrir o `out/parte1/labirinto_interativo.html` e o que cada controle faz (seleção de
> mapa e algoritmo, passo a passo, velocidade, camadas, armadilhas). Incluir 1 captura de tela.

### 2.5 Front-end em React (extra)

```bash
python -m scripts.exportar_front
cd front-react && npm install && npm run dev
```

> **[A ESCREVER — Vagner]** Uma frase sobre o que o front mostra e 1 captura de tela.

---

## 3. Implementação comum (grafo e algoritmos)

Os algoritmos estão em `src/graphs/algorithms.py`, sobre a lista de adjacência dirigida de `src/graphs/graph.py`
(vizinhos na ordem N, L, S, O). As mesmas funções são usadas nas duas partes. O `networkx` aparece só em `tests/`,
como oráculo.

| Algoritmo | Entrada | Saída | Complexidade |
|---|---|---|---|
| BFS | grafo, origem | ordem, nível de cada nó, árvore | O(V + E) |
| DFS | grafo, origem | ordem, arcos de árvore/retorno/avanço/cruzamento, existência de ciclo | O(V + E) |
| Dijkstra (`heapq`) | grafo com pesos ≥ 0, origem | distâncias e caminho; recusa peso negativo | O((V + E) log V) |
| Bellman-Ford | grafo, origem | distâncias e caminho, ou o ciclo negativo reconstruído | O(V · E) |

> **[A ESCREVER — Thomaz]** Decisões de implementação que valem explicar: como a DFS classifica cada arco (tempos de
> descoberta/término), como o Dijkstra recusa peso negativo, como o Bellman-Ford reconstrói o ciclo.

---

## 4. Parte 1 — Labirinto com Chaves

### 4.1 Modelagem: G_pos e G_est

> **[A ESCREVER — Matheus]** O que é um nó em cada grafo, o rótulo `(l,c)|chaves|{bônus}`, a numeração dos bônus em
> ordem de leitura, a construção por exploração a partir de `S`, o nó `ALVO` com arco de custo 0 e as variantes
> (portas como chão/parede, `+` fixo, fonte consumível). Incluir o G_est do m02 desenhado à mão.

### 4.2 Por que o grafo tem que ser dirigido

> **[A ESCREVER — Matheus]** Exigido pelo enunciado (Seção 2). Pensar em esteiras e em pegar uma chave.

### 4.3 Mapa mínimo contado à mão

> **[A ESCREVER — Matheus]** O mapa de até 5×7 usado em `tests/test_estados.py`, com o número de estados e de arcos
> contado à mão e a indicação do teste que confere.

### 4.4 Métricas globais e por camada

Fonte: `out/parte1/metricas_global.json` e `out/parte1/camadas.json`.

| Mapa | G_pos: ordem | tamanho | densidade | G_est: ordem | tamanho | densidade | teto teórico | ocupação |
|---|---|---|---|---|---|---|---|---|
| m01 … m08 | | | | | | | | |

> **[A ESCREVER — Matheus]** Comentário da tabela, métricas por camada, quantos arcos ligam camadas e **por que são
> exatamente aquelas casas**.

### 4.5 Graus, multiplicidade e becos

Fonte: `out/parte1/graus_<mapa>.csv`, `out/parte1/heatmap_m08.png`.

> **[A ESCREVER — Matheus]** Maior grau de entrada e de saída por mapa; multiplicidade máxima no m08, quantas casas a
> atingem e por quê; becos encontrados.

### 4.6 Comparação de modelagens (m02, m03, m04)

Fonte: `out/parte1/comparacao_modelagem.csv`.

| Mapa | Abordagem | Passos | Caminho válido | Observação |
|---|---|---|---|---|
| | portas como chão | | | |
| | portas como parede | | | |
| | G_est | | | |

> **[A ESCREVER — Matheus]** Por que (a) gera caminho inválido e (b) falha.

### 4.7 m05: pesos negativos e a prova

Fonte: Bellman-Ford no G_pos com `+` fixo em −4 × no G_est.

> **[A ESCREVER — Matheus]** Resultado dos dois casos e a **prova** de que o G_est do m05 não tem ciclo negativo
> (dica do enunciado: o que acontece com o conjunto de bônus ao longo de um caminho?).

### 4.8 Caminhos nos mapas

Fonte: `out/parte1/solucoes.csv`, `out/parte1/dfs_classificacao.csv`, `out/parte1/percurso_m03.json`.

| Mapa | BFS (passos) | Dijkstra (custo / status) | Bellman-Ford | DFS: árvore / retorno / avanço / cruzamento |
|---|---|---|---|---|
| m01 … m08, mapas do grupo | | | | |

> **[A ESCREVER — Matheus e Thomaz]** Discussões obrigatórias:
> - **m01:** por que BFS e Dijkstra dão caminhos diferentes;
> - **m06:** o ciclo negativo (sequência de estados e custo, de `ciclo_negativo_m06.json`), a correção com
>   `--fonte-consumivel` e o resultado finito do Bellman-Ford;
> - **m07:** como a busca mostra que não há solução e quantos estados são alcançáveis.

### 4.9 Estados-armadilha (m04 e m07)

Fonte: `out/parte1/armadilhas_m04.csv`, `out/parte1/armadilhas_m07.csv`.

> **[A ESCREVER — Matheus]** Método (busca a partir de `ALVO` no grafo transposto), quantos estados são armadilha e
> exemplos.

### 4.10 Mapas do grupo

Fonte: `data/mapas_grupo/`.

| Mapa | Estados | Arcos | Passos (BFS) | Custo (Dijkstra ou BF) | % armadilhas |
|---|---|---|---|---|---|
| mapa 1 (≥ 3 chaves, esteira e bônus no caminho ótimo) | | | | | |
| mapa 2 (≥ 20% de armadilhas) | | | | | |

> **[A ESCREVER — Matheus]** Desenho de cada mapa e o que ele exercita.

### 4.11 Visualizações

Figuras em `out/parte1/`:

- `percurso_m03.png` e `percurso_m08.png`: percurso de menor custo, com a cor mudando a cada chave;
- `camadas_m02.png`: G_est do m02 por camada, destacando os arcos entre camadas;
- `arvore_bfs_m02.png`: árvore BFS do m02 com os níveis;
- `heatmap_m08.png`: multiplicidade das casas do m08.

> **[A ESCREVER — Thomaz]** Inserir as figuras com legenda e uma frase sobre o que cada uma mostra.

---

## 5. Parte 2 — Elliptic++

> O conteúdo detalhado já está em [`parte2.md`](parte2.md) e em [`../PARTE2_DATASET.md`](../PARTE2_DATASET.md).
> Aqui entra a versão final, resumida, para o PDF.

### 5.1 Dataset e recorte

Fonte: Elliptic++ (<https://github.com/git-disl/EllipticPlusPlus>), grafo de carteiras (endereço → endereço).

| | Grafo completo | Recorte usado |
|---|---|---|
| Carteiras (nós) | 822.942 | 14.182 |
| Arcos | 2.868.964 | 25.111 |
| Tipo | dirigido | dirigido, ponderado |

Recorte em bola de neve a partir de 50 carteiras ilícitas sorteadas (seed 42), expandindo por vizinhos de entrada e
saída até pelo menos 25.000 arestas no subgrafo induzido. Laços removidos (45.981) e arestas repetidas agregadas em um
arco por par.

> **[A ESCREVER — Davi]** Justificativa do grafo de carteiras e do recorte (o grafo de transações é acíclico; o
> completo passa de ~500 mil arestas). Distribuição dos graus de entrada e saída.

### 5.2 Pesos, caminho mínimo e ciclo negativo

| Peso | Algoritmo | Definição |
|---|---|---|
| `valor_btc` | Dijkstra | soma do `total_BTC` das transações do par A → B (≥ 0) |
| saldo do destino | Bellman-Ford | `btc_received_total − btc_sent_total` da carteira B |

> **[A ESCREVER — Davi]** Significado de caminho mínimo e de ciclo negativo no domínio; por que o peso não pode ser
> a diferença entre os saldos de A e B; qual transformação foi usada para o Dijkstra.

**Pergunta de pesquisa:** carteiras ilícitas participam mais de ciclos de repasse (ciclos negativos) do que as lícitas?

### 5.3 BFS e DFS (3 fontes)

Fonte: `out/parte2/bfs_*.json`, `out/parte2/dfs_*.json`.

| Classe | Carteira | Alcançadas (com a origem) | Camadas | Ciclos (DFS) |
|---|---|---|---|---|
| Ilícita | `39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K` | 1.737 | 8 | sim |
| Lícita | `35fNF5Uwbsoa5ABPCUvKZNyuAV7S9sJTou` | 81 | 3 | não |
| Desconhecida | `1MFXYK1XucKFfhPhW9HDHD3vsM9BKey4qm` | 1.267 | 7 | sim |

> **[COPIAR — Davi]** Critério de escolha e interpretação a partir de `parte2.md`.

### 5.4 Dijkstra (5 pares)

Fonte: `out/parte2/dijkstra_*.json`.

> **[COPIAR — Davi]** Tabela dos 5 pares e interpretação a partir de `parte2.md`.

### 5.5 Bellman-Ford

Fonte: `out/parte2/bellman_ford_*.json`.

> **[COPIAR — Davi]** Caso com peso negativo sem ciclo e caso com ciclo negativo (sequência de carteiras e custo
> −13.226,15), com a interpretação de `parte2.md`.

### 5.6 Desempenho e escalabilidade

Fonte: `out/parte2/parte2_report.json`, `out/parte2/benchmark_escalabilidade.png`.

| Algoritmo | 10% | 50% | 100% | Complexidade |
|---|---|---|---|---|
| BFS | | | | O(V + E) |
| DFS | | | | O(V + E) |
| Dijkstra | | | | O((V + E) log V) |
| Bellman-Ford | | | | O(V · E) |

> **[A ESCREVER — Vagner]** Tempos médios (≥ 5 execuções), comparação do crescimento com a complexidade teórica e os
> gráficos de comportamento e de caminhos. Falta incluir o Dijkstra no benchmark.

### 5.7 Discussão crítica

> **[A ESCREVER — Davi e Vagner]** Quando e por que cada algoritmo é mais adequado; limites do design de pesos;
> **resposta à pergunta de pesquisa**.

---

## 6. AVD — análise exploratória e explanatória

Fonte: `notebooks/avd/01_exploratoria.ipynb`, figuras em `out/parte2/avd/`.

### 6.1 Exploração (4 pilares)

> **[A ESCREVER — Vagner]** Estrutural, distribucional, relacional e outliers, a partir das notas do notebook.

### 6.2 Dados faltantes e outliers

> **[A ESCREVER — Vagner]** Mecanismo de ausência (classe "desconhecido") e tratamento justificado; avaliação e
> tratamento dos outliers.

### 6.3 Análise multivariada

> **[A ESCREVER — Vagner]** Relação da classe com todos os demais atributos (direta ou não, linear ou não, força).

### 6.4 Visualizações exploratórias

Para cada uma: figura, título, e a nota analítica (**o que mostra · insight · por que esse tipo de gráfico**).

> **[A ESCREVER — Vagner]** Exploratórias 1 a 4.

### 6.5 Da exploratória à explanatória

> **[A ESCREVER — Vagner]** O que foi encontrado na exploração, qual história contar, por que é a mais relevante e
> qual técnica de destaque foi usada.

### 6.6 Visualizações explanatórias

> **[A ESCREVER — Vagner]** Explanatórias 1 e 2, com a nota analítica e a justificativa do tipo de gráfico, dos
> elementos exibidos e dos atributos pré-atentivos. Indicar qual responde à pergunta de pesquisa.

---

## 7. Testes

Executados com `pytest` (318 testes passando em 18/11/2026).

| Arquivo | O que confere |
|---|---|
| `test_bfs.py` | níveis corretos em grafo pequeno |
| `test_dfs.py` | ciclo e classificação dos arcos em grafo dirigido |
| `test_dijkstra.py` | caminhos com pesos ≥ 0 e recusa de peso negativo |
| `test_bellman_ford.py` | distâncias com pesos negativos sem ciclo; flag e ciclo retornado |
| `test_estados.py` | mapa mínimo, esteira contra parede, troca de camada ao pegar chave |
| `test_io.py` | mapas inválidos (não retangular, dois S, sem G, símbolo desconhecido) |
| `test_graph.py`, `test_carga_parte2.py`, `test_casos_parte2.py`, `test_benchmark.py`, `test_viz.py`, `test_visualizar_parte1.py` | grafo, carga e casos da Parte 2, benchmark e visualizações |

> **[COMPLETAR]** Atualizar a contagem e incluir `test_solve.py` na véspera da entrega.

---

## 8. Limitações

> **[A ESCREVER — todos]** Pontos já levantados que podem entrar:
> - Parte 2: as ilícitas são 37% do recorte e 1,7% do dataset completo (viés do recorte em bola de neve); no
>   Bellman-Ford todas as arestas que chegam à mesma carteira têm o mesmo peso; `valor_btc` é o valor total da
>   transação, não necessariamente o que foi de A para B.
> - Parte 1: (a preencher)
> - Benchmark: (a preencher)

---

## 9. Conclusões

> **[A ESCREVER — todos]**

---

## 10. Matriz de contribuição

### 10.1 Pacotes

| Pacote | Escopo | Dono | Revisor |
|---|---|---|---|
| P1 | modelagem e grafo de estados (`io.py`, `estados.py`) | Matheus | Thomaz |
| P2 | grafo e algoritmos (`graph.py`, `algorithms.py`) | Thomaz | Davi |
| P3 | análises da Parte 1 (`solve.py`, mapas do grupo) | Matheus | Thomaz |
| P4a | Parte 2: dados e casos obrigatórios | Davi | Vagner |
| P4b | Parte 2: benchmark e escalabilidade | Vagner | Davi |
| P5a | visualização da Parte 1 e HTML interativo | Thomaz | Matheus |
| P5b | AVD | Vagner | Davi |
| P5c | README, relatório e declaração de IA | Davi | todos |

### 10.2 Commits por integrante e pacote

Contagem de commits (sem merges) que alteram arquivos de cada pacote, em `main` + branch `matheus`, em 18/11/2026.
Um commit pode contar em mais de um pacote. P5c inclui as linhas do `REGISTRO_IA.md`, que cada um adiciona.

| Integrante | P1 | P2 | P3 | P4a | P4b | P5a | P5b | P5c |
|---|---|---|---|---|---|---|---|---|
| Matheus | 5 | 1 | 4 | | | | | 6 |
| Thomaz | | 9 | | | | 8 | | 17 |
| Davi | 2 | 2 | 1 | 20 | | 2 | 1 | 24 |
| Vagner | | | | 2 | 4 | 5 | 1 | 11 |

> **[COMPLETAR — Davi]** Refazer a contagem na véspera da entrega e incluir as revisões de PR de cada um (quem revisou
> quais PRs).

---

## 11. Uso de IA

Todo trecho feito com apoio de IA está marcado no código com `# [IA] <ferramenta> – <finalidade>` e registrado em
`docs/REGISTRO_IA.md`. A declaração assinada por todos está em `docs/DECLARACAO_IA.pdf`.

> **[A ESCREVER — todos]** Reflexão curta do grupo sobre o uso de IA, se a declaração pedir.
