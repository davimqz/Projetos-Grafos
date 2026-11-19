"""Contratos da orquestração e das entregas da Parte 1 (P3).

Os corpos ficam a cargo do integrante. Este módulo reutiliza a leitura,
a construção dos grafos e os algoritmos existentes em src.graphs.
As visualizações pertencem a src.viz e src.visualizar_parte1.

As funções de cálculo não gravam arquivos nem modificam os grafos recebidos.
ALVO participa das buscas, mas ele e seus arcos não entram nas métricas
físicas. A Parte 2 continua nos seus módulos específicos.
"""

# [IA] Codex - boilerplate de tipos, assinaturas e contratos; sem implementação.
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict

from src.graphs.estados import Estado, construir_grafo_estados, construir_grafo_posicoes, rotular_estado, rotular_posicao
from src.graphs.graph import Grafo
from src.graphs.io import encontrar_inicio, ler_mapa, encontrar_saidas
from src.graphs.algorithms import bfs, dfs, dijkstra, bellman_ford
from src.viz import reconstruir_percurso


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

    cords_inicio = encontrar_inicio(grade)
    origem = rotular_estado(Estado(cords_inicio[0], cords_inicio[1], frozenset(), frozenset()))


    return DadosMapa(
        nome = caminho.stem if nome is None else nome,
        grade = grade,
        grafo_posicoes=construir_grafo_posicoes(grade),
        grafo_estados=grafo,
        estados=estados,
        origem=origem,
        fonte_consumivel=fonte_consumivel
    )


def exportar_arestas(dados: DadosMapa, caminho: str | Path) -> None:
    """Grava os arcos de G_est em arestas_<mapa>.csv.

    Cabeçalho: origem,destino,movimento,casa_destino,peso.
    Uma linha por arco dirigido existente, sem espelhamento, preservando
    a ordem dos nós e dos vizinhos. Os metadados descrevem o movimento
    físico e o símbolo original do destino; os pesos vêm do grafo.

    Para os arcos virtuais até ALVO, movimento e casa_destino ficam vazios.
    Usa CSV com escape correto dos rótulos que contêm vírgulas.
    Não constrói novas transições nem altera as regras do mapa.
    """

    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)

        escritor.writerow([
            "origem",
            "destino",
            "movimento",
            "casa_destino",
            "peso",
        ])

        data = dados.grafo_estados.arestas()

        for i in data:
            origem = i[0]
            destino = i[1]
            peso= i[2]

            if destino == "ALVO":
                escritor.writerow([origem, destino, "", "", peso])
                continue

            estado_origem = dados.estados[origem]
            estado_destino = dados.estados[destino]
            
            diffx = estado_origem.linha - estado_destino.linha
            diffy = estado_origem.coluna - estado_destino.coluna

            if diffx == 1 and diffy == 0:
                movimento = "N"
            elif diffx == -1 and diffy == 0:
                movimento = "S"
            elif diffx == 0 and diffy == 1:
                movimento = "O"
            else:
                movimento = "L"

            

            escritor.writerow([
                origem,
                destino,
                movimento,
                dados.grade[estado_destino.linha][estado_destino.coluna],
                peso
            ])

def calcular_metricas_globais(dados: DadosMapa) -> dict[str, object]:
    """Devolve as métricas de um mapa para metricas_global.json.

    Inclui ordem, tamanho e densidade de G_pos e G_est, teto teórico
    e taxa de ocupação. Não conta ALVO nem os arcos virtuais.
    O teto considera casas livres, chaves distintas e bônus consumíveis;
    na variante fonte_consumivel, inclui também as fontes consumíveis.
    Reutiliza as consultas de Grafo e não grava arquivos.
    """

    casas_livres_list = {".", "S", "G", ",", "~", "a", "b", "c", "d", "A", "B", "C", "D", ">", "<", "^", "v", "+", "*"}

    ordem_pos = dados.grafo_posicoes.ordem()
    tamanho_pos = dados.grafo_posicoes.tamanho()
    densidade_pos = dados.grafo_posicoes.densidade()

    grafo_fisico = dados.grafo_estados.subgrafo_induzido(dados.estados)

    ordem_est = grafo_fisico.ordem()
    tamanho_est = grafo_fisico.tamanho()
    densidade_est = grafo_fisico.densidade()

    casas_livres = sum(linha.count(char) for linha in dados.grade for char in casas_livres_list)
    chaves_distintas = len({char for linha in dados.grade for char in linha if char in "abcd"})
    bonus_consumiveis = sum(linha.count("+") for linha in dados.grade)
    fontes_consumiveis = sum(linha.count("*") for linha in dados.grade)
    
    teto_teorico = casas_livres * (2 ** chaves_distintas) * (2 ** bonus_consumiveis)
    if dados.fonte_consumivel:
        teto_teorico *= (2 ** fontes_consumiveis)

    taxa_ocupacao = ordem_est / teto_teorico if teto_teorico > 0 else 0

    return {
        "ordem_pos": ordem_pos,
        "tamanho_pos": tamanho_pos,
        "densidade_pos": densidade_pos,
        "ordem_est": ordem_est,
        "tamanho_est": tamanho_est,
        "densidade_est": densidade_est,
        "teto_teorico": teto_teorico,
        "taxa_ocupacao": taxa_ocupacao
    }



