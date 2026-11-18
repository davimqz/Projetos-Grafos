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


def test_faixas_log_cobrem_o_grau_maximo():
    from scripts.graus_parte2 import faixas_log

    assert faixas_log(1) == [1, 2]
    assert faixas_log(5) == [1, 2, 4, 8]
    assert faixas_log(2719)[-1] > 2719


def test_tabela_grau_zero_por_classe():
    from scripts.graus_parte2 import tabela_grau_zero

    zeros = tabela_grau_zero(calcular_graus(ARESTAS, NOS)).set_index("classe")
    assert zeros.loc["Desconhecida", "zero_entrada"] == 1 and zeros.loc["Desconhecida", "prop_zero_saida"] == 1.0
    assert zeros.loc["Lícita", "zero_entrada"] == 0 and zeros.loc["Lícita", "carteiras"] == 2


def test_ccdf_proporcao_com_grau_maior_ou_igual():
    from scripts.graus_parte2 import ccdf

    x, y = ccdf(pd.Series([0, 1, 1, 3]))
    assert x == [1, 3]
    assert y == [0.75, 0.25]


def test_figuras_sao_geradas(tmp_path):
    from scripts.graus_parte2 import figura_ccdf, figura_histograma

    graus = calcular_graus(ARESTAS, NOS)
    figura_histograma(graus, tmp_path / "h.png")
    figura_ccdf(graus, tmp_path / "c.png")
    assert (tmp_path / "h.png").stat().st_size > 0 and (tmp_path / "c.png").stat().st_size > 0
