<!-- [IA] Claude Code – lista de tarefas finais por integrante, conferida contra enunciado, critérios, ata de 19/11 e saídas do repositório; não contém análise, interpretação nem a prova do m05 -->

# Tarefas finais por integrante (24/11/2026)

Esta lista sai da releitura completa de `referencias/Projeto_Final_TEORIADOSGRAFOS262-1.pdf` (enunciado, 15 páginas),
`referencias/CRITERIOS_PROJETO_2026-2.pdf` (critérios, 31 slides), `referencias/REUNIAO_2026-11-19.md`,
`relatorio/GUIA_RELATORIO.md`, `APRESENTACAO.md`, `declaracao/DECLARACAO_IA_rascunho.html` e `REGISTRO_IA.md`,
comparados com o que existe na `main` em 24/11 (commit `66ed17c`, depois do PR #50).

Cada tarefa tem um código (M = Matheus, T = Thomaz, V = Vagner, D = Davi, G = grupo inteiro), o critério da rubrica que
ela atende, os arquivos, o passo a passo, quando está pronta e se a IA pode ajudar. **Quando terminar uma tarefa, marque
`[x]` e coloque o número do PR.**

## Prazos

| Quando | O que precisa estar pronto |
|---|---|
| **24/11 (ter), 23h** | Seções 2.4, 2.5, 3 e 4.1 a 4.11 do relatório em PR; correções de figura e do report da Parte 2 em PR |
| **25/11 (qua), 18h** | Seções 7, 8, 9, 10.2 e 11; declaração assinada pelos 4; PDF gerado sem marcadores; README final |
| **25/11 (qua), noite** | Ensaio cronometrado (15 a 20 min) com mapa surpresa no terminal |
| **26/11 (qui)** | Cada um dos 4 posta no Classroom: link do repositório, PDF e `docs/DECLARACAO_IA.pdf` |

## Regras que valem para todas as tarefas

1. **Sem IA para escrever:** análise, discussão, interpretação, conclusão, notas analíticas e a **prova do m05**.
   Também é proibido pedir para a IA interpretar gráficos, escolher tipo de gráfico ou destaque. Uso proibido não
   declarado = **nota zero no projeto**.
2. **IA permitida (com registro):** dúvida conceitual, depurar código do grupo, sugerir testes, sintaxe de
   pandas/matplotlib/front, revisar ortografia de texto já escrito por vocês.
3. **Também é proibido** usar IA para gerar `io.py`, `estados.py`, `graph.py`, `algorithms.py` ou para "produzir as
   saídas obrigatórias".
4. Todo uso de IA: `# [IA] <ferramenta> – <finalidade>` no código **e** uma linha no `docs/REGISTRO_IA.md`, no mesmo PR.
5. Números do relatório têm que ser **iguais** aos arquivos em `out/`. As tabelas da seção 4 saem prontas de
   `python -m scripts.tabelas_relatorio_parte1 <seção>` (ex.: `... 4.8`). Copie a tabela e escreva o texto embaixo.
6. Ao terminar uma seção do relatório, **apague o bloco inteiro** `> **[A ESCREVER ...]**`.
7. Figura no relatório: `![Legenda](../../out/parte1/figuras/arquivo.png)` e, na linha de baixo, `*Figura N: o que ela
   mostra.*`
8. Uma branch por pessoa, PR para a `main`, o revisor do pacote aprova (ver `PLANO_DE_TRABALHO.md`).

---

## Achado de 24/11: o PR #49 mudou resultados do Bellman-Ford

O Bellman-Ford agora procura o ciclo a cada passada e para assim que acha um (PR #49). Os dois ciclos, o antigo e o
novo, são ciclos negativos válidos; o algoritmo só devolve outro, o primeiro que encontra. Mas **as saídas commitadas
foram geradas com o código antigo** e não batem mais com o que a CLI gera hoje. Conferido rodando a CLI atual em uma
pasta temporária, sem mexer em `out/`:

| Saída | Commitado (código antigo) | CLI atual |
|---|---|---|
| `out/parte1/json/comparacao_bonus_m05.json`, ciclo no G_pos | `(5,3) → (5,4) → (5,3)`, custo −3 | `(3,3) → (3,2) → (3,3)`, custo −3 |
| `out/parte2/bellman_ford_1MFXYK1X….json`, ciclo | 2 carteiras, `1DEcTtkr…` ↔ `12cgpFdJ…`, custo −13.226,15; a origem **não** está no ciclo | 3 carteiras, `1MFXYK1X…` → `3GwfdNG4…` → `1MFcDAzG…` → `1MFXYK1X…`, custo −1.677,39; a **origem está** no ciclo (classes: desconhecida, desconhecida, lícita) |
| mesmo arquivo, `alcancados` | 1.267 | 1.162 |
| `parte2_report.json`, Bellman-Ford | 5,5 s em 50% e 42,6 s em 100%, "executou todas as rodadas" | cerca de 1 s por execução no grafo inteiro |

O resto da Parte 1 (todos os CSVs e JSONs, inclusive o ciclo do m06) e o caso sem ciclo da Parte 2 continuam iguais.

Se a professora rodar a CLI, ela vê o ciclo novo e o relatório mostra o antigo. Por isso:

### [x] D12. Regerar as saídas do Bellman-Ford e reescrever o que depende delas
- **Andamento (24/11, noite):** feito pelo Davi o passo 1 (JSON regerado), o passo 4 (5.5 e 5.7 reescritas) e o
  front (`parte2.json` regerado, aba Rede de carteiras já mostra o ciclo de 3 carteiras). Bloco 8 do `APRESENTACAO.md`
  atualizado. **Faltam:** passo 2 (Matheus, `comparacao_bonus_m05.json`) e passo 3 (Vagner, benchmark e seção 5.6,
  junto com o V1); depois do V1, rodar de novo `python -m scripts.exportar_parte2_front` para os tempos do front.
- **Andamento (25/11):** passo 3 feito pelo Vagner no PR #55 (benchmark rodado por ele, seção 5.6 com tabela e texto
  novos, `parte2.json` do front regerado). No grafo inteiro o Bellman-Ford caiu de 42,6 s para 18,41 ms, porque para
  ao achar o ciclo na 1ª passada. Passo 5 conferido: blocos 8 e 9 e a pergunta do `APRESENTACAO.md` e o slide de
  desempenho com os números novos. **Falta:** passo 2 (Matheus).
- **Quem:** Davi (seção 5.5 e 5.7), Vagner (5.6, junto com o V1), Matheus (4.7, que já deve usar o ciclo novo do m05),
  Thomaz (confirmar que o novo `alcancados` menor é o comportamento esperado da parada antecipada e explicar na seção
  3).
- **Passo a passo:**
  1. Davi roda `python -m src.cli --dataset ./data/dataset_parte2/ --alg BELLMAN_FORD --source
     1MFXYK1XucKFfhPhW9HDHD3vsM9BKey4qm --out ./out/parte2/` e commita (vale também como parte do D2).
  2. Matheus regera a Parte 1 no M11; o único arquivo que muda é `comparacao_bonus_m05.json`.
  3. Vagner regera o benchmark no V1; a seção 5.6 precisa de tabela e texto novos (as razões de crescimento do
     Bellman-Ford e a frase "executou todas as rodadas" deixam de valer).
  4. Davi reescreve a tabela e a interpretação da 5.5 (o ciclo novo inclui a origem e não tem o outlier de −12.586) e
     os parágrafos da 5.7 que citam o ciclo de 2 carteiras e o −13.226. A resposta à pergunta de pesquisa vem da 6.4
     e não muda: nenhuma carteira do ciclo novo é ilícita.
  5. Conferir `docs/APRESENTACAO.md` (blocos 8 e 9 e a pergunta "por que o Bellman-Ford leva 42,6 s") e o front
     (`python -m scripts.exportar_parte2_front` depois de regerar).
- **Pronto quando:** `git status` limpo depois de rodar a CLI e o relatório citando o ciclo e os tempos novos.
- **IA:** pode regerar tabelas a partir dos JSONs; interpretação proibida.

---

## O que zera a nota se faltar (prioridade máxima)

| Item | Consequência | Situação em 26/11 | Tarefa |
|---|---|---|---|
| `docs/DECLARACAO_IA.pdf` assinada pelos 4 | Zero no projeto | Assinada pelos 4 pelo gov.br em 26/11 (p. 21) | D1, G3 |
| Todo uso de IA declarado | Zero no projeto | Registro completo; cada integrante conferiu os próprios blocos da declaração | T7, D1 |
| Todos sabem explicar todo o código | Zero no projeto | Estudo e ensaio feitos | G4, G5 |
| Entregar as duas partes | Apresentação zerada | As duas existem | — |
| Os 4 postam no Classroom | Falta de entrega individual | — | G6 |

---

## Matheus (P1 Modelagem + P3 Análises da Parte 1; revisor: Thomaz)

O grosso do que falta é texto da seção 4 do relatório. São 0,8 + 0,4 + 0,4 + 0,8 + 0,2 pontos que hoje estão com o
código pronto e o texto vazio.

### [x] M1. Relatório 4.1: modelagem de G_pos e G_est
- **Critério:** construção do grafo de estados (0,8) e PDF técnico, "modelagem do estado" (0,4). A professora pediu na
  reunião de 19/11 para mostrar como a modelagem foi feita.
- **Arquivo:** `docs/relatorio/RELATORIO.md`, bloco `[A ESCREVER — Matheus]` da 4.1.
- **Passo a passo:**
  1. Desenhe **à mão, no papel**, o G_est do m02 (`data/mapas/m02_uma_chave.txt`). Tire foto, salve em
     `docs/relatorio/img/gest_m02_mao.jpg` e insira no relatório.
  2. Confira o desenho com `out/parte1/csv/arestas_m02.csv`: precisa ter **39 estados e 74 arcos** (sem contar o ALVO).
     Se não bater, o desenho está errado, não o CSV.
  3. Escreva: o que é nó no G_pos (casa livre) e no G_est (estado); o rótulo `(l,c)|chaves|{bônus}`, com `-` quando não
     há chave e `{}` quando não há bônus; como os bônus são numerados (ordem de leitura); que o G_est é construído
     **por exploração a partir de S** (só alcançáveis, sem gerar as 2^k combinações); o nó ALVO com arco de custo 0 a
     partir de todo estado em G; as variantes (porta como chão/parede, `+` fixo em −4, `--fonte-consumivel`).
  4. Para conferir o comportamento: `src/graphs/estados.py`, função `construir_grafo_estados`.
- **Pronto quando:** a foto está no relatório, bate com o CSV, e alguém de fora entende por que uma casa vira vários nós.
- **IA:** proibida para escrever. Pode revisar ortografia depois (registrar).

### [x] M2. Relatório 4.2: por que o grafo é dirigido
- **Critério:** construção (0,8); slides: "Grafo dirigido: nada de espelhar arcos".
- **Passo a passo:** pegue em `out/parte1/csv/arestas_m04.csv` um arco que sai de uma esteira e, em
  `arestas_m02.csv`, o arco que entra na casa da chave `a` (linha 3, coluna 11). Para cada um, mostre o estado de origem
  e o de destino e explique o que aconteceria se existisse o arco de volta.
- **Pronto quando:** tem os dois exemplos concretos (esteira e chave), cada um com os rótulos dos estados.
- **IA:** proibida para escrever.

### [x] M3. Mapa mínimo 2D contado à mão + teste + relatório 4.3
- **Critério:** testes obrigatórios (0,4): "um mapa mínimo criado pelo grupo (até 5×7), com número de estados e de arcos
  calculado à mão no PDF e conferido pelo teste".
- **Situação:** `tests/test_estados.py` só tem grades de **uma linha** (`SG`, `S^G`, `S+G`...). Atende ao pé da letra,
  mas fica fraco na arguição. Falta um mapa 2D.
- **Passo a passo:**
  1. Desenhe um mapa pequeno (até 5×7), por exemplo 3×4, com **uma chave, uma porta e uma esteira**. Exemplo de formato (crie o
     de vocês):
     ```
     S.a#
     .#>A
     ...G
     ```
  2. No papel, liste **todos** os estados alcançáveis e **todos** os arcos (com peso). Conte.
  3. Em `tests/test_estados.py`, acrescente um teste que monta esse mapa, chama `construir_grafo_estados` e confere
     `len(estados)` e `grafo.tamanho()` contra a contagem do papel. Rode `pytest tests/test_estados.py`.
  4. Se o teste falhar, **recontem à mão** antes de mexer em qualquer coisa: ou a contagem está errada ou há bug.
  5. No relatório 4.3: o mapa, a lista de estados e arcos contados à mão e o nome do teste.
- **Pronto quando:** teste novo passando e a contagem à mão no relatório.
- **IA:** pode sugerir o caso de teste; a contagem tem que ser de vocês (registrar).

### [x] M4. Relatório 4.4: métricas globais e por camada
- **Critério:** métricas, camadas e graus (0,4).
- **Passo a passo:**
  1. `python -m scripts.tabelas_relatorio_parte1 4.4` e cole as tabelas no lugar da tabela vazia.
  2. Dados de apoio em `out/parte1/json/metricas_global.json` e `camadas.json`. Exemplos que precisam aparecer no texto:
     m02 tem 2 camadas e 1 arco entre camadas (casa da chave `a`); m03 tem 4 camadas e 3 arcos (casas `a`, `b`, `c`);
     m08 tem 5 camadas e 6 arcos (casas `a`, `b`, `c`, `d`); g01 tem 4 camadas e 5 arcos.
  3. O texto precisa responder (com as palavras de vocês): por que o teto teórico é muito maior que os alcançáveis em
     alguns mapas (ex.: m08 ocupa 15,6%); o que a taxa de ocupação diz; **quais casas geram os arcos entre camadas e por
     que são exatamente essas** (a rubrica cita essa pergunta).
- **Pronto quando:** tabela dos 10 mapas, tabela de camadas e um parágrafo para cada pergunta.
- **IA:** tabela pode ser gerada pelo script; texto proibido.

### [x] M5. Relatório 4.5: graus, multiplicidade e becos
- **Critério:** métricas, camadas e graus (0,4).
- **Passo a passo:**
  1. `python -m scripts.tabelas_relatorio_parte1 4.5`.
  2. Fatos para o texto: multiplicidade máxima do m08 é **5**, atingida por **165 casas** (campo
     `casas_multiplicidade_maxima` em `metricas_global.json`); becos: m04 tem 2, g01 tem 3, os outros mapas 0 (campo
     `becos`). Insira ou cite `out/parte1/figuras/heatmap_m08.png`.
  3. Explique **por que** a multiplicidade máxima é 5 (pensem em quantas camadas o m08 tem) e liste os becos do m04
     com o motivo de cada um não ter saída.
- **Pronto quando:** o "por quê" do 5 e os becos do m04 estão escritos.
- **IA:** texto proibido.

### [x] M6. Relatório 4.6: comparação de modelagens
- **Critério:** comparação de modelagens e prova do m05 (0,4).
- **Passo a passo:** `python -m scripts.tabelas_relatorio_parte1 4.6`. Números: m02 = 10 / falha / 34 passos;
  m03 = 21 / falha / 87; m04 = 14 / falha / 20 (porta como chão / porta como parede / G_est). Explique, com um mapa
  concreto, o que o caminho de (a) faz de errado e por que (b) não chega à saída.
- **Pronto quando:** (a) e (b) têm cada um uma explicação ligada a um mapa.
- **IA:** texto proibido.

### [x] M7. Relatório 4.7: m05 e a prova (SEM IA)
- **Critério:** comparação de modelagens e prova do m05 (0,4) e PDF técnico (0,4).
- **Passo a passo:**
  1. `python -m scripts.tabelas_relatorio_parte1 4.7`. Fatos em `out/parte1/json/comparacao_bonus_m05.json`: no G_pos
     (com `+` fixo em −4) o Bellman-Ford acha o ciclo `(5,3) → (5,4) → (5,3)` de custo −3; no G_est não há ciclo e o
     custo até o ALVO é 5.
  2. Escreva a prova: hipótese, passo central e conclusão, em poucas linhas. A dica do enunciado é olhar o que acontece
     com o conjunto de bônus ao longo de um caminho.
  3. Peça para Thomaz ler e tentar achar furo antes do PR.
- **Pronto quando:** tabela e prova no relatório, lida por pelo menos mais uma pessoa.
- **IA:** **totalmente proibida** para a prova, inclusive "dar uma olhada". Dúvida: grupo ou professora.

### [x] M8. Relatório 4.8: caminhos e discussões de m01, m06 e m07 (com Thomaz)
- **Critério:** caminhos com os 4 algoritmos (0,8): "discussão de m01, m06 e m07".
- **Passo a passo:**
  1. `python -m scripts.tabelas_relatorio_parte1 4.8`.
  2. **m01:** em `out/parte1/csv/solucoes.csv`, a BFS dá 10 passos e custo 30; o Dijkstra dá 14 passos e custo 20.
     Compare os dois caminhos casa a casa (coluna `caminho`) e explique a diferença.
  3. **m06:** `out/parte1/json/ciclo_negativo_m06.json` mostra o ciclo `(3,6) → (3,5) → (3,6)`, custo −1. Proponha a
     correção de regra (já implementada como `--fonte-consumivel`) e mostre que o Bellman-Ford passa a dar resposta
     finita: `out/parte1/fonte_consumivel/csv/solucoes.csv` dá OK com custo 10. Comando para reproduzir:
     `python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/`.
  4. **m07:** demonstre pela busca que não há solução e diga quantos estados são alcançáveis: **16** (`ordem_est` do
     m07 em `metricas_global.json`); todos os 16 são armadilha.
  5. Thomaz escreve a parte do Bellman-Ford (detecção e exibição do ciclo); Matheus escreve m01 e m07.
- **Pronto quando:** as 3 discussões estão escritas e a tabela tem os 10 mapas.
- **IA:** texto proibido.

### [x] M9. Relatório 4.9: estados-armadilha
- **Critério:** caminhos (0,8), "estados-armadilha (m04 e m07)".
- **Passo a passo:** `python -m scripts.tabelas_relatorio_parte1 4.9`. Números: m04 = 4 estados
  (`out/parte1/csv/armadilhas_m04.csv`), m07 = 16, g02 = 37 de 89. Explique o método em termos de grafo (busca a partir
  do ALVO no **transposto**, função `encontrar_armadilhas` em `src/parte1/analises.py`) e por que o transposto
  resolve. Dê os 4 estados do m04 como exemplo.
- **Pronto quando:** método explicado e exemplos do m04.
- **IA:** texto proibido.

### [x] M10. Mapas do grupo: conferência e relatório 4.10
- **Critério:** mapas do grupo (0,2). Mapas "iguais ou muito semelhantes" aos de outro grupo = plágio.
- **Situação:** os dois mapas foram **sugeridos pelo Codex** e os gabaritos dizem "não foi feita contagem manual".
  Conferi em 24/11 que os requisitos batem: o caminho de menor custo do g01 (Bellman-Ford, custo 38) coleta os 2 bônus
  e passa por 3 esteiras; o g02 tem 37 de 89 estados armadilha (41,6%).
- **Passo a passo:**
  1. Decida com o grupo se os mapas serão **editados à mão** para ficarem do grupo de fato (recomendado). Se editar,
     rode `python -m src.cli --mapas data/mapas_grupo/g01_tres_depositos.txt data/mapas_grupo/g02_poco_lateral.txt
     --out ./out/parte1/ --interactive`, confira de novo os requisitos e atualize `data/solucoes_mapas_grupo/`.
  2. Confira com outro grupo (ou pelo Slack) que ninguém tem um mapa parecido.
  3. `python -m scripts.tabelas_relatorio_parte1 4.10`.
  4. No relatório: o desenho de cada mapa (grade em bloco de código ou `percurso_g0*.png`), o gabarito (estados, arcos,
     passos BFS, custo Dijkstra ou Bellman-Ford) e o que cada mapa exercita. Para o g01, diga **em que casas** o caminho
     pega bônus e passa por esteira; para o g02, o que faz ter tantas armadilhas.
  5. Atualize o bloco do Matheus na declaração ("o que foi modificado à mão nos mapas").
- **Pronto quando:** os dois mapas no relatório com gabarito e a conferência descrita.
- **IA:** texto proibido; registro já existe (linha 110), atualizar se os mapas mudarem.

### [x] M11. Regerar as saídas da Parte 1 com a mão de vocês
- **Por quê:** o enunciado proíbe "pedir que a IA produza as saídas obrigatórias", e parte das saídas foi gerada por
  agente (ver `GUIA_RELATORIO.md`, "Pontos para o grupo decidir"). Os arquivos saem iguais, mas o registro passa a dizer
  que a execução foi do grupo.
- **Passo a passo:**
  1. Na `main` atualizada, rode **você mesmo**: `python -m src.cli --todos-mapas --out ./out/parte1/ --interactive`
     e `python -m src.cli --mapa ./data/mapas/m06_fonte.txt --fonte-consumivel --out ./out/parte1/`.
  2. `git status`: se só aparecer diferença de quebra de linha ou nada, ótimo. Se algum número mudar, avise o grupo
     antes de commitar.
  3. Commit `chore(saidas): Regera saídas da Parte 1 pela CLI do grupo`.
  4. Avise o Davi para ajustar a linha correspondente na declaração.
- **Pronto quando:** commit feito por um integrante.
- **IA:** não usar.

### [x] M12. Formato do custo da BFS em `solucoes.csv` (achado 7)
- **Situação:** a BFS sai com `30.0` e os outros algoritmos com `20`. Aparece na demonstração ao vivo.
- **Onde:** `src/solve.py` (escrita do `solucoes.csv`, por volta da linha 183) e o resumo em
  `src/parte1/interface_cli.py` (linha 95). Não é arquivo proibido.
- **Passo a passo:** formatar o custo inteiro sem `.0` (por exemplo, converter para `int` quando o valor for inteiro),
  rodar `pytest`, regerar as saídas (junto com o M11).
- **Pronto quando:** `solucoes.csv` sem `.0` e testes passando.
- **IA:** pode ajudar (é IO), com registro.

### [x] M13. Benchmark da Parte 1 (R7)
- **Situação:** `out/parte1/csv/benchmark.csv` e `json/benchmark.json` existem; falta medir na máquina da apresentação
  e colocar os números no bloco 9 da apresentação.
- **Passo a passo:** na máquina que vai ser usada no dia, `python -m src.cli --todos-mapas --benchmark --out
  ./out/parte1/`, commitar, e copiar tempo e memória por algoritmo para o bloco 9 do `APRESENTACAO.md`.
- **Pronto quando:** números da Parte 1 no bloco 9.

### [x] M14. Apresentação: blocos 2, 3, 4, 5, 9 e limitações da Parte 1
- **Arquivo:** `docs/APRESENTACAO.md`, blocos com `[A PREENCHER — Matheus]`.
- **Passo a passo:**
  - Bloco 3: preencher a tabela vértice / aresta / dirigido para G_pos e G_est (a professora pediu "o que é vértice, o
    que é aresta").
  - Bloco 5: trocar "Comando: [A PREENCHER quando o R1 entrar]" por
    `python -m src.cli --mapa <arquivo.txt> --out ./out/surpresa/ --armadilhas --interactive`.
  - Blocos 2, 4 e 9 e a linha de limitações da Parte 1: tirar do relatório depois que M1 a M9 estiverem prontos.
- **Pronto quando:** nenhum `[A PREENCHER — Matheus]` no arquivo.

### [x] M15. Declaração: os campos do Matheus
- Nome completo e matrícula na seção 1; versão/plano do Codex que usou (seção 4); conferir os 4 blocos com
  `[CONFIRMAR — Matheus]` na seção 5 e corrigir o que estiver errado. Mandar para o Davi até **24/11, 23h**.

---

## Thomaz (P2 Algoritmos + P5a Visualização da Parte 1; revisor: Matheus)

### [x] T1. Relatório 2.4: como usar o labirinto interativo
- **Critério:** visualizações e HTML (0,4) e README/manual.
- **Passo a passo:**
  1. Abra `out/parte1/html/labirinto_interativo.html` direto no navegador (não precisa de servidor).
  2. Escreva o que cada controle faz: seleção de mapa, seleção de algoritmo, camada exibida, "Mostrar armadilhas",
     Anterior / Animar / Próximo, barra de posição no percurso, velocidade (1 a 20 passos/s) e o painel de estado atual
     (posição, chaves, bônus, custo acumulado, camada).
  3. Tire **1 captura**: m07 com armadilhas ligadas (as 16 casas realçadas). Salve em `docs/relatorio/img/` e insira.
  4. Cite cada requisito da seção 9 do enunciado: seleção, passo a passo, estado atual, armadilhas, camadas, velocidade.
- **Pronto quando:** os 6 requisitos citados e a captura no relatório.

### [x] T2. Relatório 3: decisões de implementação
- **Critério:** PDF técnico e domínio conceitual.
- **Passo a passo:** um parágrafo para cada, apontando função e trecho em `src/graphs/algorithms.py`:
  1. Como a DFS classifica os arcos (tempos de descoberta e término; ordem N, L, S, O).
  2. Como o Dijkstra recusa peso negativo (onde checa e qual mensagem dá).
  3. Como o Bellman-Ford detecta e **reconstrói** o ciclo negativo. Atualize com o que entrou no PR #49 (parada
     antecipada e contagem de execuções). O texto antigo do guia sobre "faz as V−1 passadas completas" **não vale mais**:
     confira o comportamento atual antes de escrever.
- **Pronto quando:** 3 parágrafos, cada um com o nome da função.
- **IA:** texto proibido.

### [x] T3. Corrigir `percurso_m03.png` (cores escondidas)
- **Critério:** visualizações (0,4): "percurso sobre o mapa (m03, m08) com a cor do caminho mudando a cada chave".
- **Problema conferido em 24/11:** no m03 o caminho vai e volta pelos mesmos corredores, e os trechos desenhados
  depois cobrem os anteriores. A legenda mostra 4 cores (nenhuma, a, ab, abc), mas na figura **só aparecem verde e
  amarelo**: os trechos "sem chave" e "chave a" ficam escondidos. No m08 não acontece.
- **Onde:** `src/viz.py`, função `desenhar_percurso` (linha 105). Não é arquivo proibido.
- **Passo a passo:**
  1. Faça cada camada aparecer mesmo quando o caminho se repete. Opções: deslocar cada camada alguns pixels em relação
     ao centro da casa, ou diminuir a espessura das camadas mais recentes para as antigas aparecerem por baixo.
  2. Regerar: `python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --out ./out/parte1/` (e o m08 para conferir
     que não piorou).
  3. Abra o PNG e confira que as 4 cores da legenda aparecem no desenho.
  4. `pytest tests/test_viz.py tests/test_visualizar_parte1.py`.
- **Pronto quando:** as 4 cores visíveis no m03 e testes passando.
- **IA:** permitida (sintaxe do matplotlib), com `# [IA]` e registro. A escolha de como destacar é do grupo.

### [x] T4. Títulos e rótulos das figuras da Parte 1
- **Critério:** enunciado, seção 8: "título, legenda e rótulos em todas as figuras".
- **Problemas conferidos em 24/11:**
  - `camadas_m02.png` ("Grafo de estados por conjunto de chaves"), `arvore_bfs_m02.png` ("Árvore BFS por nível") e
    `heatmap_m08.png` ("Multiplicidade de estados por posição"): o título não diz o mapa.
  - `percurso_m03.png` e `percurso_m08.png`: título só "m03 — DIJKSTRA" e **sem rótulos de eixo** (o heatmap tem
    "Linha" e "Coluna").
  - Árvore BFS: os rótulos mostram só a posição, então `(3,10)` aparece duas vezes (sem e com a chave) sem diferença.
- **Onde:** `src/viz.py` (`set_title` nas linhas 141, 203 e 273).
- **Passo a passo:** incluir o nome do mapa nos títulos (ex.: "m02: grafo de estados por conjunto de chaves"), pôr
  "Linha" e "Coluna" nos percursos, mostrar a chave nos rótulos da árvore (ou colorir os nós por camada). Regerar com
  `python -m src.cli --todos-mapas --out ./out/parte1/ --interactive` e abrir cada PNG.
- **Pronto quando:** as 5 figuras obrigatórias com título que diz o mapa, legenda e eixos.
- **IA:** permitida (sintaxe), com registro.

### [x] T5. Relatório 4.11: figuras com legenda
- **Critério:** visualizações (0,4).
- **Passo a passo:** depois de T3 e T4, insira as 5 figuras (`percurso_m03.png`, `percurso_m08.png`,
  `camadas_m02.png`, `arvore_bfs_m02.png`, `heatmap_m08.png`), numeradas, cada uma com uma frase **escrita por vocês**
  sobre o que ela mostra.
- **Pronto quando:** 5 figuras numeradas, cada uma com a frase.
- **IA:** frases proibidas.

### [x] T6. Relatório 4.8: parte do Bellman-Ford (com Matheus)
- Ver M8, passo 3: detecção e exibição do ciclo do m06 e a resposta finita com `--fonte-consumivel`.

### [x] T7. Corrigir a linha "Não informado" do registro de IA
- **Situação:** em `docs/REGISTRO_IA.md` há uma linha de 23/11 com integrante "Não informado", ferramenta Codex:
  "Integração e formatação de seis testes de Bellman-Ford fornecidos pelo usuário". É do PR #49.
- **Passo a passo:** trocar "Não informado" pelo nome de quem usou (provavelmente Thomaz). Avisar o Davi para a
  declaração.
- **Pronto quando:** nenhuma linha sem autor no registro.

### [x] T8. Apresentação: bloco 6 e plano B
- **Arquivo:** `docs/APRESENTACAO.md`, bloco 6.
- **Passo a passo:** roteiro da demonstração no front (comparação 2×2, upload de `.txt`, aba Rede de carteiras) e o
  **plano B se o front falhar**: abrir `out/parte1/html/labirinto_interativo.html` direto no navegador (não depende do
  Vite nem de internet).
- **Pronto quando:** sem `[A PREENCHER]` no bloco 6.

### [x] T9. Declaração: os campos do Thomaz
- Nome completo e matrícula; versão do Codex (seção 4); conferir os 2 blocos com `[CONFIRMAR — Thomaz]`. Mandar para o
  Davi até **24/11, 23h**.

### [x] T10. Revisar os PRs do Matheus (revisor de P1 e P3)
- Para cada seção 4.x: os números batem com `out/parte1/`? O bloco `[A ESCREVER]` foi apagado? Na 4.7, tente achar um
  furo na prova.

---

## Vagner (P4b Experimentos + P5b AVD; revisor: Davi)

A parte de AVD está completa (6 figuras, seções 6.1 a 6.6). O que falta é o report da Parte 2, o front no relatório e a
apresentação.

### [x] V1. `parte2_report.json` com casos obrigatórios e repetições
- **Andamento (25/11):** feito no PR #55. O report agora é um dicionário com `repeticoes: 5`, `escalabilidade` (12
  linhas) e `casos` (BFS e DFS nas 3 fontes, Dijkstra nos 5 pares, Bellman-Ford nos 2 casos), e a 5.6 ganhou a tabela
  "Casos obrigatórios". A frase das duplicadas da 6.1 também foi corrigida.
