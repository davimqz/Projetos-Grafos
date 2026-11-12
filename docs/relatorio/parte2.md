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

### 4.4. Limitações da análise com pesos negativos

A análise realizada com o Bellman-Ford permitiu identificar um ciclo negativo no recorte estudado. Entretanto, os resultados estão limitados à quantidade de origens selecionadas e às estruturas alcançáveis a partir delas. Foram analisadas apenas duas origens, o que não permite estabelecer uma comparação estatisticamente representativa entre carteiras lícitas, ilícitas e desconhecidas.

Além disso, a magnitude do ciclo identificado é fortemente influenciada por um valor extremo associado ao saldo de uma das carteiras. Essa característica exige cautela na interpretação dos custos acumulados, especialmente porque os atributos financeiros utilizados podem apresentar limitações decorrentes da agregação dos dados ao longo dos diferentes períodos analisados.

A interpretação dos ciclos identificados e sua relação com a pergunta de pesquisa são apresentadas na seção de resultados do Bellman-Ford.

### 4.5. Alcançar uma carteira não significa participar de um ciclo

Uma carteira pode alcançar uma região do grafo que contém ciclos sem fazer parte desses ciclos.

Por exemplo, uma carteira pode estar conectada a outras carteiras que formam um ciclo, mas não possuir uma conexão que permita retornar à própria origem.

Assim, identificar ciclos na região alcançável não é suficiente para afirmar que a carteira inicial participa deles.

Essa distinção é fundamental porque a pergunta de pesquisa trata especificamente da participação das carteiras em ciclos de repasse.

## 5. Conclusão

A análise das transações e das estruturas do grafo permitiu investigar diferentes aspectos da circulação de recursos entre carteiras classificadas como lícitas, ilícitas e desconhecidas. A aplicação dos algoritmos BFS, DFS, Dijkstra e Bellman-Ford possibilitou observar tanto a conectividade entre os endereços quanto características dos caminhos e a existência de ciclos negativos.

As análises de BFS e DFS permitiram explorar a estrutura da rede a partir de diferentes origens, identificando carteiras alcançáveis e relações entre diferentes regiões do grafo. Posteriormente, a aplicação do Dijkstra possibilitou identificar caminhos de menor custo entre pares de carteiras de diferentes classificações. Os resultados do Dijkstra evidenciaram diferenças nos custos das trajetórias analisadas. No entanto, a comparação entre os sentidos Lícita → Ilícita e Ilícita → Lícita envolve pares distintos de carteiras, e não os mesmos pares percorridos em sentidos opostos. Assim, os custos observados de 49,95 BTC e 10,88 BTC, respectivamente, refletem trajetórias específicas e não permitem concluir que exista uma assimetria geral no fluxo entre essas classes. Também foi observada a repetição de determinadas carteiras intermediárias em diferentes caminhos, sugerindo a existência de pontos compartilhados de circulação na rede.

Outro resultado relevante do Dijkstra foi a identificação de uma trajetória entre duas carteiras ilícitas que passa por uma carteira desconhecida anteriormente explorada nas análises de BFS e DFS. Esse resultado demonstra que regiões investigadas separadamente podem apresentar conexões por meio de carteiras intermediárias, reforçando a importância de analisar a rede como uma estrutura interconectada.

O Bellman-Ford acrescentou uma dimensão importante à investigação ao permitir trabalhar com pesos negativos e identificar ciclos negativos. Na execução iniciada pela carteira lícita, apesar da presença de 29 arcos negativos, não foi encontrado nenhum ciclo negativo alcançável. Já na execução iniciada pela carteira desconhecida, foi identificado um ciclo composto por duas carteiras, também alcançável a partir de uma origem ilícita.

A análise desse ciclo revelou que uma de suas integrantes é classificada como lícita, embora apresente saldo fortemente negativo. Além disso, o custo acumulado da estrutura é dominado por um valor extremo, o que exige cautela na interpretação de sua magnitude. Esse resultado demonstra que comportamentos identificados pela métrica de saldo não são exclusivos de carteiras classificadas como ilícitas.

