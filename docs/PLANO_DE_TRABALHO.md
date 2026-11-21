# Plano de Trabalho

Entrega: **26/11/2026** (todos postam no Classroom). Acompanhamentos: Grafos 10, 17, 19 e 24/11 · AVD 17, 19 e 24/11.

> Regras de equilíbrio: cada pacote tem **dono + revisor**; **todos com commits em pelo menos 2 pacotes**;
> matriz de contribuição no PDF; nos acompanhamentos a professora sorteia quem reporta cada pacote,
> então **todo mundo precisa saber explicar tudo**.

## Pacotes

| Pacote | Escopo | Dono | Revisor |
|---|---|---|---|
| **P1** Modelagem e grafo de estados | `io.py`, `estados.py`, `arestas_<mapa>.csv`, `test_io`, `test_estados` | Matheus | Thomaz |
| **P2** Algoritmos e testes | `graph.py`, `algorithms.py`, grafo transposto, `test_bfs/dfs/dijkstra/bellman_ford` (usado nas duas partes) | Thomaz | Davi |
| **P3** Análises da Parte 1 | métricas, camadas, graus, comparação de modelagens, prova do m05, `--fonte-consumivel`, mapas do grupo | Matheus | Thomaz |
| **P4a** Parte 2: dados | download, amostragem, design dos pesos, casos obrigatórios (BFS/DFS 3 fontes, Dijkstra 5 pares, BF) | Davi | Vagner |
| **P4b** Parte 2: experimentos | benchmark (≥5 execuções), escalabilidade 10/50/100%, `parte2_report.json`, gráficos de comparação | Vagner | Davi |
| **P5a** Visualização da Parte 1 | percursos m03/m08, camadas m02, árvore BFS, heatmap m08, `labirinto_interativo.html` | Thomaz | Matheus |
| **P5b** AVD | exploração (4 pilares), faltantes/outliers, ≥4 exploratórias + ≥2 explanatórias, notas analíticas | Vagner | Davi |
| **P5c** README e PDF | README final, PDF (manual + técnica), matriz de contribuição, declaração de IA | Davi | todos |

Cada pessoa em 2+ pacotes: Matheus (P1, P3) · Thomaz (P2, P5a) · Davi (P4a, P5c) · Vagner (P4b, P5b).

## Cronograma sugerido

| Até | Marco |
|---|---|
| 31/10 | G_est do m02 desenhado **à mão** e conferido; `io.py` lendo e validando mapas; dataset baixado, recorte e pesos decididos |
| 07/11 | BFS/DFS/Dijkstra/BF com testes passando; G_est de m01–m08 + `arestas_*.csv`; EDA inicial do recorte |
| **10/11** | 1º acompanhamento (Grafos): Parte 1 rodando em todos os mapas |
| 14/11 | Métricas, camadas, comparação, armadilhas, m05/m06; casos obrigatórios da Parte 2 |
| **17/11** | Acompanhamento (Grafos + AVD): benchmark/escalabilidade; exploratórias prontas |
| **19/11** | Acompanhamento: figuras da Parte 1, mapas do grupo, explanatórias |
| **24/11** | Acompanhamento: HTML interativo, PDF em revisão, ensaio da apresentação (mapa surpresa rodado no terminal) |
| **26/11** | Entrega: link do GitHub + PDF + `docs/DECLARACAO_IA.pdf` (todos postam) |

---

## Parte 1 — tarefas

> Status da Parte 1 atualizado em 21/11/2026. Resumo, cronograma e pedidos da reunião de 19/11 (R1 a R8) em `PROXIMOS_PASSOS.md`.
> Enunciado e critérios em `docs/referencias/`.

### P1 · Modelagem (Matheus / rev. Thomaz)
- [x] `io.py`: ler mapa, ignorar linhas `;`, validar (retangular, 1 S, ≥1 G, símbolos conhecidos)
- [x] `estados.py`: G_pos (paredes + esteiras)
- [x] `estados.py`: G_est por exploração a partir de S (chaves, bônus numerados em ordem de leitura)
- [x] rótulo `(l,c)|chaves|{bônus}` e nó virtual `ALVO` (custo 0 a partir de G)
- [x] variantes: portas-como-chão, portas-como-parede, `+` fixo em −4, `--fonte-consumivel`
- [x] exportar `arestas_<mapa>.csv` (inclusive m08) via `executar_parte1` em `src/solve.py`
- [x] saídas versionadas nesta branch em `out/parte1/csv/`, `json/`, `figuras/` e `html/`
- [x] `test_io.py` e `test_estados.py` (mapa mínimo ≤5×7 contado à mão, esteira→parede, troca de camada)

### P2 · Algoritmos (Thomaz / rev. Davi)
- [x] `graph.py`: adjacência dirigida (ordem N, L, S, O), graus, densidade, transposto, subgrafo induzido
- [x] BFS com níveis/árvore · DFS com classificação de arcos e ciclo
- [x] Dijkstra (heapq) com recusa de peso negativo · Bellman-Ford com reconstrução do ciclo
- [x] testes dos 4 algoritmos (networkx só como oráculo em `tests/`)

