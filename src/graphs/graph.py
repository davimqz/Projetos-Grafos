"""Grafo dirigido e ponderado para os labirintos da Parte 1.

Estrutura de suporte ao grafo de posições e ao grafo de estados.

Preserva a ordem de inserção dos nós e dos vizinhos.
"""

from __future__ import annotations

from collections.abc import Iterable


class Grafo:
    """Grafo dos labirintos, com nós identificados por rótulos em strings.

    Os métodos de consulta devolvem cópias das listas, preservando a ordem
    de inserção dos vizinhos. Não há arestas paralelas para o mesmo destino.
    """

    lista_de_adjacencia: dict[str, list[tuple[str, float]]]

    def __init__(self) -> None:
        """Inicializa a representação de um grafo vazio."""
        self.lista_de_adjacencia = {}

    def adicionar_no(self, no: str) -> None:
        """Adiciona um nó, permitindo representar também nós isolados."""
        if no not in self.lista_de_adjacencia:
            self.lista_de_adjacencia[no] = []

    def adicionar_aresta(self, origem: str, destino: str, peso: float) -> None:
        """Adiciona uma aresta dirigida com peso, preservando a ordem de inserção.

        Ignora arestas duplicadas idênticas. Levanta ValueError se já existir
        uma aresta para o mesmo destino porém com peso diferente.
        """
        self.adicionar_no(origem)
        self.adicionar_no(destino)

        vizinhos = self.lista_de_adjacencia[origem]
        for vizinho, peso_existente in vizinhos:
            if vizinho == destino:
                if peso_existente == peso:
                    return
                raise ValueError(
                    f"Já existe uma aresta de '{origem}' para '{destino}' "
                    f"com peso diferente ({peso_existente} != {peso})."
                )
        vizinhos.append((destino, peso))

    def nos(self) -> list[str]:
        """Devolve os nós, incluindo os que não possuem arestas de saída."""
        return list(self.lista_de_adjacencia)

    def arestas(self) -> list[tuple[str, str, float]]:
        """Devolve as arestas como tuplas (origem, destino, peso)."""
        return [
            (origem, destino, peso)
            for origem, vizinhos in self.lista_de_adjacencia.items()
            for destino, peso in vizinhos
        ]

    def vizinhos(self, no: str) -> list[tuple[str, float]]:
        """Devolve pares (destino, peso) das arestas de saída, na ordem de inserção."""
        if no not in self.lista_de_adjacencia:
            raise ValueError(f"Nó '{no}' não existe no grafo.")
        return self.lista_de_adjacencia[no].copy()

    def ordem(self) -> int:
        """Devolve a quantidade de nós do grafo, |V|."""
        return len(self.lista_de_adjacencia)

    def tamanho(self) -> int:
        """Devolve a quantidade de arestas dirigidas do grafo, |E|."""
        return sum(len(vizinhos) for vizinhos in self.lista_de_adjacencia.values())

    def densidade(self) -> float:
        """Devolve a densidade dirigida; para menos de dois nós, deve ser zero."""
        n = self.ordem()
        if n < 2:
            return 0.0
        return self.tamanho() / (n * (n - 1))

    def grau_entrada(self, no: str) -> int:
        """Devolve a quantidade de arestas que chegam ao nó."""
        if no not in self.lista_de_adjacencia:
            raise ValueError(f"Nó '{no}' não existe no grafo.")
        return sum(
            1
            for vizinhos in self.lista_de_adjacencia.values()
            for destino, _ in vizinhos
            if destino == no
        )

    def grau_saida(self, no: str) -> int:
        """Devolve a quantidade de arestas que saem do nó."""
        if no not in self.lista_de_adjacencia:
            raise ValueError(f"Nó '{no}' não existe no grafo.")
        return len(self.lista_de_adjacencia[no])

    def transposto(self) -> Grafo:
        """Devolve o grafo com arestas invertidas para a busca de estados-armadilha."""
        grafo = Grafo()
        for origem, vizinhos in self.lista_de_adjacencia.items():
            if not vizinhos:
                grafo.adicionar_no(origem)
            for destino, peso in vizinhos:
                grafo.adicionar_no(destino)
                grafo.adicionar_no(origem)
                grafo.lista_de_adjacencia[destino].append((origem, peso))
        return grafo

    def subgrafo_induzido(self, nos: Iterable[str]) -> Grafo:
        """Devolve o subgrafo de uma camada, com os nós e arestas internos a ela."""
        grafo = Grafo()
        nos_selecionados = dict.fromkeys(nos)
        for no in nos_selecionados:
            if no not in self.lista_de_adjacencia:
                raise ValueError(f"Nó '{no}' não existe no grafo.")
            grafo.adicionar_no(no)
            for destino, peso in self.lista_de_adjacencia[no]:
                if destino in nos_selecionados:
                    grafo.adicionar_no(destino)
                    grafo.lista_de_adjacencia[no].append((destino, peso))
        return grafo