def calcular_camadas(dados: DadosMapa) -> dict[str, object]:
    """Devolve os dados de um mapa para camadas.json.

    Uma camada corresponde a um conjunto de chaves, incluindo todos os
    conjuntos de bônus que aparecem com essas chaves. Registra ordem,
    tamanho e densidade de cada subgrafo induzido, sem ALVO.
    Também registra a quantidade de arcos entre camadas e as posições
    e símbolos das casas que os geram. Não inclui interpretações textuais.
    """

    nos_por_camada: dict[str, list[str]] = {}
    for rotulo, estado in dados.estados.items():
        camada = "".join(sorted(estado.chaves)) or "-"
        nos_por_camada.setdefault(camada, []).append(rotulo)

    camadas = []
    for camada, nos in sorted(nos_por_camada.items(), key=lambda x: (0 if x[0] == "-" else len(x[0]), x[0])):
        subgrafo = dados.grafo_estados.subgrafo_induzido(nos)
        camadas.append({
            "camada": camada,
            "ordem": subgrafo.ordem(),
            "tamanho": subgrafo.tamanho(),
            "densidade": subgrafo.densidade(),
        })

    arcos_entre_camadas = 0
    casas_geradoras_dict: dict[tuple[int, int], str] = {}

    for origem, destino, _ in dados.grafo_estados.arestas():
        if destino != "ALVO" and dados.estados[origem].chaves != dados.estados[destino].chaves:
            arcos_entre_camadas += 1
            est_dest = dados.estados[destino]
            casas_geradoras_dict[(est_dest.linha, est_dest.coluna)] = dados.grade[est_dest.linha][est_dest.coluna]

    casas_geradoras = [
        {"linha": linha, "coluna": coluna, "simbolo": simbolo}
        for (linha, coluna), simbolo in sorted(casas_geradoras_dict.items())
    ]

    return {
        "camadas": camadas,
        "arcos_entre_camadas": arcos_entre_camadas,
        "casas_geradoras": casas_geradoras,
    }


def calcular_graus(dados: DadosMapa) -> list[GrauEstado]:
    """Devolve as linhas de graus_<mapa>.csv para os estados físicos.

    Os graus não contam arcos para ALVO. Mantém a ordem dos estados
    recebidos para permitir uma exportação reproduzível.
    """

    graus: list[GrauEstado] = []

    for rotulo in dados.estados:
        grau_entrada = dados.grafo_estados.grau_entrada(rotulo)
        grau_saida = dados.grafo_estados.grau_saida(rotulo)

        if any(destino == "ALVO" for destino, _peso in dados.grafo_estados.vizinhos(rotulo)):
            grau_saida -= 1

        graus.append({
            "estado": rotulo,
            "grau_entrada": grau_entrada,
            "grau_saida": grau_saida,
        })

    return graus

