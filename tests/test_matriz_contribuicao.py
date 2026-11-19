# [IA] Claude Code – testes da contagem de commits por pacote
import pytest

from scripts.matriz_contribuicao import contar, pacote_do_arquivo, tabela_markdown


@pytest.mark.parametrize("arquivo, pacote", [
    ("src/graphs/estados.py", "P1"),
    ("tests/test_io.py", "P1"),
    ("src/graphs/algorithms.py", "P2"),
    ("src/parte1/analises.py", "P3"),
    ("data/mapas_grupo/g1.txt", "P3"),
    ("out/parte1/solucoes.csv", "P3"),
    ("out/parte1/percurso_m03.png", "P5a"),
    ("out/parte2/parte2_report.json", "P4b"),
    ("out/parte2/benchmark_escalabilidade.png", "P4b"),
    ("out/parte2/avd/exploratoria_1.png", "P5b"),
    ("out/parte2/bfs_abc.json", "P4a"),
    ("front-react/src/App.jsx", "P5a"),
    ("docs/relatorio/RELATORIO.md", "P5c"),
    ("docs/relatorio/parte2.md", "P4a"),
    ("src/cli.py", None),
    ("data/mapas/m01_terreno.txt", None),
])
def test_pacote_do_arquivo(arquivo, pacote):
    assert pacote_do_arquivo(arquivo) == pacote


def test_commit_conta_uma_vez_por_pacote():
    commits = [
        ("Davi Marques Oliveira", ["src/casos_parte2.py", "tests/test_casos_parte2.py", "README.md"]),
        ("Davi Marques Oliveira", ["src/cli.py"]),
        ("Thomazrlima", ["src/viz.py"]),
    ]
    matriz, totais = contar(commits)
    assert matriz["Davi"] == {"P4a": 1, "P5c": 1}
    assert matriz["Thomaz"] == {"P5a": 1}
    assert totais == {"Davi": 2, "Thomaz": 1}


def test_autor_desconhecido_gera_erro():
    with pytest.raises(ValueError, match="Autor desconhecido"):
        contar([("Fulano", ["README.md"])])


def test_tabela_markdown_tem_todos_os_integrantes():
    matriz, totais = contar([("Vagner Montenegro de Melo", ["src/benchmark.py", "notebooks/avd/a.ipynb"])])
    tabela = tabela_markdown(matriz, totais).splitlines()
    assert tabela[0].startswith("| Integrante | P1 |")
    assert [linha.split("|")[1].strip() for linha in tabela[2:]] == ["Matheus", "Thomaz", "Davi", "Vagner"]
    assert tabela[-1] == "| Vagner |  |  |  |  | 1 |  | 1 |  | 2 | 1 |"
