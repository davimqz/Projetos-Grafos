"""Ensaios reproduzíveis de mapas surpresa, comparados com oráculos independentes."""

# [IA] Codex – geração de casos sintéticos e comparação com NetworkX nos testes.
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import networkx as nx
import pytest

from src.parte1.carga import carregar_mapa
from src.parte1.buscas import resolver_mapa

RAIZ = Path(__file__).resolve().parents[1]


def mapa_aleatorio(semente, mecanicas):
    rng = random.Random(semente)
    simbolos = '.....###,,~~' + ('aAbB><^v+*' if mecanicas else '')
    grade = [[rng.choice(simbolos) for _ in range(8)] for _ in range(6)]
    grade[0][0], grade[-1][-1] = 'S', 'G'
    return [''.join(linha) for linha in grade]


def para_networkx(grafo):
    g = nx.DiGraph()
    g.add_nodes_from(grafo.nos())
    g.add_weighted_edges_from(grafo.arestas())
    return g


def conferir_caminho(g, origem, solucao):
    if solucao['status'] != 'OK':
        assert not solucao['caminho']
        return
    caminho = solucao['caminho']
    assert caminho[0] == origem and caminho[-1] == 'ALVO'
    assert all(g.has_edge(a, b) for a, b in zip(caminho, caminho[1:]))
    assert sum(g[a][b]['weight'] for a, b in zip(caminho, caminho[1:])) == solucao['custo']
    assert solucao['passos'] == len(caminho) - 2


@pytest.mark.parametrize('semente', range(100), ids=lambda n: f'mapa-{n:03}')
def test_mapas_gerados_contra_oraculos(tmp_path, semente):
    grade = mapa_aleatorio(semente, mecanicas=semente >= 50)
    arquivo = tmp_path / 'mapa surpresa.txt'
    arquivo.write_text('\n'.join(grade) + '\n', encoding='utf-8')
    dados = carregar_mapa(arquivo)
    g = para_networkx(dados.grafo_estados)
    origem = dados.origem
    tem_saida = nx.has_path(g, origem, 'ALVO')
    bfs = resolver_mapa(dados, 'BFS')
    assert bfs['status'] == ('OK' if tem_saida else 'SEM_SOLUCAO')
    if tem_saida:
        assert bfs['passos'] == nx.shortest_path_length(g, origem, 'ALVO') - 1
    conferir_caminho(g, origem, bfs)

    negativo = any(peso < 0 for _, _, peso in dados.grafo_estados.arestas())
    dj = resolver_mapa(dados, 'DIJKSTRA')
    if negativo:
        assert dj['status'] == 'RECUSA'
    elif tem_saida:
        assert dj['status'] == 'OK'
        assert dj['custo'] == nx.shortest_path_length(g, origem, 'ALVO', weight='weight')
    else:
        assert dj['status'] == 'SEM_SOLUCAO'
    conferir_caminho(g, origem, dj)

    bf = resolver_mapa(dados, 'BELLMAN_FORD')
    if not tem_saida:
        assert bf['status'] == 'SEM_SOLUCAO'
    else:
        relevantes = nx.ancestors(g, 'ALVO') | {'ALVO'}
        subgrafo = g.subgraph(relevantes).copy()
        if nx.negative_edge_cycle(subgrafo, weight='weight'):
            assert bf['status'] == 'CICLO_NEGATIVO'
        else:
            assert bf['status'] == 'OK'
            assert bf['custo'] == nx.bellman_ford_path_length(subgrafo, origem, 'ALVO', weight='weight')
    conferir_caminho(g, origem, bf)

@pytest.mark.parametrize('caso', range(40), ids=lambda n: f'invalido-{n:02}')
def test_entrada_invalida_tem_erro_claro(tmp_path, caso):
    variantes = ['', '...', 'S..', 'G..', 'SSG', 'SG!', 'S.G\n..', 'S\n\nG', 'SG\nS.', 'SG\n.G\n@.']
    conteudo = variantes[caso % len(variantes)]
    if caso // len(variantes) == 1:
        conteudo = '; comentario\n' + conteudo
    elif caso // len(variantes) == 2:
        conteudo = conteudo.replace('\n', '\r\n')
    elif caso // len(variantes) == 3:
        conteudo = '\ufeff' + conteudo
    arquivo = tmp_path / 'invalido.txt'
    arquivo.write_bytes(conteudo.encode('utf-8'))
    with pytest.raises(ValueError, match='.'):
        carregar_mapa(arquivo)


@pytest.mark.parametrize('semente', range(10), ids=lambda n: f'cli-{n:02}')
def test_cli_mapa_novo_com_html_e_saidas(tmp_path, semente):
    grade = mapa_aleatorio(semente + 100, mecanicas=semente % 2 == 1)
    arquivo = tmp_path / f'mapa surpresa {semente}.txt'
    arquivo.write_text('\n'.join(grade) + '\n', encoding='utf-8')
    saida = tmp_path / 'saida'
    processo = subprocess.run(
        [sys.executable, '-m', 'src.cli', '--mapa', str(arquivo), '--out', str(saida), '--interactive'],
        cwd=RAIZ, capture_output=True, text=True, encoding='utf-8', errors='replace',
        timeout=60, env={**os.environ, 'MPLBACKEND': 'Agg', 'PYTHONIOENCODING': 'utf-8'},
    )
    assert processo.returncode == 0, processo.stdout + processo.stderr
    assert 'Traceback' not in processo.stdout + processo.stderr
    html = (saida / 'html' / f'labirinto_{arquivo.stem}.html').read_text(encoding='utf-8')
    mapas = json.loads(html.split('const MAPAS = ', 1)[1].split(';\n', 1)[0])
    apresentado = mapas[arquivo.stem]
    assert apresentado['grade'] == grade
    assert set(apresentado['algoritmos']) == {'BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD'}
    dados = carregar_mapa(arquivo)
    for algoritmo in ('BFS', 'DIJKSTRA', 'BELLMAN_FORD'):
        solucao = resolver_mapa(dados, algoritmo)
        assert apresentado['algoritmos'][algoritmo] == solucao['caminho'][:-1]
    assert 'armadilhas_estados' in apresentado
    assert list((saida / 'csv').glob('arestas_*.csv'))
