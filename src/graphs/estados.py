"""Grafo de posições (G_pos) e grafo de estados (G_est).

Pacote P1 — Modelagem e grafo de estados.

A implementar pelo grupo:
- G_pos: nó = casa livre (linha, coluna); arcos pela geometria (paredes e esteiras)
- G_est: nó = (linha, coluna, chaves, bônus), construído por exploração a partir de S
- rótulo obrigatório "(3,5)|ab|{0,2}" ("-" sem chaves, "{}" sem bônus)
- nó virtual ALVO com arco de custo 0 a partir de todo estado em G
- variantes: portas como chão / portas como parede, '+' fixo em -4, --fonte-consumivel
"""
