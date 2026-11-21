# O que falta para terminar o projeto (atualizado em 21/11/2026)

Este arquivo é a lista oficial do que falta. Cada item da rubrica e do enunciado aparece com o que já existe, o que
falta, o critério para considerar pronto, o responsável e o prazo. Quando um item for concluído, marque `[x]` e
coloque o número do PR.

Base: [enunciado](referencias/Projeto_Final_TEORIADOSGRAFOS262-1.pdf), [critérios](referencias/CRITERIOS_PROJETO_2026-2.pdf)
e [reunião de 19/11](referencias/REUNIAO_2026-11-19.md). Roteiro da apresentação em [`APRESENTACAO.md`](APRESENTACAO.md).

## Datas que não mudam

| Dia | O que acontece |
|---|---|
| **24/11 (ter)** | Último acompanhamento (Grafos e AVD). A professora quer ver progresso real e sorteia quem reporta cada pacote |
| **26/11 (qui)** | Entrega no Classroom, feita por **cada um dos 4**, e apresentação da turma A (15 a 20 min, ordem por sorteio) |

Na apresentação a professora entrega um **mapa surpresa** e o grupo roda o próprio código no terminal e interpreta a
saída. Ela também escolhe quem apresenta, e a nota dessa pessoa vale para o grupo.

## Situação em 21/11

