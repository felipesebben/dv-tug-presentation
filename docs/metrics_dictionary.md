# Dicionário de métricas — o que cada número do dashboard realmente mede

> **Por que este documento existe.** Todo número que aparece no V1 foi conferido contra
> `data/refined/*.parquet`. Este arquivo registra a **definição exata** (SQL), o **grão**
> e a **armadilha** de cada um. Duas coisas dependem disso: (1) não errar a lógica ao
> montar as planilhas no Tableau; (2) ter na mão, na hora da apresentação, a resposta pra
> "mas esse número quer dizer o quê?" — que é exatamente a pergunta que o V1 torna
> impossível de responder.
>
> **Ele também é um artefato da apresentação.** O V1 **não tem** dicionário de métricas,
> nota de fonte nem data de atualização (região J, pecado de Nielsen — visibilidade do
> sistema). O V2 deveria ter. Este arquivo é o rascunho do que deveria estar lá.

Todos os valores abaixo: **RS, 2019–2023**, tabelas em `data/refined/`.

---

## 1. A resposta curta pro "107,9 leitos"

**107,9 não é o número de leitos do RS.** É a **média de leitos por hospital por mês**.

```sql
SELECT AVG(leitos_total) FROM occupancy;   -- 107,947668
```

A tabela `occupancy` tem **um registro por hospital por mês** — 15.994 linhas
(287 hospitais × 60 meses, menos as combinações sem movimento). Tirar `AVG` disso
responde "quantos leitos tem um hospital típico do RS num mês típico?".

O número que qualquer pessoa **assume** ao ler um tile escrito `107,9 / LEITOS` num
cabeçalho estadual é o total de leitos do RS. Esse é:

| O que a pessoa lê | O que ela entende | O que o número é | Fator de erro |
|---|---|---|---|
| `107,9` · **LEITOS** | "o RS tem ~108 leitos?!" | média de leitos **por hospital/mês** | — |
| — | leitos instalados no RS | **≈ 28.775 por mês** (267 hospitais ativos/mês) | **267×** |

E a média por hospital é, além de tudo, uma média ruim:

| estatística de `leitos_total` | valor |
|---|---|
| média | 107,9 |
| **mediana** | **62** |
| mínimo | 3 |
| máximo | 1.127 |

A distribuição é fortemente assimétrica (poucos hospitais grandes puxam a média).
A mediana — 62 — descreve muito melhor "o hospital típico". A média está 74% acima dela.

> **Três pecados num tile só**: rótulo ambíguo (`LEITOS` não diz "por hospital/mês"),
> agregação errada pro formato (média onde cabia mediana, ou soma onde cabia total),
> e uma unidade que não existe no mundo — "107,9 leitos" não é um objeto físico.
> É o exemplo mais limpo de **contexto ausente** [p.59] do painel inteiro, e ele
> passa despercebido porque o número *parece* preciso.

---

## 2. Os 8 KPIs da faixa B, um a um

Grão de cada tabela:
- `occupancy` — **1 linha por hospital × mês** (15.994 linhas)
- `hospitalizacoes` — **1 linha por internação (AIH)** (3.739.506 linhas)
- `leitos` — 1 linha por hospital × mês × tipo de leito

| # | Tile no V1 | Valor | Definição exata | Grão / armadilha |
|---|---|---|---|---|
| 1 | `30,8%` **TAXA** | 30,82% | `AVG(taxa_ocupacao)` em `occupancy` | Média **das médias** — cada hospital pesa igual, um de 3 leitos pesa o mesmo que um de 1.127. Ver §4. |
| 2 | `3739506` Internações | 3.739.506 | `COUNT(*)` em `hospitalizacoes` | AIHs, não pacientes. Uma pessoa internada 3× conta 3. |
| 3 | `22616421` dias de permanência | 22.616.421 | `SUM(quantidade_dias_permanencia)` | Soma de diárias. É o numerador da taxa de ocupação. |
| 4 | `107,9` **LEITOS** | 107,947668 | `AVG(leitos_total)` em `occupancy` | **Média por hospital/mês.** Ver §1. |
| 5 | `6545187195,36` Valor AIH | R$ 6.545.187.195,36 | `SUM(valor_aih)` | Reais nominais, **sem correção pela inflação** — somar 2019 com 2023 direto. |
| 6 | `0,0605` taxa de óbito | 6,0477% | `SUM(indicador_obito)/COUNT(*)` | Exibido como `0,0605` (fração), rotulado "taxa". Ver §5. |
| 7 | `228` Municípios | 228 | `COUNT(DISTINCT nome_municipio)` | Municípios **com hospital**, não os 497 do RS. |
| 8 | `287` HOSPITAIS | 287 | `COUNT(DISTINCT id_estabelecimento_cnes)` | Estabelecimentos com internação **e** leito cadastrado no período. |

