"""Integração da orquestração com mapas sintéticos, sem usar as entregas reais."""

# [IA] Codex - testes de integração das chamadas e dos arquivos exportados.
# [IA] Codex - verificação das exportações em subpastas por tipo de arquivo.
import csv
import json

import pytest

from src import solve
from src.parte1 import buscas
from src.solve import executar_parte1


def ler_csv(caminho):
    caminho = caminho.parent / "csv" / caminho.name
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        linhas = list(leitor)
        return leitor.fieldnames, linhas


def ler_json(caminho):
    caminho = caminho.parent / "json" / caminho.name
    return json.loads(caminho.read_text(encoding="utf-8"))


def criar_mapa(pasta, nome, conteudo):
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"{nome}.txt"
    caminho.write_text(conteudo + "\n", encoding="utf-8")
    return caminho


def test_executar_parte1_exporta_entregas_e_mapas_do_grupo(tmp_path):
    entradas = {
        "m01_terreno": "SG",
        "m02_uma_chave": "SAG\na##",
        "m03_tres_chaves": "S~G\n...",
        "m04_esteiras": "S.G\n.v#",
        "m05_bonus": "S+G",
        "m06_fonte": "S*G",
        "m07_impossivel": "S#G",
        "m08_grande": "SG",
        "m03_grupo": "SaG",
    }
    mapas = [criar_mapa(tmp_path / "entrada", nome, grade) for nome, grade in entradas.items()]
    originais = {mapa: mapa.read_bytes() for mapa in mapas}
    saida = tmp_path / "saida" / "parte1"

    assert executar_parte1((str(mapa) for mapa in mapas), str(saida)) is None
    assert {p.name for p in saida.iterdir()} == {"csv", "json"}

    nomes = {f"m{i:02}" for i in range(1, 9)} | {"m03_grupo"}
    metricas = ler_json(saida / "metricas_global.json")
    camadas = ler_json(saida / "camadas.json")
    assert set(metricas) == set(camadas) == nomes
    assert metricas["m01"]["ordem_est"] == 2
    assert metricas["m01"]["tamanho_est"] == 1
    assert metricas["m01"]["fonte_consumivel"] is False
    assert "maior_grau_saida" in metricas["m08"]
    assert "tem_ciclo_dfs" in metricas["m08"]
    assert camadas["m03_grupo"]["arcos_entre_camadas"] == 1
    for nome in nomes:
        cabecalho, arcos = ler_csv(saida / f"arestas_{nome}.csv")
        assert cabecalho == ["origem", "destino", "movimento", "casa_destino", "peso"]
        cabecalho, graus = ler_csv(saida / f"graus_{nome}.csv")
        assert cabecalho == ["estado", "grau_entrada", "grau_saida"]
        assert all(linha["estado"] != "ALVO" for linha in graus)
        if nome != "m07":
            assert any(arco["destino"] == "ALVO" for arco in arcos)

    cabecalho, solucoes = ler_csv(saida / "solucoes.csv")
    assert cabecalho == ["mapa", "algoritmo", "passos", "custo", "status", "caminho"]
    assert len(solucoes) == 3 * len(nomes)
    por_caso = {(linha["mapa"], linha["algoritmo"]): linha for linha in solucoes}
    assert por_caso["m03", "BFS"]["passos"] == "2"
    assert float(por_caso["m03", "BFS"]["custo"]) == 6
    assert por_caso["m03", "DIJKSTRA"]["passos"] == "4"
    assert por_caso["m05", "DIJKSTRA"]["status"] == "RECUSA"
    assert por_caso["m06", "BELLMAN_FORD"]["status"] == "CICLO_NEGATIVO"
    assert por_caso["m07", "BFS"]["status"] == "SEM_SOLUCAO"
    assert por_caso["m07", "BFS"]["passos"] == ""
    assert json.loads(por_caso["m07", "BFS"]["caminho"]) == []

    cabecalho, classificacoes = ler_csv(saida / "dfs_classificacao.csv")
    assert cabecalho == ["mapa", "arvore", "retorno", "avanco", "cruzamento"]
    assert len(classificacoes) == len(nomes)
    cabecalho, comparacoes = ler_csv(saida / "comparacao_modelagem.csv")
    assert cabecalho == ["mapa", "abordagem", "passos", "caminho_valido", "observacao"]
    assert len(comparacoes) == 9
    assert {linha["mapa"] for linha in comparacoes} == {"m02", "m03", "m04"}
    assert [linha["passos"] for linha in comparacoes if linha["mapa"] == "m02"] == ["2", "", "4"]

    percurso = ler_json(saida / "percurso_m03.json")
    assert percurso["algoritmo"] == "DIJKSTRA"
    assert percurso["status"] == "OK" and percurso["custo"] == 4
    assert percurso["caminho"][-1] == "ALVO"
    bonus = ler_json(saida / "comparacao_bonus_m05.json")
    assert bonus["grafo_posicoes"]["tem_ciclo_negativo"] is True
    assert bonus["grafo_estados"]["custo_ate_alvo"] == -3
    ciclo = ler_json(saida / "ciclo_negativo_m06.json")
    assert ciclo["status"] == "CICLO_NEGATIVO" and ciclo["custo_ciclo"] < 0
    assert ciclo["ciclo_negativo"][0] == ciclo["ciclo_negativo"][-1]
    for nome, esperado in [("m04", ["(1,1)|-|{}"]), ("m07", ["(0,0)|-|{}"])]:
        cabecalho, armadilhas = ler_csv(saida / f"armadilhas_{nome}.csv")
        assert cabecalho == ["estado"]
        assert [linha["estado"] for linha in armadilhas] == esperado
        assert ler_json(saida / f"armadilhas_{nome}.json") == esperado
    assert {mapa: mapa.read_bytes() for mapa in mapas} == originais