- **Andamento (24/11):** o PR #51 (mergeado) limpou os 6 gráficos da AVD e acrescentou a checagem de duplicadas, mas
  **não mexeu** no `parte2_report.json`, no `src/benchmark.py` nem na seção 5.6. Esta tarefa e o passo 3 da D12 continuam
  abertos. Conferido no PR #51: as 6 figuras têm título, legenda e eixos.
- **Ponto do PR #51 para o Vagner conferir:** a frase nova da 6.1 diz que "nenhuma aresta está repetida" e conclui que
  também não há transações repetidas. Pela seção 5.1 e pelo `recorte_info.json`, as arestas repetidas foram agregadas
  em um arco por par na preparação (47.346 duplicatas agregadas). Ou seja, não haver arestas repetidas é consequência da
  construção, e vale dizer isso no texto.
- **Critério:** desempenho e escalabilidade (0,5): "tempo médio de ≥ 5 execuções **por algoritmo e tarefa** em
  `parte2_report.json`". O slide de arquivos obrigatórios diz: "tempos médios (≥ 5 execuções), **casos obrigatórios** e
  escalabilidade em 3 tamanhos". A ata de 19/11 pede tempo, latência e memória "por algoritmo e por tarefa".
- **Situação:** o report tem só as **12 linhas de escalabilidade** (4 algoritmos × 10%, 50%, 100%), cada algoritmo
  medido a partir de **uma** origem. Os casos obrigatórios estão em JSONs separados (`out/parte2/bfs_*.json` etc.) sem
  tempo, e o report não diz que foram 5 repetições.
