"""Casos de borda de mapas novos, para o ensaio do mapa surpresa.

Cada mapa é pequeno o bastante para conferir à mão: os números esperados foram contados pela regra do
enunciado (custo = casa de destino, ordem N, L, S, O, G sem saída) e não tirados da saída do código.
Os testes marcados com xfail descrevem formatos de arquivo que a leitura ainda recusa; quando o io.py
passar a aceitá-los, o pytest avisa com XPASS e a marcação pode ser removida.
"""

# [IA] Claude Code – casos de teste sugeridos para mapas novos (borda e formato); números conferidos à mão
import subprocess
import sys
from pathlib import Path

import pytest

from src.parte1.analises import encontrar_armadilhas
from src.parte1.buscas import resolver_mapa
from src.parte1.carga import carregar_mapa

RAIZ = Path(__file__).resolve().parents[1]
M02 = (RAIZ / "data" / "mapas" / "m02_uma_chave.txt").read_text(encoding="utf-8")


def preparar(tmp_path, conteudo, nome="surpresa"):
    arquivo = tmp_path / f"{nome}.txt"
    arquivo.write_bytes(conteudo if isinstance(conteudo, bytes) else conteudo.encode("utf-8"))
    return carregar_mapa(arquivo)


def n_estados(dados):
    return len(dados.estados)


# Casos de borda válidos -------------------------------------------------------------------------------

def test_chave_sem_porta_muda_de_camada_sem_bloquear(tmp_path):
    # S -> a (pega a) -> G; volta de a para S com a chave: 4 estados
    dados = preparar(tmp_path, "#####\n#SaG#\n#####\n")
    assert n_estados(dados) == 4
    bfs = resolver_mapa(dados, "BFS")
    assert (bfs["status"], bfs["passos"]) == ("OK", 2)


def test_porta_sem_chave_funciona_como_parede(tmp_path):
    dados = preparar(tmp_path, "#####\n#SAG#\n#####\n")
    assert n_estados(dados) == 1
    for alg in ("BFS", "DIJKSTRA", "BELLMAN_FORD"):
        assert resolver_mapa(dados, alg)["status"] == "SEM_SOLUCAO"
    assert len(encontrar_armadilhas(dados)) == 1


def test_mapa_sem_parede_na_borda_nao_sai_da_grade(tmp_path):
    # Sem moldura de '#': o movimento para fora da grade simplesmente não existe
    dados = preparar(tmp_path, "S.G\n...\n")
    bfs = resolver_mapa(dados, "BFS")
    assert (bfs["status"], bfs["passos"], bfs["custo"]) == ("OK", 2, 2)
    assert n_estados(dados) == 6


def test_esteira_para_fora_da_grade_e_esteira_de_volta(tmp_path):
    # '>' leva direto a G; '^' só volta para S. Estados: S, '>', G, '^'
    dados = preparar(tmp_path, "S>G\n^..\n")
    assert n_estados(dados) == 4
    assert resolver_mapa(dados, "BFS")["passos"] == 2


def test_s_vizinho_de_g(tmp_path):
    dados = preparar(tmp_path, "SG\n")
    assert n_estados(dados) == 2
    bfs = resolver_mapa(dados, "BFS")
    assert (bfs["passos"], bfs["custo"]) == (1, 1)


def test_varias_saidas_escolhe_a_mais_proxima(tmp_path):
    # G . S . G: as duas saídas a 2 passos; 5 estados (S, duas casas de chão, duas saídas)
    dados = preparar(tmp_path, "#######\n#G.S.G#\n#######\n")
    assert n_estados(dados) == 5
    assert resolver_mapa(dados, "DIJKSTRA")["custo"] == 2


def test_saida_isolada_todos_os_estados_sao_armadilha(tmp_path):
    dados = preparar(tmp_path, "#####\n#S.##\n###G#\n#####\n")
    assert n_estados(dados) == 2
    assert resolver_mapa(dados, "BFS")["status"] == "SEM_SOLUCAO"
    assert len(encontrar_armadilhas(dados)) == 2


