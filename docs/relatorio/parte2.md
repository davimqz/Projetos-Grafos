# Parte 2 — Design dos pesos e preparação dos dados

No Bellman-Ford, utilizamos como peso o saldo da carteira de destino (B), calculado pela diferença entre o total de BTC recebidos e enviados. Como o dataset não possui pesos nas arestas e os valores das transações são sempre não negativos, o saldo é a única grandeza que permite obter valores negativos sem inventá-los. Um saldo positivo indica acúmulo de BTC, enquanto um negativo indica que a carteira envia mais do que recebe. Não usamos a diferença entre os saldos de A e B porque, nesse caso, a soma dos pesos em qualquer ciclo seria sempre zero, impossibilitando a identificação de ciclos negativos. Assim, esses ciclos podem indicar padrões de circulação de fundos entre carteiras, que são o foco da pesquisa. Utilizamos o grafo de carteiras porque o grafo de transações não possui ciclos, já que cada transação depende de saídas anteriores.

No Dijkstra, utilizamos como peso a soma dos valores das transações entre A e B (valor_btc), pois ela já existe no dataset e é não negativa. Dessa forma, o caminho mínimo representa a rota com a menor soma dos valores movimentados.

Na preparação dos dados, removemos os laços (A → A), pois representam troco e poderiam gerar ciclos negativos artificiais. Também agregamos arestas repetidas entre as mesmas carteiras, somando os valores das transações para o Dijkstra, e somamos os atributos de cada carteira entre os diferentes intervalos de tempo (time steps). Para reduzir o tamanho do grafo, aplicamos um recorte em bola de neve, partindo das carteiras ilícitas e expandindo para seus vizinhos. Essa estratégia preserva as conexões, ao contrário da amostragem aleatória. O recorte foi necessário porque o grafo completo possui 2,87 milhões de arestas, acima do limite de aproximadamente 500 mil arestas a partir do qual o enunciado exige amostragem.

A metodologia apresenta três limitações principais: as carteiras ilícitas representam 37% do recorte, mas apenas 1,7% do dataset completo, gerando um possível viés; no Bellman-Ford, todas as arestas que chegam à mesma carteira recebem o mesmo peso; e o valor_btc representa o valor total da transação, não necessariamente a quantia exata enviada de A para B.

# Parte 2 — Resultados de BFS e DFS

## 1. Escolha das carteiras analisadas

Foram selecionadas três carteiras para a análise: uma ilícita, uma lícita e uma desconhecida.

A seleção foi feita a partir das **5 carteiras com maior número de arcos de saída de cada classe**. O objetivo foi comparar a estrutura das redes alcançáveis a partir dessas fontes.

### Carteira ilícita

- **Endereço:** `39sfuA8pY4UfybgEZi7uvA13jkGzZpsg5K`
- **Arcos de saída:** 398.
- **Critério de seleção:** maior número de arcos de saída entre as 5 carteiras ilícitas listadas.
- **BFS:** alcançou 1.737 carteiras, incluindo a origem, distribuídas em 8 camadas.
- **DFS:** identificou arcos de retorno, indicando ciclos na região alcançável.

### Carteira lícita

- **Endereço:** `35fNF5Uwbsoa5ABPCUvKZNyuAV7S9sJTou`
- **Arcos de saída:** 71.
- **Critério de seleção:** maior número de arcos de saída entre as 5 carteiras lícitas listadas.
- **BFS:** alcançou 81 carteiras, incluindo a origem, distribuídas em 3 camadas.
- **DFS:** não identificou arcos de retorno na região alcançável.

### Carteira desconhecida

- **Endereço:** `1MFXYK1XucKFfhPhW9HDHD3vsM9BKey4qm`
- **Arcos de saída:** 1.002.
- **Critério de seleção:** maior número de arcos de saída entre as 5 carteiras desconhecidas listadas.
- **BFS:** alcançou 1.267 carteiras, incluindo a origem, distribuídas em 7 camadas.
- **DFS:** identificou arcos de retorno, indicando ciclos na região alcançável.

A carteira permanece classificada como desconhecida, pois os resultados estruturais não permitem determinar sua classificação.

## 2. BFS — Busca em Largura

A BFS (Busca em Largura) permite analisar quantas carteiras podem ser alcançadas a partir de uma carteira inicial e a distância de cada uma em relação à origem.

A exploração ocorre por camadas: primeiro são analisadas as conexões mais próximas, depois as conexões seguintes e assim por diante.

Neste trabalho, **a contagem inclui a própria carteira de origem, identificada como camada 0**. Portanto, o total de carteiras alcançadas também inclui a origem.

### Resultados gerais

| Classe | Carteiras alcançadas, incluindo a origem | Camadas, incluindo a origem | Distância máxima |
|---|---:|---:|---:|
| Ilícita | 1.737 | 8 | 7 |
| Lícita | 81 | 3 | 2 |
| Desconhecida | 1.267 | 7 | 6 |