def analisar_graus(dados: DadosMapa) -> dict[str, object]:
    """Devolve rankings, multiplicidades por casa e estados de beco.

    Registra os estados de maior grau de entrada e saída, com desempate
    pela ordem de leitura do rótulo, e os respectivos graus físicos.
    Inclui a multiplicidade máxima, as casas que a atingem e sua quantidade.
    Becos são estados sem saída física que não estão em G.
    As explicações desses resultados ficam a cargo do grupo no PDF.
    """

    grafo_fisico = dados.grafo_estados.subgrafo_induzido(dados.estados)

    graus_entrada = {rotulo: grafo_fisico.grau_entrada(rotulo) for rotulo in dados.estados}
    graus_saida = {rotulo: grafo_fisico.grau_saida(rotulo) for rotulo in dados.estados}


    estado_maior_entrada = max(sorted(graus_entrada), key=graus_entrada.get, default=None)
    estado_maior_saida = max(graus_saida, key=graus_saida.get, default=None)

    multiplicidades: dict[tuple[int, int], int] = {}
    for estado in dados.estados.values():
        pos = (estado.linha, estado.coluna)
        multiplicidades[pos] = multiplicidades.get(pos, 0) + 1

    multiplicidade_maxima = max(multiplicidades.values(), default=0)
    casas_max = [
        {"linha": linha, "coluna": coluna, "simbolo": dados.grade[linha][coluna]}
        for (linha, coluna), qtd in sorted(multiplicidades.items())
        if qtd == multiplicidade_maxima
    ]

    becos = [
        rotulo
        for rotulo, estado in dados.estados.items()
        if graus_saida[rotulo] == 0 and dados.grade[estado.linha][estado.coluna] != "G"
    ]

    return {
        "estado_maior_grau_entrada": estado_maior_entrada,
        "maior_grau_entrada": graus_entrada.get(estado_maior_entrada, 0),
        "estado_maior_grau_saida": estado_maior_saida,
        "maior_grau_saida": graus_saida.get(estado_maior_saida, 0),
        "multiplicidade_maxima": multiplicidade_maxima,
        "casas_multiplicidade_maxima": casas_max,
        "quantidade_casas_multiplicidade_maxima": len(casas_max),
        "becos": becos,
        "quantidade_becos": len(becos),
    }


def resolver_mapa(dados: DadosMapa, algoritmo: AlgoritmoCaminho) -> Solucao:
    """Normaliza o resultado de um algoritmo existente até ALVO.

    BFS procura menos passos; Dijkstra e Bellman-Ford procuram menor custo.
    O caminho com status OK contém os rótulos desde a origem até ALVO.
    passos conta movimentos físicos, sem o arco virtual; custo representa
    a soma dos pesos do caminho, inclusive quando a busca usada é BFS.

    Registra RECUSA para Dijkstra com peso negativo, CICLO_NEGATIVO quando
    Bellman-Ford o detectar e SEM_SOLUCAO para ALVO inalcançável.
    Não implementa novamente os algoritmos e não grava arquivos.
    """

    grafo = dados.grafo_estados
    inicio = dados.origem

    if inicio not in grafo.nos():
        raise ValueError(f"Origem '{inicio}' não existe no grafo.")

    if algoritmo == "BFS":
        try:
            resultado = bfs(grafo, inicio)
            caminho = reconstruir_percurso(resultado, dados.origem, "ALVO")

            custo = 0.0
            for origem, destino in zip(caminho, caminho[1:]):
                for vizinho, peso in dados.grafo_estados.vizinhos(origem):
                    if vizinho == destino:
                        custo += peso
                        break
            
            if resultado["distancia"]["ALVO"] == float("inf"):
                status = "SEM_SOLUCAO"
            else:
                status = "OK"
                
        except ValueError:
                status= "SEM_SOLUCAO"

    elif algoritmo == "DIJKSTRA":
        try:
            resultado = dijkstra(grafo, inicio)
            caminho = reconstruir_percurso(resultado, dados.origem, "ALVO")
            custo = resultado["distancia"]["ALVO"]
            status = resultado["status"]

        except ValueError as e:
            if "negativo" in str(e):
                status = "RECUSA"
            else:
                status = "SEM_SOLUCAO"
                

    elif algoritmo == "BELLMAN_FORD":
        try:
            resultado = bellman_ford(grafo, inicio)

            if not resultado["tem_ciclo_negativo"]:
                caminho = reconstruir_percurso(resultado, dados.origem, "ALVO")
                custo = resultado["distancia"]["ALVO"]

            status = resultado["status"]

        except ValueError:
            status= "SEM_SOLUCAO"
    else:
        raise ValueError(f"Algoritmo desconhecido: {algoritmo}")
    
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

