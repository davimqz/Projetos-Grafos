<!-- [IA] Claude Code – lista do que falta em cada seção do relatório, com fontes dos dados e critérios de pronto; não contém análise -->

# Guia para fechar o relatório (atualizado em 23/11/2026)

O relatório é `docs/relatorio/RELATORIO.md`. Ele vira o PDF com `python -m scripts.gerar_pdf`, que também lista os
marcadores que faltam. Hoje restam **21 marcadores**. Este guia diz, para cada um, o que o enunciado pede, onde estão os
números, o que precisa aparecer no texto e quando está pronto.

## Prazos

| Quando | O que |
|---|---|
| **24/11 (ter), 23h** | Seções 2.2, 2.4, 2.5, 3 e 4.1 a 4.11 escritas e em PR |
| **25/11 (qua), 18h** | Seções 7, 8, 9, 10.2 e 11; relatório congelado; PDF gerado sem marcadores |
| **26/11 (qui)** | Cada um posta o PDF no Classroom |

## Regras antes de escrever

1. **Análise, discussão, interpretação, conclusão e a prova do m05 são escritas por nós, sem IA.** É regra da
   professora e vale nota zero. A IA pode revisar ortografia e clareza depois, e esse uso entra no `REGISTRO_IA.md`.
2. **Tabelas com números podem ser geradas.** O script `python -m scripts.tabelas_relatorio_parte1` imprime em
   Markdown as tabelas das seções 4.4 a 4.10, lidas de `out/parte1/`. Dá para pedir só uma seção:
   `python -m scripts.tabelas_relatorio_parte1 4.8`. Copiem a tabela e escrevam o comentário embaixo.
3. Ao terminar uma seção, apaguem o bloco `> **[A ESCREVER ...]**` inteiro. O PDF não pode sair com marcador.
4. Figuras entram com `![Legenda](../../out/parte1/figuras/arquivo.png)`, seguida de uma linha em itálico:
   *Figura N: o que ela mostra.*
5. Uma branch por pessoa, PR para a `main`, revisor do pacote aprova. Quem usar IA para revisar o texto acrescenta a
   linha no `REGISTRO_IA.md` no mesmo PR.
6. Quem estiver escrevendo pode rodar a CLI para conferir um número; os valores do relatório têm que ser iguais aos
   arquivos em `out/parte1/`. Em 23/11 conferimos que as saídas commitadas são idênticas ao que a CLI gera hoje.

---

## Matheus

### 2.2 Comando que gera as saídas da Parte 1 (manual de uso)

- **Pede:** o comando que gera todas as saídas, já que o R1 entrou na `main`.
- **O que escrever:** trocar o marcador por um bloco com os comandos e uma frase sobre cada um:
  - `python -m src.cli --todos-mapas --out ./out/parte1/ --interactive` (todos os mapas, com HTML conjunto);
  - `python -m src.cli --mapa <arquivo.txt> --out <pasta> --armadilhas --interactive` (o do mapa surpresa);
  - `python -m src.cli --mapa ./data/mapas/m06_fonte.txt --fonte-consumivel --out ./out/parte1/`;
  - `python -m src.cli --todos-mapas --benchmark --out ./out/parte1/`.
- Dizer onde cada tipo de arquivo vai parar (`csv/`, `json/`, `figuras/`, `html/`, `fonte_consumivel/`) e que mapa
  inválido dá mensagem de erro e código de saída 2. A seção "Parte 1" do README já tem isso e dá para resumir de lá.
- **Pronto quando:** dá para copiar os comandos do PDF e rodar sem consultar o README.

### 4.1 Modelagem: G_pos e G_est

- **Pede (enunciado, seções 1 e 2):** o que é nó em cada grafo; o rótulo `(l,c)|chaves|{bônus}` com `-` e `{}`; a
  numeração dos bônus em ordem de leitura; a construção **por exploração** a partir de `S` (só estados alcançáveis); o
  nó `ALVO` com arco de custo 0 saindo de todo estado em `G`; as variantes (portas como chão e como parede para a 4.6,
  `+` fixo em −4 para a 4.7, `--fonte-consumivel` para o m06).
- **Obrigatório:** o **G_est do m02 desenhado à mão** (foto ou scan do papel). O enunciado manda desenhar antes de
  programar e a professora pediu isso na reunião de 19/11.
- **Onde conferir:** `src/graphs/estados.py` (`construir_grafo_estados`) e `out/parte1/csv/arestas_m02.csv`
  (39 estados e 74 arcos no m02, sem contar o `ALVO`).
