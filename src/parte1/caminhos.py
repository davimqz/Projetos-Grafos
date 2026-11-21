"""Localização das saídas da Parte 1 por tipo de arquivo."""

# [IA] Codex - organização dos caminhos usados pelos geradores e consumidores.
from pathlib import Path


PASTAS = {".csv": "csv", ".json": "json", ".html": "html", ".png": "figuras", ".svg": "figuras"}


def caminho_saida(raiz: str | Path, arquivo: str | Path) -> Path:
    """Recebe a pasta da execução e o nome do arquivo, sem criar diretórios."""
    arquivo = Path(arquivo)
    try:
        pasta = PASTAS[arquivo.suffix.lower()]
    except KeyError:
        raise ValueError(f"Tipo de saída não reconhecido: {arquivo.suffix}") from None
    return Path(raiz) / pasta / arquivo.name