def classificar_arcos(dados: DadosMapa) -> dict[str, object]:
    """Prepara a linha de um mapa para dfs_classificacao.csv.

    Usa a DFS existente a partir da origem, preservando a ordem N, L, S, O.
    A linha contém mapa, arvore, retorno, avanco e cruzamento.
    Também disponibiliza a indicação de ciclo para o relatório, separada
    das colunas obrigatórias. A busca inclui ALVO e seus arcos alcançáveis.
    """

    grafo = dados.grafo_estados
    inicio = dados.origem

    resultado = dfs(grafo, inicio)

    return {
        "mapa": dados.nome,
        "arvore": resultado["contagem_arcos"]["arvore"],
        "retorno": resultado["contagem_arcos"]["retorno"],
        "avanco": resultado["contagem_arcos"]["avanco"],
        "cruzamento": resultado["contagem_arcos"]["cruzamento"],
        "tem_ciclo": resultado["tem_ciclo"],
        }





def encontrar_armadilhas(dados: DadosMapa) -> list[str]:
    """Devolve os rótulos físicos alcançáveis sem caminho até ALVO.

    Reutiliza o transposto e uma busca já implementada pelo grupo.
    ALVO não pertence ao retorno. A lista mantém a ordem dos estados
    recebidos e serve tanto ao CSV obrigatório quanto à visualização.
    Não grava arquivos nem modifica o grafo original.
    """

    grafo = dados.grafo_estados.transposto()
    alcancaveis = set(bfs(grafo, "ALVO")["ordem"])

    out = []

    for rotulo in dados.estados:
        if rotulo not in alcancaveis:
            out.append(rotulo) 

    return out


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
            caminho = []
            atual: str | None = destino
            while atual is not None:
                caminho.append(atual)
                atual = res["pai"][atual]
            caminho.reverse()

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

    dist_est = bfs(dados.grafo_estados, dados.origem)["distancia"]["ALVO"]
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

    grafo_estados = dados.grafo_estados
    grafo_pos = dados.grafo_posicoes
    inicio = dados.origem

    resultado_estados = bellman_ford(grafo_estados, inicio)
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

# [IA] Codex - escrita genérica de CSV com resultados já calculados.
def exportar_csv(
    registros: Iterable[Mapping[str, object]],
    colunas: Sequence[str],
    caminho: str | Path,
) -> None:
    """Grava registros já calculados em UTF-8, na ordem das colunas.

    Cria a pasta de destino quando necessário e escreve o cabeçalho mesmo
    sem registros. None representa campo vazio. Valores estruturados,
    como o caminho de solucoes.csv, devem ter representação JSON no campo.
    Não calcula resultados nem modifica os registros recebidos.
    """
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()

        for registro in registros:
            linha: dict[str, object] = {}
            for coluna in colunas:
                valor = registro.get(coluna)
                if isinstance(valor, Mapping):
                    valor = dict(valor)
                if isinstance(valor, (dict, list, tuple)):
                    valor = json.dumps(valor, ensure_ascii=False, allow_nan=False)
                linha[coluna] = valor
            escritor.writerow(linha)


# [IA] Codex - escrita genérica de JSON com dados já preparados.
def exportar_json(dados: object, caminho: str | Path) -> None:
    """Grava dados já preparados e serializáveis em JSON UTF-8 legível.

    Cria a pasta de destino quando necessário. Os dados devem usar tipos
    JSON, sem Estados, conjuntos ou valores numéricos não finitos.
    Não calcula resultados nem modifica os dados recebidos.
    """
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2, allow_nan=False)
        arquivo.write("\n")


