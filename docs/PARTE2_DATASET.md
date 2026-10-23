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

| # | Decisão | O que foi feito |
|---|---|---|
| 1 | **Grafo** | carteiras (addr → addr): tem ciclos, então o ciclo negativo pode vir dos próprios dados |
| 2 | **Peso (Bellman-Ford)** | `peso(A → B) = saldo líquido de B = btc_received_total − btc_sent_total` (somado em todos os time steps). Positivo: B acumula BTC. Negativo: B repassa mais do que recebe. Ciclo negativo: grupo de carteiras que ficam repassando dinheiro entre si |
| 3 | **Peso (Dijkstra)** | `valor_btc` = soma do `total_BTC` das transações do par A → B. Já vem ≥ 0 dos dados; caminho mínimo = rota que movimenta menos dinheiro |
| 4 | **Laços** (A → A) | removidos: são troco e virariam ciclos negativos falsos (45.981) |
| 5 | **Arestas duplicadas** | agregadas em um arco por par: `valor_btc` = soma, `n_txs` = nº de transações (47.346 linhas a menos) |
| 6 | **Atributos por carteira** | somados em todos os time steps (`*_total`, `total_txs`); máximo para `lifetime_in_blocks` e `num_timesteps_appeared_in` |
| 7 | **Transações sem valor** | tenta `in_BTC_total − fees`; nas 965, todas as colunas de valor faltam juntas, então ficam marcadas em `valor_faltante`. No recorte atual nenhum arco é afetado |
| 8 | **Recorte** | bola de neve a partir de 50 carteiras ilícitas sorteadas (seed 42), expandindo por vizinhos de entrada e saída até ≥ 25.000 arestas no subgrafo induzido |
| 9 | **Pergunta de pesquisa** | *Carteiras ilícitas participam mais de ciclos de repasse (ciclos negativos) do que as lícitas?* (confirmada pelo grupo) |

Como reproduzir:

```bash
python scripts/baixar_dataset.py
python scripts/amostrar_dataset.py   # --arestas 25000 --sementes 50 --seed 42
```

## Recorte gerado (`data/dataset_parte2/`)

| Arquivo | Conteúdo |
|---|---|
| `arestas.csv` | `origem, destino, peso, valor_btc, n_txs, valor_faltante` |
| `nos.csv` | `endereco, classe, saldo_btc, btc_received_total, btc_sent_total, total_txs, fees_total, lifetime_in_blocks, num_timesteps_appeared_in` |
| `recorte_info.json` | parâmetros, sementes e contagens |

| Métrica | Valor |
|---|---|
| Carteiras (nós) | 14.182 (ilícitas 5.208 · desconhecidas 4.713 · lícitas 4.261) |
| Arcos | 25.111 |
| Arcos com peso negativo | 3.279 (13%) |
| Arcos com peso zero | 8.658 (34%) |

**Pontos para o PDF (limitações):**
- **Viés da amostra:** ilícitas são 37% do recorte, mas 1,7% do dataset completo, porque as sementes são ilícitas. É intencional (a pergunta é sobre elas), mas precisa ser dito.
- O peso depende só da carteira de **destino**: todos os arcos que chegam em B têm o mesmo peso.
- O `valor_btc` é da transação inteira, não do valor exato enviado de A para B.
- **Falta conferir** com o Bellman-Ford do grupo se o recorte tem ciclo negativo. Se não tiver, o enunciado permite montar o caso a partir de um sub-recorte documentado.
- Para a escalabilidade (10/50/100%), sortear nós do recorte e usar o subgrafo induzido.

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
