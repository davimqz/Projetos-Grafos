# Roteiro da apresentação (26/11)

Duração alvo: **20 min** (o enunciado aceita de 15 a 20). Ensaio no acompanhamento de **24/11**.

A professora escolhe na hora quem apresenta, e a nota dessa pessoa vale para o grupo. Por isso a coluna
"Prepara" diz quem monta o bloco e explica o conteúdo para os outros, e não quem fala. Todo mundo precisa
conseguir apresentar qualquer bloco.

Os tópicos seguem o que a professora pediu em 19/11 (ver [`referencias/REUNIAO_2026-11-19.md`](referencias/REUNIAO_2026-11-19.md)):
modelagem com G_pos e G_est desenhados, vértice e aresta em cada parte, solução dos mapas, visualizações
com insight, limitações das duas partes e desempenho (tempo, latência e memória) por algoritmo e tarefa.

Os números abaixo foram copiados do relatório. Quando o relatório mudar, este arquivo tem que ser atualizado junto.
Blocos marcados com **[A PREENCHER]** dependem de seções que ainda não foram escritas.

## Visão geral

| # | Bloco | Min | Prepara | Material |
|---|---|---:|---|---|
| 1 | Abertura e roteiro | 0,5 | Davi | slide de título |
| 2 | Estrutura comum: grafo e algoritmos | 1 | Matheus | `src/graphs/` |
| 3 | Parte 1: modelagem (G_pos e G_est) | 2,5 | Matheus | m02 desenhado à mão, `out/parte1/figuras/arvore_bfs_m02.png`, `out/parte1/figuras/camadas_m02.png` |
| 4 | Parte 1: solução dos mapas | 2,5 | Matheus | `out/parte1/figuras/percurso_m03.png`, `out/parte1/figuras/percurso_m08.png`, `out/parte1/figuras/heatmap_m08.png` |
| 5 | Demonstração no terminal (mapa surpresa) | 1,5 | Matheus | CLI (R1), mapas de treino |
| 6 | Demonstração no front | 2,5 | Thomaz | `front-react/` (R2 a R6) |
| 7 | Parte 2: dados e modelagem | 2 | Davi | `out/parte2/graus_histograma.png`, `out/parte2/graus_ccdf.png` |
| 8 | Parte 2: BFS, DFS, Dijkstra e Bellman-Ford | 2,5 | Davi | `out/parte2/benchmark_caminhos_dijkstra.png`, `out/parte2/benchmark_caminhos_bfs_dijkstra.png` |
| 9 | Desempenho por algoritmo e tarefa | 1,5 | Vagner (P2) e Matheus (P1) | `out/parte2/benchmark_escalabilidade.png`, `out/parte2/benchmark_comportamento.png` |
| 10 | AVD: da exploratória à explanatória | 2 | Vagner | `out/parte2/avd/` |
| 11 | Pergunta de pesquisa e limitações | 1 | Davi | relatório, seções 5.7 e 8 |
| 12 | Uso de IA e encerramento | 0,5 | Davi | `docs/REGISTRO_IA.md`, declaração |
| | **Total** | **20** | | |

Para cortar até 15 min, o roteiro sugere tirar 1 min do bloco 6, 1 min do bloco 8, 1 min do bloco 10 e
juntar os blocos 2 e 3.

## Blocos

### 1. Abertura e roteiro (0,5 min)

- Integrantes e pacotes: Matheus (P1, P2, P3), Thomaz (P5a), Davi (P4a, P5c), Vagner (P4b, P5b).
- Ordem da fala: Parte 1, demonstrações, Parte 2, desempenho, AVD, conclusão.

### 2. Estrutura comum (1 min) **[A PREENCHER — Matheus]**

- Classe `Grafo` e os quatro algoritmos (BFS, DFS, Dijkstra, Bellman-Ford) usados nas duas partes.
- Mostrar que a Parte 2 importa o mesmo `src/graphs/algorithms.py` da Parte 1.

### 3. Parte 1: modelagem (2,5 min) **[A PREENCHER — Matheus]**

Pedido da professora: G_pos e G_est desenhados, de preferência o m02 feito à mão, com o rótulo do estado e o nó ALVO.

| | G_pos | G_est |
|---|---|---|
| Vértice | [A PREENCHER] | estado `(l,c)\|chaves\|{bônus}` e o nó virtual ALVO |
| Aresta | [A PREENCHER] | [A PREENCHER] |
| Dirigido? | [A PREENCHER] | sim (seção 4.2 do relatório) |

