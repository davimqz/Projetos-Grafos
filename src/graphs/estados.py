"""Contratos dos grafos de posições (G_pos) e de estados (G_est) da Parte 1.

As grades recebidas devem estar validadas por graphs.io. Coordenadas começam
em zero, na grade sem comentários. A ordem dos movimentos é sempre N, L, S, O.

Os corpos das funções ficam a cargo do integrante. Exportações e métricas
pertencem à orquestração; este módulo cuida da modelagem e da construção.
"""

# [IA] Codex - boilerplate de tipos, assinaturas e contratos; sem lógica de grafos.
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.graphs.io import encontrar_inicio, enumerar_bonus

from .graph import Grafo


Posicao = tuple[int, int]
Movimento = Literal["N", "L", "S", "O"]
ModoPortas = Literal["chao", "parede"]


@dataclass(frozen=True)
class Estado:
    """Situação do jogador após os efeitos de entrar na casa atual.

    Chaves e bônus são conjuntos imutáveis para permitir comparar estados
    e usá-los como chaves de dicionários ou elementos de conjuntos.

    Na variante fonte_consumivel, bonus também contém os identificadores
    das fontes já consumidas, definidos por enumerar_consumiveis.
    """

    linha: int
    coluna: int
    chaves: frozenset[str]
    bonus: frozenset[int]


@dataclass(frozen=True)
class Transicao:
    """Um movimento permitido e seus dados para a futura exportação de arcos.

    destino já inclui os efeitos da coleta. casa_destino é o símbolo original
    da grade. Esta representação não inclui o arco virtual de G para ALVO.
    """

    destino: Estado
    movimento: Movimento
    casa_destino: str
    peso: float


def rotular_posicao(posicao: Posicao) -> str:
    """Devolve o rótulo '(linha,coluna)', sem espaços, de um nó de G_pos."""

    return f"({posicao[0]},{posicao[1]})"


def rotular_estado(estado: Estado) -> str:
    """Devolve o rótulo obrigatório, por exemplo '(3,5)|ab|{0,2}'.

    Chaves aparecem em ordem alfabética e identificadores de bônus em ordem
    numérica, sem espaços. Sem chaves, usar '-'; sem bônus, usar '{}'.
    """

    chaves = "".join(sorted(estado.chaves)) or "-"
    bonus = "{" + ",".join(str(i) for i in sorted(estado.bonus)) + "}"
    return f"{rotular_posicao((estado.linha, estado.coluna))}|{chaves}|{bonus}"

def enumerar_consumiveis(
    grade: list[str], *, fonte_consumivel: bool = False
) -> dict[Posicao, int]:
    """Associa cada consumível à sua identificação no conjunto Estado.bonus.

    Os '+' mantêm os identificadores de io.enumerar_bonus: desde zero em
    ordem de leitura (linha, depois coluna).

    Com fonte_consumivel=True, incluir também as fontes '*', em ordem de
    leitura, com identificadores após todos os '+', sem colisões. Com False,
    as fontes não pertencem ao retorno. Não modifica a grade.
    """

    bonus = enumerar_bonus(grade)
    if fonte_consumivel:
        contador = len(bonus)
        for i, linha in enumerate(grade):
            for j, char in enumerate(linha):
                if char == "*":
                    bonus[(i, j)] = contador
                    contador += 1
    return bonus