### A colisão do 6,05 é real

| medida | valor exato |
|---|---|
| permanência média | **6,048 dias** |
| taxa de óbito | **6,0477 %** |

As duas arredondam pra `6,05`. Lado a lado sem unidade explícita, é impossível saber qual
é qual — o argumento de **contexto** [p.59] servido de graça, e não foi fabricado.

---

## 3. Métricas por gráfico (regiões C–J)

> ### ⚠️ Antes de começar: o wireframe **não** é totalmente alimentado pela nossa base
>
> `dashboard_v1_wireframe.html` é um mockup visual. Ele mistura dois tipos de número, e o
> próprio arquivo avisa isso no parágrafo de introdução:
>
> | no wireframe | procedência |
> |---|---|
> | Os 8 KPIs, divisão por sexo, médias anuais de ocupação, Porto Alegre (848.764), cauda etária 97–99, `NULL` de especialidade (41.796) | **reais**, conferidos contra a base |
> | Células mês a mês do tabelão, nomes das ~50 especialidades de cauda longa, pontos da dispersão, valores do mapa esquemático | **sintéticos** (PRNG determinístico), só pra dar volume visual |
>
> **Não use o wireframe como fonte de verdade pra construir as planilhas.** Ele foi feito
> pra *parecer* um export, não pra bater número a número. Esta seção é a fonte de verdade:
> os valores abaixo saem de `data/refined/*.parquet`. Se o Tableau divergir do wireframe,
> **o Tableau está certo**.

### Validações globais (rodadas agora, valem pra todas as planilhas)

| checagem | resultado |
|---|---|
| O `INNER JOIN` de `occupancy` descarta internações? | **Não.** `SUM(total_internacoes)` = 3.739.506 = `COUNT(*)` de `hospitalizacoes`. Diferença zero. |
| `leitos` e `occupancy` dão o mesmo total de leitos? | **Não, e é esperado.** `leitos` → 33.967,7 leitos/mês (todos os hospitais do CNES). `occupancy` → 28.775/mês (só hospitais **com internação no mês**). Populações diferentes. |

> **Regra de ouro no Tableau: nunca deixe `taxa_ocupacao` como `SUM`.** É uma razão já
> calculada por hospital/mês. O Tableau vai default pra `SUM` ao arrastar, e `SUM` de uma
> taxa não significa nada (dá 4.928 na visão estadual). Troque pra `AVG` — ou, melhor,
> reconstrua como `SUM(dias) / SUM(leitos × dias_do_mês)` para ter a versão ponderada (§4).

---

### C — Tabelão

| | |
|---|---|
| **Fonte** | `occupancy` |
| **Linhas** | `nome_municipio` + `id_estabelecimento_cnes` → **287 linhas** (uma por hospital), em **228 municípios** |
| **Colunas** | `ano_mes` contínuo → **60 meses** |
| **Medidas (6)** | `AVG(taxa_ocupacao)`, `SUM(total_internacoes)`, `SUM(total_dias_permanencia)`, `SUM(leitos_total)`, `SUM(leitos_sus)`, `AVG(taxa_ocupacao)` de novo |

Volume de células: **287 × 60 × 6 ≈ 103.320**. (O spec cita "228 × 60 × 6 ≈ 82 mil",
contando municípios; contando hospitais — que é o grão real das linhas — são ~103 mil.
Qualquer um dos dois serve pro argumento; é ruído, não informação.)