A carteira ilícita apresentou o maior alcance entre as três fontes analisadas, com 1.737 carteiras.

A carteira desconhecida alcançou 1.267 carteiras, enquanto a carteira lícita apresentou um alcance menor, com 81 carteiras.

Esses resultados mostram diferenças na extensão das regiões alcançáveis a partir das fontes selecionadas.

### Distribuição das carteiras por camada

A tabela abaixo mostra como as carteiras alcançadas estão distribuídas em cada camada da BFS. Cada linha representa a quantidade de carteiras encontradas a uma determinada distância da origem.

| Camada | Ilícita | Lícita | Desconhecida |
|---|---:|---:|---:|
| 0 — Origem | 1 | 1 | 1 |
| 1 | 398 | 71 | 1.002 |
| 2 | 90 | 9 | 141 |
| 3 | 988 | — | 19 |
| 4 | 149 | — | 17 |
| 5 | 17 | — | 56 |
| 6 | 63 | — | 31 |
| 7 | 31 | — | — |
| **Total** | **1.737** | **81** | **1.267** |

### Interpretação da distribuição

A carteira ilícita apresenta uma expansão expressiva na terceira camada, com 988 carteiras encontradas nessa distância. Isso indica que uma parcela significativa do seu alcance está concentrada a três conexões da origem.

A carteira lícita apresenta uma rede mais curta: são 71 carteiras na primeira camada e 9 na segunda. Como a origem também é contabilizada, o total alcançado é de 81 carteiras em 3 camadas.

A carteira desconhecida apresenta uma concentração muito elevada na primeira camada, com 1.002 carteiras diretamente alcançáveis a partir da origem. Nas camadas seguintes, a quantidade de carteiras diminui significativamente em relação à primeira camada, embora apresente algumas oscilações ao longo da expansão, como o aumento de 17 para 56 carteiras na camada 5.

Essas diferenças mostram que não basta observar o alcance total: a distribuição por camada também ajuda a compreender como cada rede se expande.

## 3. DFS — Busca em Profundidade

A DFS (Busca em Profundidade) explora um caminho do grafo até onde for possível antes de retornar e investigar outras conexões.

Durante a execução, os arcos são classificados em quatro categorias:

| Classe | Árvore | Retorno | Avanço | Cruzamento |
|---|---:|---:|---:|---:|
| Ilícita | 1.736 | 103 | 194 | 549 |
| Lícita | 80 | 0 | 0 | 30 |
| Desconhecida | 1.266 | 98 | 253 | 450 |

### Significado dos arcos

- **Árvore:** arcos utilizados para descobrir novos vértices durante a DFS.
- **Retorno:** arcos que conectam um vértice a um de seus ancestrais na árvore DFS. Em grafos direcionados, indicam a presença de ciclos.
- **Avanço:** arcos que conectam um ancestral a um descendente já descoberto, sem terem sido utilizados para descobrir esse descendente.
- **Cruzamento:** arcos entre vértices que não possuem relação direta de ancestralidade na árvore DFS.

### Interpretação

A carteira ilícita apresentou 103 arcos de retorno, enquanto a desconhecida apresentou 98.

Isso indica que **as regiões alcançáveis a partir dessas carteiras possuem ciclos**.

Já a carteira lícita não apresentou arcos de retorno, indicando que não foram identificados ciclos em sua região alcançável durante a execução da DFS.

É importante destacar que encontrar ciclos na região alcançável não significa que a carteira de origem participa diretamente deles. Essa distinção será importante para responder à pergunta de pesquisa.

## 4. Limitações da análise

A pergunta de pesquisa definida pelo grupo é:

> Carteiras ilícitas participam mais de ciclos de repasse (ciclos negativos) do que as lícitas?

Os resultados atuais permitem observar diferenças entre as três fontes analisadas, mas existem limitações que precisam ser consideradas.

### 4.1. Quantidade limitada de carteiras

Foram analisadas apenas três carteiras específicas, uma de cada classe.

Essa quantidade é insuficiente para representar o comportamento de todas as carteiras ilícitas, lícitas e desconhecidas do dataset.

Portanto, os resultados devem ser interpretados como uma análise exploratória.

### 4.2. Viés do recorte analisado

O recorte utilizado foi construído por meio de uma abordagem de busca em bola de neve, iniciada a partir de **50 carteiras ilícitas**.

Nesse processo, novas carteiras são identificadas a partir das conexões com as carteiras inicialmente selecionadas, ampliando progressivamente o conjunto analisado.

Como consequência desse procedimento, as carteiras ilícitas representam aproximadamente **37% do recorte analisado**, mas apenas **1,7% do dataset completo**.

Essa diferença indica que o recorte possui uma concentração de carteiras ilícitas maior do que a observada no dataset original.

Além disso, como a exploração começou a partir de carteiras ilícitas, o procedimento pode favorecer a identificação de regiões alcançáveis e ciclos relacionados a essas carteiras.

