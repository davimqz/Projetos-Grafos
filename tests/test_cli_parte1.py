"""Integração da CLI com mapas novos e falhas independentes nas exportações."""

# [IA] Codex - testes do fluxo completo, reutilização de buscas e resumo final.
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src import solve, visualizar_parte1
from src.cli import main
from src.parte1 import analises, buscas, interface_cli


def mapa_em(pasta, nome="surpresa", grade="S+G"):
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / f"{nome}.txt"
    arquivo.write_text(grade + "\n", encoding="utf-8")
    return arquivo


def linhas_csv(arquivo):
    with arquivo.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def dados_html(arquivo):
    html = arquivo.read_text(encoding="utf-8")
    return json.JSONDecoder().raw_decode(html.split("const MAPAS = ", 1)[1])[0]


def test_cli_compartilha_buscas_e_resume_depois_das_exportacoes(tmp_path, monkeypatch, capsys):
    mapa = mapa_em(tmp_path)
    saida = tmp_path / "out"
    chamadas = []

    def observar(modulo, nome):
        original = getattr(modulo, nome)

        def chamar(*args, **kwargs):
            chamadas.append((nome, args[0]))
            return original(*args, **kwargs)
        monkeypatch.setattr(modulo, nome, chamar)

    observar(solve, "carregar_mapa")
    for nome in ("bfs", "dijkstra", "bellman_ford"):
        observar(buscas, nome)
    observar(analises, "dfs")
    gerar_html = interface_cli.gerar_html_interativo

    def finalizar_html(*args):
        assert (saida / "solucoes.csv").is_file()
        assert (saida / "percurso_surpresa.png").is_file()
        assert "Resumo da execução" not in capsys.readouterr().out
        return gerar_html(*args)

    monkeypatch.setattr(interface_cli, "gerar_html_interativo", finalizar_html)
    assert main(["--mapa", str(mapa), "--out", str(saida), "--interactive"]) == 0
    assert all(sum(n == nome for n, _ in chamadas) == 1
               for nome in ("carregar_mapa", "bfs", "dijkstra", "bellman_ford", "dfs"))
    assert len({id(grafo) for nome, grafo in chamadas if nome != "carregar_mapa"}) == 1
    resultados = linhas_csv(saida / "solucoes.csv")
    assert [r["status"] for r in resultados] == ["OK", "RECUSA", "OK"]
    html = dados_html(saida / "labirinto_surpresa.html")["surpresa"]
    assert set(html["algoritmos"]) == set(interface_cli.ALGORITMOS)
    assert html["custos"]["BELLMAN_FORD"][-1] == -3
    assert html["armadilhas_estados"] == []
    assert "Resumo da execução" in capsys.readouterr().out


@pytest.mark.parametrize("grade,algoritmo,status,custo", [
    ("S#G", "BFS", "SEM_SOLUCAO", None),
    ("S+G", "DIJKSTRA", "RECUSA", None),
    ("S*G", "BELLMAN_FORD", "CICLO_NEGATIVO", None),
    ("S+G", "BELLMAN_FORD", "OK", -3),
    ("SG", "DFS", "OK", 1),
    ("#######\n#S...G#\n#v#####\n#.*####\n#######", "BELLMAN_FORD", "OK", 4),
])
def test_cli_status_e_html_para_mapa_sem_nome_especial(tmp_path, capsys, grade, algoritmo, status, custo):
    mapa = mapa_em(tmp_path, grade=grade)
    saida = tmp_path / "out"
    assert main(["--mapa", str(mapa), "--out", str(saida), "--alg", algoritmo, "--interactive", "--armadilhas"]) == 0
    texto = capsys.readouterr().out
    assert f"{algoritmo}: status={status}" in texto
    html = dados_html(saida / "labirinto_surpresa.html")["surpresa"]
    assert list(html["algoritmos"]) == [algoritmo]
    assert len(linhas_csv(saida / "solucoes.csv")) == 3
    assert json.loads((saida / "armadilhas_surpresa.json").read_text()) == html["armadilhas_estados"]
    if custo is not None:
        assert html["custos"][algoritmo][-1] == custo
    else:
        assert html["algoritmos"][algoritmo] == []