> **Armadilha:** a 1ª e a 6ª medida são a mesma coisa. Isso é proposital no V1 (redundância
> que ninguém percebe), mas no V2 é erro. E se a 1ª entrar como `SUM(taxa_ocupacao)`, o
> tabelão exibe números como `4,8213` numa coluna rotulada "taxa" — sem sentido.

---

### D1 — Pizza de especialidade de leito

| | |
|---|---|
| **Fonte** | `leitos` |
| **Cor** | `tipo_especialidade_leito_desc` |
| **Ângulo** | `SUM(quantidade_total)` |

| fato | valor real |
|---|---|
| categorias não nulas | **57** |
| fatias no total (com `NULL`) | **58** |
| fatias abaixo de 1% | **40** |
| leitos-mês em `NULL` | **41.796** |
| soma bruta `SUM(quantidade_total)` | **2.038.062** |

Top 8 reais (use estes, não os nomes sintéticos do wireframe):

| especialidade | leitos-mês | % |
|---|---|---|
| clinica geral | 615.911 | 30,2204% |
| cirurgia geral | 211.279 | 10,3667% |
| psiquiatria | 203.133 | 9,9670% |
| pediatria clinica | 146.097 | 7,1684% |
| obstetricia cirurgica | 89.334 | 4,3833% |
| obstetricia clinica | 71.710 | 3,5185% |
| uti adulto - tipo ii | 66.239 | 3,2501% |
| ortopediatraumatologia | 62.420 | 3,0627% |

> **Armadilha séria — "leito-mês" não é "leito".** `SUM(quantidade_total)` sobre a tabela
> inteira soma o mesmo leito **60 vezes** (uma por mês). Os 2.038.062 não são leitos; são
> leitos-mês. Dividido por 60 → **33.967,7 leitos/mês**, que é o número com significado
> físico. Como **proporção** a pizza continua válida (o fator 60 cancela), mas qualquer
> rótulo de valor absoluto está inflado 60×. Se for mostrar total, filtre um mês.

---

### D2 — Rosca de sexo

| | |
|---|---|
| **Fonte** | `hospitalizacoes` · **Ângulo** `COUNT(*)` · **Cor** `sexo_paciente` |

| sexo | internações | % |
|---|---|---|
| Feminino | 2.065.368 | **55,2310%** |
| Masculino | 1.674.138 | **44,7690%** |

> **Correção:** `dashboard_v1_spec.md` traz `55,2299%` / `44,7701%`. Os valores certos são
> **55,2310% / 44,7690%**. Use os desta tabela. Sem `NULL` nesta coluna — só 2 categorias.

---

### D3 — Pizza de raça/cor

| | |
|---|---|
| **Fonte** | `hospitalizacoes` · **Ângulo** `COUNT(*)` · **Cor** `raca_cor_paciente` |

| raça/cor | internações | % |
|---|---|---|
| Branca | 2.891.775 | 77,3304% |
| **Sem Informação** | **410.050** | **10,9654%** |
| Parda | 208.107 | 5,5651% |
| Preta | 195.806 | 5,2361% |
| Amarela | 23.916 | 0,6395% |
| Indígena | 9.852 | 0,2635% |

> **Armadilha:** "Sem Informação" **não é uma raça** — é ausência de preenchimento, e são
> 11% da base. Tratada como fatia igual às outras, ela sugere que 1 em cada 9 pacientes
> pertence a um grupo chamado "Sem Informação". É o pecado de contexto [p.59] do V1, e no
> V2 vira nota explícita ou fatia cinza fora da paleta.

---

### E — Dois mapas (por município)

| | |
|---|---|
| **Fonte** | `occupancy`, `nome_municipio` como papel geográfico |
| **Mapa 1** | Cor = `AVG(taxa_ocupacao)` · paleta verde→amarelo→vermelho |
| **Mapa 2** | Cor = `SUM(total_internacoes)` · paleta azul→vermelho, 9 passos |

| medida | mínimo | máximo | municípios |
|---|---|---|---|
| `AVG(taxa_ocupacao)` | **3,59%** | **72,37%** | 228 |
| `SUM(total_internacoes)` | **76** | **848.764** | 228 |

228 dos **497** municípios do RS têm dado — os outros 269 ficam em branco, sem nota.

