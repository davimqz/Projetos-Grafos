"""Exportação dos casos da Parte 2 (P4a): conteúdo do JSON e chamada pela CLI."""
# [IA] Claude Code – testes da exportação de BFS/DFS

import json

import pytest

from src.casos_parte2 import executar_busca
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
