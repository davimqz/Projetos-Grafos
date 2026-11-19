"""Contratos das funções da Parte 1; integração em test_executar_parte1.py."""

# [IA] Codex - testes de carga, CSV e análises, sem implementar algoritmos.
import csv
import json
import os
import subprocess
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from src import solve
from src.graphs.estados import Estado
from src.graphs.graph import Grafo


@pytest.fixture
def carregar(tmp_path):
    def preparar(grade, **opcoes):
        caminho = tmp_path / "mapa.txt"
        caminho.write_text("\n".join(grade) + "\n", encoding="utf-8")
        return solve.carregar_mapa(caminho, **opcoes)

    return preparar


@pytest.fixture
def vazio():
    return solve.DadosMapa("vazio", [], Grafo(), Grafo(), {}, "")


def test_calcular_graus_dirigidos_sem_arco_virtual_na_ordem_dos_estados(carregar):
    dados = carregar(["S.G"])
    dados = replace(dados, estados=dict(reversed(list(dados.estados.items()))))
    assert solve.calcular_graus(dados) == [
        {"estado": "(0,2)|-|{}", "grau_entrada": 1, "grau_saida": 0},
        {"estado": "(0,1)|-|{}", "grau_entrada": 1, "grau_saida": 2},
        {"estado": "(0,0)|-|{}", "grau_entrada": 1, "grau_saida": 1},
    ]


def test_calcular_graus_sem_saida_alcancavel(carregar):
    assert solve.calcular_graus(carregar(["S#G"])) == [
        {"estado": "(0,0)|-|{}", "grau_entrada": 0, "grau_saida": 0},
    ]


def test_calcular_graus_vazios(vazio):
    assert solve.calcular_graus(vazio) == []


def test_analisar_graus_rankings_e_exclusao_da_saida_dos_becos(carregar):
    assert solve.analisar_graus(carregar(["S.G"])) == {
        "estado_maior_grau_entrada": "(0,0)|-|{}", "maior_grau_entrada": 1,
        "estado_maior_grau_saida": "(0,1)|-|{}", "maior_grau_saida": 2,
        "multiplicidade_maxima": 1,
        "casas_multiplicidade_maxima": [
            {"linha": 0, "coluna": 0, "simbolo": "S"},
            {"linha": 0, "coluna": 1, "simbolo": "."},
            {"linha": 0, "coluna": 2, "simbolo": "G"},
        ],
        "quantidade_casas_multiplicidade_maxima": 3,
        "becos": [], "quantidade_becos": 0,
    }


@pytest.mark.parametrize("sentido, grade, rotulo, grau", [
    ("entrada", ["S.G"], "(0,0)|-|{}", 1),
    ("saida", ["S..G"], "(0,1)|-|{}", 2),
])
def test_analisar_graus_desempata_por_rotulo_independente_da_insercao(carregar, sentido, grade, rotulo, grau):
    dados = carregar(grade)
    dados = replace(dados, estados=dict(reversed(list(dados.estados.items()))))
    resultado = solve.analisar_graus(dados)
    assert resultado[f"estado_maior_grau_{sentido}"] == rotulo
    assert resultado[f"maior_grau_{sentido}"] == grau


def test_analisar_graus_multiplicidade_por_posicao_ignora_chaves_e_bonus(carregar):
    resultado = solve.analisar_graus(carregar(["Sa+G"]))
    assert resultado["multiplicidade_maxima"] == 3
    assert resultado["casas_multiplicidade_maxima"] == [
        {"linha": 0, "coluna": 0, "simbolo": "S"},
    ]
    assert resultado["quantidade_casas_multiplicidade_maxima"] == 1


def test_analisar_graus_identifica_beco_em_esteira(carregar):
    resultado = solve.analisar_graus(carregar(["S>#G"]))
    assert resultado["becos"] == ["(0,1)|-|{}"]
    assert resultado["quantidade_becos"] == 1


def test_analisar_graus_vazios(vazio):
    assert solve.analisar_graus(vazio) == {
        "estado_maior_grau_entrada": None, "maior_grau_entrada": 0,
        "estado_maior_grau_saida": None, "maior_grau_saida": 0,
        "multiplicidade_maxima": 0, "casas_multiplicidade_maxima": [],
        "quantidade_casas_multiplicidade_maxima": 0,
        "becos": [], "quantidade_becos": 0,
    }


@pytest.mark.parametrize("funcao", [
    solve.calcular_metricas_globais, solve.calcular_camadas,
    solve.calcular_graus, solve.analisar_graus, solve.exportar_arestas,
    lambda dados: solve.resolver_mapa(dados, "BFS"),
    solve.classificar_arcos, solve.encontrar_armadilhas,
    solve.comparar_modelagens, solve.comparar_bonus,
])
def test_funcoes_preservam_dados_e_calculos_nao_gravam_arquivos(carregar, tmp_path, funcao):
    dados = carregar(["Sa+G"])
    # Inclui os dicionários internos dos grafos para detectar mutações.
    antes = deepcopy(vars(dados))
    arquivos = set(tmp_path.iterdir())
    if funcao is solve.exportar_arestas:
        funcao(dados, tmp_path / "arestas.csv")
    else:
        funcao(dados)
        assert set(tmp_path.iterdir()) == arquivos

    for campo in ("grafo_posicoes", "grafo_estados"):
        assert vars(getattr(dados, campo)) == vars(antes.pop(campo))
    assert {chave: valor for chave, valor in vars(dados).items() if chave in antes} == antes


