"""Preparo dos mapas usando a leitura e a construção de grafos do grupo."""

# [IA] Codex - separação do código existente, preservando a lógica do integrante.
from __future__ import annotations

from pathlib import Path

from src.graphs.estados import Estado, construir_grafo_estados, construir_grafo_posicoes, rotular_estado
from src.graphs.io import encontrar_inicio, ler_mapa
from .modelos import DadosMapa


def carregar_mapa(
    caminho: str | Path,
    *,
    nome: str | None = None,
    fonte_consumivel: bool = False,
) -> DadosMapa:
    """Prepara os componentes usando as funções existentes de IO e estados.

    Sem nome explícito, usa o nome do arquivo sem extensão. Não implementa
    novamente a validação nem a construção dos grafos. A origem corresponde
    a S sem chaves ou bônus consumidos. Não grava saídas.
    Erros de leitura e validação são propagados ao chamador.
    """

    caminho = Path(caminho)

    grade = ler_mapa(caminho)
    grafo, estados = construir_grafo_estados(grade, fonte_consumivel=fonte_consumivel)

    linha, coluna = encontrar_inicio(grade)
    origem = rotular_estado(Estado(linha, coluna, frozenset(), frozenset()))

    return DadosMapa(
        nome=caminho.stem if nome is None else nome,
        grade=grade,
        grafo_posicoes=construir_grafo_posicoes(grade),
        grafo_estados=grafo,
        estados=estados,
        origem=origem,
        fonte_consumivel=fonte_consumivel
    )