def test_executar_parte1_separa_fonte_consumivel_da_execucao_padrao(tmp_path):
    mapa = criar_mapa(tmp_path / "entrada", "m06_fonte", "S*G")
    padrao = tmp_path / "padrao"
    corrigido = tmp_path / "consumivel"
    executar_parte1([mapa], padrao)
    antes = {arquivo.relative_to(padrao): arquivo.read_bytes() for arquivo in padrao.rglob("*") if arquivo.is_file()}

    executar_parte1([mapa], corrigido, fonte_consumivel=True)

    assert {arquivo.relative_to(padrao): arquivo.read_bytes() for arquivo in padrao.rglob("*") if arquivo.is_file()} == antes
    assert ler_json(padrao / "ciclo_negativo_m06.json")["tem_ciclo_negativo"] is True
    ciclo = ler_json(corrigido / "ciclo_negativo_m06.json")
    assert ciclo["tem_ciclo_negativo"] is False and ciclo["ciclo_negativo"] == []
    assert ciclo["status"] == "OK" and ciclo["fonte_consumivel"] is True
    _, linhas = ler_csv(corrigido / "solucoes.csv")
    bf = next(linha for linha in linhas if linha["algoritmo"] == "BELLMAN_FORD")
    assert bf["status"] == "OK" and float(bf["custo"]) == -1
    assert ler_json(corrigido / "metricas_global.json")["m06"]["fonte_consumivel"] is True


def test_executar_parte1_percurso_m03_usa_bf_quando_dijkstra_recusa(tmp_path):
    mapa = criar_mapa(tmp_path / "entrada", "m03_tres_chaves", "S+G")
    saida = tmp_path / "saida"

    executar_parte1([mapa], saida)

    percurso = ler_json(saida / "percurso_m03.json")
    assert percurso["algoritmo"] == "BELLMAN_FORD"
    assert percurso["status"] == "OK" and percurso["custo"] == -3


@pytest.mark.parametrize("nomes", [("m03_tres_chaves", "m03"), ("grupo", "grupo")])
def test_executar_parte1_rejeita_identificadores_duplicados(tmp_path, nomes):
    mapas = [criar_mapa(tmp_path / str(i), nome, "SG") for i, nome in enumerate(nomes)]
    saida = tmp_path / "saida"

    with pytest.raises(ValueError, match="identificadores distintos"):
        executar_parte1(mapas, saida)
    assert not saida.exists()


