"""Testes de exportacao da Parte 1 com mapas sintéticos."""

# [IA] Codex - testes existentes separados por responsabilidade.
import csv
import json
from copy import deepcopy
from pathlib import Path

import pytest

from src.parte1 import exportacao


@pytest.mark.parametrize("usar_string", [False, True])
def test_exportar_arestas_preserva_ordem_movimentos_simbolos_e_pesos(carregar, tmp_path, usar_string):
    dados = carregar(["#,#", ".SG", "#~#"])
    caminho = tmp_path / "arestas.csv"

    exportacao.exportar_arestas(dados, str(caminho) if usar_string else caminho)

    with caminho.open(newline="", encoding="utf-8") as arquivo:
        linhas = list(csv.reader(arquivo))
    assert linhas == [
        ["origem", "destino", "movimento", "casa_destino", "peso"],
        ["(1,1)|-|{}", "(0,1)|-|{}", "N", ",", "3"],
        ["(1,1)|-|{}", "(1,2)|-|{}", "L", "G", "1"],
        ["(1,1)|-|{}", "(2,1)|-|{}", "S", "~", "5"],
        ["(1,1)|-|{}", "(1,0)|-|{}", "O", ".", "1"],
        ["(0,1)|-|{}", "(1,1)|-|{}", "S", "S", "1"],
        ["(1,2)|-|{}", "ALVO", "", "", "0"],
        ["(2,1)|-|{}", "(1,1)|-|{}", "N", "S", "1"],
        ["(1,0)|-|{}", "(1,1)|-|{}", "L", "S", "1"],
    ]


def test_exportar_arestas_preserva_rotulos_com_bonus_e_pesos_negativos(carregar, tmp_path):
    dados = carregar(["S++G"])
    caminho = tmp_path / "arestas.csv"
    exportacao.exportar_arestas(dados, caminho)

    with caminho.open(newline="", encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    assert len(linhas) == dados.grafo_estados.tamanho()
    assert {
        "origem": "(0,1)|-|{0}", "destino": "(0,2)|-|{0,1}",
        "movimento": "L", "casa_destino": "+", "peso": "-4",
    } in linhas
    assert {
        "origem": "(0,2)|-|{0,1}", "destino": "(0,1)|-|{0,1}",
        "movimento": "O", "casa_destino": "+", "peso": "1",
    } in linhas


def test_exportar_arestas_vazias_escreve_cabecalho(vazio, tmp_path):
    caminho = tmp_path / "arestas.csv"
    exportacao.exportar_arestas(vazio, caminho)
    assert caminho.read_text(encoding="utf-8") == "origem,destino,movimento,casa_destino,peso\n"


def test_exportar_arestas_propaga_erro_de_escrita(vazio, tmp_path):
    # [IA] Codex - o exportador cria pastas, mas propaga conflitos com arquivos.
    bloqueado = tmp_path / "bloqueado"
    bloqueado.write_text("arquivo no lugar da pasta", encoding="utf-8")
    with pytest.raises(FileExistsError):
        exportacao.exportar_arestas(vazio, bloqueado / "arestas.csv")


@pytest.mark.parametrize("tipo_caminho", [str, Path])
def test_exportar_csv_utf8_escape_campos_json_e_preservacao(tmp_path, tipo_caminho):
    registros = [{"nome": 'João, "teste"\nlinha 2', "valor": None, "caminho": ["a,b", "fim"], "dados": {"ativo": True}}]
    antes = deepcopy(registros)
    destino = tmp_path / "nova" / "dados.csv"
    colunas = ["nome", "caminho", "valor", "dados", "ausente"]
    assert exportacao.exportar_csv((r for r in registros), colunas, tipo_caminho(destino)) is None
    with destino.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        linhas = list(leitor)
        assert leitor.fieldnames == colunas
    assert len(linhas) == 1 and linhas[0]["nome"] == registros[0]["nome"]
    assert linhas[0]["valor"] == linhas[0]["ausente"] == ""
    assert json.loads(linhas[0]["caminho"]) == registros[0]["caminho"]
    assert json.loads(linhas[0]["dados"]) == registros[0]["dados"]
    assert registros == antes


def test_exportar_csv_sem_registros_grava_cabecalho(tmp_path):
    destino = tmp_path / "vazio.csv"
    exportacao.exportar_csv([], ["estado", "grau"], destino)
    with destino.open(encoding="utf-8", newline="") as arquivo:
        assert list(csv.reader(arquivo)) == [["estado", "grau"]]


@pytest.mark.parametrize("tipo_caminho", [str, Path])
def test_exportar_json_roundtrip_utf8_formatacao_e_preservacao(tmp_path, tipo_caminho):
    dados = {"ação": [1, None, {"ativo": True}]}
    antes = deepcopy(dados)
    destino = tmp_path / "nova" / "dados.json"
    assert exportacao.exportar_json(dados, tipo_caminho(destino)) is None
    texto = destino.read_text(encoding="utf-8")
    assert json.loads(texto) == dados == antes
    assert '"ação"' in texto and "\n  " in texto


@pytest.mark.parametrize("dados, erro", [(float("nan"), ValueError), (float("inf"), ValueError), ({1, 2}, TypeError)])
def test_exportar_json_rejeita_dados_fora_do_contrato(tmp_path, dados, erro):
    with pytest.raises(erro):
        exportacao.exportar_json(dados, tmp_path / "invalido.json")


@pytest.mark.parametrize("formato", ["csv", "json"])
def test_exportacoes_propagam_erro_de_escrita(tmp_path, formato):
    with pytest.raises(OSError):
        if formato == "csv":
            exportacao.exportar_csv([], ["estado"], tmp_path)
        else:
            exportacao.exportar_json({}, tmp_path)