### P3 · Análises (Matheus / rev. Thomaz)
- [x] `metricas_global.json` (G_pos e G_est, teto teórico, ocupação)
- [x] `camadas.json` (por conjunto de chaves + arcos entre camadas e casas que os geram)
- [x] `graus_<mapa>.csv`, maior grau de entrada/saída, multiplicidade máxima no m08, becos
- [x] `comparacao_modelagem.csv` (m02, m03, m04 × 3 modelagens)
- [x] m05: BF no G_pos (ciclo negativo) × G_est (sem ciclo) em `comparacao_bonus_m05.json`
- [ ] prova do m05 escrita no relatório
- [x] `solucoes.csv`, `percurso_m03.json`, `ciclo_negativo_m06.json`, `dfs_classificacao.csv`
- [x] `armadilhas_m04.csv`, `armadilhas_m07.csv` (busca a partir de ALVO no transposto)
- [x] **R1** implementação da CLI: `--mapa` roda `executar_parte1`, calcula armadilhas sem arquivo externo e
      compartilha resultados com figuras/HTML; resumo ao final e execução em lote por `--todos-mapas`/`--mapas`
- [ ] **R1** revisão por Davi em outra máquina e integração na `main`
- [ ] **R7** tempo e memória por algoritmo e mapa
- [x] 2 mapas em `data/mapas_grupo/`: `g01_tres_depositos.txt` e `g02_poco_lateral.txt`, com gabaritos TXT em
      `data/solucoes_mapas_grupo/` (commit `5b1eba5`, revisão/PR pendentes). Requisitos conferidos automaticamente
      com o código existente; execução pelo agente registrada em `REGISTRO_IA.md`.
- [ ] conferência final dos mapas e gabaritos pelo grupo e revisão por Thomaz
- [x] saídas CSV/JSON dos mapas do grupo em `out/parte1/csv/` e `out/parte1/json/`, junto das demais saídas
- [ ] textos do PDF: m01 (BFS × Dijkstra), m06 (exploit e correção), m07 (sem solução), grafo não dirigido estaria errado

### P5a · Visualização Parte 1 (Thomaz / rev. Matheus)
- [x] `percurso_m03.png`, `percurso_m08.png` (cor muda a cada chave)
- [x] G_est do m02 em camadas (destacar arcos entre camadas) · árvore BFS do m02 com níveis
- [x] heatmap de multiplicidade do m08
- [x] `labirinto_interativo.html`: mapa + algoritmo, passo a passo, estado atual, camadas, controle de velocidade
- [x] mapas do grupo incluídos no HTML gerado pelo Python e no React (commit `5b1eba5`, revisão/PR pendentes)
- [ ] **R2** HTML gerado pelo Python com as armadilhas de m04/m07 realçadas
      (os geradores e o HTML da entrega já contêm as armadilhas; falta conferir o realce visual com Thomaz)
- [x] (bônus) front React (`front-react/`) com labirinto, figuras e AVD
- [ ] **R3** comparação dos 4 algoritmos no mesmo mapa · **R4** upload de `.txt` pelo front

## Parte 2 — tarefas

### P4a · Dados (Davi / rev. Vagner)
- [x] script de download (`scripts/`) e recorte em `data/dataset_parte2/`
- [x] estratégia de amostragem documentada (≥ 20 mil arestas) — ver `PARTE2_DATASET.md`
- [x] design dos pesos (com negativos vindos dos dados) + significado de caminho mínimo e ciclo negativo
- [x] pergunta de pesquisa final
- [x] BFS/DFS de ≥3 fontes (ordem, camadas, ciclos) · Dijkstra ≥5 pares (transformação para pesos ≥0)
- [x] Bellman-Ford: 1 caso negativo sem ciclo + 1 com ciclo negativo detectado e exibido

### P4b · Experimentos (Vagner / rev. Davi)
- [ ] tempo médio de ≥5 execuções por algoritmo e tarefa: Dijkstra feito na branch `Vagner`, falta o PR
- [ ] **R7** memória por algoritmo e tarefa (opcional no enunciado, pedida na reunião de 19/11)
- [x] escalabilidade 10% / 50% / 100% × complexidade teórica
- [x] `out/parte2/parte2_report.json` e gráfico de tempo
- [ ] gráficos de comportamento e de caminhos (branch `Vagner`)
- [ ] **R5** fontes e pares da Parte 2 no front · **R6** view do grafo da Parte 2

### P5b · AVD (Vagner / rev. Davi)
- [x] notebook exploratório e 4 exploratórias em `out/parte2/avd/`
- [ ] exploração escrita no relatório: estrutural, distribucional, relacional, outliers
- [ ] dados faltantes: mecanismo de ausência + tratamento justificado (não apagar)
- [ ] multivariada: atributo-alvo × todos os demais
- [ ] ≥4 exploratórias + ≥2 explanatórias (1 responde à pergunta), com título/legenda/eixos
- [ ] nota analítica autoral por visualização + raciocínio exploratória → explanatória

## Fechamento (P5c · Davi)
- [ ] **R8** roteiro e slides da apresentação (modelagem, vértice/aresta, solução dos mapas, insights, desempenho, limitações)
- [ ] README final · PDF (manual + técnica + limitações + conclusões + matriz de contribuição)
- [ ] `docs/DECLARACAO_IA.pdf` assinada por **todos** + reflexão de 10–15 linhas
- [ ] conferir marcações `# [IA]` no código e `docs/REGISTRO_IA.md`
