"""Integração das visualizações com os mapas e algoritmos reais."""
# [IA] Codex – testes de integração da apresentação com dados do projeto.
from pathlib import Path
import json
import pytest

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
    assert set(dados["estados"]) == set(estados)
    custos = dados["custos"]["BFS"]
    assert custos[0] == 0 and len(custos) == len(percurso)
    for i, (u, v) in enumerate(zip(percurso, percurso[1:])):
        peso = next(peso for destino, peso in grafo.vizinhos(u) if destino == v)
        assert custos[i + 1] == custos[i] + peso


def test_mapa_sem_saida_gera_html_com_status(tmp_path):
    status = gerar_mapa(MAPAS / "m07_impossivel.txt", tmp_path, interactive=True)
    assert "não alcançável" in status
    html = (tmp_path / "labirinto_m07_impossivel.html").read_text(encoding="utf-8")
    assert status in html and '"BFS": []' in html
    assert not list(tmp_path.glob("*.png"))


def test_dijkstra_com_peso_negativo_tem_status():
    dados, _, _, _ = preparar_mapa(MAPAS / "m05_bonus.txt", ("DIJKSTRA",))
    assert not dados["algoritmos"]["DIJKSTRA"]
    assert "peso negativo" in dados["status"]["DIJKSTRA"]


# [IA] Codex – verifica a passagem dos estados fornecidos ao HTML pela CLI.
def test_cli_recebe_estados_armadilha(tmp_path, capsys):
    from src.cli import main
    arquivo = tmp_path / "armadilhas.json"
    estado = "(1,1)|-|{}"
    arquivo.write_text(json.dumps([estado]), encoding="utf-8")
    assert main(["--mapa", str(MAPAS / "m02_uma_chave.txt"), "--out", str(tmp_path),
                 "--interactive", "--armadilhas", "--arquivo-armadilhas", str(arquivo)]) == 0
    assert estado in capsys.readouterr().out
    assert '"armadilhas_estados": ["(1,1)|-|{}"]' in (tmp_path / "labirinto_m02_uma_chave.html").read_text(encoding="utf-8")


def test_rejeita_armadilha_ausente_do_grafo(tmp_path):
    with pytest.raises(ValueError, match="estados existentes"):
        gerar_mapa(MAPAS / "m02_uma_chave.txt", tmp_path, armadilhas_estados=["(99,99)|-|{}"])


def test_cli_interativo_preserva_html_conjunto_e_outros_mapas(tmp_path):
    from src.cli import main
    conjunto = tmp_path / "labirinto_interativo.html"
    conjunto.write_text("conteúdo existente", encoding="utf-8")
    for nome in ("m02_uma_chave", "m07_impossivel"):
        assert main(["--mapa", str(MAPAS / f"{nome}.txt"), "--out", str(tmp_path),
                     "--interactive"]) == 0
    assert conjunto.read_text(encoding="utf-8") == "conteúdo existente"
    assert (tmp_path / "labirinto_m02_uma_chave.html").is_file()
    assert (tmp_path / "labirinto_m07_impossivel.html").is_file()