- **Onde:** `src/benchmark.py` (P4b). Não é arquivo proibido.
- **Passo a passo:**
  1. Em cada linha de escalabilidade, acrescentar `"repeticoes": 5`.
  2. Acrescentar uma seção `"casos"` com uma entrada por tarefa obrigatória: BFS e DFS para cada uma das 3 fontes,
     Dijkstra para cada um dos 5 pares e Bellman-Ford para os 2 casos (sem ciclo e com ciclo). Cada entrada com
     algoritmo, origem, destino (se houver), status, `tempo_medio_ms`, latência mínima e máxima, `repeticoes: 5` e
     memória. As fontes e os pares são os mesmos dos JSONs de `out/parte2/` e da seção 5 do relatório.
  3. Atenção ao tempo: o Bellman-Ford no grafo inteiro leva cerca de 42 s por execução, então 5 execuções dos 2 casos
     levam por volta de 7 minutos. Rode em background.
  4. `python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/` e confira o JSON.
  5. Atualize a seção 5.6 do relatório com uma tabela por tarefa (pode sair do JSON) e diga que os números estão no
     report.
  6. `pytest tests/test_benchmark.py`.
- **Pronto quando:** o report tem as 12 linhas de escalabilidade e os casos obrigatórios, todos com `repeticoes: 5`.
- **IA:** permitida para o código de IO/medição, com registro. Interpretação dos tempos é de vocês.