def test_fonte_ao_lado_do_inicio_gera_ciclo_negativo_e_recusa(tmp_path):
    # S -> * custa -2 e * -> S custa 1: ciclo de custo -1
    dados = preparar(tmp_path, "#####\n#S*G#\n#####\n")
    assert resolver_mapa(dados, "DIJKSTRA")["status"] == "RECUSA"
    assert resolver_mapa(dados, "BELLMAN_FORD")["status"] == "CICLO_NEGATIVO"


def test_fonte_consumivel_tira_o_ciclo(tmp_path):
    arquivo = tmp_path / "fonte.txt"
    arquivo.write_text("#####\n#S*G#\n#####\n", encoding="utf-8")
    dados = carregar_mapa(arquivo, fonte_consumivel=True)
    bf = resolver_mapa(dados, "BELLMAN_FORD")
    assert (bf["status"], bf["custo"]) == ("OK", -1)


# Formatos de arquivo que a leitura já aceita ----------------------------------------------------------

@pytest.mark.parametrize("conteudo", [
    M02.replace("\n", "\r\n").encode(),
    M02.rstrip("\n").encode(),
    ("; mapa surpresa\n" + M02).encode(),
    (M02.split("\n", 2)[0] + "\n" + M02.split("\n", 2)[1] + "\n; comentário no meio\n" + M02.split("\n", 2)[2]).encode(),
], ids=["crlf", "sem_quebra_final", "comentario_topo", "comentario_meio"])
def test_formatos_aceitos_dao_o_mesmo_grafo_do_m02(tmp_path, conteudo):
    dados = preparar(tmp_path, conteudo)
    assert n_estados(dados) == n_estados(preparar(tmp_path, M02, "original"))


# Formatos que um editor comum pode produzir e que ainda são recusados ---------------------------------

@pytest.mark.xfail(reason="io.py abre com utf-8, não utf-8-sig: o BOM do Bloco de Notas vira símbolo inválido",
                   strict=False)
def test_arquivo_com_bom(tmp_path):
    assert n_estados(preparar(tmp_path, ("﻿" + M02).encode("utf-8"))) > 0


@pytest.mark.xfail(reason="linha em branco no fim do arquivo é tratada como linha vazia da grade", strict=False)
def test_linha_em_branco_no_fim(tmp_path):
    assert n_estados(preparar(tmp_path, M02 + "\n")) > 0


@pytest.mark.xfail(reason="espaço no fim da linha vira símbolo inválido", strict=False)
def test_espaco_no_fim_da_linha(tmp_path):
    assert n_estados(preparar(tmp_path, "\n".join(l + " " for l in M02.splitlines()) + "\n")) > 0


@pytest.mark.xfail(reason="comentário com espaço antes do ';' não é reconhecido", strict=False)
def test_comentario_com_espaco_antes(tmp_path):
    assert n_estados(preparar(tmp_path, "  ; comentário\n" + M02)) > 0


@pytest.mark.xfail(reason="arquivo em latin-1 dá erro de codec em inglês em vez de mensagem do projeto",
                   strict=False)
def test_arquivo_latin1_tem_mensagem_em_portugues(tmp_path):
    arquivo = tmp_path / "latin1.txt"
    arquivo.write_bytes(("; acentuação\n" + M02).encode("latin-1"))
    with pytest.raises(ValueError, match="UTF-8"):
        carregar_mapa(arquivo)


# CLI de ponta a ponta com nome de arquivo incomum ------------------------------------------------------

def test_cli_aceita_nome_com_espaco_e_acento(tmp_path):
    arquivo = tmp_path / "mapa da professora ç.txt"
    arquivo.write_text(M02, encoding="utf-8")
    saida = tmp_path / "out"
    proc = subprocess.run([sys.executable, "-m", "src.cli", "--mapa", str(arquivo), "--out", str(saida), "--armadilhas"],
                          cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Traceback" not in proc.stdout + proc.stderr
    assert (saida / "csv" / "arestas_mapa da professora ç.csv").exists()
