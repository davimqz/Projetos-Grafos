"""Registro de arquivos concluídos e falhas independentes de exportação."""

# [IA] Codex - acompanhamento das exportações para o resumo final da CLI.
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RegistroSaidas:
    arquivos: list[Path] = field(default_factory=list)
    erros: list[str] = field(default_factory=list)

    def gravar(self, exportador, *args, **kwargs):
        """O último argumento posicional é o arquivo solicitado ao exportador."""
        destino = Path(args[-1])
        try:
            exportador(*args, **kwargs)
        except (OSError, ValueError) as erro:
            self.erros.append(f"{destino}: {erro}")
        else:
            self.arquivos.append(destino)
