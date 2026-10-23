# Próximos passos (atualizado em 23/10/2026)

## Status

| Frente | Situação |
|---|---|
| Estrutura do repositório, mapas, README | ✅ pronto |
| Dataset da Parte 2 (recorte, pesos, documentação) | ✅ pronto, em `data/dataset_parte2/` |
| **Algoritmos (`graph.py`, `algorithms.py`)** | ⏳ **vez do Thomaz**: bloqueia a Parte 2 e as análises da Parte 1 |
| Grafo de estados (`io.py`, `estados.py`) | ⏳ Matheus, em paralelo com o Thomaz |
| Exploração dos dados (AVD) | ⏳ Vagner, pode começar já |

> ⚠️ **Regra da professora:** `io.py`, `estados.py`, `graph.py` e `algorithms.py` **não podem ser gerados por IA**.
> IA só para tirar dúvida conceitual ou entender erro, sempre registrando em `docs/REGISTRO_IA.md`.

## Para todos: preparar o ambiente

```bash
git clone https://github.com/davimqz/Projetos-Grafos.git
cd Projetos-Grafos
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest          # deve rodar (ainda sem testes)
```

O recorte da Parte 2 já está no repositório; **não precisa baixar o dataset** (só se for refazer o recorte).

## Fluxo de trabalho

1. Crie uma branch por tarefa: `git checkout -b feat/p2-bfs`.
2. Commits no padrão `tipo(escopo): descrição` (ex.: `feat(algorithms): implementa BFS com níveis`, `test(bfs): ...`).
3. Abra um Pull Request para `main` e marque o **revisor do pacote** (ver `PLANO_DE_TRABALHO.md`).
4. O revisor aprova e faz o merge. Isso conta como contribuição dos dois.

---

## Thomaz — P2: Algoritmos (revisor: Davi)

Os algoritmos são usados nas **duas partes**, então são a prioridade. Faça nesta ordem, um PR por item:

**1. `src/graphs/graph.py`: grafo dirigido ponderado (lista de adjacência)**
- [ ] adicionar nó e arco `(u, v, peso)`, **preservando a ordem de inserção** dos vizinhos (a Parte 1 depende da ordem N, L, S, O)
- [ ] listar vizinhos de um nó com os pesos
- [ ] ordem |V|, tamanho |E|, densidade `|E| / (|V|(|V|-1))` (0 se |V| < 2), grau de entrada e de saída
- [ ] grafo transposto (inverte todos os arcos)
- [ ] subgrafo induzido por um conjunto de nós
- [ ] combinar com o Matheus e com o Davi o formato dos nós: rótulo de estado (string) na Parte 1 e endereço da carteira na Parte 2

**2. `src/graphs/algorithms.py` + testes, um algoritmo por vez**

| Algoritmo | Precisa devolver | Teste (`tests/`) |
|---|---|---|
| BFS | distância em passos, pai de cada nó, nível de cada nó | níveis corretos em grafo pequeno |
| DFS | contagem e lista de arcos de **árvore, retorno, avanço e cruzamento**; se há ciclo | grafo dirigido pequeno com os 4 tipos de arco |
| Dijkstra (`heapq`) | distância e pai; **erro com mensagem clara** se houver arco negativo | caminho certo com pesos ≥ 0; recusa com peso negativo |
| Bellman-Ford | distância e pai; se houver ciclo negativo: flag + **lista dos nós do ciclo** e custo | (i) negativo sem ciclo → distâncias certas; (ii) com ciclo → flag e ciclo |

- [ ] nos testes, use `networkx` **só como oráculo** para conferir os resultados (permitido apenas em `tests/`)
- [ ] `pytest` passando antes de abrir cada PR

**3. Primeiro teste real (avise o Davi do resultado)**
- [ ] carregar `data/dataset_parte2/arestas.csv` (colunas `origem, destino, peso`) e rodar o Bellman-Ford
- [ ] o recorte tem ciclo negativo? Se sim, quantos nós tem e qual o custo?

**Depois:** P5a (figuras da Parte 1 e HTML interativo), quando o Matheus tiver o G_est.

## Matheus — P1 + P3: Grafo de estados (revisor: Thomaz)

- [ ] **desenhar à mão o G_est do m02** (a professora recomenda; vai para o PDF)
- [ ] `io.py`: ler o mapa, ignorar linhas `;`, validar (retangular, 1 S, ≥1 G, símbolos conhecidos) + `tests/test_io.py`
- [ ] `estados.py`: G_pos e depois G_est por exploração a partir de S, rótulos `(l,c)|chaves|{bônus}`, nó `ALVO`
- [ ] conferir o G_est do m02 com o desenho à mão; depois m01–m08
- [ ] `tests/test_estados.py` com um mapa mínimo (≤ 5×7) contado à mão
- [ ] exportar `out/parte1/arestas_<mapa>.csv`

## Vagner — P5b: AVD (revisor: Davi)

- [ ] explorar `data/dataset_parte2/nos.csv` e `arestas.csv` em `notebooks/avd/`
- [ ] 4 pilares: estrutural, distribucional, relacional, outliers
- [ ] faltantes: a classe "desconhecido" (33% do recorte) é ausência de rótulo; discutir o mecanismo, **não apagar**
- [ ] relação da classe (ilícito/lícito/desconhecido) com **todos** os outros atributos
- [ ] lembrete: a interpretação dos gráficos e a escolha do tipo de gráfico **não podem ser feitas por IA**

## Davi — P4a + P5c

- [ ] revisar os PRs do Thomaz
- [ ] função de carga do recorte (`arestas.csv` → grafo) para a Parte 2
- [ ] quando os algoritmos estiverem prontos: BFS/DFS de 3 fontes, Dijkstra em 5 pares, Bellman-Ford com e sem ciclo negativo