### [x] V2. Relatório 2.5: front-end
- **Andamento (25/11):** feito no PR #55 (frase das quatro abas e captura `img/front_rede_carteiras.jpg`).
- **Passo a passo:** uma frase sobre o que o front mostra (abas Labirinto com comparação 2×2 e upload de `.txt`, Grafos
  e mapas, Rede de carteiras, Análise de dados) e **1 captura** (sugestão: aba Rede de carteiras). Salvar em
  `docs/relatorio/img/`.
- **Pronto quando:** frase e captura no relatório, bloco apagado.

### [x] V3. Apresentação: bloco 10 (AVD)
- **Andamento (25/11):** feito no PR #55. O Vagner ainda vai enxugar a fala por causa do tempo.
- **Situação:** o bloco ainda diz que a 6.5 e a 6.6 "ainda não foram escritas", mas já estão.
- **Passo a passo:** atualizar o texto; escolher 1 ou 2 exploratórias para mostrar, com o insight de cada uma em uma
  frase sua; as 2 explanatórias com a mensagem e a justificativa dos atributos pré-atentivos.
- **Pronto quando:** sem `[A PREENCHER]` no bloco 10.
- **IA:** proibida para interpretação e escolha.

### [x] V4. Respostas das perguntas previstas
- **Andamento (25/11):** feito no PR #55. Com o benchmark novo, a pergunta do Bellman-Ford virou "por que leva só
  18,41 ms, menos que a DFS"; as três respostas estão no `APRESENTACAO.md`.
