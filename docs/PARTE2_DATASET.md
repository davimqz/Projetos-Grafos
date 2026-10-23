# Parte 2 — Elliptic++: o que falta para cumprir o enunciado

Fonte: <https://github.com/git-disl/EllipticPlusPlus> (os CSVs ficam no Google Drive linkado no README do repositório).

| Subconjunto | Nós | Arestas | Arquivos |
|---|---|---|---|
| Transações (tx → tx, fluxo de dinheiro) | 203.769 | 234.355 | `txs_features.csv`, `txs_classes.csv`, `txs_edgelist.csv` |
| Atores / carteiras (addr → addr) | 822.942 | 2.868.964 | `wallets_features.csv`, `wallets_classes.csv`, `AddrAddr_edgelist.csv` |
| Bipartido (addr → tx → addr) | — | 1.314.241 | `AddrTx_edgelist.csv`, `TxAddr_edgelist.csv` |

Classes: 1 = ilícito, 2 = lícito, 3 = desconhecido (~77% das transações e ~68% das carteiras).

## Requisitos × situação

| Requisito do enunciado | Elliptic++ | Situação |
|---|---|---|
| Não aéreo / não grade | rede de transações Bitcoin | ✅ |
| Dirigido | arestas têm sentido (quem paga → quem recebe) | ✅ |
| ≥ 20.000 arestas | 234 mil (tx) / 2,87 milhões (addr) | ✅, mas **acima de ~500 mil exige amostragem justificada** |
| **Ponderado** | edgelists têm só `(origem, destino)` | ❌ **falta: derivar o peso das features** |
| **Pesos negativos vindos dos dados** | não há | ❌ **falta: precisa de significado no domínio, não vale sortear** |
| Ciclo negativo (Bellman-Ford) | tx → tx é **acíclico** (uma transação só gasta saídas de transações anteriores); addr → addr tem ciclos | ⚠️ depende do subgrafo escolhido |
| Dados faltantes / outliers (AVD) | classe "desconhecido" é ausência de rótulo; valores BTC muito assimétricos | ✅ material bom para discutir o mecanismo de ausência |

## Features úteis para o peso

- **Transações:** `total_BTC`, `fees`, `in_BTC_*`, `out_BTC_*`, `num_input_addresses`, `num_output_addresses`, `size`, `in_txs_degree`, `out_txs_degree`, `Time step`.
- **Carteiras:** `btc_sent_*`, `btc_received_*`, `btc_transacted_*`, `fees_*`, `fees_as_share_*`, `blocks_btwn_*`, `lifetime_in_blocks`, `num_txs_as_sender`, `transacted_w_address_*`, `Time step`.

## Armadilha conceitual a evitar

Se o peso do arco for a **diferença de um atributo dos nós**, ou seja `w(u→v) = f(v) − f(u)`
(ou `log f(v) − log f(u)`), todo ciclo soma **exatamente 0**: os termos se cancelam ao longo do ciclo.
Esse peso **nunca** gera ciclo negativo, nem no grafo de carteiras. Para existir ciclo negativo,
o peso precisa depender do **arco** (ou do destino de um jeito que não se cancele).

## Decisões tomadas (23/10)

- **Grafo de carteiras (addr → addr)**, porque tem ciclos e permite um ciclo negativo vindo dos próprios dados.
- **Recorte de 25.000 arestas.** O grafo completo tem 2,87 milhões, então a amostragem é obrigatória e precisa ser justificada no PDF.
- Download: `python scripts/baixar_dataset.py` (os CSVs brutos ficam em `data/dataset_parte2/raw/`, fora do git).

## Fatos do grafo completo (conferidos em 23/10)

| Item | Valor | Implicação |
|---|---|---|
| Arestas em `AddrAddr_edgelist.csv` | 2.868.964 | |
| Laços (carteira → ela mesma) | 45.981 | são **troco** de transação; com peso negativo, cada laço vira sozinho um ciclo negativo. Tratamento precisa ser decidido |
| Arestas duplicadas | 84.620 | o mesmo par interagiu em mais de uma transação: agregar ou manter? |
| Linhas em `wallets_features.csv` | 1.268.260 para 822.942 endereços | features são **por (endereço, time step)**: é preciso agregar por endereço |
| Origem de cada aresta addr → addr | cada linha é um trio (carteira de entrada, transação, carteira de saída): o join `AddrTx` × `TxAddr` reproduz as 2.868.964 linhas | dá para levar atributos da **transação** para o arco |
| Valor da transação (`total_BTC` = `out_BTC_total`, `in_BTC_total`, `fees`) | mínimo ≥ 0 em todas; `fees` = `in_BTC_total − out_BTC_total` | **não existe valor negativo**; o valor é da transação inteira, não de cada saída para cada carteira |
| Transações sem valor (NaN) | 965 | dado faltante para discutir (AVD) |
| `btc_received_total − btc_sent_total` por endereço | < 0: 24,3% · = 0: 22,3% · > 0: 53,5% | o dado já tem uma grandeza com sinal |

## Decisões em aberto (o grupo decide)

1. ~~Qual grafo~~: decidido, carteiras.
2. **Qual peso** e o que significam, no domínio, um *caminho mínimo* e um *ciclo negativo*.
3. **Estratégia do recorte** (tamanho decidido: 25 mil arestas): o mínimo do enunciado é ≥ 20 mil arestas. Amostrar arestas ao acaso
   quebra os caminhos. Uma alternativa é expandir por BFS ("bola de neve") a partir de sementes
   (ex.: nós ilícitos) até o tamanho alvo, preservando a conectividade.
   As frações de 10%/50%/100% da escalabilidade saem desse recorte.
4. **Transformação para o Dijkstra** (pesos ≥ 0): ex.: somar uma constante, usar |w| ou só a parte não negativa. Precisa ser justificada.
5. **Pergunta de pesquisa** final, alinhada com a proposta aprovada no checkpoint.
