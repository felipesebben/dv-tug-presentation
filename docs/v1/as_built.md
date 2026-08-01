# Dashboard V1 — como foi construído de fato (*as-built*)

`docs/v1/spec.md` é o documento de **projeto**: o que a V1 deveria ser, com o
raciocínio de cada pecado e as referências ao deck. Este documento aqui é o registro do
que **efetivamente existe** em `tableau/dashboard_v1.twb`.

Onde os dois divergem, **este documento vale para a V1 construída** e a especificação vale
como intenção de projeto. A especificação não foi reescrita porque o raciocínio dela é o
material que a dupla de UX usa no redesign — o valor dela é a argumentação, não o
inventário.

Verificado por leitura do XML do workbook (não por inspeção visual), em 2026-07-28.

---

## 1. Resumo das divergências

| # | Item | Especificação | Construído | Por quê |
|---|---|---|---|---|
| 1 | Eixo Y da série temporal (H) | fixado em 0,26–0,34 | **automático** | decisão de escopo — não será alterado |
| 2 | Série temporal (H) | eixo único, `AVG(taxa_ocupacao)` | **eixo duplo sincronizado** | melhoria em relação à spec (ver §3) |
| 3 | Escopo dos 11 filtros | cada bloco controla só as planilhas da coluna "controla" (§6·I) | escopo aproximado, 3 filtros globais | ver §2 |
| 4 | Nº de planilhas | 22 | **21** | contagem anterior estava errada |
| 5 | Captura dos artefatos "antes" (§9) | prints, cronometragem, gravação | **removido do escopo** | apresentação é responsabilidade da dupla de UX |

Nenhuma dessas divergências afeta a **corretude dos cálculos**. As medidas foram
conferidas contra `docs/foundations/metrics_dictionary.md` e batem.

---

## 2. Escopo real dos filtros

O escopo foi aplicado pela interface do Tableau (não por edição de XML — ver
`tableau/README.md`). O resultado é **aproximado** em relação à tabela da seção 6·I da
especificação, e isso foi aceito: o pecado de proximidade continua demonstrável.

**Globais** (*todas as planilhas que usam a fonte*):

| filtro | especificação dizia | observação |
|---|---|---|
| `Ano` | tudo (global) | ✅ conforme |
| `Caráter da internação` | idade F1 + dispersão G | global |
| `Hospital` (`id_estabelecimento_cnes`) | tabelão C, mapas E, barras F2 | global |

**Com escopo por planilha:**

| filtro | planilhas que controla | nº |
|---|---|---|
| `Município` | Line·Occupancy, Map·Avg Occupancy, Map·Total Hospitalization, Table·Occupancy Rates per ID, VBar·Occupancy by Municipality | 5 |
| `Tipo de leito` | Pie·Bed Types + sua legenda | 2 |
| `Especialidade` | Pie·Bed Types + sua legenda | 2 |
| `Complexidade` | Scatter·AIH vs N Days, VBar·Age Distribution | 2 |
| `Motivo de saída` | Scatter·AIH vs N Days, Table·Occupancy Rates per ID | 2 |
| `Faixa de valor` (`valor_aih`) | Scatter·AIH vs N Days, Table·Occupancy Rates per ID | 2 |
| `Sexo` | Pie·Sex | 1 |
| `Raça/cor` | Pie·Ethnicity | 1 |

**Efeito no pecado de proximidade (placar nº 1):** continua válido — 8 dos 11 filtros estão
longe, especificamente, do que controlam. Ele fica **enfraquecido** nos dois filtros globais
(`Caráter`, `Hospital`): sobre eles não dá pra dizer "este filtro controla aquilo lá em
cima", porque controlam tudo. Ao vivo, use `Município`, `Tipo de leito` ou `Sexo` para
demonstrar — esses três têm alvo único e distante.

### Problema conhecido: legendas de pizza fora do escopo

`Pie | Sex | Legend` e `Pie | Ethnicity | Legend` **não recebem** os filtros `Sexo` e
`Raça/cor`, enquanto as pizzas correspondentes recebem. `Pie | Bed Types | Legend` recebe
os dois filtros dela, corretamente.