- Por que o grafo tem que ser dirigido (seção 4.2).
- Mapa mínimo contado à mão (seção 4.3).

### 4. Parte 1: solução dos mapas (2,5 min) **[A PREENCHER — Matheus]**

- Tabela com estado final, custo e status dos algoritmos em cada mapa, tirada de `out/parte1/csv/solucoes.csv`.
- m05: pesos negativos e a prova (seção 4.7).
- Estados-armadilha de m04 e m07 (seção 4.9).
- Mapas do grupo (seção 4.10): arquivos em `data/mapas_grupo/` e gabaritos TXT em `data/solucoes_mapas_grupo/`.
- Uma figura com o insight dela dito em uma frase.

### 5. Demonstração no terminal (1,5 min) **[A PREENCHER — Matheus]**

A professora disse que vai rodar no terminal. Ensaiar com os mapas de `data/mapas_treino/`, que já têm gabarito:

| Mapa | O que mostra | Resultado esperado |
|---|---|---|
| `t01_duas_portas` | caminho com chave | BFS 20, Dijkstra 24, Bellman-Ford 24 |
| `t02_esteiras_fonte` | peso negativo e ciclo | Dijkstra RECUSA, Bellman-Ford CICLO_NEGATIVO |
| `t04_chave_trancada` | mapa sem saída | SEM_SOLUCAO nos três |
| `t05_invalido` | erro de leitura | mensagem clara de mapa inválido |

Comando: [A PREENCHER quando o R1 entrar].

### 6. Demonstração no front (2,5 min) **[A PREENCHER — Thomaz]**

Ordem sugerida, seguindo os pedidos de 19/11:

1. Subir um `.txt` pelo front (R4).
2. Mesmo mapa com todos os algoritmos ao mesmo tempo (R3).
3. Armadilhas no HTML gerado pelo Python (R2).
4. Parte 2: escolher uma fonte ou um par e ver o resultado (R5) e o recorte do grafo (R6). Os dados estão em
   `front-react/src/parte2.json`, gerado por `python -m scripts.exportar_parte2_front`.

Plano B se o front falhar na hora: [A PREENCHER].

### 7. Parte 2: dados e modelagem (2 min)

| | Parte 2 |
|---|---|
| Vértice | carteira (endereço) |
| Arco | par de carteiras que transacionou (A → B) |
| Tipo | dirigido e ponderado |
| Tamanho | 14.182 vértices e 25.111 arcos, recortados de 822.942 vértices e 2.868.964 arcos |

- Fonte: Elliptic++, grafo de carteiras.
- Recorte em bola de neve a partir de 50 carteiras ilícitas (seed 42), até pelo menos 25.000 arestas. O enunciado
  exige amostragem acima de cerca de 500 mil arestas.
- Preparação: laços removidos (45.981), arestas repetidas agregadas em um arco por par, uma linha por carteira.
- Pesos (seção 5.2):

| Peso | Algoritmo | Definição |
|---|---|---|
| `valor_btc` | Dijkstra | soma do `total_BTC` das transações do par A → B (≥ 0) |
| saldo do destino | Bellman-Ford | `btc_received_total − btc_sent_total` da carteira B |

- Graus: média 1,77 de entrada e de saída; 8.021 carteiras (56,6%) com grau de entrada zero e 2.089 (14,7%) com
  grau de saída zero. Figuras 5.1 e 5.2.
- Pergunta de pesquisa: carteiras ilícitas participam mais de ciclos de repasse (ciclos negativos) do que as lícitas?

### 8. Parte 2: resultados (2,5 min)

**BFS e DFS (3 fontes).** Critério: maior número de arcos de saída entre as 5 maiores de cada classe.

| Classe | Carteira | Arcos de saída | Alcançadas (BFS) | Camadas | Arcos de retorno (DFS) |
|---|---|---:|---:|---:|---:|
| Ilícita | `39sfuA8p…` | 398 | 1.737 | 8 | 103 |
| Lícita | `35fNF5Uw…` | 71 | 81 | 3 | 0 |
| Desconhecida | `1MFXYK1X…` | 1.002 | 1.267 | 7 | 98 |

**Dijkstra (5 pares).**

| Par | Custo (BTC) | Arcos |
|---|---:|---:|
| Ilícita → Ilícita | 26,55 | 5 |
| Ilícita → Lícita | 10,88 | 3 |
| Lícita → Ilícita | 49,95 | 4 |
| Desconhecida → Ilícita | 59,81 | 3 |
| Ilícita → Desconhecida | 5,54 | 3 |

