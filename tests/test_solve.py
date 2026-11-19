"""Compatibilidade dos imports públicos de src.solve após a separação."""

# [IA] Codex - regressões da interface pública preservada na reorganização.
from importlib import import_module

import pytest

from src import solve


PUBLICOS = {
    "modelos": ("AlgoritmoCaminho", "DadosMapa", "GrauEstado", "Solucao", "StatusSolucao"),
    "carga": ("carregar_mapa",),
    "analises": (
        "analisar_graus", "calcular_camadas", "calcular_graus",
        "calcular_metricas_globais", "classificar_arcos", "encontrar_armadilhas",
    ),
    "buscas": ("comparar_bonus", "comparar_modelagens", "resolver_mapa"),
    "exportacao": ("exportar_arestas", "exportar_csv", "exportar_json"),
}


@pytest.mark.parametrize("modulo,nome", [
    (modulo, nome) for modulo, nomes in PUBLICOS.items() for nome in nomes
])
def test_solve_preserva_imports_publicos(modulo, nome):
    assert getattr(solve, nome) is getattr(import_module(f"src.parte1.{modulo}"), nome)


def test_solve_declara_interface_publica_completa():
    esperados = {nome for nomes in PUBLICOS.values() for nome in nomes}
    assert set(solve.__all__) == esperados | {"executar_parte1"}