- **Pronto quando:** alguém que não conhece o projeto entende por que a mesma casa vira vários nós, e o desenho bate
  com o CSV do m02.

### 4.2 Por que o grafo tem que ser dirigido

- **Pede:** explicar por que um grafo não dirigido estaria errado, pensando em esteiras e em pegar uma chave.
- **Dica para montar o argumento (não é o texto):** escolham um arco de esteira e um arco que pega a chave no
  `arestas_m02.csv` ou no `arestas_m04.csv` e mostrem o que aconteceria se existisse o arco de volta.
- **Pronto quando:** tem os dois casos (esteira e chave), cada um com um exemplo concreto de estado.

### 4.3 Mapa mínimo contado à mão

- **Pede (testes mínimos do enunciado):** um mapa mínimo **criado pelo grupo, até 5×7**, com estados e arcos contados à
  mão no PDF e conferidos por teste; esteira apontando para parede gera estado sem saída; pegar a chave muda de camada.
- **Atenção:** hoje o `tests/test_estados.py` só tem grades de uma linha (`SaAG`, `S+G`, `S^G`...). Isso atende ao pé
  da letra, mas fica fraco. **Sugestão:** criar um mapa 2D pequeno (por exemplo 3×5 com uma chave, uma porta e uma
  esteira), contar estados e arcos no papel, pôr a contagem no PDF e acrescentar um teste com esses números.
- **Pronto quando:** o PDF mostra o mapa, a contagem à mão (lista de estados e arcos) e o nome do teste que confere.

### 4.4 Métricas globais e por camada

- **Tabela:** `python -m scripts.tabelas_relatorio_parte1 4.4` (substitui a tabela vazia que está lá).
- **Pede (seção 3 do enunciado):** ordem, tamanho e densidade de G_pos e G_est; teto teórico; ocupação; métricas por
  camada; **quantos arcos ligam camadas e quais casas os geram, e por que são exatamente essas casas**.
- **O texto precisa responder:** por que o teto é muito maior que os estados alcançáveis em alguns mapas; o que a
  ocupação diz; e a pergunta das casas que geram arcos entre camadas (é o item que a rubrica cita).
- **Pronto quando:** tabela dos 10 mapas, tabela de camadas e um parágrafo para cada pergunta acima.

### 4.5 Graus, multiplicidade e becos

- **Tabela:** `python -m scripts.tabelas_relatorio_parte1 4.5`.
- **Pede (seção 4):** maior grau de entrada e de saída por mapa (desempate pela ordem de leitura do rótulo);
  **multiplicidade máxima no m08, quantas casas a atingem e por quê**; becos (estados sem saída fora de `G`).
- **Fontes:** `out/parte1/json/metricas_global.json` (campos `multiplicidade_maxima`, `casas_multiplicidade_maxima`,
  `becos`) e `out/parte1/figuras/heatmap_m08.png`, que vale inserir aqui ou citar da 4.11.
- **Pronto quando:** o "por quê" da multiplicidade do m08 está explicado e os becos do m04 estão listados.

### 4.6 Comparação de modelagens (m02, m03, m04)

- **Tabela:** `python -m scripts.tabelas_relatorio_parte1 4.6`.
- **Pede:** explicar por que (a) portas como chão produz caminho inválido e (b) portas como parede falha.
- **Pronto quando:** cada abordagem tem uma explicação ligada a um mapa concreto (ex.: o que o caminho de (a) faz de
  errado no m02).

### 4.7 m05: pesos negativos e a prova (sem IA)

- **Tabela:** `python -m scripts.tabelas_relatorio_parte1 4.7`, que mostra o ciclo no G_pos e o resultado no G_est.
- **Pede:** mostrar o ciclo negativo no G_pos com `+` fixo em −4, mostrar que ele some no G_est e escrever um
  **argumento curto (prova)** de por que o G_est do m05 não pode ter ciclo negativo. Dica do enunciado: o que acontece
  com o conjunto de bônus ao longo de um caminho?
- **Proibido usar IA para escrever a prova.** Pode tirar dúvida conceitual com o grupo ou com a professora.
- **Pronto quando:** a prova tem hipótese, passo central e conclusão, em poucas linhas.

### 4.8 Caminhos nos mapas (com Thomaz)

- **Tabela:** `python -m scripts.tabelas_relatorio_parte1 4.8`. Ela já traz o ciclo do m06 e o resultado com
  `--fonte-consumivel`.