# [IA] Codex - cobertura dos contratos restantes, com mapas sintéticos e IO temporário.
@pytest.mark.parametrize("grade, algoritmo, consumivel, esperado", [
    (["SG"], "BFS", False, ("OK", 1, 1)),
    (["SG"], "DIJKSTRA", False, ("OK", 1, 1)),
    (["SG"], "BELLMAN_FORD", False, ("OK", 1, 1)),
    (["S~G", "..."], "BFS", False, ("OK", 2, 6)),
    (["S~G", "..."], "DIJKSTRA", False, ("OK", 4, 4)),
    (["S~G", "..."], "BELLMAN_FORD", False, ("OK", 4, 4)),
    (["S+G"], "BFS", False, ("OK", 2, -3)),
    (["S+G"], "BELLMAN_FORD", False, ("OK", 2, -3)),
    (["S+G"], "DIJKSTRA", False, ("RECUSA", None, None)),
    (["S*G"], "BELLMAN_FORD", False, ("CICLO_NEGATIVO", None, None)),
    (["S*G"], "BELLMAN_FORD", True, ("OK", 2, -1)),
    (["S#G"], "BFS", False, ("SEM_SOLUCAO", None, None)),
    (["S#G"], "DIJKSTRA", False, ("SEM_SOLUCAO", None, None)),
    (["S#G"], "BELLMAN_FORD", False, ("SEM_SOLUCAO", None, None)),
])
def test_resolver_mapa_normaliza_status_passos_custo_e_caminho(carregar, grade, algoritmo, consumivel, esperado):
    dados = carregar(grade, fonte_consumivel=consumivel)
    resultado = solve.resolver_mapa(dados, algoritmo)
    assert set(resultado) == {"mapa", "algoritmo", "passos", "custo", "status", "caminho"}
    assert resultado["mapa"] == dados.nome and resultado["algoritmo"] == algoritmo
    assert (resultado["status"], resultado["passos"], resultado["custo"]) == esperado
    caminho = resultado["caminho"]
    if resultado["status"] == "OK":
        assert caminho[0] == dados.origem and caminho[-1] == "ALVO"
        assert len(caminho) - 2 == resultado["passos"]
        assert sum(dict(dados.grafo_estados.vizinhos(u))[v] for u, v in zip(caminho, caminho[1:])) == resultado["custo"]
    else:
        assert caminho == []


@pytest.mark.parametrize("algoritmo", ["BFS", "DIJKSTRA", "BELLMAN_FORD", "DESCONHECIDO"])
def test_resolver_mapa_rejeita_origem_ou_algoritmo_invalidos(carregar, algoritmo):
    dados = carregar(["SG"])
    if algoritmo != "DESCONHECIDO":
        dados = replace(dados, origem="origem_inexistente")
    with pytest.raises(ValueError, match="não existe|desconhecido"):
        solve.resolver_mapa(dados, algoritmo)


@pytest.mark.parametrize("grade, contagens, ciclo", [
    (["SG"], (2, 0, 0, 0), False),
    (["S.G"], (3, 1, 0, 0), True),
    (["S#G"], (0, 0, 0, 0), False),
])
def test_classificar_arcos_inclui_alvo_alcancavel_e_indica_ciclo(carregar, grade, contagens, ciclo):
    resultado = solve.classificar_arcos(carregar(grade))
    assert resultado == {
        "mapa": "mapa", **dict(zip(("arvore", "retorno", "avanco", "cruzamento"), contagens)),
        "tem_ciclo": ciclo,
    }


def test_classificar_arcos_mapeia_categorias_e_passa_origem(carregar, monkeypatch):
    dados = carregar(["SG"])
    contagens = {"arvore": 1, "retorno": 2, "avanco": 3, "cruzamento": 4}

    def dfs_simulada(grafo, origem):
        assert grafo is dados.grafo_estados and origem == dados.origem
        return {"contagem_arcos": contagens, "tem_ciclo": True}

    monkeypatch.setitem(solve.classificar_arcos.__globals__, "dfs", dfs_simulada)
    assert solve.classificar_arcos(dados) == {"mapa": "mapa", **contagens, "tem_ciclo": True}


@pytest.mark.parametrize("inverter", [False, True])
@pytest.mark.parametrize("grade, esperado", [
    (["SG"], []),
    (["S#G"], ["(0,0)|-|{}"]),
    (["S.G", ".v#"], ["(1,1)|-|{}"]),
    (["S.G", ".><"], ["(1,1)|-|{}", "(1,2)|-|{}"]),
    (["S>.AG", "a####"], ["(0,1)|-|{}", "(0,2)|-|{}"]),
    (["S*G"], []),
])
def test_encontrar_armadilhas_reachabilidade_por_estado_e_ordem(carregar, grade, esperado, inverter):
    dados = carregar(grade)
    if inverter:
        dados = replace(dados, estados=dict(reversed(list(dados.estados.items()))))
        esperado = list(reversed(esperado))
    assert solve.encontrar_armadilhas(dados) == esperado


