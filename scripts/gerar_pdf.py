"""Gera o PDF do relatório a partir de docs/relatorio/RELATORIO.md.

Uso (na raiz do repositório):
    python -m scripts.gerar_pdf
    python -m scripts.gerar_pdf --saida docs/relatorio/RELATORIO.pdf --html /tmp/relatorio.html

Converte o Markdown em HTML (com as figuras embutidas) e imprime em PDF com o Chrome ou o Edge
em modo headless. Avisa quando ainda há marcadores [A ESCREVER] ou [COMPLETAR] no texto.
Para usar outro navegador, defina a variável NAVEGADOR_PDF com o caminho do executável.
"""
# [IA] Claude Code – conversão Markdown -> HTML -> PDF (IO e formatação, sem conteúdo do relatório)
from __future__ import annotations

import argparse
import base64
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "docs" / "relatorio" / "RELATORIO.md"
SAIDA = RAIZ / "docs" / "relatorio" / "RELATORIO.pdf"
REPOSITORIO = "https://github.com/davimqz/Projetos-Grafos/blob/main/"

MARCADORES = re.compile(r"\[(A ESCREVER[^\]]*|COMPLETAR[^\]]*)\]")
IMAGEM = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")')
LINK = re.compile(r'(<a\b[^>]*?\bhref=")([^"]+)(")')

CANDIDATOS_NAVEGADOR = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge",
)

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm;
        @bottom-center { content: counter(page); font: 9pt 'Segoe UI', Arial, sans-serif; color: #666; } }
html { font: 10.5pt/1.5 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; color: #1a1a1a; }
body { margin: 0; }
h1 { font-size: 22pt; margin: 0 0 4pt; }
h2 { font-size: 15pt; margin: 22pt 0 8pt; padding-bottom: 3pt; border-bottom: 1.5pt solid #1a1a1a;
     break-before: page; }
h1 + p + p + p + hr + h2, .sem-quebra { break-before: auto; }
h3 { font-size: 12.5pt; margin: 16pt 0 6pt; }
h4 { font-size: 11pt; margin: 12pt 0 4pt; }
h5 { font-size: 10.5pt; margin: 10pt 0 4pt; font-style: italic; }
h2, h3, h4, h5 { break-after: avoid; }
p, li { orphans: 3; widows: 3; }
hr { border: 0; border-top: 0.5pt solid #bbb; margin: 14pt 0; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0 12pt; font-size: 9pt; break-inside: avoid; }
th, td { border: 0.5pt solid #999; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #eee; }
code { font: 8.8pt Consolas, 'Courier New', monospace; background: #f3f3f3; padding: 0 2pt; border-radius: 2pt;
       overflow-wrap: anywhere; }
pre { background: #f3f3f3; padding: 6pt 8pt; border-radius: 3pt; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; padding: 0; }
img { display: block; max-width: 100%; max-height: 200mm; margin: 8pt auto 2pt; break-inside: avoid; }
p:has(> img) { break-inside: avoid; text-align: center; }
blockquote { margin: 8pt 0; padding: 4pt 10pt; border-left: 3pt solid #c9a227; background: #fbf6e6; }
a { color: #1a4f8b; text-decoration: none; }
"""


def encontrar_navegador() -> str:
    candidatos = (os.environ.get("NAVEGADOR_PDF"),) + CANDIDATOS_NAVEGADOR
    for candidato in candidatos:
        if not candidato:
            continue
        if Path(candidato).is_file():
            return candidato
        if encontrado := shutil.which(candidato):
            return encontrado
    raise FileNotFoundError(
        "Chrome ou Edge não encontrado. Instale um deles ou defina NAVEGADOR_PDF com o caminho do executável."
    )


def listar_marcadores(texto: str) -> list[str]:
    """Marcadores [A ESCREVER ...] e [COMPLETAR ...] que ainda estão no texto."""
    return [m.group(1) for m in MARCADORES.finditer(texto)]


def _embutir_imagem(src: str, base: Path) -> str:
    if src.startswith(("data:", "http://", "https://")):
        return src
    arquivo = (base / src).resolve()
    if not arquivo.is_file():
        raise FileNotFoundError(f"Figura não encontrada: {src} (procurada em {arquivo})")
    tipo = mimetypes.guess_type(arquivo.name)[0] or "application/octet-stream"
    return f"data:{tipo};base64,{base64.b64encode(arquivo.read_bytes()).decode('ascii')}"


def _link_absoluto(href: str, base: Path) -> str:
    """Links relativos para arquivos do repositório viram links do GitHub (no PDF não há como abrir o arquivo)."""
    if href.startswith(("#", "http://", "https://", "mailto:")):
        return href
    caminho = (base / href.split("#")[0]).resolve()
    try:
        relativo = caminho.relative_to(RAIZ).as_posix()
    except ValueError:
        return href
    return REPOSITORIO + relativo


def markdown_para_html(texto: str, base: Path, titulo: str = "Relatório") -> str:
    """HTML completo, com figuras embutidas em base64 e links relativos apontando para o GitHub."""
    corpo = markdown.markdown(
        texto, extensions=["tables", "fenced_code", "sane_lists", "attr_list", "toc"], output_format="html",
    )
    corpo = IMAGEM.sub(lambda m: m.group(1) + _embutir_imagem(m.group(2), base) + m.group(3), corpo)
    corpo = LINK.sub(lambda m: m.group(1) + _link_absoluto(m.group(2), base) + m.group(3), corpo)
    return (
        "<!doctype html>\n<html lang=\"pt-BR\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{titulo}</title>\n<style>{CSS}</style>\n</head>\n<body>\n{corpo}\n</body>\n</html>\n"
    )


def imprimir_pdf(html: Path, pdf: Path, navegador: str | None = None) -> None:
    navegador = navegador or encontrar_navegador()
    pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run(
            [navegador, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
             f"--user-data-dir={perfil}", f"--print-to-pdf={pdf}", html.resolve().as_uri()],
            check=True, capture_output=True, timeout=180,
        )
    if not pdf.is_file() or pdf.stat().st_size == 0:
        raise RuntimeError(f"O navegador não gerou o PDF em {pdf}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--entrada", type=Path, default=ENTRADA, help="Markdown do relatório")
    parser.add_argument("--saida", type=Path, default=SAIDA, help="PDF gerado")
    parser.add_argument("--html", type=Path, help="também grava o HTML intermediário neste caminho")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # acentos no terminal do Windows

    texto = args.entrada.read_text(encoding="utf-8")
    pendentes = listar_marcadores(texto)
    html = markdown_para_html(texto, args.entrada.parent, titulo="Projeto Final — Teoria dos Grafos + AVD")

    with tempfile.TemporaryDirectory() as pasta:
        destino_html = args.html or Path(pasta) / "relatorio.html"
        destino_html.parent.mkdir(parents=True, exist_ok=True)
        destino_html.write_text(html, encoding="utf-8")
        imprimir_pdf(destino_html, args.saida)

    print(f"PDF gravado em {args.saida}")
    if pendentes:
        print(f"Atenção: {len(pendentes)} marcadores ainda no texto:")
        for marcador in pendentes:
            print(f"  - [{marcador}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
