# [IA] Claude Code – testes da contagem de graus da Parte 2

import pandas as pd

from scripts.graus_parte2 import calcular_graus, frequencia, resumo

ARESTAS = pd.DataFrame({"origem": ["a", "a", "b", "c"], "destino": ["b", "c", "c", "a"]})
NOS = pd.DataFrame({"endereco": ["a", "b", "c", "d"], "classe": ["ilicito", "licito", "licito", "desconhecido"]})


def test_graus_contados_por_carteira():
    graus = calcular_graus(ARESTAS, NOS).set_index("endereco")
    assert graus.loc["a", "grau_saida"] == 2 and graus.loc["a", "grau_entrada"] == 1
    assert graus.loc["c", "grau_entrada"] == 2 and graus.loc["c", "grau_saida"] == 1


def test_carteira_sem_arestas_tem_grau_zero():
    graus = calcular_graus(ARESTAS, NOS).set_index("endereco")
    assert graus.loc["d", "grau_entrada"] == 0 and graus.loc["d", "grau_saida"] == 0


def test_soma_dos_graus_igual_ao_numero_de_arestas():
    graus = calcular_graus(ARESTAS, NOS)
    assert graus["grau_entrada"].sum() == graus["grau_saida"].sum() == len(ARESTAS)


def test_frequencia_soma_o_numero_de_carteiras():
    freq = frequencia(calcular_graus(ARESTAS, NOS))
    for direcao in ("entrada", "saida"):
        assert freq[freq["direcao"] == direcao]["carteiras"].sum() == len(NOS)


def test_resumo_maior_grau_de_saida_e_por_classe():
    r = resumo(calcular_graus(ARESTAS, NOS), len(ARESTAS))
    assert r["saida"]["maiores"][0] == {"endereco": "a", "classe": "ilicito", "grau": 2}
    assert r["entrada"]["total"]["com_grau_zero"] == 1
    assert r["saida"]["por_classe"]["licito"]["carteiras"] == 2
