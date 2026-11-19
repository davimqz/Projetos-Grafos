"""Normalização, reutilização de buscas e comparação de modelagens da Parte 1.

Os algoritmos e a construção dos grafos são reutilizados de src.graphs.
"""

# [IA] Codex - separação do código existente, preservando os resultados e a lógica.
from __future__ import annotations

from src.graphs.algorithms import bellman_ford, bfs, dijkstra
from src.graphs.estados import construir_grafo_posicoes, rotular_posicao
from src.graphs.io import encontrar_inicio, encontrar_saidas
from src.viz import reconstruir_percurso
from .modelos import AlgoritmoCaminho, DadosMapa, Solucao


def resolver_mapa(dados: DadosMapa, algoritmo: AlgoritmoCaminho) -> Solucao:
    """Normaliza o resultado de um algoritmo existente até ALVO.

    BFS procura menos passos; Dijkstra e Bellman-Ford procuram menor custo.
    O caminho com status OK contém os rótulos desde a origem até ALVO.
    passos conta movimentos físicos, sem o arco virtual; custo representa
    a soma dos pesos do caminho, inclusive quando a busca usada é BFS.

    Registra RECUSA para Dijkstra com peso negativo, CICLO_NEGATIVO quando
    um ciclo alcançável puder chegar a ALVO e SEM_SOLUCAO para ALVO inalcançável.
    Não implementa novamente os algoritmos e não grava arquivos.
    """
    return _resolver_mapa(dados, algoritmo, {})


def _resultado_busca(dados: DadosMapa, algoritmo: AlgoritmoCaminho, resultados: dict[str, dict]) -> dict:
    """Reutiliza as buscas no grafo completo durante a orquestração."""
    if algoritmo not in resultados:
        buscar = {"BFS": bfs, "DIJKSTRA": dijkstra, "BELLMAN_FORD": bellman_ford}[algoritmo]
        resultados[algoritmo] = buscar(dados.grafo_estados, dados.origem)
    return resultados[algoritmo]


# [IA] Codex - correção da normalização até ALVO, reutilizando buscas e subgrafo existentes.
def _bellman_ford_ate_alvo(dados: DadosMapa, resultado: dict) -> dict:
    """Separa ciclos presos em armadilhas dos que afetam o custo até ALVO."""
    if not resultado["tem_ciclo_negativo"] or resultado["distancia"]["ALVO"] == float("inf"):
        return resultado

    grafo = dados.grafo_estados
    relevantes = set(bfs(grafo.transposto(), "ALVO")["ordem"])
    if any(no in relevantes for no in resultado["ciclo_negativo"]):
        return resultado

    # Pode haver outro ciclo negativo relevante além da testemunha global.
    subgrafo = grafo.subgrafo_induzido(no for no in grafo.nos() if no in relevantes)
    return bellman_ford(subgrafo, dados.origem)


def _resolver_mapa(dados: DadosMapa, algoritmo: AlgoritmoCaminho, resultados: dict[str, dict]) -> Solucao:
    """Normaliza buscas existentes, com reutilização local dos resultados."""

    grafo = dados.grafo_estados
    inicio = dados.origem

    if inicio not in grafo.nos():
        raise ValueError(f"Origem '{inicio}' não existe no grafo.")

    if algoritmo not in ("BFS", "DIJKSTRA", "BELLMAN_FORD"):
        raise ValueError(f"Algoritmo desconhecido: {algoritmo}")

    caminho: list[str] = []
    custo: float | None = None
    try:
        resultado = _resultado_busca(dados, algoritmo, resultados)
        if algoritmo == "BELLMAN_FORD":
            resultado = _bellman_ford_ate_alvo(dados, resultado)
        status = "OK" if algoritmo == "BFS" else resultado["status"]
        if resultado["distancia"]["ALVO"] == float("inf"):
            status = "SEM_SOLUCAO"
        if status == "OK":
            caminho = reconstruir_percurso(resultado, inicio, "ALVO")
            if algoritmo == "BFS":
                custo = 0.0
                for origem, destino in zip(caminho, caminho[1:]):
                    for vizinho, peso in grafo.vizinhos(origem):
                        if vizinho == destino:
                            custo += peso
                            break
            else:
                custo = resultado["distancia"]["ALVO"]
    except ValueError as erro:
        status = "RECUSA" if algoritmo == "DIJKSTRA" and "negativo" in str(erro) else "SEM_SOLUCAO"

    if status != "OK":
        passos = None
        custo = None
        caminho = []
    else:
        passos = len(caminho) - 2

    return Solucao(
        mapa=dados.nome,
        algoritmo=algoritmo,
        passos=passos,
        custo=custo,
        status=status,
        caminho=caminho
    )