def movimentos_possiveis(
    grade: list[str], posicao: Posicao
) -> list[tuple[Movimento, Posicao]]:
    """Devolve movimentos geométricos na ordem N, L, S, O.

    posicao deve identificar uma casa não parede. Destinos ficam dentro da
    grade e não são paredes. Uma esteira permite sair somente na direção
    da seta; se apontar para fora ou para parede, não há movimento.

    Portas ainda são candidatas: a permissão depende da modelagem usada
    pelo chamador. Não aplica coleta nem custos. Em G, não há movimentos
    físicos; a ligação virtual a ALVO pertence à construção de G_est.
    """

    movimentos = []
    linhas = len(grade)
    colunas = len(grade[0]) if linhas > 0 else 0
    i, j = posicao

    # Norte
    if i > 0 and grade[i - 1][j] != "#":
        movimentos.append(("N", (i - 1, j)))
    # Leste
    if j < colunas - 1 and grade[i][j + 1] != "#":
        movimentos.append(("L", (i, j + 1)))
    # Sul
    if i < linhas - 1 and grade[i + 1][j] != "#":
        movimentos.append(("S", (i + 1, j)))
    # Oeste
    if j > 0 and grade[i][j - 1] != "#":
        movimentos.append(("O", (i, j - 1)))

    casa_atual = grade[i][j]

    if casa_atual == "G":
        return []

    if casa_atual in "^>v<":
        direcao_esteira = {"^": "N", ">": "L", "v": "S", "<": "O"}[casa_atual]
        movimentos = [
            (mov, dest) for mov, dest in movimentos if mov == direcao_esteira
        ]

    return movimentos

def gerar_transicoes(
    grade: list[str],
    estado: Estado,
    consumiveis: dict[Posicao, int],
    *,
    fonte_consumivel: bool = False,
) -> list[Transicao]:
    """Devolve as transições válidas de um estado, na ordem N, L, S, O.

    consumiveis deve corresponder à grade e à opção fonte_consumivel.
    estado deve representar uma situação válida, com as coletas da casa
    atual já registradas. Não modifica a grade nem o estado recebido.

    Portas exigem sua chave; chaves coletadas permanecem com o jogador.
    O peso é o custo de entrar no destino: chão/S/G/chaves/portas/esteiras
    valem 1, lama vale 3 e água vale 5. '+' vale -4 na primeira coleta e 1
    nas seguintes. '*' vale -2 sempre, ou apenas na primeira coleta quando
    fonte_consumivel=True, passando a valer 1 depois.

    A transição registra o estado após as coletas. Estados em G não têm
    transições físicas. Não inclui a ligação virtual para ALVO.
    """

    transicoes = []
    posicao_atual = (estado.linha, estado.coluna)
    movimentos = movimentos_possiveis(grade, posicao_atual)

    for movimento, destino in movimentos:
        i, j = destino
        casa_destino = grade[i][j]

        if casa_destino in "ABCD" and casa_destino.lower() not in estado.chaves:
            continue

        chaves_novas = set(estado.chaves)
        bonus_novos = set(estado.bonus)

        if casa_destino in "abcd":
            chaves_novas.add(casa_destino)

        if destino in consumiveis:
            bonus_id = consumiveis[destino]
            bonus_novos.add(bonus_id)

        peso = 1
        if casa_destino == "~":
            peso = 5
        elif casa_destino == ",":
            peso = 3
        elif casa_destino == "+":
            if bonus_id not in estado.bonus:
                peso = -4 
            else:
                peso = 1
        elif casa_destino == "*":
            if not fonte_consumivel or bonus_id not in estado.bonus:
                peso = -2
            else:
                peso = 1

        novo_estado = Estado(
            linha=i,
            coluna=j,
            chaves=frozenset(chaves_novas),
            bonus=frozenset(bonus_novos),
        )

        transicoes.append(
            Transicao(
                destino=novo_estado,
                movimento=movimento,
                casa_destino=casa_destino,
                peso=peso,
            )
        )

    return transicoes


