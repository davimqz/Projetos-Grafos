"""Valida e calcula um mapa enviado pelo front, sem gravá-lo no projeto."""
# [IA] Codex – adaptação dos resultados existentes para o carregamento no front.
import json
import sys
import tempfile
from pathlib import Path

from src.graphs.io import ler_mapa
from src.visualizar_parte1 import preparar_mapa


def main():
    texto = sys.stdin.read(16385)
    if len(texto) > 16384:
        raise ValueError("O arquivo deve ter no máximo 16 KiB.")
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "mapa.txt"
        arquivo.write_text(texto, encoding="utf-8")
        grade = ler_mapa(arquivo)
        if len(grade) * len(grade[0]) > 2500 or sum(linha.count('+') for linha in grade) > 8:
            raise ValueError("O mapa deve ter no máximo 2.500 casas e 8 bônus.")
        dados, grafo, _, _ = preparar_mapa(arquivo, ("BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD"))
        print(json.dumps({"grade": dados["grade"], "percursos": dados["algoritmos"],
                          "custos": dados["custos"], "status": dados["status"],
                          "n_estados": len([no for no in grafo.nos() if no != "ALVO"]),
                          "n_arcos": grafo.tamanho()}, ensure_ascii=False))


# [IA] Claude Code – erro inesperado vira mensagem curta, sem traceback na tela.
def cli():
    try:
        main()
    except (ValueError, UnicodeError) as erro:
        print(str(erro), file=sys.stderr)
        sys.exit(2)
    except Exception as erro:  # noqa: BLE001
        print(f"Erro interno ao processar o mapa ({type(erro).__name__}).", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
