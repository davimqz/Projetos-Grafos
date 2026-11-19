# Próximos passos (atualizado em 19/11/2026)

Entrega em **26/11** (todos postam no Classroom). Último acompanhamento: **24/11**. Apresentação de 15 a 20 min com
**mapa surpresa rodado ao vivo no terminal**.

Documentos de base em `docs/referencias/`: enunciado, critérios de avaliação, mapas originais e a
[reunião de 19/11](referencias/REUNIAO_2026-11-19.md) com os pedidos novos da professora.
Checklist completo por pacote em `PLANO_DE_TRABALHO.md`.

## Situação em 19/11

`pytest`: 477 testes passando. A tabela compara o que o enunciado e a rubrica pedem com o que está na `main`.

| Item da rubrica | Peso | Situação |
|---|---|---|
| Construção do grafo de estados (P1) | 0,8 | Pronto no código. Os `arestas_<mapa>.csv` são gerados por `executar_parte1`, mas **não estão em `out/parte1/`** e nenhum comando da CLI chama essa função |
| Métricas, camadas e graus (P3) | 0,4 | Pronto no código (`src/parte1/analises.py`). Saídas fora do repositório e texto do relatório vazio |
| Comparação de modelagens e prova do m05 (P3) | 0,4 | CSV e experimento do m05 gerados. **Falta a prova escrita** |
| Caminhos com os 4 algoritmos (P3) | 0,8 | `solucoes.csv`, DFS, armadilhas e ciclo do m06 gerados. Faltam as discussões de m01, m06 e m07 |
| Mapas do grupo | 0,2 | **Não começado**: `data/mapas_grupo/` está vazio |
| Visualizações e HTML interativo (P5a) | 0,4 | As 5 figuras estão prontas. O `labirinto_interativo.html` **não realça as armadilhas** (`gerar_figuras` não as passa) |
| Proposta e descrição do dataset (P4a) | 0,5 | Pronto (seção 5.1 do relatório, distribuição de graus incluída) |
| Implementação e casos obrigatórios da Parte 2 | 0,9 | Pronto (3 fontes, 5 pares, BF com e sem ciclo) |
| Desempenho e escalabilidade (P4b) | 0,5 | Dijkstra e figuras de comportamento e caminhos na branch `Vagner`, **ainda sem PR**. Falta memória (pedida na reunião) |
| Discussão crítica | 0,4 | Seções 5.7 e 8 (Parte 2) escritas; falta a Parte 1 nas limitações |
| Análise visual dos resultados | 0,3 | Depende do merge da branch `Vagner` |
| AVD (≥4 exploratórias + ≥2 explanatórias) | 0,4 + nota AVD | 4 exploratórias em `out/parte2/avd/`. **Faltam as 2 explanatórias, as notas analíticas e toda a seção 6 do relatório** |
| Demonstração ao vivo (mapa surpresa) | 0,4 | **Risco**: a CLI com `--mapa` não gera as saídas obrigatórias, e `--armadilhas` exige um JSON pronto |
| PDF técnico | 0,4 | Esqueleto em `docs/relatorio/RELATORIO.md`. Parte 1 e AVD vazias |
| Declaração de IA assinada | 0,3 | **Falta `docs/DECLARACAO_IA.pdf`.** Sem ela, a nota do projeto é zero |
| Participação equilibrada | 0,3 | Todos têm commits em 2+ pacotes. Vagner tem poucos na `main` (12); o merge da branch dele ajuda |
| Bônus visual/UX | +1,0 | O React tem labirinto, figuras e AVD. Os pedidos da reunião (comparação lado a lado, upload, Parte 2) contam aqui |

> **Regra da professora:** `io.py`, `estados.py`, `graph.py` e `algorithms.py` **não podem ser gerados por IA**.
> Também não podem as análises, as notas analíticas, a escolha e a interpretação de gráficos e a prova do m05.
> Todo uso de IA vai em `docs/REGISTRO_IA.md`, com `# [IA]` no código.