> **Armadilha:** o Mapa 2 varia por **4 ordens de grandeza** (76 → 848.764). Numa escala
> linear de cor, Porto Alegre fica sozinho no extremo e os outros 227 municípios viram um
> bloco chapado indistinguível. Não é só a paleta que está errada — a **escala** também.

---

### F1 — Barras por idade

| | |
|---|---|
| **Fonte** | `hospitalizacoes` · **Colunas** `idade_paciente` (discreta, não agrupada) · **Linhas** `COUNT(*)` |

100 barras, idades **0 a 99**, todas as 100 presentes. Cauda superior real:

| idade | internações |
|---|---|
| 96 | 2.676 |
| 97 | 1.889 |
| 98 | 1.343 |
| 99 | 951 |

Sem empilhamento artificial no topo (99 não acumula "100+"). Os picos reais ficam em
idade 1 (63.254) e na faixa 62–66 (~58 mil cada). O problema aqui é **só de design**:
100 barras onde caberiam 6 faixas etárias.

---

### F2 — Barras por município (ordem alfabética)

| | |
|---|---|
| **Fonte** | `occupancy` · **Colunas** `nome_municipio` (A→Z) · **Linhas** `SUM(total_internacoes)` |

| município | internações | % do estado |
|---|---|---|
| **Porto Alegre** | **848.764** | **22,70%** |
| Passo Fundo | 167.299 | 4,47% |
| Canoas | 161.282 | 4,31% |
| Caxias do Sul | 136.601 | 3,65% |
| Pelotas | 110.518 | 2,96% |
| Santa Maria | 102.607 | 2,74% |

228 barras. Porto Alegre sozinho é **22,70%** do estado (o spec arredonda pra 23%) e, na
ordem alfabética, cai entre "Portão" e "Progresso" — sem destaque de cor. É o antes literal
do exemplo dos UXers: o dado mais importante da tela, escondido pela ordenação.

---

### G — Dispersão (nível de registro)

| | |
|---|---|
| **Fonte** | `hospitalizacoes` · marca = **registro individual** → **3.739.506 marcas** |
| **Eixos** | X = `quantidade_dias_permanencia` · Y = `valor_aih` |

| medida | mín | máx | média | mediana |
|---|---|---|---|---|
| `valor_aih` | R$ 0,00 | R$ 198.575,01 | R$ 1.750,28 | **R$ 688,11** |
| `quantidade_dias_permanencia` | 0 | 280 | 6,048 | — |

> **Armadilha:** média R$ 1.750,28 contra mediana R$ 688,11 — a média é **2,5×** a mediana.
> Distribuição extremamente assimétrica. Sem transparência e sem tratamento de outlier, as
> 3,7 mi de marcas viram uma mancha sólida no canto inferior esquerdo com alguns pontos
> perdidos no topo. É a planilha que sozinha destrói a performance [p.111] — primeira a
> cortar se o tempo apertar.

---

### H — Série temporal (o gráfico enterrado)

| | |
|---|---|
| **Fonte** | `occupancy` · **Colunas** `ano_mes` contínuo · **Linhas** `AVG(taxa_ocupacao)` |
| **Detalhe** | `id_estabelecimento_cnes` → **287 linhas sobrepostas** |
| **Eixo Y** | fixado em **0,26 – 0,34** |

Médias anuais reais:

| ano | taxa média |
|---|---|
| 2019 | **31,76%** |
| 2020 | **26,80%** |
| 2021 | **29,76%** |
| 2022 | **32,32%** |
| 2023 | **33,50%** |

Série mensal (agregada em todos os hospitais): mínimo **23,13%** em **2020-05**, máximo
**35,40%** em **2023-11**.

> **O eixo truncado não só distorce — ele corta dado fora.** A janela 0,26–0,34 é *mais
> estreita que a própria série*: **14 dos 60 meses** caem fora dela (5 abaixo de 26%,
> 9 acima de 34%). Ou seja, 23% dos pontos são clipados pela escala. O mês mais baixo da
> pandemia (23,13%, maio/2020) simplesmente não aparece. Nada foi calculado errado — só o
> eixo mente, e mente omitindo.