@pytest.mark.parametrize("grade, esperado", [
    (["SAG", "a##"], [(2, False), (None, False), (4, True)]),
    (["SaAG"], [(3, True), (None, False), (3, True)]),
    (["SG"], [(1, True)] * 3),
    (["S#G"], [(None, False)] * 3),
])
def test_comparar_modelagens_passos_e_validade(carregar, grade, esperado):
    resultado = solve.comparar_modelagens(carregar(grade))
    assert [r["abordagem"] for r in resultado] == ["portas_como_chao", "portas_como_parede", "grafo_estados"]
    assert [(r["passos"], r["caminho_valido"]) for r in resultado] == esperado
    assert all(r["mapa"] == "mapa" and isinstance(r["observacao"], str) for r in resultado)


@pytest.mark.parametrize("hash_seed", ["0", "1"])
def test_comparar_modelagens_desempata_saidas_pela_bfs(tmp_path, hash_seed):
    mapa = tmp_path / "empate.txt"
    mapa.write_text("GAS.G\n", encoding="utf-8")
    script = (
        "import json,sys; from src.solve import carregar_mapa,comparar_modelagens; "
        "r=comparar_modelagens(carregar_mapa(sys.argv[1])); "
        "print(json.dumps([(x['passos'],x['caminho_valido']) for x in r]))"
    )
    ambiente = {**os.environ, "PYTHONHASHSEED": hash_seed}
    processo = subprocess.run(
        [sys.executable, "-c", script, str(mapa)], cwd=Path(__file__).resolve().parents[1],
        env=ambiente, capture_output=True, text=True, check=True,
    )
    assert json.loads(processo.stdout) == [[2, True], [2, True], [2, True]]


@pytest.mark.parametrize("grade, custo", [(["S+G"], -3), (["S++G"], -7), (["G+S"], -3)])
def test_comparar_bonus_separa_modelagens_e_preserva_ciclo(carregar, grade, custo):
    dados = carregar(grade)
    resultado = solve.comparar_bonus(dados)
    pos = resultado["grafo_posicoes"]
    assert resultado["mapa"] == dados.nome
    assert pos["status"] == "CICLO_NEGATIVO" and pos["tem_ciclo_negativo"] is True
    ciclo = pos["ciclo_negativo"]
    assert ciclo[0] == ciclo[-1]
    assert sum(dict(dados.grafo_posicoes.vizinhos(u))[v] for u, v in zip(ciclo, ciclo[1:])) == pos["custo_ciclo"] < 0
    assert resultado["grafo_estados"] == {
        "status": "OK", "tem_ciclo_negativo": False, "ciclo_negativo": [],
        "custo_ciclo": None, "custo_ate_alvo": custo,
    }


# [IA] Codex - regressões de desempenho das análises, sem limites de tempo frágeis.
@pytest.mark.parametrize("funcao", [solve.calcular_graus, solve.analisar_graus])
def test_graus_consultam_cada_lista_de_vizinhos_uma_vez(carregar, monkeypatch, funcao):
    dados = carregar(["S" + "." * 100 + "G"])
    vizinhos = dados.grafo_estados.vizinhos
    consultas = []

    def consultar(no):
        consultas.append(no)
        return vizinhos(no)

    def varredura_repetida(*args):
        pytest.fail("Calcular cada grau de entrada separadamente volta a custar O(VE).")

    monkeypatch.setattr(dados.grafo_estados, "vizinhos", consultar)
    monkeypatch.setattr(Grafo, "grau_entrada", varredura_repetida)
    funcao(dados)

    assert consultas == list(dados.estados)


@pytest.mark.parametrize("operacao", ["metricas", "camadas", "arestas"])
def test_contagens_e_exportacao_nao_copiam_grafos_ou_lista_de_arcos(carregar, tmp_path, monkeypatch, operacao):
    dados = carregar(["Sa+G"])

    def copiar(*args):
        pytest.fail("Esta operação deve consultar os arcos sem materializar cópias completas.")

    monkeypatch.setattr(Grafo, "subgrafo_induzido", copiar)
    monkeypatch.setattr(Grafo, "arestas", copiar)
    if operacao == "metricas":
        assert solve.calcular_metricas_globais(dados)["ordem_est"] == len(dados.estados)
    elif operacao == "camadas":
        assert sum(c["ordem"] for c in solve.calcular_camadas(dados)["camadas"]) == len(dados.estados)
    else:
        solve.exportar_arestas(dados, tmp_path / "arestas.csv")
        with (tmp_path / "arestas.csv").open(newline="", encoding="utf-8") as arquivo:
            assert len(list(csv.DictReader(arquivo))) == dados.grafo_estados.tamanho()