Por esse motivo, os resultados não devem ser generalizados diretamente para o dataset completo.

### 4.3. Viés na seleção das fontes

A escolha das fontes foi baseada nas 5 carteiras com maior número de arcos de saída em cada classe.

Isso significa que as carteiras analisadas possuem muitas conexões em comparação com outras carteiras da mesma categoria.

Essa característica pode favorecer tanto o alcance na BFS quanto a identificação de ciclos na DFS.

Consequentemente, as carteiras selecionadas não representam necessariamente uma carteira típica de cada classe.

### 4.4. Identificação de ciclos negativos

A DFS permite identificar a existência de ciclos no grafo, mas não determina se esses ciclos possuem peso negativo.

A identificação de ciclos negativos depende da análise dos pesos dos arcos e da utilização de um algoritmo apropriado, como o Bellman-Ford.

**A implementação do Bellman-Ford é uma etapa obrigatória do projeto e ainda está pendente.**

Portanto, os resultados atuais permitem identificar ciclos estruturais, mas ainda não confirmar a existência de ciclos negativos.

Essa seção deverá ser atualizada após a implementação do algoritmo, incorporando os resultados da verificação.

### 4.5. Alcançar uma carteira não significa participar de um ciclo

Uma carteira pode alcançar uma região do grafo que contém ciclos sem fazer parte desses ciclos.

Por exemplo, uma carteira pode estar conectada a outras carteiras que formam um ciclo, mas não possuir uma conexão que permita retornar à própria origem.

Assim, identificar ciclos na região alcançável não é suficiente para afirmar que a carteira inicial participa deles.

Essa distinção é fundamental porque a pergunta de pesquisa trata especificamente da participação das carteiras em ciclos de repasse.

## 5. Conclusão

Os resultados mostram diferenças estruturais entre as três carteiras analisadas.

A carteira ilícita apresentou o maior alcance na BFS, com 1.737 carteiras alcançadas, incluindo a origem, e 103 arcos de retorno na DFS.

A carteira desconhecida alcançou 1.267 carteiras, incluindo a origem, e apresentou 98 arcos de retorno.

Já a carteira lícita alcançou 81 carteiras, incluindo a origem, e não apresentou arcos de retorno.

Esses resultados indicam que **as regiões alcançáveis a partir das carteiras ilícita e desconhecida possuem ciclos**, enquanto não foram identificados ciclos na região alcançável a partir da carteira lícita selecionada.

Entretanto, ainda não é possível responder definitivamente à pergunta de pesquisa.

A análise considera apenas três carteiras, selecionadas entre as 5 com maior número de arcos de saída em cada classe. Além disso, o recorte foi construído a partir de 50 carteiras ilícitas, o que pode favorecer a observação de estruturas relacionadas a essa categoria.

Também é necessário distinguir a existência de ciclos na região alcançável da participação direta da carteira de origem nesses ciclos.

Por fim, a DFS identifica ciclos estruturais, mas não confirma se eles possuem peso negativo. Essa verificação depende da implementação do Bellman-Ford, que é uma entrega obrigatória do projeto.

Após a implementação, será necessário atualizar os resultados e verificar se as carteiras participam efetivamente de ciclos negativos.

Dessa forma, os resultados atuais representam uma etapa exploratória importante para compreender a estrutura das redes analisadas, mas ainda não permitem concluir que carteiras ilícitas participam mais de ciclos negativos do que carteiras lícitas.

# Parte 2 — Desempenho e escalabilidade

## Como foi medido

Escrever: quais algoritmos, quais tamanhos (10%, 50% e 100%) e a média de 5 execuções.

## Decisões

A escolha da carteira de maior grau de saída como origem no BFS e Bellman-Ford foi arbitrária, escolhido porque com mais graus de saída tem uma maior probabilidade de se conseguir uma maior sequência de nós conectados, mesmo que não tenha sido o caso, a regra diz que a origem pode ser escolhida de forma arbitrária. A escala log foi escolhida porque permite ver melhor a diferença entre os números. A fórmula do custo vem da complexidade de cada algoritmo, com base no código deles.

O gráfico de tempo é um gráfico de linha, escolhido por ser simples.

## Resultados

Comentar o Json e a tabela
## Comparação com a complexidade teórica

Escrever

## Limitações

Uma limitação é a amostra de 10%. Ela é um sorteio com seed fixa, que pega 1.418 carteiras e só as arestas que têm as duas pontas entre as sorteadas. Escolhemos como origem a carteira com mais arcos de saída, e ela tem só 3, ligados a outras carteiras sorteadas. Essas 3 carteiras não levam a nenhuma carteira nova, por isso, em 10%, o BFS e o Bellman-Ford alcançam só 4 carteiras. A DFS roda sem origem: quando termina uma busca, recomeça em uma carteira ainda não visitada e, por isso, alcança todas as carteiras sorteadas.
