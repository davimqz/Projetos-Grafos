"""Integração das visualizações com os mapas e algoritmos reais."""
# [IA] Codex – testes de integração da apresentação com dados do projeto.
from pathlib import Path

from src.visualizar_parte1 import preparar_mapa, gerar_mapa

MAPAS = Path(__file__).resolve().parents[1] / "data" / "mapas"


def test_percurso_real_usa_arestas_do_grafo():
    dados, grafo, estados, resultados = preparar_mapa(MAPAS / "m03_tres_chaves.txt")
    percurso = dados["algoritmos"]["BFS"]
    assert percurso and all(no in estados for no in percurso)
    assert all(any(v == destino for v, _ in grafo.vizinhos(origem))
               for origem, destino in zip(percurso, percurso[1:]))
    assert dados["grade"][estados[percurso[-1]].linha][estados[percurso[-1]].coluna] == "G"
    assert resultados["BFS"]["pai"]["ALVO"] == percurso[-1]


def test_mapa_sem_saida_gera_html_com_status(tmp_path):
    status = gerar_mapa(MAPAS / "m07_impossivel.txt", tmp_path, interactive=True)
    assert "não alcançável" in status
    html = (tmp_path / "labirinto_interativo.html").read_text(encoding="utf-8")
    assert status in html and '"BFS": []' in html
    assert not list(tmp_path.glob("*.png"))


def test_dijkstra_com_peso_negativo_tem_status():
    dados, _, _, _ = preparar_mapa(MAPAS / "m05_bonus.txt", ("DIJKSTRA",))
    assert not dados["algoritmos"]["DIJKSTRA"]
    assert "peso negativo" in dados["status"]["DIJKSTRA"]
