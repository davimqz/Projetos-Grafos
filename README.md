# Projeto Final — Teoria dos Grafos + AVD (2026.2)

**Parte 1:** Labirinto com Chaves (grafo de estados) · **Parte 2:** dataset Elliptic++ (rede de transações Bitcoin)

> **👉 Acabou de clonar? Leia [`docs/PROXIMOS_PASSOS.md`](docs/PROXIMOS_PASSOS.md):** status atual, como preparar o ambiente
> e o passo a passo de cada integrante. **Agora é a vez do Thomaz (algoritmos).**

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
python -m src.cli --mapa ./data/mapas/m04_esteiras.txt --armadilhas --arquivo-armadilhas ./out/parte1/armadilhas_m04.json --interactive --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --interactive --out ./out/parte1/

# PARTE 2
python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source A --target Z --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/

# Testes
pytest
```

Para gerar as figuras P5a e o HTML com os mapas m02, m03 e m08:

```bash
python -m src.visualizar_parte1 --out ./out/parte1/
```

Os percursos m03 e m08 desse conjunto usam Dijkstra (menor custo). A árvore
do m02 usa BFS. O HTML mostra
que as armadilhas não foram fornecidas até que a análise do grupo esteja pronta.
Na CLI, `--mapa` gera o percurso do algoritmo escolhido (Dijkstra por padrão) e `--interactive`
gera `labirinto_<nome-do-mapa>.html`, preservando o HTML conjunto
`labirinto_interativo.html`; se o percurso não existir ou o algoritmo não se aplicar,
o motivo é exibido. Para mostrar armadilhas, `--arquivo-armadilhas` recebe um
JSON com uma lista de rótulos de estados calculados pelo grupo, por exemplo
`["(1,1)|-|{}"]`; o exemplo ilustra o formato e não declara que o estado é uma
armadilha. Com `--armadilhas`, a CLI também lista os estados no terminal. Os
resultados reais da análise ainda precisam ser produzidos pelo grupo. Quando o P3
estiver pronto, seu cálculo deverá ser integrado ao fluxo `--mapa` da CLI para
que `--armadilhas` não dependa de um arquivo previamente gerado.

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
│  ├─ solve.py            # orquestração da Parte 1 e interface pública
│  ├─ parte1/
│  │  ├─ modelos.py      # tipos compartilhados
│  │  ├─ carga.py        # preparo dos mapas
│  │  ├─ analises.py     # métricas, camadas, graus e armadilhas
│  │  ├─ buscas.py       # normalização das buscas e comparações
│  │  └─ exportacao.py   # escrita de CSV e JSON
│  ├─ viz.py
│  └─ graphs/
│     ├─ io.py            # ler/validar mapas e dataset
│     ├─ estados.py       # G_pos e G_est
│     ├─ graph.py         # lista de adjacência DIRIGIDA
│     └─ algorithms.py    # BFS, DFS, Dijkstra, Bellman-Ford (próprios)
└─ tests/
   ├─ test_solve.py       # compatibilidade da interface pública
   └─ parte1/            # testes por responsabilidade e integração
```

As funções e os tipos da Parte 1 continuam disponíveis por `src.solve`.
Suas implementações ficam em `src/parte1/`, com a lógica existente preservada.
Os algoritmos e a construção dos grafos permanecem em `src/graphs/`.

## Uso de IA

Todo trecho feito com apoio de IA é marcado no código com `# [IA] <ferramenta> – <finalidade>`
e registrado em [`docs/REGISTRO_IA.md`](docs/REGISTRO_IA.md). A declaração assinada fica em `docs/DECLARACAO_IA.pdf`.
