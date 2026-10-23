# Registro de uso de IA

Exigido pelo enunciado: todo uso de IA é declarado aqui e na `DECLARACAO_IA.pdf`. Os trechos de código ficam marcados com `# [IA] <ferramenta> – <finalidade>`.

| Data | Integrante | Ferramenta | Finalidade | Arquivos afetados | Categoria |
|---|---|---|---|---|---|
| 23/10/2026 | Davi | Claude Code | Estruturar o repositório: pastas, `.gitkeep`, `.gitignore`, `README`, `requirements`, docstrings de escopo dos módulos e argparse da CLI. Nenhum algoritmo nem construção de grafo foi gerado | estrutura, `src/cli.py`, `README.md`, `requirements.txt` | Permitido (organização/IO) |
| 23/10/2026 | Davi | Claude Code | Montar o plano de trabalho por pacote e levantar o que falta no dataset Elliptic++ em relação ao enunciado (lacunas e decisões em aberto; as escolhas ficam com o grupo) | `docs/PLANO_DE_TRABALHO.md`, `docs/PARTE2_DATASET.md` | Permitido (dúvidas conceituais) |
| 23/10/2026 | Davi | Claude Code | Script de download do dataset (IO) e contagens de conferência do grafo completo (laços, duplicatas, linhas por endereço) | `scripts/baixar_dataset.py`, `docs/PARTE2_DATASET.md` | Permitido (IO/pandas) |
| 23/10/2026 | Davi | Claude Code | Conferência de sinal, faltantes e origem das arestas a partir do valor das transações | `docs/PARTE2_DATASET.md`, `scripts/baixar_dataset.py` | Permitido (IO/pandas) |
| 23/10/2026 | Davi | Claude Code | Script de limpeza, agregação e recorte em bola de neve do dataset (pandas); decisões de peso, laços, duplicatas e sementes escolhidas pelo grupo a partir das opções apresentadas | `scripts/amostrar_dataset.py`, `data/dataset_parte2/*`, `docs/PARTE2_DATASET.md` | Permitido (IO/pandas) — ver nota: a escolha do peso foi recomendada pela IA e aceita pelo grupo |
| 23/10/2026 | Davi | Claude Code | Revisão de clareza/precisão de texto escrito pelo grupo (3 ajustes pontuais de redação) | `docs/relatorio/parte2.md` | Permitido (revisão de texto) |