## Pedidos da reunião de 19/11

Detalhes e interpretação em [`referencias/REUNIAO_2026-11-19.md`](referencias/REUNIAO_2026-11-19.md).

| # | Pedido | Responsável |
|---|---|---|
| R1 | CLI completa para o mapa surpresa: um comando gera todas as saídas e o HTML de um mapa qualquer | Matheus |
| R2 | O Python gera o `labirinto_interativo.html` em `out/` (com armadilhas); o React continua como interface extra | Thomaz |
| R3 | Comparação de todos os algoritmos ao mesmo tempo no mesmo mapa | Thomaz |
| R4 | Upload de `.txt` pelo front | Thomaz |
| R5 | Parte 2 no front: fontes de BFS/DFS e pares de Dijkstra/Bellman-Ford, com resultado de cada um | Vagner |
| R6 | View do grafo da Parte 2 | Vagner |
| R7 | Desempenho por algoritmo e tarefa: tempo, latência e memória | Vagner (Parte 2) e Matheus (Parte 1) |
| R8 | Apresentação: modelagem (G_pos e G_est desenhados), vértice e aresta, solução dos mapas, visualizações com insight, limitações P1/P2, desempenho | Davi (roteiro e slides), todos (conteúdo) |

## Cronograma até a entrega

| Até | O que precisa estar pronto |
|---|---|
| **21/11 (sex)** | R1 na `main` e `out/parte1/` com todas as saídas commitadas; mapas do grupo; PR da branch `Vagner` revisado e mergeado |
| **23/11 (dom)** | R2 a R7; seções da Parte 1 e da AVD do relatório escritas; explanatórias prontas |
| **24/11 (ter)** | Acompanhamento: ensaio completo com cronômetro, e cada um roda um mapa surpresa no terminal |
| **25/11 (qua)** | Relatório congelado e exportado em PDF; declaração assinada por todos; README final |
| **26/11 (qui)** | Todos postam no Classroom: link do repositório, PDF e declaração |

## Ambiente

```bash
git clone https://github.com/davimqz/Projetos-Grafos.git
cd Projetos-Grafos
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest          # 477 testes passando em 19/11
```

O recorte da Parte 2 já está no repositório, então **não é preciso baixar o dataset** (só para refazer o recorte).

## Fluxo de trabalho

1. Uma branch por tarefa.
2. Commits no padrão `tipo(escopo): descrição`.
3. PR para `main` marcando o **revisor do pacote** (ver `PLANO_DE_TRABALHO.md`). O revisor aprova e faz o merge.

---

## Matheus: P1 + P3 (revisor: Thomaz) · prioridade: mapa surpresa

- [x] `io.py`, `estados.py`, G_pos/G_est, variantes e testes
- [x] `src/parte1/` + `executar_parte1`: arestas, métricas, camadas, graus, comparação, m05, soluções, DFS, armadilhas
- [ ] **R1** ligar `executar_parte1` à CLI. `python -m src.cli --mapa <arquivo> --out <pasta>` deve gerar todas as
      saídas daquele mapa (sem `--alg`, roda os quatro). `--armadilhas` deve calcular as armadilhas sozinho, sem
      `--arquivo-armadilhas`. Testar com um mapa que não seja m01–m08
- [ ] comando único que gera tudo de `data/mapas/` e `data/mapas_grupo/` em `out/parte1/`, e commitar as saídas
- [ ] 2 mapas em `data/mapas_grupo/`: (1) ≥3 chaves, esteira e bônus no caminho ótimo; (2) ≥20% de armadilhas.
      Gabarito: estados, arcos, passos e custo
- [ ] **R7 (Parte 1)** tempo e memória de cada algoritmo por mapa (pode reaproveitar `src/benchmark.py`)
- [ ] relatório, seções 4.1 a 4.10: modelagem com o G_est do m02 desenhado à mão, grafo dirigido, mapa mínimo, tabelas
      preenchidas, **prova do m05**, discussões de m01/m06/m07, armadilhas, mapas do grupo