- Em `docs/APRESENTACAO.md`, "Perguntas que a professora pode fazer": escrever as respostas das duas que são suas (por
  que o Bellman-Ford leva 42,6 s e os outros milissegundos; por que a DFS alcança todas as carteiras no benchmark e a
  BFS não). Acrescente a sua resposta para "por que com 10% dos nós sobram só 130 arestas?", que tende a aparecer.

### [x] V5. Declaração: os campos do Vagner
- **Andamento (25/11):** feito no PR #55 (versão, usos 18, 20, 21 e 22 e linhas 149 e 150 no Anexo A).
- Nome completo e matrícula; versão do Claude Code ou ChatGPT que usou; conferir os 2 blocos com
  `[CONFIRMAR — Vagner]`. Mandar para o Davi até **24/11, 23h**.

### [x] V6. Revisar os PRs do Davi (revisor de P4a)
- Principalmente D2 (saídas da Parte 2 regeneradas) e D5 (revisão da seção 5).

---

## Davi (P4a Dados + P5c README, PDF e declaração)

### [x] D1. Declaração de IA completa e assinada
- **Critério:** declaração e uso responsável de IA (0,3) e **condição para não zerar o projeto**.
- **Arquivo:** `docs/declaracao/DECLARACAO_IA_rascunho.html` → `docs/DECLARACAO_IA.pdf`.
- **Passo a passo:**
  1. Preencher grupo nº e turma (`[CONFIRMAR — turma]`).
  2. Juntar nome completo e matrícula dos 4 (M15, T9, V5) e as versões das ferramentas (seção 4).
  3. Resolver `[CONFIRMAR — Davi: reexecutar a CLI e confirmar que os JSONs commitados são idênticos]` depois do D2.
  4. Atualizar os blocos com o que mudou depois de 23/11: PR #49 (testes do Bellman-Ford, autor do T7), PR #50
     (front do Matheus e testes do `ler_mapa`), as tarefas desta lista.
  5. Colar a reflexão da seção 7 (G2) quando o grupo escrever.
  6. Gerar o PDF, mandar para os 4 assinarem (gov.br ou à mão) e salvar como **`docs/DECLARACAO_IA.pdf`** (esse nome
     exato). Conferir que tem **4 assinaturas**.
