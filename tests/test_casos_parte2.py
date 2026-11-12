"""Exportação dos casos da Parte 2 (P4a): conteúdo do JSON e chamada pela CLI."""
# [IA] Claude Code – testes da exportação de BFS/DFS

import json

import pytest

from src.casos_parte2 import executar_bellman_ford, executar_busca, executar_dijkstra
from src.cli import main


@pytest.fixture
def pasta(tmp_path):
    """Recorte mínimo: ciclo A→B→C→A, folha D e E, que A não alcança."""
    dados = tmp_path / "dados"
    dados.mkdir()
    (dados / "arestas.csv").write_text(
        "origem,destino,peso\nA,B,1\nA,D,1\nB,C,1\nC,A,-2\nE,A,1\n",
        encoding="utf-8",
    )
    return dados


def ler(caminho):
    def recusar(valor):
        raise AssertionError(f"valor fora do padrão JSON: {valor}")

    return json.loads(caminho.read_text(encoding="utf-8"), parse_constant=recusar)


def test_bfs_exporta_camadas_e_omite_nao_alcancados(pasta, tmp_path):
    r = ler(executar_busca("BFS", pasta, "A", tmp_path / "saida"))

    assert r["ordem"] == ["A", "B", "D", "C"]
    assert r["camadas"] == [["A"], ["B", "D"], ["C"]]
    assert r["distancia"] == {"A": 0, "B": 1, "D": 1, "C": 2}
    assert r["pai"] == {"A": None, "B": "A", "D": "A", "C": "B"}
    assert (r["total_nos"], r["alcancados"]) == (5, 4)


def test_dfs_exporta_ciclo_a_partir_da_origem(pasta, tmp_path):
    r = ler(executar_busca("DFS", pasta, "A", tmp_path / "saida"))

    assert r["tem_ciclo"] is True
    assert r["escopo_ciclo"] == "alcancaveis_da_origem"
    assert r["arcos"]["retorno"] == [["C", "A"]]
    assert r["contagem_arcos"]["arvore"] == 3
    assert "E" not in r["pai"]


def test_dfs_sem_ciclo_alcancavel(pasta, tmp_path):
    r = ler(executar_busca("DFS", pasta, "D", tmp_path / "saida"))

    assert r["tem_ciclo"] is False
    assert r["ordem"] == ["D"]


@pytest.mark.parametrize("alg", ["BFS", "DFS"])
def test_cli_grava_um_arquivo_por_fonte(pasta, tmp_path, alg):
    saida = tmp_path / "saida"

    assert main(["--dataset", str(pasta), "--alg", alg, "--source", "A", "--out", str(saida)]) == 0
    assert ler(saida / f"{alg.lower()}_A.json")["origem"] == "A"


def test_cli_exige_source(pasta, tmp_path):
    with pytest.raises(SystemExit):
        main(["--dataset", str(pasta), "--alg", "BFS", "--out", str(tmp_path)])


def test_cli_recusa_fonte_inexistente(pasta, tmp_path, capsys):
    with pytest.raises(SystemExit):
        main(["--dataset", str(pasta), "--alg", "BFS", "--source", "Z", "--out", str(tmp_path)])

    assert "não existe" in capsys.readouterr().err


# [IA] Claude Code – testes da exportação de Dijkstra/Bellman-Ford
@pytest.fixture
def pasta_pesos(tmp_path):
    """A→B→C com atalho A→C caro em valor_btc; saldo negativo em C; ciclo X→Y→X negativo."""
    dados = tmp_path / "pesos"
    dados.mkdir()
    (dados / "arestas.csv").write_text(
        "origem,destino,peso,valor_btc\n"
        "A,B,2,1\nB,C,-3,1\nA,C,-3,5\nC,D,1,1\n"
        "X,Y,-2,1\nY,X,1,1\n",
        encoding="utf-8",
    )
    return dados


def test_dijkstra_usa_valor_btc_e_reconstroi_caminho(pasta_pesos, tmp_path):
    r = ler(executar_dijkstra(pasta_pesos, "A", "D", tmp_path / "saida"))

    assert r["peso"] == "valor_btc"
    assert r["caminho"] == ["A", "B", "C", "D"]
    assert r["custo"] == 3
    assert r["passos"] == 3
    assert r["arcos"] == [["A", "B", 1.0], ["B", "C", 1.0], ["C", "D", 1.0]]


def test_dijkstra_recusa_destino_inalcancavel(pasta_pesos, tmp_path):
    with pytest.raises(ValueError, match="não é alcançável"):
        executar_dijkstra(pasta_pesos, "A", "X", tmp_path / "saida")


def test_bellman_ford_sem_ciclo_exporta_distancias(pasta_pesos, tmp_path):
    r = ler(executar_bellman_ford(pasta_pesos, "A", tmp_path / "saida"))

    assert r["status"] == "OK"
    assert r["tem_ciclo_negativo"] is False
    assert r["distancia"] == {"A": 0, "B": 2, "C": -3, "D": -2}
    assert r["arcos_negativos_alcancaveis"] == 2
    assert (r["total_nos"], r["alcancados"]) == (6, 4)


def test_bellman_ford_com_ciclo_exporta_ciclo(pasta_pesos, tmp_path):
    r = ler(executar_bellman_ford(pasta_pesos, "X", tmp_path / "saida"))

    assert r["status"] == "CICLO_NEGATIVO"
    assert r["ciclo_negativo"][0] == r["ciclo_negativo"][-1]
    assert set(r["ciclo_negativo"]) == {"X", "Y"}
    assert r["custo_ciclo"] == -1
    assert "distancia" not in r


def test_cli_dijkstra_exige_target(pasta_pesos, tmp_path):
    with pytest.raises(SystemExit):
        main(["--dataset", str(pasta_pesos), "--alg", "DIJKSTRA", "--source", "A", "--out", str(tmp_path)])


def test_cli_grava_dijkstra_e_bellman_ford(pasta_pesos, tmp_path):
    saida = tmp_path / "saida"
    args = ["--dataset", str(pasta_pesos), "--out", str(saida), "--source", "A"]

    assert main(args + ["--alg", "DIJKSTRA", "--target", "D"]) == 0
    assert main(args + ["--alg", "BELLMAN_FORD"]) == 0
    assert ler(saida / "dijkstra_A_D.json")["custo"] == 3
    assert ler(saida / "bellman_ford_A.json")["status"] == "OK"