- **Discussões obrigatórias:**
  - **m01:** por que BFS e Dijkstra dão caminhos diferentes. Comparem os dois caminhos em `solucoes.csv`.
  - **m06:** o ciclo negativo como "exploit", a correção de regra (`--fonte-consumivel`) e o resultado finito do
    Bellman-Ford.
  - **m07:** demonstrar pela busca que não há solução e dizer quantos estados são alcançáveis.
- **Pronto quando:** as três discussões estão escritas e a tabela tem os 10 mapas.

### 4.9 Estados-armadilha (m04 e m07)

- **Tabela:** `python -m scripts.tabelas_relatorio_parte1 4.9`.
- **Pede:** o método (busca a partir de `ALVO` no grafo transposto, em `src/parte1/analises.py`,
  `encontrar_armadilhas`), quantos estados são armadilha e exemplos.
- **Pronto quando:** o método está explicado em termos de grafo (por que o transposto) e há exemplos do m04.

### 4.10 Mapas do grupo

- **Tabela:** `python -m scripts.tabelas_relatorio_parte1 4.10`. Os números batem com
  `data/solucoes_mapas_grupo/`.
- **Pede:** o desenho de cada mapa e o gabarito do grupo (estados, arcos, passos BFS e custo). O mapa 1 precisa ter
  3 chaves, esteiras e bônus, com o caminho de menor custo coletando bônus e passando por esteira. O mapa 2 precisa ter
  pelo menos 20% de estados-armadilha.
- **Atenção:** os dois mapas foram sugeridos pelo Codex e os gabaritos dizem "não foi feita contagem manual". O texto
  precisa mostrar que o grupo conferiu: dizer em que ponto o caminho ótimo do g01 pega bônus e passa por esteira, e o
  que faz o g02 ter tantas armadilhas. Se der tempo, vale ajustar os mapas à mão para ficarem do grupo de fato.
- **Pronto quando:** cada mapa tem o desenho (grade em bloco de código ou figura `percurso_g0*.png`), a tabela e uma
  frase do que ele exercita.

---

## Thomaz

### 2.4 Labirinto interativo

- **Pede:** como abrir `out/parte1/html/labirinto_interativo.html` (é só abrir no navegador, sem servidor) e o que
  cada controle faz: mapa, algoritmo, camada exibida, mostrar armadilhas, anterior/animar/próximo, posição no
  percurso, velocidade e o painel de estado atual (posição, chaves, bônus, custo acumulado, camada).
- **Inserir 1 captura de tela.** Uma boa opção é o m07 com armadilhas ligadas (em 23/11 conferimos que as 16 casas
  aparecem realçadas).
- **Pronto quando:** cada requisito da seção 9 do enunciado (seleção, passo a passo, estado atual, armadilhas,
  camadas, velocidade) aparece citado.

### 3. Decisões de implementação

- **Pede:** explicar, com as palavras do grupo, como a DFS classifica os arcos (tempos de descoberta e término), como o
  Dijkstra recusa peso negativo e como o Bellman-Ford reconstrói o ciclo (`src/graphs/algorithms.py`).
- **Achado do teste de 23/11, que vale citar aqui ou na seção 8:** quando há ciclo negativo, o Bellman-Ford faz as
  V−1 passadas completas (não para cedo). No m06 isso é instantâneo, mas num mapa grande com fonte `*` (ex.: 25 mil
  estados) a execução passa de 10 minutos. Ver "Achados" no `PROXIMOS_PASSOS.md`.
- **Pronto quando:** os três algoritmos têm um parágrafo cada, apontando a função e o trecho.

### 4.11 Visualizações

- **Pede:** inserir as figuras de `out/parte1/figuras/` (`percurso_m03.png`, `percurso_m08.png`, `camadas_m02.png`,
  `arvore_bfs_m02.png`, `heatmap_m08.png`) com legenda e uma frase sobre o que cada uma mostra.
- **Requisito da seção 8 do enunciado:** título, legenda e rótulos em todas as figuras. Conferir isso abrindo cada PNG.
- **Pronto quando:** as 5 figuras estão no PDF, numeradas, cada uma com uma frase escrita por vocês.

---

## Vagner

### 2.5 Front-end em React

- **Pede:** uma frase sobre o que o front mostra e uma captura de tela.
- O front agora tem 4 abas: Labirinto (com os 4 algoritmos lado a lado e upload de `.txt`), Grafos e mapas, **Rede de
  carteiras** (nova, R5/R6: fontes, pares, ciclo negativo e subgrafo colorido por classe) e Análise de dados.
