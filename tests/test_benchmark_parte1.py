"""Medições reais, isolamento das execuções e integração do benchmark da Parte 1."""

# [IA] Codex - testes de medição, status, exportação e seleção pela CLI.
import csv
import json
import tracemalloc

import pytest

from src.cli import main
from src.parte1 import benchmark


def criar_mapa(pasta, nome="mapa", grade="SG"):
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / f"{nome}.txt"
    arquivo.write_text(grade + "\n", encoding="utf-8")
    return arquivo


def ler_relatorio(saida):
    return json.loads((saida / "json" / "benchmark.json").read_text(encoding="utf-8"))


def test_mede_buscas_novas_no_mesmo_grafo_e_memoria_separada(tmp_path, monkeypatch):
    mapa = criar_mapa(tmp_path)
    chamadas, carregados = [], []
    carregar = benchmark.carregar_mapa

    def preparar(*args, **kwargs):
        dados = carregar(*args, **kwargs)
        carregados.append(dados)
        return dados

    monkeypatch.setattr(benchmark, "carregar_mapa", preparar)
    for nome, funcao in list(benchmark.ALGORITMOS.items()):
        def observar(grafo, origem, nome=nome, funcao=funcao):
            chamadas.append((nome, grafo, origem, tracemalloc.is_tracing()))
            return funcao(grafo, origem)
        monkeypatch.setitem(benchmark.ALGORITMOS, nome, observar)
    relatorio, registro = benchmark.executar_benchmark([mapa], tmp_path / "out")
    assert not registro.erros and len(carregados) == 1
    assert len(chamadas) == 4 * 7  # aquecimento + cinco tempos + uma memória
    for nome in benchmark.ALGORITMOS:
        assert [c[3] for c in chamadas if c[0] == nome] == [False] * 6 + [True]
    assert all(c[1] is carregados[0].grafo_estados and c[2] == carregados[0].origem for c in chamadas)
    assert not tracemalloc.is_tracing()
    for linha in relatorio["resultados"]:
        assert len(linha["tempos_ms"]) == 5 and linha["memoria_pico_bytes"] > 0
        assert linha["tempo_medio_ms"] == pytest.approx(sum(linha["tempos_ms"]) / 5)
        assert linha["latencia_min_ms"] == min(linha["tempos_ms"])
        assert linha["latencia_max_ms"] == max(linha["tempos_ms"])


def test_lote_registra_recusa_ciclo_e_alvo_sem_alterar_outras_saidas(tmp_path):
    mapas = [criar_mapa(tmp_path, nome, grade) for nome, grade in
             (("positivo", "SG"), ("bonus", "S+G"), ("fonte", "S*G"), ("isolado", "S#G"),
              ("ciclo_preso", "#######\n#S...G#\n#v#####\n#.*####\n#######"))]
    saida = tmp_path / "out"
    (saida / "csv").mkdir(parents=True)
    anterior = saida / "csv" / "solucoes.csv"
    anterior.write_bytes(b"preservado")
    assert main(["--mapas", *map(str, mapas), "--benchmark", "--out", str(saida)]) == 0
    relatorio = ler_relatorio(saida)
    linhas = relatorio["resultados"]
    assert len(linhas) == 20 and anterior.read_bytes() == b"preservado"
    por_caso = {(r["mapa"], r["algoritmo"]): r for r in linhas}
    assert por_caso["bonus", "DIJKSTRA"]["status"] == "RECUSA"
    assert por_caso["bonus", "DIJKSTRA"]["alvo_alcancavel"] is None
    assert por_caso["fonte", "BELLMAN_FORD"]["status"] == "CICLO_NEGATIVO"
    assert por_caso["ciclo_preso", "BELLMAN_FORD"]["status"] == "CICLO_NEGATIVO"
    assert por_caso["ciclo_preso", "BELLMAN_FORD"]["alvo_alcancavel"] is True
    assert all(not por_caso["isolado", alg]["alvo_alcancavel"] for alg in benchmark.ALGORITMOS)
    assert relatorio["ambiente"]["python"] and relatorio["metodo"]["aquecimentos"] == 1
    with (saida / "csv" / "benchmark.csv").open(encoding="utf-8", newline="") as stream:
        csv_linhas = list(csv.DictReader(stream))
    assert len(csv_linhas) == 20 and "tempos_ms" not in csv_linhas[0]
    assert float(csv_linhas[0]["tempo_medio_ms"]) == linhas[0]["tempo_medio_ms"]
    assert len(linhas[0]["sha256"]) == 64 and linhas[0]["nos"] == 3  # S, G e ALVO
    assert {p.name for p in saida.iterdir()} == {"csv", "json"}