---

### I — Filtros (cardinalidade real de cada um)

| filtro | fonte | nº de valores |
|---|---|---|
| Ano *(fica na região B)* | `occupancy` | 5 |
| Município | `occupancy` | **228** |
| Hospital | `occupancy` | **287** |
| Tipo de leito | `leitos` | 7 |
| Especialidade | `leitos` | 57 (+`NULL` = **58**) |
| Sexo | `hospitalizacoes` | 2 |
| Raça/cor | `hospitalizacoes` | 6 |
| Complexidade | `hospitalizacoes` | 2 |
| Caráter da internação | `hospitalizacoes` | 4 |
| Motivo de saída | `hospitalizacoes` | **27** |
| Faixa de valor | `hospitalizacoes` | contínuo (R$ 0 – 198.575,01) |

Total: **11 filtros**, sendo `Ano` na faixa de KPIs (região B) + 10 espalhados em **5 blocos**
ao longo da página (região I), cada bloco deliberadamente longe do gráfico que controla:

| bloco | filtros | fica | controla |
|---|---|---|---|
| I·1 | Faixa de valor, Motivo de saída | entre B e C | dispersão **G** |
| I·2 | Complexidade, Caráter da internação | entre D e E | idade **F1**, dispersão **G** |
| I·3 | Tipo de leito, Especialidade | entre F e G | pizza **D1** (muito acima) |
| I·4 | Sexo, Raça/cor | abaixo da dobra | roscas **D2/D3** (muito acima) |
| I·5 | Município, Hospital | rodapé | tabelão **C**, mapas **E**, barras **F2** |

> Ao construir no Tableau: os filtros são de contexto/dashboard, então a **posição no
> layout não muda o resultado** de nenhuma planilha — só o custo de encontrá-los. O número
> que cada planilha produz é o mesmo desta seção independentemente de onde o filtro esteja.

---

### J — Rodapé

Sem métrica — está vazio de propósito. O que **deveria** estar lá é a lista da §7.

---

## 4. Taxa de ocupação — a métrica mais delicada do projeto

```sql
taxa_ocupacao = total_dias_permanencia / (leitos_total × dias_no_mês)
```

Calculada **por hospital/mês** (`src/transform/transformers.py`, `OccupancyCalculator`).
O KPI do topo é `AVG` dessas 15.994 taxas.

Três decisões embutidas que mudam o resultado:

| decisão | valor resultante | comentário |
|---|---|---|
| `AVG` das taxas por hospital (**o que o V1 mostra**) | **30,8%** | cada hospital pesa igual |
| Ponderada por leito (`SUM(dias)/SUM(leitos×dias_mês)`) | **43,1%** | a taxa "do estado" de fato |
| Denominador só com leitos SUS | **39,6%** | ver abaixo |

### O viés estrutural: numerador SUS, denominador total

O numerador vem do **SIH-SUS** — só internações pagas pelo SUS. O denominador usa
`leitos_total` do CNES, que inclui **leitos privados/convênio**. Em média, só **77,1%**
dos leitos cadastrados são SUS (`leitos_sus` / `leitos_total`).

Ou seja: a taxa está **sistematicamente subestimada** — divide-se demanda SUS por
capacidade total. Trocar o denominador por `leitos_sus` sobe a média de 30,8% para 39,6%.

> **Decisão para o V1: manter `leitos_total`.** O V1 precisa ser *plausível*, não correto —
> e essa é uma escolha que times reais fazem sem perceber. Mas ela precisa estar
> **documentada aqui** e virar tema no V2: é o melhor exemplo do projeto de um erro que
> nenhuma quantidade de design conserta. Layout bonito não salva denominador errado.

### Ocupação acima de 100%

| linhas com taxa > 100% | 57 |
|---|---|
| % do total | 0,36% |
| máximo observado | **187,8%** |

Não é bug: um leito pode ser ocupado por mais de um paciente no mesmo mês (rotatividade,
altas e internações no mesmo dia), e o CNES informa o leito **cadastrado**, não o
operante. O DATASUS documenta que tempo de permanência sozinho não produz taxa de
ocupação verdadeira. **É uma aproximação** — e no V1 esses 187,8% aparecem crus na tabela
e no mapa, sem nota nenhuma (região J).

