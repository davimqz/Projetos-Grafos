"""Testes das funções de apresentação do P5a, com dados artificiais.

# [IA] ChatGPT — geração de testes das visualizações sem algoritmos de modelagem.
"""
import pytest
from pathlib import Path
from src.viz import (ler_rotulo, reconstruir_percurso, desenhar_percurso,
                     desenhar_camadas, desenhar_arvore_bfs, desenhar_heatmap,
                     gerar_html_interativo)


class GrafoPequeno:
    def __init__(self):
        self.a = "(1,1)|-|{}"
        self.b = "(1,2)|-|{}"
        self.c = "(1,3)|a|{0}"
        self._nos = [self.a, self.b, self.c, "ALVO"]
    def nos(self):
        return self._nos.copy()
    def arestas(self):
        return [(self.a,self.b,1),(self.b,self.c,1),(self.c,"ALVO",0)]


def test_rotulo():
    assert ler_rotulo("(3,5)|ab|{0,2}") == (3,5,"ab",(0,2))
    assert ler_rotulo("(1,2)|-|{}") == (1,2,"",())
    assert ler_rotulo("ALVO") is None
    with pytest.raises(ValueError):
        ler_rotulo("estado-nao-padrao")


def test_reconstruir_percurso():
    r = {"pai": {"A":None,"B":"A","C":"B","D":None}}
    assert reconstruir_percurso(r,"A","C") == ["A","B","C"]
    with pytest.raises(ValueError):
        reconstruir_percurso(r,"A","D")


def test_percurso_png(tmp_path):
    g = GrafoPequeno()
    grade = ["######", "#S.aG#", "######"]
    saida = desenhar_percurso(grade, [g.a,g.b,g.c,"ALVO"], tmp_path/"percurso.png")
    assert saida.is_file() and saida.stat().st_size > 1000


def test_camadas_png(tmp_path):
    saida = desenhar_camadas(GrafoPequeno(),tmp_path/"camadas.png")
    assert saida.exists()


def test_arvore_png(tmp_path):
    g = GrafoPequeno()
    r = {"camadas": {0:[g.a],1:[g.b],2:[g.c]}, "arvore": [(g.a,g.b),(g.b,g.c)]}
    saida = desenhar_arvore_bfs(r,tmp_path/"arvore.png")
    assert saida.exists()


def test_heatmap_png(tmp_path):
    saida = desenhar_heatmap(["######", "#S.aG#", "######"],GrafoPequeno(),tmp_path/"heatmap.png")
    assert saida.exists()


def test_html_interativo(tmp_path):
    g = GrafoPequeno()
    dados = {"demo": {"grade":["######", "#S.aG#", "######"],
                      "algoritmos":{"BFS":[g.a,g.b,g.c]}, "armadilhas":[g.c]}}
    arquivo = gerar_html_interativo(dados,tmp_path/"demo.html")
    conteudo = arquivo.read_text(encoding="utf-8")
    assert "Labirinto interativo" in conteudo
    assert "<script>" in conteudo
    assert "(1,3)|a|{0}" in conteudo
    assert "anterior" in conteudo and "reproduzir" in conteudo


def test_grade_invalida(tmp_path):
    g = GrafoPequeno()
    with pytest.raises(ValueError):
        desenhar_percurso(["##", "###"], [g.a], tmp_path/"erro.png")


def test_limite_sem_amostragem(tmp_path):
    with pytest.raises(ValueError):
        desenhar_camadas(GrafoPequeno(), tmp_path/"nao.png",max_nos=1)


# [IA] Codex – regressão para entrada que quebrava o visualizador no navegador.
def test_html_rejeita_mapa_sem_algoritmos(tmp_path):
    with pytest.raises(ValueError, match="algoritmos"):
        gerar_html_interativo({"demo": {"grade": ["S.G"], "algoritmos": {}}}, tmp_path / "erro.html")


# [IA] Codex – verifica a distinção entre estados com bônus diferentes.
def test_camadas_identifica_bonus_no_rotulo(tmp_path, monkeypatch):
    from matplotlib.axes import Axes

    rotulos = []
    anotar = Axes.annotate

    def registrar(ax, texto, *args, **kwargs):
        rotulos.append(texto)
        return anotar(ax, texto, *args, **kwargs)

    monkeypatch.setattr(Axes, "annotate", registrar)
    grafo = GrafoPequeno()
    grafo._nos = ["(1,1)|a|{}", "(1,1)|a|{0}", "(1,1)|a|{0,2}"]
    desenhar_camadas(grafo, tmp_path / "bonus.png")
    assert rotulos == ["(1,1)|a", "(1,1)|a {0}", "(1,1)|a {0,2}"]