Considerando a pergunta de pesquisa, os resultados não permitem afirmar que carteiras ilícitas participam mais frequentemente de ciclos de repasse do que carteiras lícitas. A identificação de um único ciclo negativo, alcançável por origens de diferentes classificações, não é suficiente para estabelecer essa relação. Também é necessário distinguir entre alcançar uma estrutura cíclica e participar diretamente dela, uma vez que as origens utilizadas nas execuções não integram o ciclo identificado.

Por fim, devem ser consideradas as limitações metodológicas da investigação. O recorte utilizado apresenta viés de seleção, pois foi construído a partir de carteiras previamente identificadas, não representando necessariamente a distribuição real das classes na rede completa. Além disso, a quantidade reduzida de pares analisados pelo Dijkstra e de origens utilizadas pelo Bellman-Ford limita a generalização dos resultados.

Outra limitação está relacionada aos pesos empregados nos algoritmos. No Dijkstra, o valor integral das transações foi utilizado como peso, não representando necessariamente o montante efetivamente transferido entre cada par de carteiras. No Bellman-Ford, a utilização do saldo das carteiras como peso permite identificar ciclos negativos segundo a definição adotada, mas valores extremos podem influenciar significativamente os custos acumulados.

Portanto, o trabalho contribui para compreender as relações de conectividade, os caminhos de circulação e a existência de estruturas compatíveis com ciclos de repasse entre carteiras. Entretanto, a hipótese de que carteiras ilícitas participam mais frequentemente dessas estruturas do que carteiras lícitas permanece inconclusiva, sendo necessária uma investigação com maior quantidade de origens, destinos e ciclos identificados para sustentar essa afirmação.

# Parte 2 — Resultados de Dijkstra e Bellman-Ford

<!-- [IA] Claude Code – estrutura da seção, tabelas montadas a partir dos JSONs de out/parte2/ e transcrição literal das justificativas escritas pelo Davi. As interpretações foram escritas pelo Davi. -->

## 1. Critérios de escolha

### Bellman-Ford

- **Caso com ciclo negativo:** carteira desconhecida `1MFXYK1XucKFfhPhW9HDHD3vsM9BKey4qm`, a mesma usada no BFS e na DFS.
- **Caso sem ciclo negativo:** escolher a carteira lícita `3Fzzji5nFaSptmYL8bNsm3KcpYm3qnxqBS`, pois, entre as carteiras que atendem ao requisito de pesos negativos sem ciclo negativo, é a que alcança a maior quantidade de arcos negativos (29).

### Dijkstra

Peso: `valor_btc`, a soma dos valores das transações entre as duas carteiras (ver "Design dos pesos").

Quero analisar cinco combinações: Ilícita → Ilícita; Ilícita → Lícita; Lícita → Ilícita; Desconhecida → Ilícita; Ilícita → Desconhecida. O objetivo é comparar a circulação entre as classes e investigar principalmente as relações entre carteiras lícitas e ilícitas, considerando os dois sentidos das conexões.

As origens são as mesmas carteiras usadas no BFS e na DFS.

**Critério do destino:** selecionar o primeiro destino da classe desejada na ordem de visita do BFS, desde que esteja a pelo menos 3 passos da origem. Assim, conseguimos analisar trajetórias com carteiras intermediárias, em vez de considerar apenas transferências diretas.

**Origem do par Lícita → Ilícita:** a carteira lícita usada no BFS só alcança carteiras ilícitas a até 2 passos. Utilizar outra carteira lícita como origem mantém o critério de pelo menos 3 passos uniforme entre as combinações do Dijkstra, evitando uma exceção metodológica. Para selecionar a origem: escolher a carteira lícita que alcança o maior número de carteiras ilícitas a partir de 3 passos de distância. Em caso de empate, utilizar a que apresentar a maior distância mínima média até os destinos ilícitos selecionados.