def test_cli_fonte_consumivel_preserva_exportacoes_padrao(tmp_path):
    mapa = mapa_em(tmp_path, grade="S*G")
    saida = tmp_path / "out"
    argumentos = ["--mapa", str(mapa), "--out", str(saida)]
    assert main(argumentos) == 0
    antes = {p.name: p.read_bytes() for p in saida.iterdir()}
    assert main(argumentos + ["--fonte-consumivel"]) == 0
    assert all((saida / nome).read_bytes() == conteudo for nome, conteudo in antes.items())
    resultados = linhas_csv(saida / "fonte_consumivel" / "solucoes.csv")
    bf = next(r for r in resultados if r["algoritmo"] == "BELLMAN_FORD")
    assert bf["status"] == "OK" and float(bf["custo"]) == -1


def test_cli_lote_inclui_grupo_e_ignora_pasta_de_solucoes(tmp_path, monkeypatch):
    mapa_em(tmp_path / "data" / "mapas", "m01_terreno", "SG")
    mapa_em(tmp_path / "data" / "mapas_grupo", "grupo", "S#G")
    mapa_em(tmp_path / "data" / "solucoes_mapas_grupo", "gabarito", "texto invalido")
    monkeypatch.chdir(tmp_path)
    assert main(["--todos-mapas", "--out", "out", "--interactive"]) == 0
    assert set(json.loads(Path("out/metricas_global.json").read_text())) == {"m01", "grupo"}
    assert len(linhas_csv(Path("out/solucoes.csv"))) == 6
    assert set(dados_html(Path("out/labirinto_interativo.html"))) == {"m01_terreno", "grupo"}


@pytest.mark.parametrize("tipo", ["csv", "png", "html"])
def test_cli_informa_falha_e_preserva_outros_arquivos(tmp_path, monkeypatch, capsys, tipo):
    mapa = mapa_em(tmp_path)
    saida = tmp_path / "out"
    modulo, nome, destino = {
        "csv": (solve, "exportar_csv", "solucoes.csv"),
        "png": (visualizar_parte1, "desenhar_percurso", "percurso_surpresa.png"),
        "html": (interface_cli, "gerar_html_interativo", "labirinto_surpresa.html"),
    }[tipo]
    original = getattr(modulo, nome)

    def falhar(*args, **kwargs):
        if Path(args[-1]).name == destino:
            raise PermissionError("falha simulada")
        return original(*args, **kwargs)

    monkeypatch.setattr(modulo, nome, falhar)
    assert main(["--mapa", str(mapa), "--out", str(saida), "--interactive"]) == 1
    capturado = capsys.readouterr()
    assert destino in capturado.err and "falha simulada" in capturado.err
    assert not (saida / destino).exists()
    assert (saida / "metricas_global.json").is_file()
    assert str(saida / destino) not in capturado.out


def test_cli_entrada_invalida_tem_mensagem_sem_traceback(tmp_path, capsys):
    mapa = mapa_em(tmp_path, grade="SSG")
    assert main(["--mapa", str(mapa), "--out", str(tmp_path / "out")]) == 2
    erro = capsys.readouterr().err
    assert "exatamente um 'S'" in erro and "Traceback" not in erro


@pytest.mark.parametrize("conteudo", ["{", "{}", "[1]"])
def test_cli_rejeita_json_de_armadilhas_invalido(tmp_path, capsys, conteudo):
    mapa = mapa_em(tmp_path)
    arquivo = tmp_path / "armadilhas.json"
    arquivo.write_text(conteudo, encoding="utf-8")
    assert main(["--mapa", str(mapa), "--out", str(tmp_path / "out"),
                 "--arquivo-armadilhas", str(arquivo)]) == 2
    assert "Traceback" not in capsys.readouterr().err
    assert not (tmp_path / "out" / "solucoes.csv").exists()


def test_cli_lote_rejeita_identificadores_repetidos(tmp_path, capsys):
    mapas = [mapa_em(tmp_path / pasta, nome) for pasta, nome in (("a", "m01"), ("b", "m01_terreno"))]
    assert main(["--mapas", *(str(m) for m in mapas), "--out", str(tmp_path / "out")]) == 2
    assert "identificadores distintos" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


def test_cli_subprocesso_imprime_utf8_mesmo_com_ambiente_ascii(tmp_path):
    mapa = mapa_em(tmp_path, grade="S#G")
    processo = subprocess.run(
        [sys.executable, "-m", "src.cli", "--mapa", str(mapa), "--out", str(tmp_path / "out")],
        cwd=Path(__file__).resolve().parents[1], capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "ascii"},
    )
    assert processo.returncode == 0, processo.stderr.decode("utf-8")
    assert "Saída não alcançável." in processo.stdout.decode("utf-8")
