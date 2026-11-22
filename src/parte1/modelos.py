"""Tipos compartilhados pelas entregas da Parte 1."""

# [IA] Codex - contratos originais e separação por responsabilidade.
# [IA] Codex - resultado compartilhado entre exportações e apresentação da CLI.
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from src.graphs.estados import Estado
from src.graphs.graph import Grafo


AlgoritmoCaminho = Literal["BFS", "DIJKSTRA", "BELLMAN_FORD"]


StatusSolucao = Literal["OK", "RECUSA", "CICLO_NEGATIVO", "SEM_SOLUCAO"]


@dataclass(frozen=True)
class DadosMapa:
    """Componentes de um mapa preparados para as análises da Parte 1.

    nome identifica o mapa nas tabelas e nos arquivos. grade já está
    validada. grafo_posicoes usa portas como chão; grafo_estados inclui
    ALVO. estados associa somente os rótulos físicos aos seus Estados.
    origem é o rótulo do estado inicial em grafo_estados.

    fonte_consumivel registra a variante usada no grafo de estados;
    o grafo de posições mantém os custos fixos da modelagem ingênua.
    """

    nome: str
    grade: list[str]
    grafo_posicoes: Grafo
    grafo_estados: Grafo
    estados: dict[str, Estado]
    origem: str
    fonte_consumivel: bool = False


class GrauEstado(TypedDict):
    """Uma linha de graus_<mapa>.csv, sem o nó virtual."""

    estado: str
    grau_entrada: int
    grau_saida: int


class Solucao(TypedDict):
    """Resultado normalizado de uma execução para solucoes.csv.

    Sem solução finita, passos e custo são None e caminho é vazio.
    A representação desses valores no CSV pertence à exportação.
    """

    mapa: str
    algoritmo: AlgoritmoCaminho
    passos: int | None
    custo: float | None
    status: StatusSolucao
    caminho: list[str]


@dataclass
class ExecucaoMapa:
    """Resultados existentes de um mapa, sem refazer grafos ou buscas."""

    dados: DadosMapa
    solucoes: dict[str, Solucao]
    classificacao: dict
    buscas: dict[str, dict]
    armadilhas: list[str]