Como as cinco carteiras empataram nos dois primeiros critérios (quantidade de destinos ilícitos alcançados e distância média), utilizamos o número de transações como terceiro critério de desempate. Isso privilegia a carteira com maior atividade transacional e oferece uma origem mais representativa para a análise de caminhos.

## 2. Resultados do Dijkstra

| Par | Origem | Destino | Custo (BTC) | Arcos | Caminho |
|---|---|---|---|---|---|
| Ilícita → Ilícita | `39sfuA8p…` | `17uQbqBG…` | 26,55 | 5 | `39sfuA8p` → `1MLvzsdb` → `1FAv42Ga` → `16PaWFJt` → `1MFXYK1X` → `17uQbqBG` |
| Ilícita → Lícita | `39sfuA8p…` | `16PaWFJt…` | 10,88 | 3 | `39sfuA8p` → `1MLvzsdb` → `1FAv42Ga` → `16PaWFJt` |
| Lícita → Ilícita | `3MTTgd2B…` | `17tqJV8U…` | 49,95 | 4 | `3MTTgd2B` → `1KNd3pk9` → `3Fp5ejYY` → `3AhpkBp2` → `17tqJV8U` |
| Desconhecida → Ilícita | `1MFXYK1X…` | `1GeFfWdv…` | 59,81 | 3 | `1MFXYK1X` → `1LVQMGJ9` → `14GA7Uy9` → `1GeFfWdv` |
| Ilícita → Desconhecida | `39sfuA8p…` | `1J5U1rN5…` | 5,54 | 3 | `39sfuA8p` → `1MLvzsdb` → `1FAv42Ga` → `1J5U1rN5` |

Endereços completos e peso de cada arco: `out/parte2/dijkstra_<origem>_<destino>.json`.

### Interpretação dos resultados do Dijkstra

A aplicação do algoritmo de Dijkstra permitiu identificar os caminhos de menor custo entre cinco pares de carteiras de diferentes classificações, utilizando `valor_btc` como peso das arestas. Os custos encontrados variaram entre 5,54 BTC e 59,81 BTC, evidenciando diferenças nas trajetórias de circulação de recursos entre as classes analisadas.

Na comparação entre os pares Lícita → Ilícita e Ilícita → Lícita, foram observados custos de 49,95 BTC e 10,88 BTC, respectivamente. É importante destacar que se trata de pares distintos de carteiras, com origens e destinos diferentes, e não da inversão de um mesmo trajeto. Portanto, a diferença evidencia características específicas dos caminhos selecionados, mas não permite estabelecer uma assimetria geral na circulação entre essas classes.

Outro aspecto observado foi a repetição da sequência de carteiras `39sfuA8p → 1MLvzsdb → 1FAv42Ga` em três caminhos que partem de uma origem ilícita. Essa recorrência sugere que esses endereços desempenham um papel de intermediação na rede, funcionando como pontos de passagem compartilhados por diferentes trajetórias. A presença dessas carteiras em múltiplos caminhos indica uma possível concentração da circulação em determinados endereços, que podem atuar como pontes entre diferentes regiões do grafo. Contudo, essa observação, isoladamente, não comprova que sejam os principais pontos de intermediação da rede, sendo necessária uma análise estrutural complementar para confirmar essa hipótese.

O caminho identificado pelo Dijkstra reforça uma conexão que já estava presente nos resultados do BFS: a carteira desconhecida `1MFXYK1X` é alcançável a partir da origem ilícita. A análise do caminho de menor custo permitiu destacar essa relação, evidenciando a conexão entre as regiões exploradas.