- **Pronto quando:** `docs/DECLARACAO_IA.pdf` na `main` com 4 assinaturas e sem nenhum `[PREENCHER]`/`[CONFIRMAR]`.

### [x] D2. Regerar as saídas da Parte 2 com a mão do grupo
- **Andamento (24/11, noite):** Davi rodou a CLI para as 3 fontes, os 5 pares e os 2 casos do Bellman-Ford; os 12
  JSONs saíram idênticos aos commitados (só a quebra de linha difere no Windows). Declaração atualizada. **Falta:** o
  `--benchmark` depois do merge do V1.
- **Por quê:** igual ao M11. Os JSONs de `out/parte2/` foram gerados pelo agente (registro, linhas 32 e 49).
- **Passo a passo:** rodar você mesmo os comandos da seção 2.3 do relatório para as 3 fontes, os 5 pares e os 2 casos
  do Bellman-Ford; `git status`; commitar se idêntico; ajustar o registro e a declaração. Se o V1 mudar o benchmark,
  rodar o `--benchmark` depois do merge dele.
- **Pronto quando:** commit feito por você, sem diferença de números.

### [x] D3. Testes: tirar os `xfail` e atualizar a seção 7
- **Situação:** `pytest` dá **583 passed, 5 xpassed**. Os 5 `xfail` de `tests/test_mapa_surpresa.py` (linhas 118 a 139)
  passaram porque o Matheus corrigiu o `io.py`. A seção 7 do relatório ainda diz "503 testes passando em 19/11".