- **Pronto quando:** a frase cita as abas e há uma captura (sugestão: a aba Rede de carteiras ou a comparação dos
  algoritmos).

---

## Davi

| Seção | O que fazer | Quando |
|---|---|---|
| Topo | Apagar o aviso "Como usar este esqueleto" | 25/11 |
| 7 | Rodar `pytest`, atualizar a contagem (572 passando e 5 `xfail` em 23/11) e incluir `test_mapa_surpresa.py` na tabela | 25/11 |
| 10.2 | `python -m scripts.matriz_contribuicao --revisoes` e colar as duas tabelas | 25/11 |
| 5.1 a 5.7 | Conferir números contra os JSONs de `out/parte2/` | 25/11 |
| Geral | Juntar os PRs, gerar o PDF, conferir figuras e tabelas | 25/11 |

---

## Todos (escrever juntos, sem IA)

### 8. Limitações (Parte 1)

- A Parte 2 já está escrita. Falta a Parte 1.
- Pontos que o grupo pode avaliar se entram: o crescimento do número de estados com chaves e bônus (teto
  teórico × alcançáveis); o Bellman-Ford sem parada antecipada quando há ciclo negativo; formatos de arquivo que a
  leitura recusa (BOM, linha em branco no fim, espaço no fim da linha), se não forem corrigidos até lá; mapas do grupo
  sugeridos por IA.
- **Pronto quando:** cada limitação diz o que limita e qual seria a saída.

### 9. Conclusões

- Responder ao que o projeto se propôs: o que a modelagem por estados resolveu na Parte 1, o que os quatro algoritmos
  mostraram na Parte 2 e a resposta à pergunta de pesquisa (já discutida nas seções 5 e 6).
- **Pronto quando:** dá para ler só a conclusão e saber os principais resultados das duas partes.

### 11. Reflexão sobre o uso de IA (10 a 15 linhas)

- É o mesmo texto da seção 7 da declaração. Escrevam uma vez e usem nos dois lugares.
- A declaração pergunta: onde a IA ajudou, onde ela errou ou sugeriu algo inadequado, o que fez de certo e de errado,
  como o grupo verificou e o que aprendeu.
- Fatos do registro que podem servir de exemplo (o texto é de vocês): a agregação errada do `wallets_features.csv`
  encontrada e corrigida em 12/11; o Kosaraju escrito pela IA e trocado pela BFS do grupo em 16/11; o peso da Parte 2
  recomendado pela IA e aceito pelo grupo; as mutações nos testes que passavam sem ser detectadas (PR #8); os mapas do
  grupo sugeridos pelo Codex; os testes que expuseram o desempate de grau em desacordo com o contrato.

---

## Declaração de IA (o que cada um precisa fazer)

O rascunho está em `docs/declaracao/DECLARACAO_IA_rascunho.html` (editável) e `.pdf`. Os trechos em amarelo faltam.

| Quem | O que | Quando |
|---|---|---|
| Todos | Nome completo e matrícula na seção 1 | 24/11 |
| Davi | Grupo nº e turma (confirmar 5A) | 24/11 |
| Cada um | Versão ou plano da ferramenta que usou (seção 4) | 24/11 |
| Cada um | Conferir os blocos da seção 5 com o seu nome e corrigir o que estiver errado | 24/11 |
| Todos | Reflexão da seção 7 (a mesma da seção 11 do relatório) | 25/11 |
| Todos | Assinar (gov.br ou à mão) e salvar como `docs/DECLARACAO_IA.pdf` | 25/11 |

**Pontos para o grupo decidir antes de assinar:**

1. **Saídas obrigatórias geradas por agente.** O enunciado proíbe "pedir que a IA produza as saídas obrigatórias". Os
   JSONs de `out/parte2/` foram gerados pelo Claude Code rodando a CLI do grupo (registro, linhas 32 e 49), e os
   gabaritos dos mapas do grupo também (linha 110). Saída simples: um de nós roda os comandos de novo e commita
   (`python -m src.cli --todos-mapas --out ./out/parte1/ --interactive` e os comandos da Parte 2 do README). Os
   arquivos saem iguais, e o registro passa a dizer que a execução foi do grupo.
2. **Mapas do grupo sugeridos pelo Codex** (linha 110). "Sugerir mapas extras" é permitido, mas os mapas do grupo valem
   nota e a professora fala em plágio. Ajustar os mapas à mão ou, no mínimo, mostrar a conferência na 4.10.
3. **Peso da Parte 2 recomendado pela IA** (linha 11). Já está declarado; é só manter.