A comparação entre o número de arcos também demonstra que o caminho de menor custo não corresponde necessariamente ao caminho com menor quantidade de transferências. No par Ilícita → Ilícita, por exemplo, o destino estava a três passos da origem na exploração por BFS, mas o caminho selecionado pelo Dijkstra utilizou cinco arcos. Isso ocorre porque o Dijkstra prioriza a soma dos pesos das arestas, podendo selecionar uma trajetória com mais etapas quando ela apresenta um custo acumulado inferior.

É importante considerar, entretanto, que `valor_btc` representa o valor integral de cada transação, e não necessariamente o montante efetivamente transferido entre a carteira de origem e a carteira de destino. Dessa forma, o custo acumulado representa a soma dos valores associados às transações que compõem o caminho, não devendo ser interpretado como uma medida exata do volume transferido entre os endereços. Além disso, a análise contempla apenas cinco pares de carteiras, de modo que os resultados representam exemplos de trajetórias possíveis na rede, não sendo suficientes para estabelecer padrões gerais de circulação entre as diferentes classes.

## 3. Resultados do Bellman-Ford

| Caso | Origem | Status | Resultado |
|---|---|---|---|
| Sem ciclo negativo | `3Fzzji5n…` (lícita) | OK | 45 carteiras alcançadas (incluindo a origem), 29 arcos negativos alcançáveis; distâncias de −4,23 a 169,82; 8 carteiras com distância negativa |
| Com ciclo negativo | `1MFXYK1X…` (desconhecida) | CICLO_NEGATIVO | ciclo de 2 carteiras: `1DEcTtkrbdXxS1wbrMvzub5X4VpByYmAwo` → `12cgpFdJViXbwHbhrA3TuW1EGnL25Zqc3P` → `1DEcTtkr…` |

Arcos do ciclo negativo:

| Arco | Peso (saldo do destino) |
|---|---|
| `1DEcTtkr…` → `12cgpFdJ…` | −1.082.372,06 |
| `12cgpFdJ…` → `1DEcTtkr…` | −30.740,64 |
| **Custo do ciclo** | **−1.113.112,70** |

Resultados completos: `out/parte2/bellman_ford_<origem>.json`.

### Interpretação dos resultados do Bellman-Ford

A aplicação do algoritmo de Bellman-Ford permitiu investigar a existência de ciclos negativos na rede, utilizando como peso das arestas o saldo da carteira de destino, calculado pela diferença entre os valores recebidos e enviados. Nesse modelo, arcos negativos representam conexões cujo destino apresenta saldo negativo, enquanto ciclos negativos representam estruturas nas quais a soma dos pesos das arestas do circuito também é negativa.

**Caso 1: origem lícita (`3Fzzji5n…`)**

Na execução iniciada pela carteira lícita, o algoritmo terminou normalmente, sem identificar ciclos negativos alcançáveis. Foram alcançadas 45 carteiras, com passagem por 29 arcos negativos. Além disso, oito carteiras apresentaram distâncias acumuladas negativas.

Esse resultado demonstra que a presença de arcos negativos não implica necessariamente a formação de ciclos de repasse. Uma carteira pode apresentar saldo negativo e estar conectada a outras carteiras com a mesma característica sem que exista um caminho direcionado de retorno que forme um circuito negativo. Nesse caso, os arcos negativos aparecem em trajetórias que não constituem ciclos negativos alcançáveis pela origem analisada.

As oito distâncias negativas também indicam que existem trajetórias cujo custo acumulado, segundo os pesos definidos, permanece abaixo de zero. Isso reforça a distinção entre alcançar carteiras por caminhos de custo negativo e identificar efetivamente uma estrutura cíclica. Portanto, a ausência de ciclos negativos nessa execução não significa ausência de comportamentos de repasse, mas demonstra que os arcos negativos encontrados não formaram um ciclo negativo alcançável a partir daquela origem.

**Caso 2: origem desconhecida (`1MFXYK1X…`)**

Na execução iniciada pela carteira desconhecida, o Bellman-Ford identificou um ciclo negativo composto por duas carteiras que possuem conexões direcionadas entre si. Os dois arcos apresentam pesos negativos, indicando que ambas possuem saldos negativos segundo a métrica adotada.