---

## 5. Óbito — a lógica foi validada por duas fontes independentes

Havia duas formas de calcular, e **elas concordam 100%**:

```sql
-- A: flag pronta do SIH
SUM(CASE WHEN indicador_obito = 1 THEN 1 ELSE 0 END)          -- 226.154

-- B: derivada da descrição de motivo_saida (via dicionário)
SUM(CASE WHEN motivo_saida_desc ILIKE 'Óbito%' THEN 1 ELSE 0 END)  -- 226.154
```

Tabela cruzada: **zero discordância** nas 3.739.506 linhas.

O detalhe que faz a diferença é o `ILIKE 'Óbito%'` (**começa com**), não
`ILIKE '%óbito%'` (**contém**). Duas categorias contêm "óbito" mas o paciente da AIH
**saiu vivo**:

| motivo_saida_desc | n | o paciente da AIH morreu? |
|---|---|---|
| Óbito com DO fornecida pelo médico assistente | 217.331 | sim |
| Óbito com DO fornecida pelo SVO | 5.346 | sim |
| Óbito com DO fornecida pelo IML | 3.417 | sim |
| Óbito da mãe/puérpera e alta do recém-nascido | 32 | sim |
| Óbito da gestante e do concepto | 14 | sim |
| Óbito da mãe/puérpera e permanência recém-nascido | 14 | sim |
| *Alta* da mãe/puérpera com óbito fetal | 2.404 | **não** |
| *Alta* da mãe/puérpera e óbito do recém-nascido | 1.473 | **não** |

Usar "contém" daria **6,15%** em vez de 6,05% — inflado por 3.877 óbitos fetais/neonatais
atribuídos à mãe, que é outra métrica.

> **Recomendação para o Tableau: use `indicador_obito`.** É a flag oficial do SIH, já veio
> na extração, é booleana e dispensa depender de string matching em português acentuado.
> A derivação por `motivo_saida_desc` fica registrada aqui como a **validação** dela.

---

## 6. De onde vem o significado dos códigos (metadados)

### O que já temos, e é o suficiente

As colunas codificadas são resolvidas pelas tabelas `dicionario` do próprio BigQuery,
extraídas em `data/raw/` — **não** dependem de nenhum bucket externo:

| arquivo local | origem BigQuery | cobertura |
|---|---|---|
| `br_ms_sih_dicionario.parquet` | `basedosdados.br_ms_sih.dicionario` | 18 colunas de `aihs_reduzidas` |
| `br_ms_cnes_dicionario.parquet` | `basedosdados.br_ms_cnes.dicionario` | `tipo_leito` (7), `tipo_especialidade_leito` (66) |

Esquema idêntico nas duas: `id_tabela`, `nome_coluna`, `chave`, `valor` — uma linha por
(tabela, coluna, código). Cada tabela-fato tem que ser resolvida contra o dicionário
**do seu próprio dataset**; não existe dicionário compartilhado entre datasets.

**Colunas de `aihs_reduzidas` cobertas pelo dicionário SIH** (18): `carater_internacao`,
`complexidade`, `especialidade_leito`, `etnia_paciente`, `grau_instrucao_paciente`,
`motivo_autorizacao_aih`, `motivo_saida`, `natureza_juridica_estabelecimento`
(+`_ate_2012`), `procedimento_realizado`, `procedimento_solicitado`, `tipo_aih`,
`tipo_contraceptivo_principal`/`_secundario`, `tipo_gestao_estabelecimento`, `tipo_uci`,
`tipo_uti`, `tipo_vinculo_previdencia`.

**Resolvidas hoje** (4, em `AihsEnricher.DICTIONARY_COLUMNS`): `tipo_aih`,
`carater_internacao`, `motivo_saida`, `complexidade` — porque a extração puxou 16 das 109
colunas de `aihs_reduzidas`, e só essas 4 são codificadas. **Não há lacuna**: toda coluna
codificada que temos está resolvida.