def comparar_modelagens(dados: DadosMapa) -> list[dict[str, object]]:
    """Prepara as três linhas de um mapa para comparacao_modelagem.csv.

    Compara BFS com portas como chão, portas como parede e G_est correto.
    Colunas: mapa,abordagem,passos,caminho_valido,observacao.
    Os passos são movimentos físicos até uma saída; ausência de caminho
    deve ser representada explicitamente. Não compara os pesos dos caminhos.

    A validade considera as regras originais de chaves e portas.
    As observações interpretativas devem ser escritas pelo integrante.
    Os casos obrigatórios são m02, m03 e m04.
    """
    return _comparar_modelagens(dados, {})


def _comparar_modelagens(dados: DadosMapa, resultados_buscas: dict[str, dict]) -> list[dict[str, object]]:
    """Compara as modelagens aproveitando a BFS de estados quando disponível."""

    inicio_pos = rotular_posicao(encontrar_inicio(dados.grade))
    saidas_pos = {rotular_posicao(pos) for pos in encontrar_saidas(dados.grade)}

    grafos_posicoes = [
        ("portas_como_chao", dados.grafo_posicoes, "Ignora chaves e atravessa portas diretamente."),
        ("portas_como_parede", construir_grafo_posicoes(dados.grade, portas="parede"), "Bloqueia portas mesmo quando há chave disponível."),
    ]

    resultados: list[dict[str, object]] = []

    for abordagem, grafo, obs in grafos_posicoes:
        res = bfs(grafo, inicio_pos)
        destino = next((no for no in res["ordem"] if no in saidas_pos), None)

        if destino is None:
            passos = None
            valido = False
        else:
            caminho = reconstruir_percurso(res, inicio_pos, destino)

            passos = len(caminho) - 1
            chaves: set[str] = set()
            valido = True
            for no in caminho:
                linha, coluna = map(int, no.strip("()").split(","))
                casa = dados.grade[linha][coluna]
                if casa in "abcd":
                    chaves.add(casa)
                elif casa in "ABCD" and casa.lower() not in chaves:
                    valido = False
                    break

        resultados.append({
            "mapa": dados.nome,
            "abordagem": abordagem,
            "passos": passos,
            "caminho_valido": valido,
            "observacao": obs,
        })

    dist_est = _resultado_busca(dados, "BFS", resultados_buscas)["distancia"]["ALVO"]
    passos_est = None if dist_est == float("inf") else int(dist_est) - 1

    resultados.append({
        "mapa": dados.nome,
        "abordagem": "grafo_estados",
        "passos": passos_est,
        "caminho_valido": passos_est is not None,
        "observacao": "Modelagem exata com memória de chaves coletadas.",
    })

    return resultados


def comparar_bonus(dados: DadosMapa) -> dict[str, object]:
    """Reúne as execuções de Bellman-Ford do experimento do m05.

    Compara G_pos com bônus de custo fixo e G_est com memória de consumo.
    Disponibiliza os resultados, incluindo ciclo e custo quando retornados
    pelo algoritmo existente. Recebe o m05 na variante padrão.
    Não escreve a prova nem a interpretação exigida no PDF.
    """
    return _comparar_bonus(dados, {})


def _comparar_bonus(dados: DadosMapa, resultados_buscas: dict[str, dict]) -> dict[str, object]:
    """Reaproveita o Bellman-Ford de estados sem alterar o experimento."""

    grafo_pos = dados.grafo_posicoes

    resultado_estados = _resultado_busca(dados, "BELLMAN_FORD", resultados_buscas)
    resultado_pos = bellman_ford(grafo_pos, rotular_posicao(encontrar_inicio(dados.grade)))

    return{
        "mapa": dados.nome,
        "grafo_posicoes": {
            "status":resultado_pos["status"],
            "tem_ciclo_negativo": resultado_pos["tem_ciclo_negativo"],
            "ciclo_negativo":resultado_pos["ciclo_negativo"],
            "custo_ciclo":resultado_pos["custo_ciclo"]
        },
        "grafo_estados": {
            "status":resultado_estados["status"],
            "tem_ciclo_negativo": resultado_estados["tem_ciclo_negativo"],
            "ciclo_negativo":resultado_estados["ciclo_negativo"],
            "custo_ciclo":resultado_estados["custo_ciclo"],
            "custo_ate_alvo":resultado_estados["distancia"]["ALVO"]
        }
    }
