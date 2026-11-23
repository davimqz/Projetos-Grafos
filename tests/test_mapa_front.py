"""Contratos do processamento de mapas enviados pelo front."""
# [IA] Codex – verificação dos resultados e mensagens do carregamento.
import json
import subprocess
import sys
from pathlib import Path


def executar(conteudo):
    return subprocess.run([sys.executable, '-X', 'utf8', '-m', 'scripts.mapa_front'],
                          input=conteudo.encode('utf-8'), capture_output=True)


def test_mapa_valido_retorna_os_quatro_resultados():
    texto = Path('data/mapas_treino/t01_duas_portas.txt').read_text(encoding='utf-8')
    resultado = executar(texto)
    assert resultado.returncode == 0, resultado.stderr.decode('utf-8')
    dados = json.loads(resultado.stdout)
    assert set(dados['percursos']) == {'BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD'}
    assert dados['percursos']['BFS']


def test_mapa_invalido_exibe_erro_da_validacao():
    resultado = executar('SSG')
    assert resultado.returncode == 2
    assert 'exatamente um' in resultado.stderr.decode('utf-8')
