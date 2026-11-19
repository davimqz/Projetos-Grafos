"""Testes de carga da Parte 1 com mapas sintéticos."""

# [IA] Codex - testes existentes separados por responsabilidade.
from pathlib import Path

import pytest

from src.graphs.estados import Estado
from src.parte1 import carga


@pytest.mark.parametrize("tipo_caminho", [str, Path])
@pytest.mark.parametrize("nome", [None, "personalizado", ""])
def test_carregar_mapa_prepara_componentes_e_nome(tmp_path, tipo_caminho, nome):
    caminho = tmp_path / "duas_saidas.txt"
    caminho.write_text("; comentário\nG.\n.S\n", encoding="utf-8")

    dados = carga.carregar_mapa(tipo_caminho(caminho), nome=nome)

    assert dados.nome == ("duas_saidas" if nome is None else nome)
    assert dados.grade == ["G.", ".S"]
    assert dados.origem == "(1,1)|-|{}"
    assert dados.estados[dados.origem] == Estado(1, 1, frozenset(), frozenset())
    assert dados.fonte_consumivel is False
    assert set(dados.grafo_posicoes.nos()) == {"(0,0)", "(0,1)", "(1,0)", "(1,1)"}
    assert set(dados.grafo_estados.nos()) == set(dados.estados) | {"ALVO"}
    assert dados.grafo_estados.vizinhos("(0,0)|-|{}") == [("ALVO", 0)]
    assert list(tmp_path.iterdir()) == [caminho]


@pytest.mark.parametrize("consumivel", [False, True])
def test_carregar_mapa_encaminha_variante_da_fonte(carregar, consumivel):
    dados = carregar(["S*G"], fonte_consumivel=consumivel)

    assert dados.fonte_consumivel is consumivel
    assert dados.estados[dados.origem].bonus == frozenset()
    assert dados.grafo_posicoes.vizinhos("(0,0)") == [("(0,1)", -2)]
    rotulo_fonte = "(0,1)|-|{0}" if consumivel else "(0,1)|-|{}"
    assert dados.grafo_estados.vizinhos(dados.origem) == [(rotulo_fonte, -2)]
    assert dados.estados[rotulo_fonte].bonus == (frozenset({0}) if consumivel else frozenset())


def test_carregar_mapa_propaga_arquivo_ausente(tmp_path):
    with pytest.raises(FileNotFoundError):
        carga.carregar_mapa(tmp_path / "ausente.txt")


def test_carregar_mapa_propaga_validacao(carregar):
    with pytest.raises(ValueError, match="Símbolo inválido"):
        carregar(["S?G"])


@pytest.mark.parametrize("construtor", ["construir_grafo_estados", "construir_grafo_posicoes"])
def test_carregar_mapa_propaga_erro_dos_construtores(carregar, monkeypatch, construtor):
    erro = RuntimeError("falha do construtor")

    def falhar(*args, **kwargs):
        raise erro

    monkeypatch.setattr(carga, construtor, falhar)
    with pytest.raises(RuntimeError) as capturado:
        carregar(["SG"])
    assert capturado.value is erro
