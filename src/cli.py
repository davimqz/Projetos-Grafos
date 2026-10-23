"""Ponto de entrada: python -m src.cli ...

Exemplos (do enunciado):
    python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg BFS --out ./out/parte1/
    python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/
    python -m src.cli --mapa ./data/mapas/m04_esteiras.txt --armadilhas --out ./out/parte1/
    python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source A --target Z --out ./out/parte2/
    python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/
"""
# [IA] Claude Code – esqueleto do argparse com as flags do enunciado
import argparse

ALGORITMOS = ["BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD"]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="src.cli", description="Projeto Final de Grafos 2026.2")
    entrada = p.add_mutually_exclusive_group(required=True)
    entrada.add_argument("--mapa", help="arquivo .txt do labirinto (Parte 1)")
    entrada.add_argument("--dataset", help="pasta do dataset da Parte 2")
    p.add_argument("--alg", choices=ALGORITMOS, help="algoritmo a executar")
    p.add_argument("--out", required=True, help="pasta de saída")
    p.add_argument("--fonte-consumivel", action="store_true", help="'*' vale -2 só na primeira vez")
    p.add_argument("--armadilhas", action="store_true", help="lista estados-armadilha")
    p.add_argument("--interactive", action="store_true", help="gera o labirinto interativo")
    p.add_argument("--source", help="nó de origem (Parte 2)")
    p.add_argument("--target", help="nó de destino (Parte 2)")
    p.add_argument("--benchmark", action="store_true", help="tempos e escalabilidade (Parte 2)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raise NotImplementedError("orquestração ainda não implementada (ver src/solve.py)")


if __name__ == "__main__":
    raise SystemExit(main())
