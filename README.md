# Projeto Final — Teoria dos Grafos + AVD (2026.2)

**Parte 1:** Labirinto com Chaves (grafo de estados) · **Parte 2:** dataset Elliptic++ (rede de transações Bitcoin)

## Equipe

| Integrante | Frente principal |
|---|---|
| Matheus | Parte 1 |
| Thomaz | Parte 1 |
| Davi | Parte 2 |
| Vagner | Parte 2 + AVD |

Divisão detalhada por pacote (dono/revisor) em [`docs/PLANO_DE_TRABALHO.md`](docs/PLANO_DE_TRABALHO.md).

## Instalação

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Como executar

```bash
# PARTE 1
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg BFS --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg DIJKSTRA --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m05_bonus.txt --alg BELLMAN_FORD --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m04_esteiras.txt --armadilhas --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --interactive --out ./out/parte1/

# PARTE 2
python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source A --target Z --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/

# Testes
pytest
```

## Estrutura

```
.
├─ README.md
├─ requirements.txt
├─ docs/                  # DECLARACAO_IA.pdf, plano de trabalho, registro de IA, PDF técnico
├─ data/
│  ├─ mapas/              # mapas fornecidos (m01 a m08)
│  ├─ mapas_grupo/        # 2 mapas criados pelo grupo
│  └─ dataset_parte2/     # recorte do Elliptic++ (bruto em raw/, fora do git)
├─ notebooks/avd/         # exploração de dados (AVD)
├─ scripts/               # download e amostragem do dataset
├─ out/
│  ├─ parte1/
│  └─ parte2/
├─ src/
│  ├─ cli.py
│  ├─ solve.py
│  ├─ viz.py
│  └─ graphs/
│     ├─ io.py            # ler/validar mapas e dataset
│     ├─ estados.py       # G_pos e G_est
│     ├─ graph.py         # lista de adjacência DIRIGIDA
│     └─ algorithms.py    # BFS, DFS, Dijkstra, Bellman-Ford (próprios)
└─ tests/
```

## Uso de IA

Todo trecho feito com apoio de IA é marcado no código com `# [IA] <ferramenta> – <finalidade>`
e registrado em [`docs/REGISTRO_IA.md`](docs/REGISTRO_IA.md). A declaração assinada fica em `docs/DECLARACAO_IA.pdf`.