Figura de apoio: `benchmark_caminhos_bfs_dijkstra.png`, em que o mesmo par ilícita → ilícita tem 3 arcos no BFS e 5 no Dijkstra.

**Bellman-Ford (2 casos).**

| Origem | Status | Resultado |
|---|---|---|
| `3Fzzji5n…` (lícita) | OK | 45 carteiras alcançadas, 29 arcos negativos alcançáveis |
| `1MFXYK1X…` (desconhecida) | CICLO_NEGATIVO | ciclo de 2 carteiras com custo −13.226,15 |

Falas e interpretação deste bloco: usar as seções 5.3 a 5.5 do relatório.

### 9. Desempenho por algoritmo e tarefa (1,5 min) **[A PREENCHER — Matheus, Parte 1]**

Parte 2, média de 5 execuções com `timeit`, latência (execução mais rápida e mais lenta) e pico de memória com
`tracemalloc` (seção 5.6):

| Algoritmo | Média 10% (ms) | Média 50% (ms) | Média 100% (ms) | Latência 100% (ms) | Pico de memória 10% / 50% / 100% (KiB) | Complexidade |
|---|---:|---:|---:|---:|---|---|
| BFS | 0,36 | 2,48 | 6,03 | 4,33 a 8,85 | 270 / 1.131 / 2.265 | O(V + E) |
| DFS | 0,88 | 6,31 | 21,77 | 17,42 a 24,82 | 306 / 1.693 / 4.380 | O(V + E) |
| Dijkstra | 0,37 | 3,25 | 6,16 | 5,77 a 6,52 | 169 / 726 / 1.454 | O((V + E) log V) |
| Bellman-Ford | 0,51 | 5.538,81 | 42.610,19 | 41.337,47 a 44.237,39 | 220 / 1.195 / 3.497 | O(V · E) |

Falas: seção 5.6 ("Latência", "Memória" e "Comparação com a complexidade teórica").

Falta, pelo pedido R7: os mesmos números para a Parte 1.

### 10. AVD (2 min) **[A PREENCHER — Vagner, explanatórias]**

- Os 4 pilares da exploração (seção 6.1), dados faltantes e outliers (6.2), análise multivariada (6.3).
- Uma ou duas das exploratórias de `out/parte2/avd/` (seção 6.4), cada uma com o insight dela.
- As 2 figuras explanatórias e a mensagem de cada uma (seções 6.5 e 6.6, ainda não escritas).

### 11. Pergunta de pesquisa e limitações (1 min)

- Quando usar cada algoritmo: seção 5.7 ("Quando e por que usar cada algoritmo").
- Resposta: seção 5.7 do relatório ("Resposta à pergunta de pesquisa").
- Limitações da Parte 2: seção 8 (quantidade de carteiras, viés do recorte, viés na escolha das fontes, pesos
  negativos, alcançar um ciclo não é participar dele).
- Limitações da Parte 1: [A PREENCHER — Matheus].

### 12. Uso de IA e encerramento (0,5 min)

- Onde a IA foi usada e onde não foi: `docs/REGISTRO_IA.md` e a declaração em PDF.
- Abrir para perguntas.

## Perguntas que a professora pode fazer

Cada um escreve a resposta da sua parte e todos leem antes do ensaio.

| Pergunta | Quem responde no texto |
|---|---|
| O que é vértice e o que é aresta em G_est? E na Parte 2? | Matheus / Davi |
| Por que o Dijkstra recusa o m05? | Matheus |
| Por que o peso do Bellman-Ford é o saldo do destino e não a diferença de saldos? | Davi |
| Por que o Bellman-Ford leva 42,6 s no grafo inteiro e os outros levam milissegundos? | Vagner |
| Por que a DFS alcança todas as carteiras no benchmark e a BFS não? | Vagner |
| Como o front sabe o resultado da Parte 2? | Thomaz |

## Checklist do ensaio (24/11)

- [ ] Rodar o roteiro inteiro cronometrado.
- [ ] Rodar um mapa de treino no terminal, do zero, em uma máquina que não seja a de quem fez a CLI.
- [ ] Abrir o front e repetir a demonstração.
- [ ] Cada integrante apresenta pelo menos um bloco que não preparou.
- [ ] Conferir se os números deste arquivo ainda batem com o relatório.