- **Passo a passo:** remover os 5 `@pytest.mark.xfail` e o parágrafo do topo do arquivo que fala deles; rodar `pytest`
  (tem que dar 588 passed); atualizar a seção 7 com a contagem e a data e incluir `test_mapa_surpresa.py` na tabela.
- **Pronto quando:** sem `xfail`/`xpassed` e seção 7 atualizada.

### [x] D4. Matriz de contribuição (seção 10.2)
- **Critério:** participação equilibrada e registro de contribuições (0,3).
- **Passo a passo:** na véspera, depois dos últimos merges, `python -m scripts.matriz_contribuicao --revisoes`, colar as
  duas tabelas no lugar das de 19/11 e apagar o bloco `[COMPLETAR — Davi]`. Conferir que os 4 têm commits em pelo menos
  2 pacotes.
- **Pronto quando:** tabelas com data de 25/11.

### [x] D5. Revisar as seções 5.1 a 5.7 contra os JSONs
- **Passo a passo:** para cada número das seções 5.x, abrir o JSON de `out/parte2/` citado e conferir. Atenção à 5.6
  depois do V1.
- **Pronto quando:** nenhum número diferente dos arquivos.

### [ ] D6. Comprovante da proposta do dataset
- **Critério:** proposta e descrição do dataset (0,5): "proposta aprovada no checkpoint (até 12/10)".
- **Passo a passo:** guardar o print da entrega e da aprovação no Classroom e citar a data na seção 5.1.

### [x] D7. README final
- **Critério:** README (0,2) e organização do repositório (0,3).
- **Passo a passo:** comando do mapa surpresa em destaque no topo; conferir instalação (`pip install -r
  requirements.txt`), exemplos das duas partes, estrutura de pastas; citar o `labirinto_interativo.html` e o front.
  Rodar os comandos do README em um clone limpo.
- **Pronto quando:** todos os comandos do README funcionam num clone novo.

### [x] D8. Fechar o relatório e gerar o PDF
- **Critério:** PDF técnico (0,4): modelagem do estado, prova do m05, correção do m06, resultados, visualizações,
  limitações, conclusões e matriz.
- **Passo a passo:**
  1. Juntar os PRs de M1 a M10, T1, T2, T5, V2, G1, G2.
  2. Apagar a nota "Como usar este esqueleto" do topo.
  3. Atualizar a seção 11 do relatório com a reflexão (G2) e tirar a frase "deve ser assinada... antes da entrega".
  4. `python -m scripts.gerar_pdf` tem que dizer **zero marcadores**.
  5. Abrir o PDF e conferir figuras, tabelas e acentos página por página.
- **Pronto quando:** PDF gerado, zero marcadores, conferido.

### [x] D9. Slides
- A partir do `APRESENTACAO.md`, depois de M14, T8 e V3. Incluir a foto do G_est do m02 desenhado à mão (pedido da
  reunião) e a tabela vértice/aresta das duas partes.