def construir_grafo_posicoes(
    grade: list[str], *, portas: ModoPortas = "chao"
) -> Grafo:
    """Constrói G_pos para a comparação das modelagens ingênuas.

    Inclui todas as casas permitidas pela variante, mesmo as inalcançáveis
    a partir de S. Rótulos seguem rotular_posicao. 'chao' permite atravessar
    portas sem chaves; 'parede' exclui as portas. Outro valor deve provocar
    ValueError com mensagem clara.

    Respeita paredes, esteiras, término em G e a ordem N, L, S, O. Não inclui
    ALVO. Os pesos seguem o destino, mas '+' vale -4 em toda entrada e '*'
    vale -2 em toda entrada, sem memória de consumo ou coleta de chaves.
    Não espelha arcos automaticamente e não modifica a grade.
    """

    if portas not in ("chao", "parede"):
        raise ValueError(
            f"Valor inválido para portas: '{portas}'. "
            "Use 'chao' ou 'parede'."
        )

    grafo = Grafo()

    for i, linha in enumerate(grade):
        for j, char in enumerate(linha):
            if char == "#" or portas == "parede" and char in "ABCD":
                continue
            posicao = (i, j)
            grafo.adicionar_no(rotular_posicao(posicao))
            movimentos = movimentos_possiveis(grade, posicao)
            for mov, destino in movimentos:
                if portas == "parede" and grade[destino[0]][destino[1]] in "ABCD":
                    continue
                casa_destino = grade[destino[0]][destino[1]]
                peso = 1
                if casa_destino == "~":
                    peso = 5
                elif casa_destino == ",":
                    peso = 3
                elif casa_destino == "+":
                    peso = -4
                elif casa_destino == "*":
                    peso = -2
                grafo.adicionar_aresta(
                    rotular_posicao(posicao),
                    rotular_posicao(destino),
                    peso,
                )

    return grafo

def construir_grafo_estados(
    grade: list[str], *, fonte_consumivel: bool = False
) -> tuple[Grafo, dict[str, Estado]]:
    """Constrói G_est e devolve (grafo, estados_por_rotulo).

    O estado inicial está em S, sem chaves nem bônus consumidos. Só inclui
    estados alcançáveis a partir dele, por exploração, sem criar todas as
    combinações antecipadamente. Vizinhos seguem a ordem N, L, S, O e os
    rótulos seguem rotular_estado. Estados equivalentes são um único nó.

    Inclui o nó virtual 'ALVO', mesmo quando nenhuma saída é alcançável.
    Todo estado em G tem somente um arco para ALVO, com custo zero; ALVO
    não tem saída. As demais transições seguem gerar_transicoes.

    O dicionário associa cada rótulo físico ao Estado correspondente, para
    consulta de posição, camadas e consumíveis, sem precisar interpretar
    strings. ALVO não pertence ao dicionário. Ele e seus arcos devem ser
    excluídos das métricas físicas pela orquestração.

    A opção fonte_consumivel usa os identificadores adicionais descritos
    em enumerar_consumiveis. Não modifica a grade nem grava arquivos.
    """

    grafo = Grafo()
    estados_por_rotulo: dict[str, Estado] = {}

    consumiveis = enumerar_consumiveis(grade, fonte_consumivel=fonte_consumivel)
    posicao_inicio = encontrar_inicio(grade)
    estado_inicial = Estado(
        linha=posicao_inicio[0],
        coluna=posicao_inicio[1],
        chaves=frozenset(),
        bonus=frozenset(),
    )
    rotulo_inicial = rotular_estado(estado_inicial)

    fila_exploracao = [estado_inicial]
    estados_por_rotulo[rotulo_inicial] = estado_inicial
    grafo.adicionar_no(rotulo_inicial)

    while fila_exploracao:
        estado_atual = fila_exploracao.pop(0)
        rotulo_atual = rotular_estado(estado_atual)

        transicoes = gerar_transicoes(
            grade, estado_atual, consumiveis, fonte_consumivel=fonte_consumivel
        )

        for transicao in transicoes:
            rotulo_destino = rotular_estado(transicao.destino)
            if rotulo_destino not in estados_por_rotulo:
                estados_por_rotulo[rotulo_destino] = transicao.destino
                grafo.adicionar_no(rotulo_destino)
                fila_exploracao.append(transicao.destino)

            grafo.adicionar_aresta(
                rotulo_atual,
                rotulo_destino,
                transicao.peso,
            )

    grafo.adicionar_no("ALVO")
    for rotulo, estado in estados_por_rotulo.items():
        if grade[estado.linha][estado.coluna] == "G":
            grafo.adicionar_aresta(rotulo, "ALVO", 0)

    return grafo, estados_por_rotulo