def test_fonte_consumivel_separa_arquivos_e_preserva_execucao_padrao(tmp_path):
    mapa = criar_mapa(tmp_path, grade="S*G")
    saida = tmp_path / "out"
    argumentos = ["--mapa", str(mapa), "--benchmark", "--alg", "BELLMAN_FORD", "--out", str(saida)]
    assert main(argumentos) == 0
    padrao = (saida / "json" / "benchmark.json").read_bytes()
    assert main([*argumentos, "--fonte-consumivel", "--repeticoes", "2"]) == 0
    linha = ler_relatorio(saida / "fonte_consumivel")["resultados"][0]
    assert linha["fonte_consumivel"] and linha["status"] == "OK" and linha["repeticoes"] == 2
    assert (saida / "json" / "benchmark.json").read_bytes() == padrao
    assert (saida / "fonte_consumivel" / "csv" / "benchmark.csv").is_file()


def test_todos_mapas_seleciona_algoritmo_e_descobre_as_duas_pastas(tmp_path, monkeypatch):
    criar_mapa(tmp_path / "data" / "mapas", "fornecido")
    criar_mapa(tmp_path / "data" / "mapas_grupo", "grupo")
    monkeypatch.chdir(tmp_path)
    assert main(["--todos-mapas", "--benchmark", "--alg", "BFS", "--out", "out"]) == 0
    linhas = ler_relatorio(tmp_path / "out")["resultados"]
    assert [(r["mapa"], r["algoritmo"]) for r in linhas] == [("fornecido", "BFS"), ("grupo", "BFS")]


@pytest.mark.parametrize("tipo", ["csv", "json"])
def test_falha_de_exportacao_nao_impede_outro_formato(tmp_path, capsys, tipo):
    mapa = criar_mapa(tmp_path)
    saida = tmp_path / "out"
    bloqueado = saida / tipo / f"benchmark.{tipo}"
    bloqueado.mkdir(parents=True)
    assert main(["--mapa", str(mapa), "--benchmark", "--out", str(saida)]) == 1
    capturado = capsys.readouterr()
    assert str(bloqueado) in capturado.err and str(bloqueado) not in capturado.out
    outro = "json" if tipo == "csv" else "csv"
    assert (saida / outro / f"benchmark.{outro}").is_file()


@pytest.mark.parametrize("opcao", ["--interactive", "--armadilhas", "--repeticoes 0", "--repeticoes -2"])
def test_cli_rejeita_opcoes_invalidas_sem_traceback(tmp_path, capsys, opcao):
    mapa = criar_mapa(tmp_path)
    argumentos = ["--mapa", str(mapa), "--benchmark", "--out", str(tmp_path / "out"), *opcao.split()]
    if opcao.startswith("--repeticoes"):
        assert main(argumentos) == 2
    else:
        with pytest.raises(SystemExit) as erro:
            main(argumentos)
        assert erro.value.code == 2
    assert "Traceback" not in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


def test_entrada_invalida_e_lote_vazio_nao_gravam_resultados(tmp_path, monkeypatch):
    mapa = criar_mapa(tmp_path, grade="SSG")
    assert main(["--mapa", str(mapa), "--benchmark", "--out", str(tmp_path / "out")]) == 2
    monkeypatch.chdir(tmp_path)
    assert main(["--todos-mapas", "--benchmark", "--out", "out"]) == 2
    assert not (tmp_path / "out").exists()


def test_tracemalloc_e_encerrado_apos_erro_na_medicao_de_memoria(tmp_path, monkeypatch):
    dados = benchmark.carregar_mapa(criar_mapa(tmp_path))

    def falhar(grafo, origem):
        if tracemalloc.is_tracing():
            raise RuntimeError("falha na medição")
        return {"ordem": [origem, "ALVO"]}

    monkeypatch.setitem(benchmark.ALGORITMOS, "BFS", falhar)
    with pytest.raises(RuntimeError, match="falha na medição"):
        benchmark.medir_caso(dados, "BFS", 1)
    assert not tracemalloc.is_tracing()


def test_recusa_nao_oculta_outros_erros(tmp_path, monkeypatch):
    dados = benchmark.carregar_mapa(criar_mapa(tmp_path))

    def falhar(grafo, origem):
        raise ValueError("erro inesperado")

    monkeypatch.setitem(benchmark.ALGORITMOS, "DIJKSTRA", falhar)
    with pytest.raises(ValueError, match="erro inesperado"):
        benchmark.medir_caso(dados, "DIJKSTRA", 1)


def test_medicao_rejeita_rastreamento_externo_sem_desliga_lo(tmp_path):
    mapa = criar_mapa(tmp_path)
    tracemalloc.start()
    try:
        with pytest.raises(ValueError, match="tracemalloc externo"):
            benchmark.executar_benchmark([mapa], tmp_path / "out")
        assert tracemalloc.is_tracing()
    finally:
        tracemalloc.stop()


def test_lote_rejeita_nomes_duplicados_e_repeticoes_exigem_benchmark(tmp_path):
    mapas = [criar_mapa(tmp_path / pasta) for pasta in ("a", "b")]
    with pytest.raises(ValueError, match="identificadores distintos"):
        benchmark.executar_benchmark(mapas, tmp_path / "out")
    with pytest.raises(SystemExit) as erro:
        main(["--mapa", str(mapas[0]), "--out", str(tmp_path / "out"), "--repeticoes", "2"])
    assert erro.value.code == 2 and not (tmp_path / "out").exists()
