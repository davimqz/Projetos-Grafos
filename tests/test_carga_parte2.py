"""Carga do recorte da Parte 2 (P4a)."""
# [IA] Claude Code – testes da leitura dos CSVs (IO)
import pytest

from src.carga_parte2 import carregar_grafo, ler_arestas, ler_nos


class GrafoFalso:
    """Substitui o graph.py enquanto ele não existe: só guarda os arcos recebidos."""

    def __init__(self):
        self.arcos = []

    def adicionar_arco(self, u, v, peso):
        self.arcos.append((u, v, peso))


def _escrever(pasta, nome, texto):
    (pasta / nome).write_text(texto, encoding="utf-8")


def test_le_arestas_na_ordem_do_arquivo(tmp_path):
    _escrever(tmp_path, "arestas.csv", "origem,destino,peso,n_txs\nB,A,-1.5,1\nA,C,2,3\n")
    assert ler_arestas(tmp_path) == [("B", "A", -1.5), ("A", "C", 2.0)]


def test_carregar_grafo_insere_todos_os_arcos(tmp_path):
    _escrever(tmp_path, "arestas.csv", "origem,destino,peso\nA,B,1\nB,C,0\n")
    g = carregar_grafo(GrafoFalso(), tmp_path)
    assert g.arcos == [("A", "B", 1.0), ("B", "C", 0.0)]


def test_endereco_numerico_continua_string(tmp_path):
    _escrever(tmp_path, "arestas.csv", "origem,destino,peso\n0123,456,1\n")
    assert ler_arestas(tmp_path) == [("0123", "456", 1.0)]


def test_erro_coluna_faltando(tmp_path):
    _escrever(tmp_path, "arestas.csv", "origem,destino\nA,B\n")
    with pytest.raises(ValueError, match="peso"):
        ler_arestas(tmp_path)


def test_erro_valor_vazio(tmp_path):
    _escrever(tmp_path, "arestas.csv", "origem,destino,peso\nA,B,1\nA,,2\n")
    with pytest.raises(ValueError, match="linha 3"):
        ler_arestas(tmp_path)


def test_erro_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        ler_arestas(tmp_path)


def test_le_nos_com_atributos(tmp_path):
    _escrever(tmp_path, "nos.csv", "endereco,saldo_btc,classe\nA,1.5,licito\nB,0,ilicito\n")
    nos = ler_nos(tmp_path)
    assert nos["A"] == {"saldo_btc": 1.5, "classe": "licito"}
    assert nos["B"]["classe"] == "ilicito"


def test_recorte_real():
    arestas = ler_arestas()
    nos = ler_nos()
    assert len(arestas) == 25111
    assert {u for u, _, _ in arestas} | {v for _, v, _ in arestas} <= set(nos)
