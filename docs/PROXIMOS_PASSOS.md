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

- `pytest`: 553 testes passando na última execução local desta branch em 21/11/2026.
- PRs mergeados até aqui: 37. Aberto: #38 (roteiro e dados da Parte 2 para o front).
- Branches `matheus`, `thomaz` e `vagner-front` não têm nada além da `main`.
- `pytest`: 515 testes passando na `main`.
- PRs mergeados até aqui: 38 (o #38 trouxe o roteiro e o `parte2.json` do front). Aberto: **#39 do Vagner**
  (exploratória 2 refeita, explanatórias 1 e 2, tabela de outliers por classe na 6.2), esperando revisão do Davi.
- Branches `matheus`, `thomaz`, `vagner-front` e `vagner-labirinto` não têm nada além da `main`. Matheus e Thomaz
  ainda não subiram nada desde a reunião de 19/11.
- O relatório tem **23 marcadores** `[A ESCREVER]`/`[COMPLETAR]`: 11 na Parte 1 (seção 4), 4 no manual e na
  implementação (2.2, 2.4, 2.5, 3), 2 na AVD (6.5 e 6.6), 5 de fechamento (7, 8, 9, 10.2, 11) e a nota do topo. O #39
  já preenche boa parte da 6.6, mas o marcador continua lá.
- `python -m scripts.gerar_pdf` já gera o PDF e lista os marcadores que faltam.
- Nesta branch, os dois mapas do grupo, seus gabaritos TXT e a integração ao HTML/React estão no commit
  `5b1eba5`. Foram verificados com 157 testes selecionados, build do React e geração das cinco figuras P5a.
  Revisão por Thomaz e integração na `main` permanecem pendentes; ainda não há número de PR registrado aqui.
- CLI R1 implementada nesta branch: exportações completas, armadilhas automáticas, figuras/HTML compartilhando
  resultados e resumo ao final. Fluxo conferido nos dez mapas e nos cinco mapas de treino, incluindo o inválido.
  Falta a revisão por Davi em outra máquina. As saídas geradas pelo usuário foram organizadas por tipo em
  `out/parte1/csv/`, `json/`, `figuras/` e `html/`, com a mesma estrutura em `fonte_consumivel/`.
- Conferido de novo no repositório na tarde de 21/11:
  - `out/parte1/` só tem as 5 figuras e o HTML. Nenhum CSV ou JSON da Parte 1 está commitado.
  - `data/mapas_grupo/` continua só com o `.gitkeep`.
  - `src/cli.py` não mudou: `--mapa` chama só `gerar_mapa`, `--armadilhas` ainda exige `--arquivo-armadilhas` e
    nada chama `executar_parte1`.
  - O front não tem tela da Parte 2 (nenhum componente lê `parte2.json`), nem upload de `.txt`, nem os 4 algoritmos
    lado a lado.
  - `docs/DECLARACAO_IA.pdf` não existe.
  - `APRESENTACAO.md` tem 7 blocos `[A PREENCHER]`: 2, 3, 4, 5 e 9 (Matheus), 6 (Thomaz) e 10 (Vagner).

## Riscos agora

1. **Matheus concentra o caminho crítico.** R1, mapas do grupo, saídas da Parte 1 e 11 dos 23 marcadores do relatório
   dependem dele, inclusive a demonstração ao vivo, que vale 0,4 e é o momento de maior risco da apresentação. Nada
   dele entrou desde 19/11. Precisa dizer hoje (21/11) no grupo o que consegue entregar até 22/11 à noite. Se o R1 não
   estiver na `main` até lá, o grupo divide o R1 no dia 23 (por exemplo: Davi faz as armadilhas automáticas e os
   acentos, Matheus faz a orquestração com `executar_parte1`).
2. **Thomaz sem entrega desde 18/11.** O R2 (armadilhas no HTML) é obrigatório. R3 e R4 são bônus e saem antes do R2
   se faltar tempo.
3. **Declaração de IA.** Sem ela o projeto leva zero, e ainda falta o modelo da professora. Pedir hoje por e-mail ou
   Classroom, sem esperar o dia 24.
4. **Conflitos de merge.** O #39 e o #40 mexem no fim do `REGISTRO_IA.md`. Mergear o #39 primeiro e atualizar o #40
   em seguida.

## O que zera nota se faltar

Estes itens não valem pontos isolados: sem eles, perde-se tudo ou um bloco inteiro.

| Item | Consequência se faltar | Situação | Responsável |
|---|---|---|---|
| `docs/DECLARACAO_IA.pdf` no modelo da professora, **assinada pelos 4** (manuscrita ou gov.br), também postada no Classroom | Nota **zero** no projeto | **Não existe.** Falta o modelo da professora | Davi consegue o modelo; os 4 assinam |
| Todo uso de IA declarado, com `# [IA]` no código e linha no `REGISTRO_IA.md` | Nota **zero** no projeto | Registros até o PR #38 e desta sessão da Parte 1, incluindo a feature dos mapas (`5b1eba5`). Cada PR novo precisa trazer a sua linha | Cada autor |
| Todo integrante sabe explicar qualquer código, inclusive o feito com IA | Nota **zero** no projeto | Depende do ensaio | Todos |
| Entregar as duas partes | Apresentação (2,0) **zerada** | As duas partes existem | — |
| Os 4 postam todo o material no Classroom em 26/11 | Desconto ou falta de entrega individual | — | Cada um |

## Checklist completo pela rubrica

### Parte 1: labirinto (3,0)

**Construção do grafo de estados (0,8)**
- [x] Leitura e validação dos mapas, G_pos, G_est por exploração, rótulo `(l,c)|chaves|{bônus}`, nó ALVO.
- [x] `out/parte1/csv/arestas_<mapa>.csv` de m01 a m08 e dos 2 mapas do grupo versionados nesta branch,
      gerados pelo usuário e organizados por tipo de arquivo.
  - Pronto quando: `git ls-files out/parte1/csv/arestas_*.csv` lista 10 arquivos, inclusive o do m08.
  - Responsável: Matheus. Prazo: 22/11.

**Métricas, camadas e graus (0,4)**
- [x] Cálculo em `src/parte1/analises.py`.
- [x] `metricas_global.json` e `camadas.json` em `out/parte1/json/`, e `graus_<mapa>.csv` em
      `out/parte1/csv/`, versionados nesta branch.
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
- [x] `solucoes.csv`, `dfs_classificacao.csv` e `armadilhas_<mapa>.csv` em `out/parte1/csv/`; percursos,
      ciclo do m06 e comparação de bônus do m05 em `out/parte1/json/`, versionados nesta branch.
- [ ] Relatório 4.8: discussão do m01 (BFS × Dijkstra), do m06 (correção da regra e resposta finita) e do m07 (prova
      pela busca e quantos estados são alcançáveis).
- [ ] Relatório 4.9: método das armadilhas (busca a partir de ALVO no transposto) e quantos estados são armadilha.
  - Responsável: Matheus (4.8 com Thomaz). Prazo: 23/11.

**Mapas do grupo (0,2)**
- [x] Dois mapas em `data/mapas_grupo/` (commit `5b1eba5`, revisão/PR pendentes):
  1. `g01_tres_depositos.txt`: 3 chaves; o percurso de menor custo retornado pelo código coleta 2 bônus e passa
     por 3 esteiras. G_est: 104 estados e 194 arcos físicos; BFS: 48 passos; Bellman-Ford: custo 38.
  2. `g02_poco_lateral.txt`: 75 de 94 estados são armadilha (79,79%). G_est: 94 estados e 230 arcos físicos;
     BFS: 18 passos; menor custo: 18.
- [x] Execução pelo agente das funções existentes do grupo e gabaritos com métricas, status e caminhos em
      `data/solucoes_mapas_grupo/solucao_<mapa>.txt` (commit `5b1eba5`; uso descrito em `REGISTRO_IA.md`).
- [ ] Conferência final dos mapas e gabaritos pelo grupo, incluindo originalidade em relação aos outros grupos.
- [x] CSVs/JSONs definitivos dos dois mapas em `out/parte1/csv/` e `out/parte1/json/`, junto das saídas
      obrigatórias dos mapas fornecidos, versionados nesta branch.
- [ ] Relatório 4.10: desenho de cada mapa e gabarito (estados, arcos, passos BFS e custo).
  - Não podem ser os mapas de `data/mapas_treino/`, nem parecidos com os de outro grupo.
  - Responsável: Matheus. Prazo: 22/11.

**Visualizações e HTML interativo (0,4)**
- [x] `percurso_m03.png`, `percurso_m08.png`, `camadas_m02.png`, `arvore_bfs_m02.png` e `heatmap_m08.png`.
- [x] `labirinto_interativo.html` com escolha de mapa e algoritmo, passo a passo, controle de velocidade e troca de
      camada.
- [ ] **Realce dos estados-armadilha no HTML (R2).** Os geradores já recebem as armadilhas calculadas pelo código.
      O HTML da entrega já contém esses dados; falta conferir o realce visual com Thomaz.
  - Pronto quando: abrir m04 e m07 no HTML e ver as armadilhas marcadas.
- [x] Mapas do grupo incluídos no HTML e na seleção do React (commit `5b1eba5`, revisão/PR pendentes).
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
      outliers, multivariada com Spearman). No #39 a exploratória 2 virou "transações por quantidade de arestas
      geradas", a 6.2 ganhou a tabela de outliers por classe (só limite superior no grau de saída) e a 6.4 explica o
      peso como saldo da carteira de destino.
