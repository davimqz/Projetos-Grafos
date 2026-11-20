# Mapas de treino (mapa surpresa)

<!-- [IA] Claude Code – sugestão dos mapas de treino; números conferidos com o código do grupo -->

Mapas para ensaiar a demonstração ao vivo com mapa surpresa. **Não são os mapas do grupo da Seção 10**, que ficam em
`data/mapas_grupo/`. Os nomes não seguem o padrão m01–m08 de propósito, para testar a CLI do jeito que a professora vai
usar: com um arquivo que o código nunca viu.

## Gabarito (gerado por `executar_parte1` em 19/11)

| Mapa | O que exercita | Estados | Arcos | Armadilhas | Becos | BFS (passos) | Dijkstra | Bellman-Ford |
|---|---|---|---|---|---|---|---|---|
| `t01_duas_portas` | duas portas, cada chave abre um caminho | 151 | 316 | 0 | 0 | 20 | custo 24 | custo 24 |
| `t02_esteiras_fonte` | esteira de mão única, beco, fonte `*` | 29 | 55 | 1 | 1 | 13 | RECUSA | CICLO_NEGATIVO |
| `t03_bonus_esteiras` | chaves, bônus `+` e esteiras | 302 | 577 | 0 | 0 | 16 | RECUSA | custo 11 |
| `t04_chave_trancada` | chave atrás da própria porta | 10 | 20 | 10 (todos) | 0 | SEM_SOLUCAO | SEM_SOLUCAO | SEM_SOLUCAO |
| `t05_invalido` | dois `S` | erro do `io.py`: "A grade deve conter exatamente um 'S'" | | | | | | |

## O que o teste da CLI mostrou (19/11)

Rodando `python -m src.cli --mapa data/mapas_treino/<mapa>.txt --out <pasta>`:

- só sai `percurso_<mapa>.png` e uma linha de status. Nenhum dos CSV/JSON obrigatórios é gerado, porque a CLI não chama
  `executar_parte1` (R1);
- `--armadilhas` falha com "exige --arquivo-armadilhas", então não dá para mostrar as armadilhas de um mapa novo;
- mesmo pelo `executar_parte1`, `armadilhas_<mapa>.csv` só é gerado quando o mapa se chama m04 ou m07. O mapa surpresa
  não teria armadilhas exportadas;
- no terminal do Windows os acentos saem quebrados ("Sa�da n�o alcan��vel"). Vale forçar UTF-8 na saída da CLI
  (`sys.stdout.reconfigure(encoding="utf-8")`) ou rodar com `PYTHONIOENCODING=utf-8`;
- o mapa inválido gera erro claro, como o enunciado pede.