### [x] D10. Atualizar `PROXIMOS_PASSOS.md`
- Marcar como resolvidos os achados 1 a 6 (leitura do `io.py` no commit 808271e e Bellman-Ford no PR #49) e apontar
  para esta lista.

### [x] D11. Revisar o PR do Vagner (V1)
- Conferir que as fontes e os pares do report são os mesmos dos JSONs e da seção 5, e que há 5 repetições em cada
  tarefa.
- **Andamento (25/11):** conferido no PR #55. As fontes e os pares do report são os mesmos dos JSONs (o teste novo
  `test_casos_obrigatorios_batem_com_os_jsons` garante isso), todas as linhas têm `repeticoes: 5` e as tabelas da 5.6 e
  do bloco 9 batem com o JSON. Um detalhe: no Bellman-Ford com ciclo, a linha de 100% da escalabilidade dá 1.161
  alcançadas e o caso obrigatório dá 1.162 (o mesmo do `bellman_ford_1MFXYK1X….json`). A amostra de 100% passa
  pelo `random.sample`, que embaralha a ordem dos vértices, e como o algoritmo para ao achar o ciclo, essa ordem muda
  quantas carteiras ele alcança antes de parar. A 5.6 só cita o 1.162.

---

## Grupo inteiro

### [x] G1. Seções 8 (limitações da Parte 1) e 9 (conclusões), escritas juntas e sem IA
- **Critério:** PDF técnico (0,4).
- **8:** cada limitação diz o que limita e qual seria a saída. Pontos que podem ser avaliados: crescimento do número
  de estados com chaves e bônus (teto × alcançáveis); mapas do grupo sugeridos por IA (se não forem editados);
  comportamento do Bellman-Ford em mapa grande com fonte (conferir depois do PR #49).
- **9:** dá para ler só a conclusão e saber os principais resultados das duas partes e a resposta à pergunta de
  pesquisa.

### [x] G2. Reflexão sobre o uso de IA (10 a 15 linhas), sem IA
- **Critério:** declaração e uso responsável de IA (0,3): "reflexão de 10 a 15 linhas".
- O mesmo texto vai na seção 7 da declaração e na seção 11 do relatório. A declaração pergunta: onde a IA ajudou, onde
  errou ou sugeriu algo inadequado, como o grupo verificou e o que aprendeu. Os fatos para exemplo estão no fim do
  `GUIA_RELATORIO.md`.

### [x] G3. Assinar a declaração (25/11)
- gov.br ou à mão, no PDF que o Davi mandar. Sem as 4 assinaturas = zero.

### [x] G4. Estudar o que não fez
- **Critério:** domínio conceitual e perguntas individuais (0,5). A professora pode escolher quem apresenta, e a nota
  dessa pessoa vale para o grupo. Falas divididas ("cada um fala da sua parte") têm redução severa.
- Todo mundo precisa saber explicar: o estado e o rótulo; por que o grafo é dirigido; a prova do m05; a correção do m06;
  por que o m07 não tem solução; como as armadilhas são achadas (transposto); vértice, aresta e peso na Parte 2; o que
  é caminho mínimo e ciclo negativo no Elliptic++; a pergunta de pesquisa e a resposta; cada gráfico da AVD; e qualquer
  trecho feito com IA.

### [x] G5. Ensaio com mapa surpresa (25/11 à noite)
- **Critério:** demonstração ao vivo (0,4) e clareza da apresentação (0,3), 15 a 20 min.
- Cada um roda, no próprio computador, um mapa de `data/mapas_treino/` que não conhece:
  `python -m src.cli --mapa ./data/mapas_treino/t02_esteiras_fonte.txt --out ./out/surpresa/ --armadilhas --interactive`
  e explica a saída (estados, arcos, passos BFS, custo, armadilhas, ciclo negativo se houver). Testar também o
  `t05_invalido.txt` (tem que dar mensagem clara).
- Cronometrar o roteiro inteiro. **Plano B:** se o mapa for grande e tiver `*`, rodar `--alg BFS` ou `--alg DIJKSTRA`
  primeiro e o Bellman-Ford por último.

### [ ] G6. Entrega no Classroom (26/11)
- **Cada um dos 4** posta: link `https://github.com/davimqz/Projetos-Grafos`, o PDF do relatório e
  `docs/DECLARACAO_IA.pdf`.
- Antes de postar, conferir na `main`: `pytest` passando; `out/parte1/` com todas as saídas obrigatórias;
  `out/parte2/parte2_report.json` e as figuras; PDF sem marcadores; README com o comando do mapa surpresa.

---

## Já pronto (não mexer sem avisar)

Conferido arquivo por arquivo em 24/11:

- **Saídas da Parte 1:** `arestas_<mapa>.csv` dos 10 mapas (inclusive m08), `metricas_global.json`, `camadas.json`,
  `graus_<mapa>.csv`, `comparacao_modelagem.csv`, `solucoes.csv` (30 linhas, status OK/RECUSA/CICLO_NEGATIVO/
  SEM_SOLUCAO), `dfs_classificacao.csv`, `percurso_m03.json`, `ciclo_negativo_m06.json`, `armadilhas_m04.csv`,
  `armadilhas_m07.csv`, `comparacao_bonus_m05.json`, variante `fonte_consumivel/`.
- **Figuras:** as 5 obrigatórias existem (com os ajustes de T3 e T4 pendentes); `labirinto_interativo.html` com os 10
  mapas, seleção, passo a passo, estado atual, armadilhas, camadas e velocidade.
- **Mapas do grupo:** requisitos conferidos (g01: 3 chaves, caminho ótimo com 2 bônus e 3 esteiras; g02: 41,6% de
  armadilhas).
- **Parte 2:** recorte com 14.182 nós e 25.111 arestas; BFS/DFS de 3 fontes com ordem, camadas e ciclo; Dijkstra em 5
  pares com `valor_btc`; Bellman-Ford sem ciclo (29 arcos negativos alcançáveis) e com ciclo (3 nós, custo −13.226);
  escalabilidade em 10/50/100% com média de 5 execuções, latência, memória e comparação com a complexidade; seção 5.7.
- **AVD:** 4 exploratórias + 2 explanatórias (o enunciado pede no mínimo 6), seções 6.1 a 6.6.
- **Código e testes:** estrutura de pastas do enunciado, testes mínimos de BFS, DFS, Dijkstra, Bellman-Ford, estados e
  IO; leitura do mapa aceitando BOM, linha em branco e espaço no fim; Bellman-Ford com parada antecipada (PR #49).
- **Bônus visual/UX:** comparação 2×2 dos algoritmos, upload/colagem de `.txt`, aba Rede de carteiras com grafo
  colorido por classe, troca de camadas e controle de velocidade.