- `pytest`: 515 testes passando (507 na `main` + 8 do PR #38).
- PRs mergeados até aqui: 37. Aberto: #38 (roteiro e dados da Parte 2 para o front).
- Branches `matheus`, `thomaz` e `vagner-front` não têm nada além da `main`.
- O relatório tem **23 marcadores** `[A ESCREVER]`/`[COMPLETAR]`: 11 na Parte 1 (seção 4), 4 no manual e na
  implementação (2.2, 2.4, 2.5, 3), 2 na AVD, 5 de fechamento (7, 8, 9, 10.2, 11) e a nota do topo.
- `python -m scripts.gerar_pdf` já gera o PDF e lista os marcadores que faltam.

## O que zera nota se faltar

Estes itens não valem pontos isolados: sem eles, perde-se tudo ou um bloco inteiro.

| Item | Consequência se faltar | Situação | Responsável |
|---|---|---|---|
| `docs/DECLARACAO_IA.pdf` no modelo da professora, **assinada pelos 4** (manuscrita ou gov.br), também postada no Classroom | Nota **zero** no projeto | **Não existe.** Falta o modelo da professora | Davi consegue o modelo; os 4 assinam |
| Todo uso de IA declarado, com `# [IA]` no código e linha no `REGISTRO_IA.md` | Nota **zero** no projeto | Em dia até o PR #38. Cada PR novo precisa trazer a sua linha | Cada autor |
| Todo integrante sabe explicar qualquer código, inclusive o feito com IA | Nota **zero** no projeto | Depende do ensaio | Todos |
| Entregar as duas partes | Apresentação (2,0) **zerada** | As duas partes existem | — |
| Os 4 postam todo o material no Classroom em 26/11 | Desconto ou falta de entrega individual | — | Cada um |

## Checklist completo pela rubrica

### Parte 1: labirinto (3,0)

**Construção do grafo de estados (0,8)**
- [x] Leitura e validação dos mapas, G_pos, G_est por exploração, rótulo `(l,c)|chaves|{bônus}`, nó ALVO.
- [ ] `out/parte1/arestas_<mapa>.csv` de m01 a m08 e dos 2 mapas do grupo **commitados**. Hoje são gerados por
      `executar_parte1`, mas não estão no repositório.
  - Pronto quando: `git ls-files out/parte1/arestas_*.csv` lista 10 arquivos, inclusive o do m08.
  - Responsável: Matheus. Prazo: 22/11.

**Métricas, camadas e graus (0,4)**
- [x] Cálculo em `src/parte1/analises.py`.
- [ ] `metricas_global.json`, `camadas.json` e `graus_<mapa>.csv` commitados em `out/parte1/`.
- [ ] Relatório 4.4 e 4.5: tabela por mapa (ordem, tamanho, densidade, teto, ocupação), métricas por camada, arcos
      entre camadas e **por que são essas casas**, maior grau de entrada e de saída, multiplicidade máxima no m08,
      becos.
  - Responsável: Matheus. Prazo: 23/11.

**Comparação de modelagens e prova do m05 (0,4)**
- [x] `comparacao_modelagem.csv` e experimento do m05 gerados pelo código.
- [ ] Relatório 4.6: por que "porta como chão" gera caminho inválido e "porta como parede" falha.
- [ ] Relatório 4.7: ciclo negativo no G_pos do m05, ausência no G_est e a **prova escrita** (é proibido usar IA
      para escrevê-la).
  - Responsável: Matheus. Prazo: 23/11.

**Caminhos com os 4 algoritmos (0,8)**
- [x] BFS, Dijkstra com recusa, Bellman-Ford (m05 e ciclo do m06), DFS com classificação, armadilhas e
      `--fonte-consumivel` no código.
- [ ] `solucoes.csv`, `percurso_m03.json`, `ciclo_negativo_m06.json`, `dfs_classificacao.csv`, `armadilhas_m04.csv`
      e `armadilhas_m07.csv` commitados em `out/parte1/`.
- [ ] Relatório 4.8: discussão do m01 (BFS × Dijkstra), do m06 (correção da regra e resposta finita) e do m07 (prova
      pela busca e quantos estados são alcançáveis).
- [ ] Relatório 4.9: método das armadilhas (busca a partir de ALVO no transposto) e quantos estados são armadilha.
  - Responsável: Matheus (4.8 com Thomaz). Prazo: 23/11.

**Mapas do grupo (0,2)**
- [ ] `data/mapas_grupo/` com 2 mapas (hoje está **vazio**):
  1. pelo menos 3 chaves, esteiras e bônus, com o caminho de menor custo coletando um bônus e passando por uma esteira;
  2. pelo menos 20% dos estados alcançáveis sendo armadilha.
- [ ] Os dois rodados pelo código, com saídas em `out/parte1/`.
- [ ] Relatório 4.10: desenho de cada mapa e gabarito (estados, arcos, passos BFS e custo).
  - Não podem ser os mapas de `data/mapas_treino/`, nem parecidos com os de outro grupo.
  - Responsável: Matheus. Prazo: 22/11.

**Visualizações e HTML interativo (0,4)**
- [x] `percurso_m03.png`, `percurso_m08.png`, `camadas_m02.png`, `arvore_bfs_m02.png` e `heatmap_m08.png`.
- [x] `labirinto_interativo.html` com escolha de mapa e algoritmo, passo a passo, controle de velocidade e troca de
      camada.
- [ ] **Realce dos estados-armadilha no HTML (R2).** Hoje o HTML mostra "Não fornecidas" porque `gerar_figuras` não
      passa as armadilhas.
  - Pronto quando: abrir m04 e m07 no HTML e ver as armadilhas marcadas.
- [ ] Mapas do grupo incluídos no HTML.
- [ ] Relatório 4.11: as figuras com legenda e uma frase sobre o que cada uma mostra.
  - Responsável: Thomaz. Prazo: 23/11.

### Parte 2: Elliptic++ (3,0)

| Item | Peso | Situação |
|---|---|---|
| Proposta e descrição do dataset | 0,5 | Pronto (5.1, 5.2, graus, 6.1 a 6.3) |
| Implementação e casos obrigatórios | 0,9 | Pronto (3 fontes, 5 pares, Bellman-Ford com e sem ciclo) |
| Desempenho e escalabilidade | 0,5 | Pronto (5 execuções, 3 tamanhos, latência, memória e comparação com a complexidade, PR #37) |
| Discussão crítica | 0,4 | Pronto (5.7). Falta só a revisão final |
| Análise visual dos resultados | 0,3 | Pronto (escalabilidade, comportamento e caminhos) |

- [ ] Revisão final das seções 5.1 a 5.7: números iguais aos JSONs. Responsável: Davi. Prazo: 25/11.

### AVD (0,4 em Grafos + nota inteira de AVD)

- [x] 4 exploratórias em `out/parte2/avd/` e seções 6.1 a 6.4 (4 pilares, faltantes e mecanismo de ausência,
      outliers, multivariada com Spearman).
- [ ] **2 explanatórias** em `out/parte2/avd/`, nascidas de algo visto nas exploratórias. Pelo menos uma responde
      à pergunta de pesquisa.
- [ ] Relatório 6.5: o que foi encontrado na exploração, qual história contar, por que é a mais relevante e qual
      técnica de destaque foi usada.
- [ ] Relatório 6.6: nota analítica autoral de cada explanatória (o que mostra, insight, por que esse gráfico) e
      justificativa dos atributos pré-atentivos.
- [ ] Conferir título, legenda e eixos nas 6 figuras. Pizza e radar só com justificativa forte.
  - Responsável: Vagner. Prazo: 23/11.
  - A IA não pode escolher o gráfico, os destaques ou a história, nem interpretar os gráficos.

### Apresentação e participação (2,0)

| Item | Peso | O que falta | Responsável | Prazo |
|---|---|---|---|---|
| Participação nos acompanhamentos | 0,5 | Ir ao de 24/11 com progresso real. Cada um precisa saber reportar qualquer pacote | Todos | 24/11 |
| Clareza da apresentação | 0,3 | Slides a partir do roteiro, preencher os blocos `[A PREENCHER]` do `APRESENTACAO.md` e ensaiar com cronômetro (15 a 20 min) | Davi (slides), dono de cada bloco | 24/11 |
| Domínio conceitual | 0,5 | Cada um estuda as partes que não fez e responde por escrito as perguntas previstas no roteiro | Todos | 25/11 |
| Demonstração ao vivo (mapa surpresa) | 0,4 | **R1**: a CLI tem que rodar um mapa qualquer de ponta a ponta (ver abaixo). Ensaiar com `data/mapas_treino/` | Matheus | 22/11 |
| Participação equilibrada | 0,3 | Todos já têm commits em 2 ou mais pacotes. Atualizar a matriz da seção 10.2 na véspera | Davi | 25/11 |

Regras da professora: falas divididas ("cada um fala da sua parte") ou leitura mecânica têm redução severa de nota. Se
alguém parar de contribuir, o grupo tem que avisar a professora por e-mail **antes** da entrega.

### Código, repositório, relatório e IA (2,0)

| Item | Peso | O que falta | Responsável | Prazo |
|---|---|---|---|---|
| Organização do repositório | 0,3 | Pronto. Conferir no fim se `out/parte1/` tem todas as saídas | Davi | 25/11 |
| Qualidade do código | 0,4 | Pronto. Corrigir os acentos quebrados no terminal do Windows junto com o R1 | Matheus | 22/11 |
| Testes obrigatórios | 0,4 | Pronto (BFS, DFS, Dijkstra, Bellman-Ford, estados com mapa mínimo, IO). Atualizar a contagem na seção 7 | Davi | 25/11 |
| README | 0,2 | Comando do mapa surpresa em destaque (depende do R1) e revisão geral | Davi | 25/11 |
| PDF técnico | 0,4 | Fechar os 23 marcadores, gerar o PDF e conferir figuras e tabelas | Davi junta; cada dono escreve | 25/11 |
| Declaração e uso responsável de IA | 0,3 | Declaração assinada, reflexão de 10 a 15 linhas do grupo, `REGISTRO_IA.md` completo | Davi organiza; todos assinam e escrevem | 25/11 |

### Bônus visual/UX (até +1,0)

Pedidos da reunião que contam aqui. Não são obrigatórios, mas a professora pediu.

| # | Pedido | Situação | Responsável |
|---|---|---|---|
| R3 | Os 4 algoritmos ao mesmo tempo no mesmo mapa | Não começado | Thomaz |
| R4 | Upload de `.txt` pelo front (rota do Vite que já existe, validação pelo `io.py`, erro claro) | Não começado | Thomaz |
| R5 | Parte 2 no front: fontes e pares com caminho, custo, camadas e tempo | Dados prontos em `front-react/src/parte2.json` (PR #38). Falta a tela | Vagner |
| R6 | View do grafo da Parte 2, colorida por classe | Recortes prontos no mesmo JSON. Falta a tela | Vagner |

## R1: o que a CLI precisa fazer

É o item mais arriscado, porque a demonstração ao vivo depende dele. Hoje `--mapa` só gera o PNG e uma linha de
status, `--armadilhas` exige um JSON pronto e nenhum comando chama `executar_parte1`.

- [ ] `python -m src.cli --mapa <arquivo> --out <pasta>` gera todas as saídas daquele mapa: arestas, métricas, graus,
      soluções dos 4 algoritmos, DFS, armadilhas e figura. Sem `--alg`, roda os quatro.
- [ ] `--alg BFS|DFS|DIJKSTRA|BELLMAN_FORD` imprime no terminal passos, custo, status e caminho.
- [ ] `--armadilhas` calcula as armadilhas sozinho, sem `--arquivo-armadilhas`, para qualquer mapa (não só m04/m07).
- [ ] `--fonte-consumivel` e `--interactive` continuam funcionando.
- [ ] Mapa inválido dá mensagem clara, sem traceback.
- [ ] Acentos corretos no terminal do Windows (`sys.stdout.reconfigure(encoding="utf-8")`).
- [ ] Um comando que gera tudo de `data/mapas/` e `data/mapas_grupo/` em `out/parte1/`.
- [ ] Testado com os mapas de `data/mapas_treino/`. As respostas têm que bater com o gabarito do README da pasta.
- [ ] Revisado por Davi rodando a CLI numa máquina diferente da do Matheus.

## Marcadores do relatório

| Seção | Responsável | O que falta |
|---|---|---|
| Topo | Davi | Apagar a nota "Como usar este esqueleto" no fechamento |
| 2.2 | Matheus | Comando que gera as saídas da Parte 1 (depende do R1) |
| 2.4 | Thomaz | Como abrir o `labirinto_interativo.html` e o que cada controle faz |
| 2.5 | Vagner | Uma frase sobre o front e uma captura de tela |
| 3 | Thomaz | Decisões de implementação (classificação dos arcos na DFS, recusa do Dijkstra, ciclo no Bellman-Ford) |
| 4.1 | Matheus | Nó em cada grafo, rótulo, numeração dos bônus, G_est do m02 desenhado à mão |
| 4.2 | Matheus | Por que o grafo tem que ser dirigido (esteiras e chave) |
| 4.3 | Matheus | Mapa mínimo de `tests/test_estados.py` com estados e arcos contados à mão |
| 4.4 | Matheus | Tabela de métricas e comentário, arcos entre camadas e por que são essas casas |
| 4.5 | Matheus | Graus, multiplicidade no m08 e becos |
| 4.6 | Matheus | Por que (a) gera caminho inválido e (b) falha |
| 4.7 | Matheus | Resultado do m05 e a prova |
| 4.8 | Matheus e Thomaz | Discussões de m01, m06 e m07 |
| 4.9 | Matheus | Método e contagem das armadilhas |
| 4.10 | Matheus | Desenho e gabarito dos mapas do grupo |
| 4.11 | Thomaz | Figuras com legenda e uma frase cada |
| 6.5 | Vagner | Da exploratória à explanatória |
| 6.6 | Vagner | Explanatórias 1 e 2 com nota analítica |
| 7 | Davi | Contagem de testes na véspera |
| 8 | Todos | Limitações da Parte 1 (a da Parte 2 já está escrita) |
| 9 | Todos | Conclusões |
| 10.2 | Davi | Rodar `python -m scripts.matriz_contribuicao --revisoes` e colar as tabelas |
| 11 | Todos | Reflexão do grupo sobre o uso de IA (10 a 15 linhas, pedida pela rubrica) |

## Cronograma

| Até | Entrega |
|---|---|
| **22/11 (dom)** | R1 na `main`; mapas do grupo; saídas de `out/parte1/` commitadas; R2 |
| **23/11 (seg)** | Seções 4.1 a 4.11, 2.4, 3, 6.5 e 6.6 escritas; 2 explanatórias; R3 a R6 se der tempo; modelo da declaração em mãos |
| **24/11 (ter)** | Acompanhamento. Antes: ensaio cronometrado. Na aula: cada um roda um mapa de treino no terminal |
| **25/11 (qua)** | Seções 8, 9 e 11; relatório congelado e PDF gerado; declaração assinada pelos 4; README final; matriz e testes atualizados |
| **26/11 (qui)** | Os 4 postam no Classroom e apresentam |

## Checklist por pessoa

### Matheus (P1 + P3, revisor: Thomaz)
- [ ] R1 completo (lista acima) — 22/11
- [ ] 2 mapas do grupo com gabarito — 22/11
- [ ] Todas as saídas de `out/parte1/` commitadas — 22/11
- [ ] R7 da Parte 1: tempo e memória por algoritmo e mapa (pode reaproveitar `src/benchmark.py`) — 23/11
- [ ] Seções 2.2 e 4.1 a 4.10, com o G_est do m02 desenhado à mão e a prova do m05 — 23/11
- [ ] Blocos 2 a 5 e 9 (Parte 1) do `APRESENTACAO.md` — 24/11
- [ ] Limitações da Parte 1 (seção 8) — 25/11

### Thomaz (P2 + P5a, revisor: Matheus)
- [ ] R2: armadilhas e mapas do grupo no `labirinto_interativo.html` — 22/11
- [ ] Seções 2.4, 3, 4.8 (com Matheus) e 4.11 — 23/11
- [ ] R3 e R4 no front — 23/11
- [ ] Bloco 6 do `APRESENTACAO.md`, com plano B se o front falhar — 24/11

### Vagner (P4b + P5b, revisor: Davi)
- [ ] 2 explanatórias e seções 6.5 e 6.6 — 23/11
- [ ] Seção 2.5 (frase e captura do front) — 23/11
- [ ] R5 e R6 lendo `front-react/src/parte2.json` — 23/11
- [ ] Bloco 10 do `APRESENTACAO.md` — 24/11

### Davi (P4a + P5c)
- [ ] Mergear o PR #38 depois da aprovação
- [ ] Conseguir com a professora o modelo da declaração de IA — 23/11
- [ ] Revisar o R1 rodando os mapas de treino — 22/11
- [ ] Slides a partir do roteiro — 24/11
- [ ] Revisar os PRs de Vagner (P4b/P5b)
- [ ] README final, seções 7 e 10.2, revisão da Parte 2, apagar a nota do esqueleto — 25/11
- [ ] Juntar o relatório, gerar o PDF com `python -m scripts.gerar_pdf` (zero marcadores) — 25/11
- [ ] Declaração preenchida com o registro e assinada pelos 4 em `docs/DECLARACAO_IA.pdf` — 25/11

### Todos
- [ ] Escrever juntos as seções 8 (Parte 1), 9 e 11 — 25/11
- [ ] Estudar o que não fez: modelagem do estado, prova do m05, correção do m06, por que o m07 não tem solução,
      vértice e aresta na Parte 2, pesos, pergunta de pesquisa, cada gráfico da AVD
- [ ] Saber rodar a CLI num mapa novo
- [ ] Assinar a declaração
- [ ] Postar no Classroom em 26/11

## Checklist da entrega (26/11)

Cada integrante posta no Classroom:

- [ ] link do repositório (`https://github.com/davimqz/Projetos-Grafos`)
- [ ] PDF do relatório (manual + parte técnica)
- [ ] `docs/DECLARACAO_IA.pdf` assinada pelos 4
- [ ] o que mais a professora pedir no Classroom (código e saídas já estão no repositório)

Antes de postar, conferir na `main`:

- [ ] `pytest` passando
- [ ] `out/parte1/` com todas as saídas da seção "Saídas obrigatórias" do enunciado
- [ ] `out/parte2/parte2_report.json` e as figuras da Parte 2 e da AVD
- [ ] `python -m scripts.gerar_pdf` sem marcadores pendentes
- [ ] README com o comando do mapa surpresa

## Ambiente

```bash
git clone https://github.com/davimqz/Projetos-Grafos.git
cd Projetos-Grafos
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest
```

O recorte da Parte 2 já está no repositório, então **não é preciso baixar o dataset** (só para refazer o recorte).

## Fluxo de trabalho

1. Uma branch por tarefa.
2. Commits no padrão `tipo(escopo): descrição`.
3. PR para `main` marcando o **revisor do pacote** (ver `PLANO_DE_TRABALHO.md`). O revisor aprova e faz o merge.
4. Todo PR com uso de IA traz a linha no `REGISTRO_IA.md` e o `# [IA]` no código.