- [ ] limitações da Parte 1 (seção 8)

## Thomaz: P2 + P5a (revisor: Matheus)

- [x] `graph.py`, `algorithms.py` e testes
- [x] percursos m03/m08, camadas e árvore BFS do m02, heatmap do m08, HTML interativo
- [ ] **R2** `labirinto_interativo.html` gerado pelo Python com as armadilhas de m04/m07 realçadas (passar
      `encontrar_armadilhas` em `gerar_figuras`/`gerar_html_conjunto`) e incluindo os mapas do grupo
- [ ] **R3** comparação dos 4 algoritmos no mesmo mapa (React e, se der, no HTML): percursos sobrepostos ou lado a lado, com
      passos, custo e status de cada um
- [ ] **R4** upload de `.txt` no React: enviar para o gerador local (já existe a rota do Vite usada no "Gerar HTML"),
      validar com o `io.py` e mostrar o erro claro quando o mapa for inválido
- [ ] relatório, seção 4.11: figuras com legenda e uma frase sobre o que cada uma mostra

## Vagner: P4b + P5b (revisor: Davi)

- [x] benchmark de BFS, DFS e Bellman-Ford, escalabilidade 10/50/100%
- [x] notebook exploratório e 4 exploratórias
- [ ] **abrir PR da branch `Vagner`** (Dijkstra no benchmark e figuras de comportamento e caminhos)
- [ ] **R7 (Parte 2)** memória por algoritmo e tarefa (`tracemalloc`) no `parte2_report.json`, junto com o tempo médio
- [ ] **R5** aba da Parte 2 no React: lista das 3 fontes (BFS/DFS) e dos 5 pares (Dijkstra) + casos do Bellman-Ford,
      com caminho, custo, camadas e tempo de cada execução (dados exportados por `scripts/exportar_front.py`)
- [ ] **R6** view do grafo da Parte 2: subgrafo em volta das fontes ou dos caminhos, colorido por classe
- [ ] 2 explanatórias (uma responde à pergunta de pesquisa), nascidas de algo visto nas exploratórias
- [ ] nota analítica autoral para cada uma das 6 visualizações (o que mostra, insight, por que esse gráfico)
- [ ] relatório, seção 6 inteira: 4 pilares, faltantes e outliers, multivariada, exploratória → explanatória

## Davi: P4a + P5c

- [x] carga do recorte, casos obrigatórios, distribuição de graus e seções 5.1 a 5.7 do relatório
- [x] documentos de referência em `docs/referencias/` e reunião de 19/11 registrada
- [ ] revisar e mergear o PR do Vagner; revisar R1 (Matheus) testando a CLI com um mapa novo
- [ ] **R8** roteiro da apresentação (15 a 20 min) e slides: vértice e aresta nas duas partes, modelagem, solução dos
      mapas, figuras com insight, desempenho, limitações, resposta à pergunta de pesquisa
- [ ] preparar 2 ou 3 mapas surpresa de treino (diferentes dos nossos) para o ensaio de 24/11
- [ ] README final: comando do mapa surpresa em destaque, front React e `docs/referencias/`
- [ ] PDF: juntar as seções, matriz de contribuição (10.2 com commits reais), testes atualizados, conclusões
- [ ] `docs/DECLARACAO_IA.pdf` com a reflexão de 10 a 15 linhas, assinada por **todos**; conferir `# [IA]` e `REGISTRO_IA.md`

## Para todos antes de 26/11

A professora escolhe na hora quem apresenta, e a nota dessa pessoa vale para o grupo. Todo mundo precisa saber
explicar a modelagem do estado, a prova do m05, a correção do m06, por que o m07 não tem solução, o que é vértice e
aresta na Parte 2, a pergunta de pesquisa e cada gráfico da AVD. Cada um também precisa saber rodar a CLI num mapa novo.