O custo acumulado do ciclo foi de aproximadamente −1.113.113 BTC. Entretanto, esse valor é fortemente influenciado por um único arco, com peso de aproximadamente −1.082.372 BTC. A consulta ao arquivo `nos.csv` permitiu identificar a carteira responsável por esse valor: `12cgpFdJViXbwHbhrA3TuW1EGnL25Zqc3P`, classificada como lícita. O endereço apresenta 7.396 transações, aproximadamente 568.470,94 BTC recebidos e 1.650.843 BTC enviados, resultando em saldo de aproximadamente −1.082.372 BTC.

Esse resultado evidencia a presença de um valor extremo (*outlier*) na composição do ciclo. Embora o custo acumulado seja expressivo, sua magnitude não representa necessariamente um comportamento típico das carteiras envolvidas. A concentração de grande parte do valor negativo em uma única carteira exige cautela ao interpretar a intensidade econômica da estrutura identificada.

É importante destacar que a carteira de origem `1MFXYK1X…` não participa diretamente do ciclo negativo: ela apenas possui um caminho que permite alcançá-lo. A mesma estrutura também pode ser alcançada a partir da carteira ilícita `39sfuA8p…`. Dessa forma, duas origens de classificações diferentes conseguem alcançar o mesmo ciclo, embora nenhuma delas seja necessariamente integrante de sua estrutura.

A classificação das carteiras que compõem o ciclo também é relevante para a interpretação dos resultados. Uma delas pertence à classe lícita (`12cgpFdJViXbwHbhrA3TuW1EGnL25Zqc3P`), enquanto a outra é desconhecida (`1DEcTtkrbdXxS1wbrMvzub5X4VpByYmAwo`), com 2.304 transações e saldo aproximado de −30.740 BTC. Portanto, o ciclo negativo identificado é formado por uma carteira lícita e uma desconhecida, sem participação direta de carteiras classificadas como ilícitas. Embora uma origem ilícita consiga alcançar esse ciclo, alcançar uma estrutura não significa participar dela. Esse resultado, portanto, não sustenta a hipótese de que carteiras ilícitas participem mais de ciclos de repasse; além disso, a quantidade limitada de origens analisadas impede uma conclusão geral sobre essa relação.

**Relação com a pergunta de pesquisa**

A pergunta de pesquisa investiga se carteiras ilícitas participam mais frequentemente de ciclos de repasse do que carteiras lícitas. Os resultados obtidos permitem identificar uma estrutura compatível com a definição de ciclo negativo adotada no trabalho, mas não são suficientes para confirmar essa hipótese.

A execução iniciada pela carteira lícita não identificou ciclos negativos alcançáveis, enquanto a execução iniciada pela carteira desconhecida encontrou um ciclo composto por duas outras carteiras. A consulta ao `nos.csv` revelou que uma das integrantes do ciclo é classificada como lícita, apesar de apresentar saldo fortemente negativo. Esse achado demonstra que a classificação de uma carteira não determina, isoladamente, seu comportamento segundo a métrica de saldo utilizada.

Além disso, o fato de uma origem ilícita também alcançar o mesmo ciclo não significa que ela participe diretamente dele. Portanto, não é possível utilizar esse resultado como evidência de que carteiras ilícitas integram mais ciclos de repasse. A quantidade reduzida de origens analisadas e a identificação de apenas uma estrutura cíclica limitam qualquer comparação entre as classes.

Por fim, o valor extremo identificado influencia significativamente a magnitude do custo acumulado, mas não elimina a existência matemática do ciclo negativo encontrado. Como os dois arcos apresentam pesos negativos, a soma permanece negativa. Assim, o *outlier* enfraquece a interpretação da magnitude do resultado como medida representativa, mas não invalida a identificação do ciclo segundo os critérios definidos.

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
