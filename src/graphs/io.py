"""Leitura e validação dos labirintos da Parte 1 (pacote P1).

A grade é uma lista de strings, com acesso por grade[linha][coluna].
As coordenadas começam em zero e não contam as linhas de comentário.
A construção dos grafos de posições e de estados pertence a estados.py.

O módulo fornece a leitura, a validação e a localização dos elementos do mapa.
"""

# [IA] Codex - boilerplate de assinaturas, tipos e docstrings, sem lógica de leitura.
from __future__ import annotations

from pathlib import Path


# [IA] Codex - constante imutável dos símbolos definidos no enunciado.
SIMBOLOS_VALIDOS: frozenset[str] = frozenset({
    "#", ".", "S", "G", ",", "~",
    "a", "b", "c", "d", "A", "B", "C", "D",
    ">", "<", "^", "v", "+", "*",
})


def ler_mapa(caminho: str | Path) -> list[str]:
    """Lê um mapa em UTF-8 e devolve a grade validada.

    Linhas iniciadas com ';' são comentários e não integram a grade.
    As quebras de linha não fazem parte das strings devolvidas; os demais
    caracteres devem ser preservados para a validação.

    Erros de acesso ao arquivo devem ser propagados. Um mapa inválido deve
    provocar ValueError com mensagem clara, conforme validar_mapa.
    """

    with open(caminho, "r", encoding="utf-8") as mapa:
        grade = []
        for linha in mapa:
            if linha[0] != ";":
                grade.append(linha.strip("\n"))
        validar_mapa(grade)

    return grade


# [IA] Codex - revisão das mensagens de erro e da consulta aos símbolos permitidos.
def validar_mapa(grade: list[str]) -> None:
    """Valida a grade sem modificá-la.

    Exige grade não vazia, linhas não vazias de mesma largura, exatamente
    um S, pelo menos um G e apenas símbolos permitidos:
    '#', '.', 'S', 'G', ',', '~', 'a' a 'd', 'A' a 'D', '>', '<', '^', 'v', '+', '*'.

    Levanta ValueError com mensagem clara para entradas inválidas.
    Linhas e colunas nas mensagens usam índices começando em zero, na grade
    sem comentários.
    """

    flag_entrada = False
    flag_saida = False

    if len(grade) == 0:
        raise ValueError("A grade não pode ser vazia.")

    largura = len(grade[0])
    for indice_linha, linha in enumerate(grade):
        if len(linha) == 0:
            raise ValueError(f"A linha {indice_linha} está vazia.")
        elif len(linha) != largura:
            raise ValueError(
                f"A linha {indice_linha} tem largura {len(linha)}; "
                f"a largura esperada é {largura}."
            )

        for indice_coluna, char in enumerate(linha):
            if char not in SIMBOLOS_VALIDOS:
                raise ValueError(
                    f"Símbolo inválido {char!r} na posição "
                    f"({indice_linha}, {indice_coluna})."
                )

            if char == "S" and not flag_entrada:
                flag_entrada = True
            elif char == "S" and flag_entrada:
                raise ValueError(
                    "A grade deve conter exatamente um 'S'; outro início "
                    f"foi encontrado na posição ({indice_linha}, {indice_coluna})."
                )
            elif char == "G":
                flag_saida = True

    if not flag_entrada:
        raise ValueError("A grade deve conter exatamente um 'S'; nenhum foi encontrado.")
    if not flag_saida:
        raise ValueError("A grade deve conter pelo menos um 'G'; nenhum foi encontrado.")


def encontrar_inicio(grade: list[str]) -> tuple[int, int]:
    """Devolve a posição (linha, coluna) de S em uma grade já validada."""

    for i, linha in enumerate(grade):
        for j, char in enumerate(linha):
            if char == "S":
                return (i, j)
    raise ValueError("A grade não contém um ponto de início 'S' válido.")


def encontrar_saidas(grade: list[str]) -> list[tuple[int, int]]:
    """Devolve as posições de G em uma grade já validada, em ordem de leitura.

    A ordem de leitura percorre linhas de cima para baixo e, dentro de cada
    linha, colunas da esquerda para a direita.
    """

    saidas = []
    for i, linha in enumerate(grade):
        for j, char in enumerate(linha):
            if char == "G":
                saidas.append((i, j))
    return saidas


def enumerar_bonus(grade: list[str]) -> dict[tuple[int, int], int]:
    """Associa a posição de cada '+' ao seu identificador em uma grade validada.

    Os identificadores começam em zero e seguem a ordem de leitura.
    O retorno não inclui fontes '*'; a opção de fonte consumível pertence
    à modelagem dos estados.
    """

    bonus = {}
    contador = 0
    for i, linha in enumerate(grade):
        for j, char in enumerate(linha):
            if char == "+":
                bonus[(i, j)] = contador
                contador += 1
    return bonus
