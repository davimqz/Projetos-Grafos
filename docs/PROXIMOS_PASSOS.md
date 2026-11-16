# Próximos passos (atualizado em 16/11/2026)

Entrega em **26/11**. Acompanhamentos: 17, 19 e 24/11. Checklist completo por pacote em `PLANO_DE_TRABALHO.md`.

## Status

| Frente | Situação |
|---|---|
| Estrutura do repositório, mapas, README inicial | ✅ pronto |
| **P2** Grafo e algoritmos (`graph.py`, BFS, DFS, Dijkstra, Bellman-Ford + testes) | ✅ pronto (PRs #2, #3, #6, #8, #10, #12) |
| **P4a** Dataset e casos obrigatórios da Parte 2 | ✅ pronto, com resultados e interpretação em `docs/relatorio/parte2.md` (PR #16) |
| **P1** `io.py`, `estados.py` (G_pos, G_est, variantes) + testes | ✅ pronto (PRs #15 e #18) |
| **P5a** Figuras da Parte 1 e `labirinto_interativo.html` | 🟡 template do HTML na main (PR #20); figuras e integração com o G_est no PR #19, em revisão |
| **P3** Análises da Parte 1 | ⏳ **não começado**: falta `src/solve.py` (métricas, camadas, graus, `arestas_<mapa>.csv`, armadilhas, m05, mapas do grupo) |
| **P4b** Benchmark e escalabilidade | 🟡 DFS, BFS e Bellman-Ford medidos; falta Dijkstra e os gráficos de comportamento/caminhos |
| **P5b** AVD (notebooks) | ⏳ `notebooks/avd/` ainda vazio; **acompanhamento de AVD em 17/11** |
| **P5c** README final, PDF, declaração de IA | ⏳ no fim |

> ⚠️ **Regra da professora:** `io.py`, `estados.py`, `graph.py` e `algorithms.py` **não podem ser gerados por IA**,
> nem análises, notas analíticas, escolha/interpretação de gráficos e a prova do m05. Todo uso de IA vai em `docs/REGISTRO_IA.md`.

### Correção de 12/11: saldo inflado

`wallets_features.csv` repete em cada time step os totais da vida inteira da carteira. Somar as linhas contava o mesmo valor várias vezes.
A carga agora usa uma linha por endereço. O recorte manteve os mesmos nós e arcos, mas 8.206 pesos mudaram (nenhum de sinal).
O Bellman-Ford foi refeito: o ciclo continua, com custo −13.226,15 (antes −1.113.112,70). O Dijkstra e o benchmark não mudam.
**Quem usar `nos.csv` (AVD) deve partir da versão nova.**

## Ambiente

```bash
git clone https://github.com/davimqz/Projetos-Grafos.git
cd Projetos-Grafos
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest          # 311 testes passando em 16/11
```

O recorte da Parte 2 já está no repositório; **não precisa baixar o dataset** (só para refazer o recorte).

## Fluxo de trabalho

1. Uma branch por tarefa.
2. Commits no padrão `tipo(escopo): descrição`.
3. PR para `main` marcando o **revisor do pacote** (ver `PLANO_DE_TRABALHO.md`); o revisor aprova e faz o merge.

---

## Matheus — P1 + P3 (revisor: Thomaz) · **prioridade do grupo**

- [x] `estados.py`: G_pos, G_est, rótulos, nó `ALVO` e variantes (portas chão/parede, `+` fixo, fonte consumível)
- [x] `test_estados.py`
- [ ] revisar o PR #19 (figuras e HTML do Thomaz)
- [ ] `src/solve.py`: exportar `out/parte1/arestas_<mapa>.csv` (m01–m08)
- [ ] análises do P3: `metricas_global.json`, `camadas.json`, graus, `comparacao_modelagem.csv`, m05 (BF no G_pos × G_est + prova), `solucoes.csv`
- [ ] armadilhas do m04 e do m07 (busca a partir de ALVO no transposto); o HTML e a CLI já recebem a lista de estados
- [ ] 2 mapas em `data/mapas_grupo/` + gabarito

## Thomaz — P2 + P5a (revisor: Matheus)

- [x] revisar o PR do `estados.py`
- [ ] PR #19: percursos m03/m08, camadas e árvore BFS do m02, heatmap do m08 e HTML com os dados reais (em revisão)
- [ ] ajustes pedidos na revisão do PR #19
- [ ] quando o P3 gerar as armadilhas, ligar o HTML a elas

## Vagner — P4b + P5b (revisor: Davi)

- [x] template do `labirinto_interativo.html` (PR #20)
- [ ] **AVD em `notebooks/avd/` (acompanhamento em 17/11)**: 4 pilares, faltantes (classe "desconhecido" não se apaga), classe × todos os atributos
- [ ] ≥4 exploratórias + ≥2 explanatórias com nota analítica autoral (sem IA na escolha/interpretação dos gráficos)
- [ ] usar o `nos.csv` corrigido em 12/11
- [ ] benchmark: incluir o Dijkstra e os gráficos de comportamento/caminhos

## Davi — P4a + P5c

- [x] carga do recorte, casos obrigatórios e relatório da Parte 2 (PR #16)
- [x] correção do saldo inflado e atualização dos resultados
- [ ] revisar o PR #19
- [ ] revisar os PRs do Vagner (benchmark e AVD)
- [ ] README final, PDF (manual + técnica + limitações + conclusões + matriz de contribuição)
- [ ] `docs/DECLARACAO_IA.pdf` assinada por todos; conferir marcações `# [IA]` e `REGISTRO_IA.md`