> Se o V2 quiser cortes por **especialidade de leito** ou por **procedimento**, aí sim é
> preciso voltar ao `run_extraction.py` e incluir `especialidade_leito` /
> `procedimento_realizado` em `COLUMNS` — o dicionário já cobre as duas (41 e 5.472
> códigos), então é só custo de extração, não de metadado.

### O bucket que dá erro — e por que não precisamos dele

```
https://storage.googleapis.com/basedosdados-dev/auxiliary_files/br_ms_sih/servicos_profissionais/TAB_SIH.zip
→ <Code>UserProjectMissing</Code>  Bucket is a requester pays bucket but no user project provided.
```

O link **não está quebrado**. `basedosdados-dev` é um bucket **requester-pays**: quem baixa
paga a saída de dados, então o Google exige que você declare *qual projeto GCP* será
cobrado. Um `GET` anônimo por HTTPS não tem como declarar isso — daí o erro. Nada a ver
com o arquivo ter sumido.

Para baixar mesmo assim, é preciso estar autenticado **e** passar o projeto de cobrança:

```bash
# gcloud (recomendado)
gcloud storage cp --billing-project=SEU_PROJECT_ID \
  gs://basedosdados-dev/auxiliary_files/br_ms_sih/servicos_profissionais/TAB_SIH.zip .

# gsutil (equivalente antigo)
gsutil -u SEU_PROJECT_ID cp \
  gs://basedosdados-dev/auxiliary_files/br_ms_sih/servicos_profissionais/TAB_SIH.zip .
```

> ⚠️ Isso **gera cobrança** no seu projeto (egresso de GCS). Não foi executado neste repo.

**Mas não precisamos.** Esse `TAB_SIH.zip` é o material **bruto do DATASUS** que a Base dos
Dados usou pra *construir* as tabelas `dicionario` — é a matéria-prima, não o produto. O
produto já está no BigQuery, já foi extraído, e é o que os `_desc` do pipeline usam. Além
disso, o caminho é de `servicos_profissionais`, tabela que este projeto nem utiliza.

**Conclusão: nenhuma ação necessária.** A cadeia de metadados está fechada —
`dicionario` (BigQuery) → `data/raw/*_dicionario.parquet` → `DictionaryResolver` →
colunas `*_desc` nas tabelas refinadas.

### Geografia

Não vem de dicionário, vem do diretório `br_bd_diretorios_brasil.municipio`, e as duas
tabelas-fato usam **larguras de código diferentes** — erro fácil de cometer:

| tabela-fato | coluna | chave no diretório |
|---|---|---|
| `aihs_reduzidas` | `id_municipio_estabelecimento` (6 dígitos, DATASUS legado) | `municipio.id_municipio_6` |
| `leito` | `id_municipio` (7 dígitos, IBGE) | `municipio.id_municipio` |

---

## 7. Ressalvas que precisam aparecer no dashboard

Herdadas de `data_briefing.md`, agora com o número medido junto:

1. **A taxa de ocupação é aproximação**, não medida real — e pode passar de 100%
   (57 linhas passam; máximo 187,8%).
2. **O denominador inclui leitos não-SUS** enquanto o numerador é só SUS → taxa
   subestimada em ~28% relativos (30,8% vs 39,6%).
3. **Dado administrativo (faturamento), não clínico** — AIH é cobrança, não prontuário.
4. **Escopo único**: RS, 2019–2023. Nada aqui generaliza pro Brasil.
5. **Defasagem de ~6 meses** no tier gratuito da Base dos Dados.
6. **Valores em reais nominais**, sem correção pela inflação no período.

No V1 **nenhuma** delas aparece — a região J é um rodapé vazio. É o pecado de
visibilidade do sistema (Nielsen) que os UXers marcaram, e a lista acima é o insumo
pronto pra virar a nota de rodapé do V2.

---

## Como reproduzir

Todos os números deste arquivo saem de `data/refined/*.parquet` via DuckDB. Exemplo:

```python
import duckdb
c = duckdb.connect()
c.execute("""
    SELECT AVG(leitos_total)  AS media_por_hospital_mes,
           MEDIAN(leitos_total) AS mediana,
           COUNT(*)          AS linhas_hospital_mes
    FROM read_parquet('data/refined/occupancy.parquet')
""").df()
```
