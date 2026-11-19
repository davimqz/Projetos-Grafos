"""Testes de buscas da Parte 1 com mapas sintéticos."""

# [IA] Codex - testes existentes separados por responsabilidade.
import json
import os
import subprocess
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from src.parte1 import buscas


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
    resultado = buscas.resolver_mapa(dados, algoritmo)
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
        buscas.resolver_mapa(dados, algoritmo)


@pytest.mark.parametrize("grade, esperado", [
    (["SAG", "a##"], [(2, False), (None, False), (4, True)]),
    (["SaAG"], [(3, True), (None, False), (3, True)]),
    (["SG"], [(1, True)] * 3),
    (["S#G"], [(None, False)] * 3),
])
def test_comparar_modelagens_passos_e_validade(carregar, grade, esperado):
    resultado = buscas.comparar_modelagens(carregar(grade))
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
        [sys.executable, "-c", script, str(mapa)], cwd=Path(__file__).resolve().parents[2],
        env=ambiente, capture_output=True, text=True, check=True,
    )
    assert json.loads(processo.stdout) == [[2, True], [2, True], [2, True]]


@pytest.mark.parametrize("grade, custo", [(["S+G"], -3), (["S++G"], -7), (["G+S"], -3)])
def test_comparar_bonus_separa_modelagens_e_preserva_ciclo(carregar, grade, custo):
    dados = carregar(grade)
    resultado = buscas.comparar_bonus(dados)
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


# [IA] Codex - regressões do ciclo negativo que não afeta a saída, conforme PR #32.
@pytest.mark.parametrize("rota,status,passos,custo", [
    ("#S...G#", "OK", 4, 4),
    ("#S~..G#", "OK", 4, 8),
    ("#S+..G#", "OK", 4, -1),
    ("#S#..G#", "SEM_SOLUCAO", None, None),
    ("#S*..G#", "CICLO_NEGATIVO", None, None),
])
def test_bellman_ford_distingue_ciclo_em_armadilha_do_custo_ate_alvo(carregar, rota, status, passos, custo):
    dados = carregar(["#######", rota, "#v#####", "#.*####", "#######"])
    arcos = dados.grafo_estados.arestas()
    assert buscas.bellman_ford(dados.grafo_estados, dados.origem)["tem_ciclo_negativo"] is True

    resultado = buscas.resolver_mapa(dados, "BELLMAN_FORD")

    assert (resultado["status"], resultado["passos"], resultado["custo"]) == (status, passos, custo)
    if status == "OK":
        caminho = resultado["caminho"]
        assert caminho[0] == dados.origem and caminho[-1] == "ALVO"
        assert len(caminho) - 2 == passos
        assert sum(dict(dados.grafo_estados.vizinhos(u))[v] for u, v in zip(caminho, caminho[1:])) == custo
    else:
        assert resultado["caminho"] == []
    assert dados.grafo_estados.arestas() == arcos


def test_solucao_finita_preserva_resultado_global_em_cache(carregar):
    dados = carregar(["#######", "#S...G#", "#v#####", "#.*####", "#######"])
    resultados = {"BELLMAN_FORD": buscas.bellman_ford(dados.grafo_estados, dados.origem)}
    antes = deepcopy(resultados)

    solucao = buscas._resolver_mapa(dados, "BELLMAN_FORD", resultados)

    assert solucao["status"] == "OK" and solucao["custo"] == 4
    assert resultados == antes
    assert resultados["BELLMAN_FORD"]["tem_ciclo_negativo"] is True