Consequência: ao aplicar `Sexo` ou `Raça/cor`, a pizza recalcula e a legenda ao lado não —
os percentuais das duas passam a discordar. **Isto não é um pecado de design da V1**: não
está no placar, não ilustra princípio nenhum, e é o tipo de inconsistência que alguém da
plateia percebe e reporta como erro. Corrigir aplicando os dois filtros às planilhas de
legenda (interface do Tableau, "Aplicar a planilhas selecionadas").

---

## 3. Série temporal (região H)

**Cálculos conferidos e corretos:**

- `AVG(taxa_ocupacao)`, não `SUM` — respeita a regra de ouro do
  `docs/foundations/metrics_dictionary.md` (com `SUM` a taxa daria 4.928).
- Média **das médias**, não ponderada por leito: 30,8% em vez de 43,1%. É intencional e está
  documentado no `docs/foundations/metrics_dictionary.md` §4.
- Fórmula de origem: `total_dias_permanencia / (leitos_total × dias_do_mês)`
  (`src/transform/transformers.py:152`), com dias reais do mês via `day(last_day(...))`.
- Eixo X: `ano_mes` truncado por mês, contínuo — 60 meses.

**Eixo duplo (não estava na especificação).** As Linhas são
`AVG(taxa_ocupacao) + AVG(taxa_ocupacao)`, com:

- painel 1 — detalhe por `id_estabelecimento_cnes`, linha fina, transparência 157 → o
  espaguete de 287 hospitais;
- painel 2 — sem detalhe, linha grossa `#0f3460` → a média estadual por cima.

Os dois eixos estão **sincronizados** (`synchronized='true'`) e o cabeçalho do eixo
secundário está oculto, então as duas séries compartilham a mesma escala — não há distorção.
Isto está mais próximo da intenção do wireframe (a linha de média existe, mas sem prioridade
visual sobre o espaguete) do que o texto da especificação.

**Eixo Y automático.** O eixo fixado em 0,26–0,34 **não foi implementado**. Consequência
direta no placar de pecados:

- **item 32 — "Eixo truncado" [p.103]: não realizado na V1.** É o único item que esta
  revisão identificou como não construído — mas a revisão cobriu a série temporal e os
  filtros, não os 46 itens um a um. Antes do workshop, vale uma passada de conferência do
  placar inteiro contra o workbook.
- Os demais pecados da região H continuam válidos: conteúdo mais importante abaixo da dobra
  [p.90], destino comum mal usado com 287 linhas [p.31], ausência de anotação da pandemia
  [p.59], livro embaralhado [p.84].

A especificação chama o eixo truncado de "a mentira central da V1" (seções 5·H e 6·H).
Com o eixo automático, essa frase descreve a intenção de projeto, não o artefato. A série
real varia de 23,13% (maio/2020) a 35,40% (nov/2023) e agora aparece inteira.

---

## 4. Inventário construído

- **21 planilhas** (a especificação e o `README.md` diziam 22), num único dashboard fixo de
  1200×2600 px.
- 8 KPIs · 1 série temporal · 2 mapas · 3 pizzas (+3 legendas) · 1 dispersão · 1 tabelão ·
  2 barras.
- Uma fonte de dados única (`sih_cnes_rs.hyper`), três tabelas ligadas por **Relationships**
  — ver `tableau/README.md`.
- `include-phone-layouts='false'` — nada se reorganiza ao reduzir a janela. Não há item de
  placar cobrindo isso; fica registrado aqui como característica do artefato.

---

## 5. Fora de escopo

A **seção 9 da especificação** (registrar o "antes": prints, tempo de carga, gravação de
teste de usabilidade) foi **retirada do escopo deste repositório**. A divisão de trabalho é:
este repositório constrói e documenta os dashboards; a dupla de UX cuida da apresentação e
dos materiais dela. A pasta `docs/assets/v1/` nunca foi criada e não é mais esperada.