# [IA] Codex - integração das análises do integrante e exportação dos resultados.
def executar_parte1(mapas: Iterable[str | Path], saida: str | Path, *, fonte_consumivel: bool = False,) -> None:
    """Orquestra as entregas dos mapas informados, incluindo mapas do grupo.

    Prepara os mapas e reúne métricas globais, camadas, graus, rankings,
    multiplicidades, becos, soluções e classificação DFS. Exporta os arcos
    de todos os mapas, inclusive m08 quando estiver entre as entradas.

    Saídas: metricas_global.json, camadas.json, graus_<mapa>.csv,
    arestas_<mapa>.csv, solucoes.csv e dfs_classificacao.csv.
    Para os mapas correspondentes, inclui comparacao_modelagem.csv,
    percurso_m03.json (menor custo, estado a estado), ciclo_negativo_m06.json
    (sequência de estados e custo), armadilhas_m04.csv e armadilhas_m07.csv.
    Reúne ainda o experimento padrão em comparacao_bonus_m05.json e listas
    armadilhas_m04.json/armadilhas_m07.json compatíveis com a CLI existente.
    Os mapas fornecidos usam identificadores m01 a m08; mapas próprios
    mantêm o nome do arquivo sem extensão. Identificadores repetidos são erro.

    Os resultados da variante fonte_consumivel devem ir para uma pasta
    de saída diferente da execução padrão, escolhida pelo chamador.
    Não implementa algoritmos, desenha figuras nem redige análises do PDF.
    Erros de entrada e escrita são propagados para tratamento pela CLI.
    """

    #TODO Adicionar mapas do grupo

    nomes_fornecidos = {
        "m01_terreno": "m01",
        "m02_uma_chave": "m02",
        "m03_tres_chaves": "m03",
        "m04_esteiras": "m04",
        "m05_bonus": "m05",
        "m06_fonte": "m06",
        "m07_impossivel": "m07",
        "m08_grande": "m08",
    }
    entradas: list[tuple[Path, str]] = []
    for mapa in mapas:
        arquivo = Path(mapa)
        nome = nomes_fornecidos.get(arquivo.stem, arquivo.stem)
        entradas.append((arquivo, nome))
    nomes = [nome for _, nome in entradas]
    if len(nomes) != len(set(nomes)):
        raise ValueError("Os mapas devem ter identificadores distintos na mesma execução.")

    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    metricas: dict[str, object] = {}
    camadas: dict[str, object] = {}
    solucoes: list[Solucao] = []
    classificacoes: list[dict[str, object]] = []
    comparacoes: list[dict[str, object]] = []
    algoritmos: tuple[AlgoritmoCaminho, ...] = ("BFS", "DIJKSTRA", "BELLMAN_FORD")

    for arquivo, nome in entradas:
        dados = carregar_mapa(arquivo, nome=nome, fonte_consumivel=fonte_consumivel)
        classificacao = classificar_arcos(dados)
        classificacoes.append(classificacao)
        metricas[nome] = {
            **calcular_metricas_globais(dados),
            **analisar_graus(dados),
            "tem_ciclo_dfs": classificacao["tem_ciclo"],
            "fonte_consumivel": fonte_consumivel,
        }
        camadas[nome] = calcular_camadas(dados)
        exportar_arestas(dados, saida / f"arestas_{nome}.csv")
        exportar_csv(
            calcular_graus(dados),
            ("estado", "grau_entrada", "grau_saida"),
            saida / f"graus_{nome}.csv",
        )

        solucoes_mapa = {}
        for algoritmo in algoritmos:
            solucao = resolver_mapa(dados, algoritmo)
            solucoes.append(solucao)
            solucoes_mapa[algoritmo] = solucao

        if nome in ("m02", "m03", "m04"):
            comparacoes.extend(comparar_modelagens(dados))
        if nome == "m03":
            percurso = solucoes_mapa["DIJKSTRA"]
            if percurso["status"] == "RECUSA":
                percurso = solucoes_mapa["BELLMAN_FORD"]
            exportar_json(percurso, saida / "percurso_m03.json")
        if nome == "m05" and not fonte_consumivel:
            exportar_json(comparar_bonus(dados), saida / "comparacao_bonus_m05.json")
        if nome == "m06":
            resultado = bellman_ford(dados.grafo_estados, dados.origem)
            exportar_json(
                {
                    "mapa": nome,
                    "fonte_consumivel": fonte_consumivel,
                    "status": solucoes_mapa["BELLMAN_FORD"]["status"],
                    "tem_ciclo_negativo": resultado["tem_ciclo_negativo"],
                    "ciclo_negativo": resultado["ciclo_negativo"],
                    "custo_ciclo": resultado["custo_ciclo"],
                },
                saida / "ciclo_negativo_m06.json",
            )
        if nome in ("m04", "m07"):
            armadilhas = encontrar_armadilhas(dados)
            exportar_csv(
                ({"estado": rotulo} for rotulo in armadilhas),
                ("estado",),
                saida / f"armadilhas_{nome}.csv",
            )
            exportar_json(armadilhas, saida / f"armadilhas_{nome}.json")

    exportar_json(metricas, saida / "metricas_global.json")
    exportar_json(camadas, saida / "camadas.json")
    exportar_csv(
        solucoes,
        ("mapa", "algoritmo", "passos", "custo", "status", "caminho"),
        saida / "solucoes.csv",
    )
    exportar_csv(
        classificacoes,
        ("mapa", "arvore", "retorno", "avanco", "cruzamento"),
        saida / "dfs_classificacao.csv",
    )
    exportar_csv(
        comparacoes,
        ("mapa", "abordagem", "passos", "caminho_valido", "observacao"),
        saida / "comparacao_modelagem.csv",
    )
