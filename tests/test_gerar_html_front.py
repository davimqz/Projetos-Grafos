"""Verifica a geração de HTML solicitada pelo front local."""
# [IA] Codex – testes de integração do gerador usado pelo front.
import json
import pytest

from scripts.gerar_html_front import ALGORITMOS, RAIZ, gerar_html, gerar_html_conjunto


def test_gera_html_com_resultado_do_mapa_selecionado(tmp_path):
    arquivo = gerar_html("m02_uma_chave", "BFS", tmp_path)
    html = arquivo.read_text(encoding="utf-8")
    assert arquivo.name == "labirinto_m02_uma_chave.html"
    assert '"m02_uma_chave"' in html
    assert '"BFS"' in html and '"custos"' in html
    assert "data:font/woff2;base64," in html and "SIL OPEN FONT LICENSE" in html
    assert "<title>Grafos · Teoria e visualização</title>" in html
    assert 'rel="icon" type="image/svg+xml" href="data:image/svg+xml,' in html


def test_gera_html_mesmo_quando_algoritmo_nao_se_aplica(tmp_path):
    html = gerar_html("m05_bonus", "DIJKSTRA", tmp_path).read_text(encoding="utf-8")
    assert '"DIJKSTRA": []' in html
    assert "peso negativo" in html


def test_conjunto_reune_todos_os_mapas_e_algoritmos(tmp_path):
    html = gerar_html_conjunto(tmp_path).read_text(encoding="utf-8")
    dados = json.loads(html.split("const MAPAS = ", 1)[1].split(";\n", 1)[0])
    esperados = {p.stem for pasta in ("mapas", "mapas_grupo")
                 for p in (RAIZ / "data" / pasta).glob("*.txt")}
    assert set(dados) == esperados
    assert all(set(mapa["algoritmos"]) == set(ALGORITMOS) for mapa in dados.values())


@pytest.mark.parametrize("mapa, algoritmo", [("../m02_uma_chave", "BFS"), ("inexistente", "BFS"), ("m02_uma_chave", "outro")])
def test_rejeita_entrada_invalida(mapa, algoritmo, tmp_path):
    with pytest.raises(ValueError):
        gerar_html(mapa, algoritmo, tmp_path)
    assert not list(tmp_path.iterdir())
