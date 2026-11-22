"""Gera o HTML de um mapa solicitado pela interface local."""
# [IA] Codex – integra a interface ao gerador HTML existente.
# [IA] Codex - geração dos arquivos na subpasta html da saída solicitada.
import argparse
from pathlib import Path

from src.parte1.caminhos import caminho_saida
from src.visualizar_parte1 import preparar_mapa
from src.viz import gerar_html_interativo

RAIZ = Path(__file__).resolve().parents[1]
ALGORITMOS = ("BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD")


def gerar_html(mapa: str, algoritmo: str, saida: Path | None = None) -> Path:
    if algoritmo not in ALGORITMOS or not mapa or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in mapa):
        raise ValueError("Mapa ou algoritmo inválido")
    arquivos = [p for pasta in ("mapas", "mapas_grupo")
                for p in (RAIZ / "data" / pasta).glob("*.txt") if p.stem == mapa]
    if len(arquivos) != 1:
        raise ValueError("Mapa não encontrado ou ambíguo")
    dados, _, _, _ = preparar_mapa(arquivos[0], (algoritmo,))
    destino = caminho_saida(saida if saida is not None else RAIZ / "out" / "parte1", f"labirinto_{mapa}.html")
    return gerar_html_interativo({mapa: dados}, destino)


def gerar_html_conjunto(saida: Path | None = None) -> Path:
    arquivos = [arquivo for pasta in ("mapas", "mapas_grupo")
                for arquivo in sorted((RAIZ / "data" / pasta).glob("*.txt"))]
    if len({arquivo.stem for arquivo in arquivos}) != len(arquivos):
        raise ValueError("Há mapas com o mesmo nome nas pastas de entrada")
    mapas = {arquivo.stem: preparar_mapa(arquivo, ALGORITMOS)[0] for arquivo in arquivos}
    destino = caminho_saida(saida if saida is not None else RAIZ / "out" / "parte1", "labirinto_interativo.html")
    return gerar_html_interativo(mapas, destino)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mapa")
    parser.add_argument("algoritmo", choices=ALGORITMOS)
    args = parser.parse_args()
    print(gerar_html_conjunto() if args.mapa == "conjunto" else gerar_html(args.mapa, args.algoritmo))
