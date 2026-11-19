"""Testes de contratos da Parte 1 com mapas sintéticos."""

# [IA] Codex - testes existentes separados por responsabilidade.
from copy import deepcopy

import pytest

from src.parte1 import analises, buscas, exportacao


@pytest.mark.parametrize("funcao", [
    analises.calcular_metricas_globais, analises.calcular_camadas,
    analises.calcular_graus, analises.analisar_graus, exportacao.exportar_arestas,
    lambda dados: buscas.resolver_mapa(dados, "BFS"),
    analises.classificar_arcos, analises.encontrar_armadilhas,
    buscas.comparar_modelagens, buscas.comparar_bonus,
])
def test_funcoes_preservam_dados_e_calculos_nao_gravam_arquivos(carregar, tmp_path, funcao):
    dados = carregar(["Sa+G"])
    # Inclui os dicionários internos dos grafos para detectar mutações.
    antes = deepcopy(vars(dados))
    arquivos = set(tmp_path.iterdir())
    if funcao is exportacao.exportar_arestas:
        funcao(dados, tmp_path / "arestas.csv")
    else:
        funcao(dados)
        assert set(tmp_path.iterdir()) == arquivos

    for campo in ("grafo_posicoes", "grafo_estados"):
        assert vars(getattr(dados, campo)) == vars(antes.pop(campo))
    assert {chave: valor for chave, valor in vars(dados).items() if chave in antes} == antes
