# Próximos passos (atualizado em 12/11/2026)

Entrega em **26/11**. Acompanhamentos: 17, 19 e 24/11. Checklist completo por pacote em `PLANO_DE_TRABALHO.md`.

## Status

| Frente | Situação |
|---|---|
| Estrutura do repositório, mapas, README inicial | ✅ pronto |
| **P2** Grafo e algoritmos (`graph.py`, BFS, DFS, Dijkstra, Bellman-Ford + testes) | ✅ pronto (PRs #2, #3, #6, #8, #10, #12) |
| **P4a** Dataset da Parte 2 (recorte, pesos, carga) | ✅ pronto; saldo das carteiras corrigido em 12/11 (ver abaixo) |
| **P4a** Casos obrigatórios (BFS/DFS 3 fontes, Dijkstra 5 pares, Bellman-Ford 2 casos) | ✅ pronto, com resultados e interpretação em `docs/relatorio/parte2.md` (PR #16) |
| **P4b** Benchmark e escalabilidade | 🟡 DFS, BFS e Bellman-Ford medidos (`parte2_report.json` + gráfico); falta Dijkstra e os gráficos de comportamento/caminhos |
| **P1** `io.py` + `test_io.py` | ✅ pronto (PR #15) |
| **P1** `estados.py` (G_pos, G_est, variantes) + `test_estados.py` | ⏳ **não começado**: bloqueia P3 e P5a |
| **P3** Análises da Parte 1 | ⏳ depende do G_est |
| **P5a** Figuras e `labirinto_interativo.html` | ⏳ depende do G_est |
| **P5b** AVD (notebooks) | ⏳ `notebooks/avd/` ainda vazio |
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
pytest          # 225 testes passando em 12/11
```

O recorte da Parte 2 já está no repositório; **não precisa baixar o dataset** (só para refazer o recorte).

## Fluxo de trabalho

1. Uma branch por tarefa.
2. Commits no padrão `tipo(escopo): descrição`.
3. PR para `main` marcando o **revisor do pacote** (ver `PLANO_DE_TRABALHO.md`); o revisor aprova e faz o merge.

---

## Matheus — P1 + P3 (revisor: Thomaz) · **prioridade do grupo**

- [ ] `estados.py`: G_pos e G_est por exploração a partir de S, rótulos `(l,c)|chaves|{bônus}`, nó `ALVO`
- [ ] variantes: portas como chão/parede, `+` fixo em −4, `--fonte-consumivel`
- [ ] `test_estados.py` com mapa mínimo contado à mão; conferir o G_est do m02 com o desenho
- [ ] exportar `out/parte1/arestas_<mapa>.csv` (m01–m08)
- [ ] depois: análises do P3 (métricas, camadas, graus, comparação de modelagens, m05, armadilhas, mapas do grupo)

## Thomaz — P5a (revisor: Matheus)

- [ ] revisar o PR do `estados.py`
- [ ] quando houver G_est: percursos m03/m08, camadas e árvore BFS do m02, heatmap do m08
- [ ] `labirinto_interativo.html`

## Vagner — P4b + P5b (revisor: Davi)

- [ ] benchmark: incluir o Dijkstra e os gráficos de comportamento/caminhos
- [ ] AVD em `notebooks/avd/`: 4 pilares, faltantes (classe "desconhecido" não se apaga), classe × todos os atributos
- [ ] ≥4 exploratórias + ≥2 explanatórias com nota analítica autoral (sem IA na escolha/interpretação dos gráficos)
- [ ] usar o `nos.csv` corrigido em 12/11

## Davi — P4a + P5c

- [x] carga do recorte, casos obrigatórios e relatório da Parte 2
- [x] correção do saldo inflado e atualização dos resultados
- [ ] merge do PR #16 (revisão do Vagner)
- [ ] revisar os PRs do Vagner (benchmark e AVD)
- [ ] README final, PDF (manual + técnica + limitações + conclusões + matriz de contribuição)
- [ ] `docs/DECLARACAO_IA.pdf` assinada por todos; conferir marcações `# [IA]` e `REGISTRO_IA.md`
