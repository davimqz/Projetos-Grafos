# [IA] Claude Code – testes da exportação dos casos da Parte 2 para o front
import json

import pytest

import pandas as pd

from scripts.exportar_parte2_front import arcos_entre, caso_bellman_ford, caso_busca, montar, recorte_bfs, rede_bfs

BFS = {
    "algoritmo": "BFS", "origem": "a", "total_nos": 6, "alcancados": 5,
    "ordem": ["a", "b", "c", "d", "e"],
    "camadas": [["a"], ["b", "c"], ["d", "e"]],
    "distancia": {"a": 0, "b": 1, "c": 1, "d": 2, "e": 2},
    "pai": {"a": None, "b": "a", "c": "a", "d": "b", "e": "c"},
    "arvore": [["a", "b"], ["a", "c"], ["b", "d"], ["c", "e"]],
}
DFS = {
    "algoritmo": "DFS", "origem": "a", "total_nos": 6, "alcancados": 5,
    "ordem": ["a", "b", "d", "c", "e"], "pai": {},
    "contagem_arcos": {"arvore": 4, "retorno": 1, "avanco": 0, "cruzamento": 0},
    "arcos": {}, "tem_ciclo": True, "escopo_ciclo": "alcancaveis_da_origem",
}


def test_recorte_segue_as_camadas_e_corta_no_limite():
    recorte = recorte_bfs(BFS, limite=4)
    assert recorte["nos"] == ["a", "b", "c", "d"]
    assert recorte["arcos"] == [["a", "b"], ["a", "c"], ["b", "d"]]
    assert recorte["nivel"] == {"a": 0, "b": 1, "c": 1, "d": 2}
    assert recorte["completo"] is False


def test_recorte_completo_quando_cabe_tudo():
    assert recorte_bfs(BFS, limite=40)["completo"] is True


def test_caso_busca_junta_bfs_e_dfs():
    caso = caso_busca(BFS, DFS, limite=3)
    assert caso["tamanho_camadas"] == [1, 2, 2]
    assert caso["dfs"]["tem_ciclo"] is True
    assert caso["dfs"]["ordem_inicio"] == ["a", "b", "d"]


def test_caso_busca_recusa_origens_diferentes():
    with pytest.raises(ValueError, match="origens diferentes"):
        caso_busca(BFS, {**DFS, "origem": "z"})


def test_bellman_ford_com_ciclo_traz_so_o_ciclo():
    resultado = {
        "origem": "a", "total_nos": 3, "alcancados": 3, "status": "CICLO_NEGATIVO", "tem_ciclo_negativo": True,
        "ciclo_negativo": ["b", "c", "b"], "arcos_ciclo": [["b", "c", -2.0], ["c", "b", 1.0]], "custo_ciclo": -1.0,
    }
    caso = caso_bellman_ford(resultado)
    assert caso["ciclo"] == ["b", "c", "b"] and caso["custo_ciclo"] == -1.0
    assert "distancia" not in caso


def test_bellman_ford_sem_ciclo_vira_arvore_de_pais():
    resultado = {
        "origem": "a", "total_nos": 3, "alcancados": 3, "status": "OK", "tem_ciclo_negativo": False,
        "arcos_negativos_alcancaveis": 1, "distancia": {"a": 0, "b": -1.0, "c": 2.0},
        "pai": {"a": None, "b": "a", "c": "b"},
    }
    assert caso_bellman_ford(resultado)["arcos"] == [["a", "b"], ["b", "c"]]


def test_montar_com_pasta_de_exemplo(tmp_path):
    (tmp_path / "bfs_a.json").write_text(json.dumps(BFS), encoding="utf-8")
    (tmp_path / "dfs_a.json").write_text(json.dumps(DFS), encoding="utf-8")
    (tmp_path / "dijkstra_a_e.json").write_text(json.dumps({
        "origem": "a", "destino": "e", "custo": 3.0, "passos": 2, "caminho": ["a", "c", "e"],
        "arcos": [["a", "c", 1.0], ["c", "e", 2.0]],
    }), encoding="utf-8")
    (tmp_path / "parte2_report.json").write_text(json.dumps([
        {"algoritmo": "BFS", "fracao": 0.5, "tempo_medio_ms": 1.0},
        {"algoritmo": "BFS", "fracao": 1.0, "tempo_medio_ms": 2.0, "memoria_pico_kb": 10.5},
    ]), encoding="utf-8")
    nos = tmp_path / "nos.csv"
    nos.write_text("endereco,classe\na,licito\nb,ilicito\nc,desconhecido\nd,licito\ne,licito\nf,licito\n",
                   encoding="utf-8")

    dados = montar(tmp_path, nos)
    assert [c["origem"] for c in dados["buscas"]] == ["a"]
    assert dados["dijkstra"][0]["custo"] == 3.0
    assert dados["bellman_ford"] == []
    assert [t["tempo_medio_ms"] for t in dados["tempos"]] == [2.0]
    assert dados["tempos"][0]["memoria_pico_kb"] == 10.5
    assert dados["classe"] == {"a": "licito", "b": "ilicito", "c": "desconhecido", "d": "licito", "e": "licito"}


def test_montar_sem_resultados_gera_erro_claro(tmp_path):
    with pytest.raises(FileNotFoundError, match="casos_parte2"):
        montar(tmp_path, tmp_path / "nos.csv")


# [IA] Claude Code – amostra em várias camadas e arcos extras para o grafo interativo
def test_rede_desce_camadas_com_poucos_filhos_por_carteira():
    rede = rede_bfs(BFS, limite=10, por_pai=(1,))
    assert rede["nos"] == ["a", "b", "d"]
    assert rede["arvore"] == [["a", "b"], ["b", "d"]]
    assert rede["nivel"] == {"a": 0, "b": 1, "d": 2}


def test_rede_respeita_o_limite():
    assert len(rede_bfs(BFS, limite=3, por_pai=(2,))["nos"]) == 3


def test_arcos_entre_ignora_arvore_lacos_e_repeticoes():
    arestas = pd.DataFrame({"origem": ["a", "b", "b", "b", "d", "x"], "destino": ["b", "c", "c", "b", "a", "a"]})
    assert arcos_entre(["a", "b", "c", "d"], arestas, [["a", "b"]]) == [["b", "c"], ["d", "a"]]
