# [IA] Claude Code – testes do script que leva o rótulo das transações para as arestas do recorte
import pandas as pd
import pytest

from scripts.rotular_transacoes import rotular


def _dados():
    # tx1: A -> B (ilícita); tx2: A -> B e A -> C (desconhecida, vira 2 arcos); tx3: B -> B (laço, ignorado)
    arestas = pd.DataFrame({"origem": ["A", "A"], "destino": ["B", "C"], "n_txs": [2, 1]})
    addr_tx = pd.DataFrame({"input_address": ["A", "A", "B"], "txId": [1, 2, 3]})
    tx_addr = pd.DataFrame({"txId": [1, 2, 2, 3], "output_address": ["B", "B", "C", "B"]})
    classes = pd.DataFrame({"txId": [1, 2, 3], "class": [1, 3, 2]})
    return arestas, addr_tx, tx_addr, classes


def test_conta_classes_por_aresta():
    arestas_tx, _ = rotular(*_dados())
    ab = arestas_tx.set_index(["origem", "destino"]).loc[("A", "B")]
    assert (ab["n_tx_ilicito"], ab["n_tx_licito"], ab["n_tx_desconhecido"]) == (1, 0, 1)
    ac = arestas_tx.set_index(["origem", "destino"]).loc[("A", "C")]
    assert ac["n_tx_desconhecido"] == 1


def test_transacao_em_varias_arestas():
    _, transacoes = rotular(*_dados())
    t = transacoes.set_index("txId")
    assert t.loc[2, "n_arestas"] == 2 and t.loc[2, "classe"] == "desconhecido"
    assert 3 not in t.index


def test_falha_se_contagem_nao_bate_com_n_txs():
    arestas, addr_tx, tx_addr, classes = _dados()
    arestas.loc[0, "n_txs"] = 5
    with pytest.raises(ValueError):
        rotular(arestas, addr_tx, tx_addr, classes)
