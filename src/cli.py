"""Ponto de entrada: python -m src.cli ...

Exemplos (do enunciado):
    python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg BFS --out ./out/parte1/
    python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/
    python -m src.cli --mapa ./data/mapas/m04_esteiras.txt --armadilhas --arquivo-armadilhas ./out/parte1/json/armadilhas_m04.json --out ./out/parte1/
    python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source A --target Z --out ./out/parte2/
    python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/
"""
# [IA] Claude Code – esqueleto do argparse com as flags do enunciado
# [IA] Codex - orquestração da Parte 1, execução em lote e resumo final.
# [IA] Codex - atualização do exemplo para a pasta organizada de JSON.
# [IA] Codex - seleção do benchmark da Parte 1 e número de repetições.
import argparse
import sys
from pathlib import Path

ALGORITMOS = ["BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD"]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="src.cli", description="Projeto Final de Grafos 2026.2")
    entrada = p.add_mutually_exclusive_group(required=True)
    entrada.add_argument("--mapa", help="arquivo .txt do labirinto (Parte 1)")
    entrada.add_argument("--mapas", nargs="+", help="arquivos .txt para executar em lote (Parte 1)")
    entrada.add_argument("--todos-mapas", action="store_true", help="executa data/mapas e data/mapas_grupo")
    entrada.add_argument("--dataset", help="pasta do dataset da Parte 2")
    p.add_argument("--alg", choices=ALGORITMOS, help="algoritmo a executar")
    p.add_argument("--out", required=True, help="pasta de saída")
    p.add_argument("--fonte-consumivel", action="store_true", help="'*' vale -2 só na primeira vez")
    p.add_argument("--armadilhas", action="store_true", help="lista estados-armadilha")
    p.add_argument("--arquivo-armadilhas", help="JSON com lista de rótulos de estados-armadilha calculados pelo grupo")
    p.add_argument("--interactive", action="store_true", help="gera o labirinto interativo")
    p.add_argument("--source", help="nó de origem (Parte 2)")
    p.add_argument("--target", help="nó de destino (Parte 2)")
    p.add_argument("--benchmark", action="store_true", help="tempo e memória (Parte 1); escalabilidade (Parte 2)")
    p.add_argument("--repeticoes", type=int, help="execuções de tempo no benchmark da Parte 1 (padrão: 5)")
    return p


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if callable(getattr(stream, "reconfigure", None)):
            stream.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    parte1 = args.mapa or args.mapas or args.todos_mapas
    if args.repeticoes is not None and not (parte1 and args.benchmark):
        parser.error("--repeticoes exige --benchmark com mapas da Parte 1")
    if args.mapa or args.mapas or args.todos_mapas:
        mapas = [args.mapa] if args.mapa else args.mapas
        if args.todos_mapas:
            mapas = [arquivo for pasta in ("data/mapas", "data/mapas_grupo")
                     for arquivo in sorted(Path(pasta).glob("*.txt"))]
        if args.benchmark:
            if args.interactive or args.armadilhas or args.arquivo_armadilhas:
                parser.error("--benchmark gera apenas medições; remova as opções de HTML e armadilhas")
            from src.parte1.benchmark import executar_interface as executar_benchmark
            return executar_benchmark(
                mapas, args.out, fonte_consumivel=args.fonte_consumivel, algoritmo=args.alg,
                repeticoes=args.repeticoes if args.repeticoes is not None else 5,
            )
        from src.parte1.interface_cli import executar_interface
        return executar_interface(
            mapas, args.out, algoritmo=args.alg, interactive=args.interactive,
            fonte_consumivel=args.fonte_consumivel, mostrar_armadilhas=args.armadilhas,
            arquivo_armadilhas=args.arquivo_armadilhas, lote=not bool(args.mapa),
        )
    if args.dataset and args.benchmark:
        # chamada do benchmark da Parte 2 (P4b)
        from src.benchmark import executar_benchmark
        executar_benchmark(args.dataset, args.out)
        print("Relatório gravado em", args.out)
        return 0
    if args.dataset and args.alg in ("BFS", "DFS"):
        # casos obrigatórios da Parte 2 (P4a): uma execução por fonte
        if not args.source:
            parser.error(f"--alg {args.alg} exige --source")
        from src.casos_parte2 import executar_busca
        try:
            caminho = executar_busca(args.alg, args.dataset, args.source, args.out)
        except ValueError as erro:
            parser.error(str(erro))
        print("Resultado gravado em", caminho)
        return 0
    if args.dataset and args.alg in ("DIJKSTRA", "BELLMAN_FORD"):
        # casos obrigatórios da Parte 2 (P4a): Dijkstra por par, Bellman-Ford por fonte
        if not args.source:
            parser.error(f"--alg {args.alg} exige --source")
        if args.alg == "DIJKSTRA" and not args.target:
            parser.error("--alg DIJKSTRA exige --target")
        from src.casos_parte2 import executar_bellman_ford, executar_dijkstra
        try:
            if args.alg == "DIJKSTRA":
                caminho = executar_dijkstra(args.dataset, args.source, args.target, args.out)
            else:
                caminho = executar_bellman_ford(args.dataset, args.source, args.out)
        except ValueError as erro:
            parser.error(str(erro))
        print("Resultado gravado em", caminho)
        return 0
    raise NotImplementedError("orquestração ainda não implementada (ver src/solve.py)")


if __name__ == "__main__":
    raise SystemExit(main())