- [ ] **2 explanatórias** em `out/parte2/avd/` (PR #39, falta mergear):
  1. `explanatoria_arestas_por_transacao.png`: 84,5% das transações geram de 1 a 10 arestas, mas os 15,5% restantes
     respondem por 84,4% das arestas. Vem da exploratória 2. Tem nota analítica e justificativa.
  2. `explanatoria_2.png`: dot plot da proporção de arestas com peso positivo por classe do destino, lícitas em
     verde. Vem da exploratória 4. Tem só a justificativa do gráfico.
- [ ] Explanatória 2: escrever o que o gráfico mostra, com as porcentagens de cada classe, e o insight. Hoje a 6.6 só
      diz por que é um dot plot.
- [ ] Dizer na 6.6 qual das duas responde à pergunta de pesquisa e ligar isso à Parte 2 (pesos e caminhos).
- [ ] Revisar o último parágrafo da explanatória 1 ("é uma forma de utlizar barras no eixo x,y..."), que está confuso
      e com erro de digitação, e citar os atributos pré-atentivos pelo nome (cor, comprimento, posição).
- [ ] Apagar o marcador `[A ESCREVER — Vagner]` da 6.6 quando fechar os itens acima.
- [ ] Renomear `explanatoria_arestas_por_transacao.png` para `explanatoria_1.png`, para ficar no mesmo padrão.
- [ ] Relatório 6.5: o que foi encontrado na exploração, qual história contar, por que é a mais relevante e qual
      técnica de destaque foi usada. **Ainda não começada.**
- [ ] Conferir título, legenda e eixos nas 6 figuras. Pizza e radar só com justificativa forte.
  - Responsável: Vagner (revisor: Davi). Prazo: 23/11.
  - A IA não pode escolher o gráfico, os destaques ou a história, nem interpretar os gráficos.

### Apresentação e participação (2,0)

| Item | Peso | O que falta | Responsável | Prazo |
|---|---|---|---|---|
| Participação nos acompanhamentos | 0,5 | Ir ao de 24/11 com progresso real. Cada um precisa saber reportar qualquer pacote | Todos | 24/11 |
| Clareza da apresentação | 0,3 | Slides a partir do roteiro, preencher os blocos `[A PREENCHER]` do `APRESENTACAO.md` e ensaiar com cronômetro (15 a 20 min) | Davi (slides), dono de cada bloco | 24/11 |
| Domínio conceitual | 0,5 | Cada um estuda as partes que não fez e responde por escrito as perguntas previstas no roteiro | Todos | 25/11 |
| Demonstração ao vivo (mapa surpresa) | 0,4 | **R1** implementado e verificado localmente com os mapas de treino. Falta revisão por Davi em outra máquina e ensaio do grupo | Matheus | 22/11 |
| Participação equilibrada | 0,3 | Todos já têm commits em 2 ou mais pacotes. Atualizar a matriz da seção 10.2 na véspera | Davi | 25/11 |

Regras da professora: falas divididas ("cada um fala da sua parte") ou leitura mecânica têm redução severa de nota. Se
alguém parar de contribuir, o grupo tem que avisar a professora por e-mail **antes** da entrega.

### Código, repositório, relatório e IA (2,0)

| Item | Peso | O que falta | Responsável | Prazo |
|---|---|---|---|---|
| Organização do repositório | 0,3 | Pronto. Conferir no fim se `out/parte1/` tem todas as saídas | Davi | 25/11 |
| Qualidade do código | 0,4 | Pronto. CLI com UTF-8 no Windows e teste em subprocesso com ambiente ASCII | Matheus | 22/11 |
| Testes obrigatórios | 0,4 | Pronto (BFS, DFS, Dijkstra, Bellman-Ford, estados com mapa mínimo, IO). Atualizar a contagem na seção 7 | Davi | 25/11 |
| README | 0,2 | Comando do mapa surpresa em destaque (depende do R1) e revisão geral | Davi | 25/11 |
| PDF técnico | 0,4 | Fechar os 23 marcadores, gerar o PDF e conferir figuras e tabelas | Davi junta; cada dono escreve | 25/11 |
| Declaração e uso responsável de IA | 0,3 | Declaração assinada, reflexão de 10 a 15 linhas do grupo, `REGISTRO_IA.md` completo | Davi organiza; todos assinam e escrevem | 25/11 |

### Bônus visual/UX (até +1,0)

Pedidos da reunião que contam aqui. Não são obrigatórios, mas a professora pediu.

| # | Pedido | Situação | Responsável |
|---|---|---|---|
| R3 | Os 4 algoritmos ao mesmo tempo no mesmo mapa | Implementado no front; build e testes passaram, falta conferência visual pelo grupo | Thomaz |
| R4 | Upload de `.txt` pelo front (rota do Vite que já existe, validação pelo `io.py`, erro claro) | Implementado no servidor local; validação e integração HTTP testadas, falta conferência visual pelo grupo | Thomaz |
| R5 | Parte 2 no front: fontes e pares com caminho, custo, camadas e tempo | Dados prontos em `front-react/src/parte2.json` (PR #38). Falta a tela | Vagner |
| R6 | View do grafo da Parte 2, colorida por classe | Recortes prontos no mesmo JSON. Falta a tela | Vagner |

## R1: o que a CLI precisa fazer

Implementação concluída nesta branch e verificada com 533 testes e execuções reais em pastas temporárias.
Os resultados das buscas são compartilhados entre as exportações e o resumo é apresentado ao final. O aceite
do R1 depende ainda da revisão por Davi em outra máquina.

- [x] `python -m src.cli --mapa <arquivo> --out <pasta>` gera todas as saídas daquele mapa: arestas, métricas, graus,
      soluções dos 4 algoritmos, DFS, armadilhas e figura. Sem `--alg`, roda os quatro.
- [x] `--alg BFS|DFS|DIJKSTRA|BELLMAN_FORD` seleciona o resumo e a visualização; CSVs/JSONs mantêm as análises completas.
- [x] `--armadilhas` calcula as armadilhas sozinho, sem `--arquivo-armadilhas`, para qualquer mapa (não só m04/m07).
- [x] `--fonte-consumivel` e `--interactive` continuam funcionando; a variante grava em `fonte_consumivel/`.
- [x] Mapa inválido dá mensagem clara, sem traceback.
- [x] Acentos corretos no terminal do Windows (`sys.stdout.reconfigure(encoding="utf-8")`).
- [x] `--todos-mapas` gera tudo de `data/mapas/` e `data/mapas_grupo/`; `--mapas` aceita uma lista de arquivos.
- [x] Testado com os mapas de `data/mapas_treino/`: estados, arcos, armadilhas, passos BFS e custo/status do BF
      conferidos com o gabarito do README da pasta.
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
| 6.5 | Vagner | Da exploratória à explanatória (não começada) |
| 6.6 | Vagner | Quase pronta no #39. Falta o insight da explanatória 2, a pergunta de pesquisa e apagar o marcador |
| 7 | Davi | Contagem de testes na véspera |
| 8 | Todos | Limitações da Parte 1 (a da Parte 2 já está escrita) |
| 9 | Todos | Conclusões |
| 10.2 | Davi | Rodar `python -m scripts.matriz_contribuicao --revisoes` e colar as tabelas |
| 11 | Todos | Reflexão do grupo sobre o uso de IA (10 a 15 linhas, pedida pela rubrica) |

## Cronograma

| Até | Entrega |
|---|---|
| **21/11 (sáb)** | Pedir o modelo da declaração; Matheus e Thomaz dizem no grupo o que entregam até 22/11; mergear #39 e #40 |
| **22/11 (dom)** | R1 na `main`; mapas do grupo; saídas de `out/parte1/` commitadas; R2 |
| **23/11 (seg)** | Plano B do R1 se ele não tiver entrado; seções 4.1 a 4.11, 2.4, 3, 6.5 e 6.6 escritas; R3 a R6 se der tempo; modelo da declaração em mãos |
| **24/11 (ter)** | Acompanhamento. Antes: ensaio cronometrado. Na aula: cada um roda um mapa de treino no terminal |
| **25/11 (qua)** | Seções 8, 9 e 11; relatório congelado e PDF gerado; declaração assinada pelos 4; README final; matriz e testes atualizados |
| **26/11 (qui)** | Os 4 postam no Classroom e apresentam |

## Checklist por pessoa

### Matheus (P1 + P3, revisor: Thomaz)
- [x] Implementação do R1 e verificação local dos oito critérios técnicos — 21/11
- [ ] R1: revisão por Davi em outra máquina e integração na `main` — 22/11
- [x] 2 mapas do grupo com gabaritos TXT — commit `5b1eba5` (revisão/PR pendentes).
- [ ] Conferência final dos mapas/gabaritos pelo grupo e revisão por Thomaz — 22/11
- [x] Saídas de `out/parte1/` versionadas nesta branch, organizadas por tipo, incluindo a variante consumível.
- [x] R7 da Parte 1: benchmark integrado à CLI, com aquecimento, tempo e memória separados e CSV/JSON.
- [ ] R7: gerar e versionar as medições finais na máquina da apresentação; confirmar o escopo da memória
      na Parte 1 com a professora, conforme dúvida da ata de 19/11 — 23/11
- [ ] Seções 2.2 e 4.1 a 4.10, com o G_est do m02 desenhado à mão e a prova do m05 — 23/11
- [ ] Blocos 2 a 5 e 9 (Parte 1) do `APRESENTACAO.md` — 24/11
- [ ] Limitações da Parte 1 (seção 8) — 25/11

### Thomaz (P2 + P5a, revisor: Matheus)
- [x] Mapas do grupo no `labirinto_interativo.html` — commit `5b1eba5` (revisão/PR pendentes).
- [ ] R2: realce das armadilhas no `labirinto_interativo.html` — 22/11
- [ ] Seções 2.4, 3, 4.8 (com Matheus) e 4.11 — 23/11
- [x] R3 e R4 no front — 23/11; build e testes automatizados passaram. Conferência visual pelo grupo pendente.
- [ ] Bloco 6 do `APRESENTACAO.md`, com plano B se o front falhar — 24/11

### Vagner (P4b + P5b, revisor: Davi)
- [x] 2 explanatórias geradas (PR #39)
- [ ] Ajustes da 6.6 pedidos acima (insight da explanatória 2, pergunta de pesquisa, texto da explanatória 1) — 22/11
- [ ] Seção 6.5 — 23/11
- [ ] Seção 2.5 (frase e captura do front) — 23/11
- [ ] R5 e R6 lendo `front-react/src/parte2.json` — 23/11
- [ ] Bloco 10 do `APRESENTACAO.md` — 24/11

### Davi (P4a + P5c)
- [x] Mergear o PR #38
- [ ] Revisar o PR #39 do Vagner (conferir as porcentagens da 6.2 e da 6.6 com o notebook) — 22/11
- [ ] Pedir à professora o modelo da declaração de IA — hoje (21/11)
- [ ] Cobrar no grupo o que Matheus e Thomaz entregam até 22/11 e combinar o plano B do R1 — hoje (21/11)
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