def test_executar_parte1_entrada_vazia_exporta_agregados_vazios(tmp_path):
    saida = tmp_path / "saida"

    executar_parte1([], saida)

    assert ler_json(saida / "metricas_global.json") == {}
    assert ler_json(saida / "camadas.json") == {}
    for nome in ("solucoes", "dfs_classificacao", "comparacao_modelagem"):
        assert ler_csv(saida / f"{nome}.csv")[1] == []
    assert len([arquivo for arquivo in saida.rglob("*") if arquivo.is_file()]) == 5


def test_executar_parte1_propaga_erro_de_leitura(tmp_path):
    with pytest.raises(FileNotFoundError):
        executar_parte1([tmp_path / "ausente.txt"], tmp_path / "saida")


# [IA] Codex - regressão da reutilização de buscas e graus por mapa e execução.
@pytest.mark.parametrize("consumivel", [False, True])
def test_executar_parte1_nao_repete_buscas_nem_graus(tmp_path, monkeypatch, consumivel):
    mapas = [
        criar_mapa(tmp_path / "entrada", nome, grade)
        for nome, grade in [("m03_tres_chaves", "S~G\n..."), ("m05_bonus", "S+G"), ("m06_fonte", "S*G")]
    ]
    carregar = solve.carregar_mapa
    preparados = []
    chamadas = {nome: [] for nome in ("bfs", "bellman_ford", "calcular_graus")}

    def observar_carga(*args, **kwargs):
        dados = carregar(*args, **kwargs)
        preparados.append(dados)
        return dados

    def observar(nome, funcao):
        def chamar(primeiro, *args, **kwargs):
            chamadas[nome].append(primeiro)
            return funcao(primeiro, *args, **kwargs)
        return chamar

    monkeypatch.setattr(solve, "carregar_mapa", observar_carga)
    for nome in chamadas:
        modulo = solve if nome == "calcular_graus" else buscas
        monkeypatch.setattr(modulo, nome, observar(nome, getattr(modulo, nome)))
    for rodada in range(2):
        executar_parte1(mapas, tmp_path / f"saida{rodada}", fonte_consumivel=consumivel)

    assert len(preparados) == 6
    for dados in preparados:
        assert sum(item is dados for item in chamadas["calcular_graus"]) == 1
        for nome in ("bfs", "bellman_ford"):
            assert sum(item is dados.grafo_estados for item in chamadas[nome]) == 1
    for arquivo in (tmp_path / "saida0").rglob("*"):
        if arquivo.is_file():
            assert arquivo.read_bytes() == (tmp_path / "saida1" / arquivo.relative_to(tmp_path / "saida0")).read_bytes()


# [IA] Codex - regressão da solução finita e da evidência global de ciclo negativo.
@pytest.mark.parametrize("nome", ["m03_tres_chaves", "m06_fonte"])
def test_executar_parte1_exporta_solucao_finita_com_ciclo_em_armadilha(tmp_path, nome):
    mapa = criar_mapa(tmp_path / "entrada", nome, "#######\n#S...G#\n#v#####\n#.*####\n#######")
    saida = tmp_path / "saida"

    executar_parte1([mapa], saida)

    _, solucoes = ler_csv(saida / "solucoes.csv")
    bf = next(linha for linha in solucoes if linha["algoritmo"] == "BELLMAN_FORD")
    assert bf["status"] == "OK" and bf["passos"] == "4" and float(bf["custo"]) == 4
    assert json.loads(bf["caminho"])[-1] == "ALVO"
    if nome == "m03_tres_chaves":
        percurso = ler_json(saida / "percurso_m03.json")
        assert percurso["algoritmo"] == "BELLMAN_FORD" and percurso["status"] == "OK"
        assert percurso["custo"] == 4 and percurso["passos"] == 4
    else:
        ciclo = ler_json(saida / "ciclo_negativo_m06.json")
        assert ciclo["status"] == "OK" and ciclo["tem_ciclo_negativo"] is True
        assert ciclo["custo_ciclo"] < 0 and ciclo["ciclo_negativo"][0] == ciclo["ciclo_negativo"][-1]
