# [IA] Claude Code – testes da conversão do relatório para PDF
import base64

import pytest

from scripts import gerar_pdf
from scripts.gerar_pdf import RAIZ, REPOSITORIO, listar_marcadores, markdown_para_html

PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def test_lista_marcadores_pendentes():
    texto = "> **[A ESCREVER — Matheus]** prova\n\n[COMPLETAR] contagem\n\n[link](x.md) e [outro texto]"
    assert listar_marcadores(texto) == ["A ESCREVER — Matheus", "COMPLETAR"]


def test_sem_marcadores():
    assert listar_marcadores("# Relatório\n\nTudo escrito.") == []


def test_embute_figura_relativa_em_base64(tmp_path):
    (tmp_path / "fig.png").write_bytes(PNG_1X1)
    html = markdown_para_html("![Figura](fig.png)", tmp_path)
    assert 'src="data:image/png;base64,' in html
    assert "fig.png\"" not in html


def test_figura_ausente_gera_erro_claro(tmp_path):
    with pytest.raises(FileNotFoundError, match="Figura não encontrada: nada.png"):
        markdown_para_html("![x](nada.png)", tmp_path)


def test_link_relativo_do_repositorio_vira_link_do_github():
    base = RAIZ / "docs" / "relatorio"
    html = markdown_para_html("[registro](../REGISTRO_IA.md) [site](https://exemplo.com) [ancora](#sec)", base)
    assert f'href="{REPOSITORIO}docs/REGISTRO_IA.md"' in html
    assert 'href="https://exemplo.com"' in html
    assert 'href="#sec"' in html


def test_tabela_e_codigo_viram_html():
    html = markdown_para_html("| a | b |\n|---|---|\n| 1 | 2 |\n\n```\npytest\n```", RAIZ)
    assert "<table>" in html and "<td>1</td>" in html
    assert "<pre><code>pytest" in html
    assert '<meta charset="utf-8">' in html


def test_navegador_ausente_gera_erro_claro(monkeypatch):
    monkeypatch.setattr(gerar_pdf, "CANDIDATOS_NAVEGADOR", ("nao-existe-123",))
    monkeypatch.delenv("NAVEGADOR_PDF", raising=False)
    with pytest.raises(FileNotFoundError, match="NAVEGADOR_PDF"):
        gerar_pdf.encontrar_navegador()
