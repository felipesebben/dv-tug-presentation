# V2 — referência de construção no Tableau

> ### 🔧 Este documento é para quem constrói a pasta de trabalho
>
> **UXers: podem pular este arquivo.** Ele não contém decisão de design nenhuma — só a
> tradução das decisões que já foram tomadas em outro lugar para cliques, campos calculados
> e prateleiras do Tableau. Se você quer saber *por que* um gráfico é como é, o arquivo é
> `docs/v2/spec.md`; se quer saber o que um número significa, é
> `docs/foundations/metrics_dictionary.md`.
>
> Nada aqui pode contrariar aqueles dois. Se contrariar, **eles vencem** e este arquivo é
> que está errado.

Ordem de leitura para construir: seção 0 inteira antes da primeira planilha, seção 1 para
criar os campos de uma vez só, depois seção 2 folha a folha. A seção 3 lista onde o Tableau
não faz o que o wireframe faz, e o que aceitamos no lugar.

Todos os valores de conferência abaixo foram verificados contra `data/refined/*.parquet`.

---

## 0. Antes da primeira planilha

Fazer nesta ordem. Formatar no fim custa o dobro, e é exatamente como a V1 acumulou
inconsistência.

### 0.1 Fonte de dados

Uma fonte, três tabelas de `data/refined/sih_cnes_rs.hyper`, ligadas por **Relacionamentos**
(camada lógica), **nunca por junção física**:

```
occupancy  ──○  hospitalizacoes      em  id_estabelecimento_cnes + ano_mes
occupancy  ──○  leitos               em  id_estabelecimento_cnes + ano_mes
```

`occupancy` é a âncora porque já está agregada em hospital × mês. `hospitalizacoes` (1 linha
por internação) e `leitos` (1 linha por hospital × mês × tipo) têm grãos diferentes — uma
junção física entre elas infla toda soma silenciosamente. O porquê completo está no
`README.md` da raiz.

### 0.2 Arquivo espacial do mapa

Adicionar uma **segunda conexão** na mesma fonte de dados: `data/raw/municipios_rs.geojson`
(gerado por `scripts/fetch_municipal_geometry.py`, grátis). Relacionar:

| esquerda | direita |
|---|---|
| `occupancy.id_municipio` | `municipios_rs.codarea` |

**Casar por código, nunca por nome.** 38 nomes de municípios do RS existem também em outros
estados (Alto Alegre em RR e SP; Bom Jesus em PB, SC, PI e RN) — a geocodificação por nome
do Tableau erra ou descarta esses em silêncio. Conferido: os 497 polígonos batem exatamente
com o diretório da BD, e os 245 municípios com leito casam todos.

### 0.3 Formatação no nível da pasta de trabalho

**Formatar → Pasta de trabalho** antes de qualquer planilha:

| item | valor |
|---|---|
| Fonte | **Roboto** (instalar antes — o Tableau não embute fonte, e substitui em silêncio) |
| Tamanho mínimo | 9pt |
| Linhas de grade | horizontais `#e4e4e1`; verticais **nenhuma** |
| Linhas de zero | `#e4e4e1` |
| Sombreamento do dashboard | `#f4f4f2` |
| Sombreamento de contêiner | `#ffffff` |
| Bordas | nenhuma (separar por espaço e superfície) |

Paletas: copiar `tableau/Preferences.tps` para `Documentos/Meu repositório do
Tableau/Preferences.tps` e **reiniciar o Tableau**.

### 0.4 Parâmetros

| nome | tipo | valores | uso |
|---|---|---|---|
| `p_Periodo` | string, lista | `Todos` · `Pré-pandemia` · `Pandemia` · `Pós` | filtro global |
| `p_Visao` | string, lista | `Rede SUS` · `UTI` | troca a população |
| `p_LimiarAtencao` | float | `0.85` | limiar de atenção |
| `p_LimiarCritico` | float | `0.95` | limiar crítico |

Os dois limiares são parâmetros de propósito: os valores vêm da literatura de crise de leito
(Bagust, Place & Posnett, *BMJ* 1999) e **não são alvo oficial da SES-RS nem do Ministério**.
Ficando em parâmetro, mudam num lugar só — inclusive ao vivo, se alguém na plateia
perguntar.

---

## 1. Campos calculados compartilhados

Criar todos antes de começar as planilhas. Nomes com prefixo para agruparem no painel de
dados.

### 1.1 Filtro de período

```
// c_FiltroPeriodo  (booleano — arrastar para Filtros, manter True)
CASE [p_Periodo]
  WHEN "Todos"         THEN TRUE
  WHEN "Pré-pandemia"  THEN YEAR([ano_mes]) = 2019
  WHEN "Pandemia"      THEN YEAR([ano_mes]) IN (2020, 2021)
  WHEN "Pós"           THEN YEAR([ano_mes]) IN (2022, 2023)
END
```

Aplicar em **todas as planilhas** da aba (Filtro → Aplicar a planilhas → Selecionadas).

### 1.2 A troca de visão

O padrão vale para o painel inteiro: **trocar numerador e denominador separadamente, nunca
duas taxas já divididas.** Razão pré-dividida não se re-agrega.

```
// c_Num  — numerador da visão corrente
IF [p_Visao] = "UTI" THEN SUM([dias_uti]) ELSE SUM([dias_permanencia_sus]) END

// c_Den  — denominador da visão corrente
IF [p_Visao] = "UTI" THEN SUM([leito_dias_uti_sus]) ELSE SUM([leito_dias_sus]) END

// c_Taxa  — a taxa de ocupação da visão corrente
[c_Num] / [c_Den]

// c_Leitos  — leitos médios por mês, da visão corrente
(IF [p_Visao] = "UTI" THEN SUM([leitos_uti_sus]) ELSE SUM([leitos_sus]) END)
/ COUNTD([ano_mes])
```

> **Por que `COUNTD([ano_mes])` e não `SUM([dias_no_mes])`.** `leitos_sus` é por
> hospital × mês; somar sobre hospitais e dividir por `SUM(dias_no_mes)` daria a média *por
> hospital*, que é exatamente a armadilha dos "107,9 leitos" da V1 (§1 do dicionário de
> métricas). Conferido: `SUM(leitos_sus) / COUNTD(ano_mes)` = **21.838,1** em 2023, que é o
> número certo.

### 1.3 Taxas fixas das duas visões

O gráfico herói mostra as duas ao mesmo tempo, então precisa das duas independentes da
visão selecionada:

```
// c_TaxaRede
SUM([dias_permanencia_sus]) / SUM([leito_dias_sus])

// c_TaxaUti
SUM([dias_uti]) / SUM([leito_dias_uti_sus])
```

### 1.4 Nível de alerta

```
// c_Nivel
IF [c_Taxa] >= [p_LimiarCritico] THEN "crítico"
ELSEIF [c_Taxa] >= [p_LimiarAtencao] THEN "atenção"
ELSE "sob controle" END
```

Usar em **Cor**, com a paleta `V2 Neutro e Destaque` mapeada assim:

| valor | cor |
|---|---|
| sob controle | `#2a78d6` azul |
| atenção | `#eb6834` laranja |
| crítico | `#eb6834` laranja (a diferença é **rótulo e peso**, não hue) |

Os dois níveis dividem o mesmo laranja de propósito: uma terceira cor estouraria o
orçamento do sistema. A distinção entre atenção e crítico é a palavra e o negrito.

### 1.5 Índice (2019 = 100)

Cálculo de tabela, não LOD — assim a base acompanha o filtro de período automaticamente:

```
// c_IndiceCapacidade     Calcular usando: Tabela (horizontal)
100 * ZN([c_Leitos]) / LOOKUP(ZN([c_Leitos]), FIRST())

// c_IndiceDemanda        Calcular usando: Tabela (horizontal)
100 * ZN([c_Num]) / LOOKUP(ZN([c_Num]), FIRST())
```

`LOOKUP(expr, FIRST())` devolve o valor da primeira marca da partição — que é o primeiro ano
selecionado. Trocar o período re-indexa sozinho.

### 1.6 Decomposição da barra de capacidade

Para a barra preenchida do Território. Comprimento = leitos, parte cheia = ocupação:

```
// c_LeitosOcupados
[c_Taxa] * [c_Leitos]

// c_Ocupado      (parte cheia, limitada à capacidade)
MIN([c_LeitosOcupados], [c_Leitos])

// c_Livre        (o vazio — é a capacidade livre, que é o que um pleito discute)
MAX(0, [c_Leitos] - [c_LeitosOcupados])

// c_Excedente    (demanda acima da capacidade, desenhada passando do fim da barra)
MAX(0, [c_LeitosOcupados] - [c_Leitos])
```

> Conferido: em 2023, `taxa × leitos` = 13.109,1 e as diárias ÷ 365 = 13.109,0 — a
> identidade fecha, então `c_LeitosOcupados` é mesmo "leitos ocupados em média".

---

## 2. Planilha por planilha

Legenda das colunas: **Colunas/Linhas** = prateleiras; **Marcas** = tipo e encoding.

### Aba 1 · Panorama

#### 1.1–1.4 — Os quatro KPIs

Quatro planilhas separadas, tipo **Texto**.

| tile | medida | contexto |
|---|---|---|
| Taxa de ocupação UTI | `c_TaxaUti` | barra + 2 linhas de referência |
| Taxa de ocupação SUS (rede) | `c_TaxaRede` | barra + 2 linhas de referência |
| Leitos (da visão) | `c_Leitos` | minigráfico de linha |
| Internações | `SUM([total_internacoes])` | minigráfico de linha |

Cada tile:

- **Marcas → Texto**: a medida, formatada em percentual com 1 casa (taxas) ou número
  inteiro com separador de milhar pt-BR (volumes).
- **Título dinâmico**: `Taxa de ocupação UTI · <Parâmetros.p_Periodo>`. Isto é obrigatório —
  é a correção do defeito em que o tile dizia 60,0% enquanto o filtro dizia 2019–2023, e os
  dois estavam certos.
- **Variação**: campo de tabela `(ZN([c_Taxa]) - LOOKUP(ZN([c_Taxa]), -1))` para p.p., ou
  razão − 1 para volumes. Sempre com **seta e sinal**, nunca só cor.

**Só os dois tiles de taxa recebem alvo.** Leitos e internações não: alvo implica direção
que se persegue, e ninguém tem meta de quantas pessoas adoecem.

Medidor dos tiles de taxa: barra horizontal com **duas linhas de referência constantes**
vindas de `p_LimiarAtencao` e `p_LimiarCritico`. Não usar gráfico de marcador (bullet) do
Tableau — ele é eixo duplo, que o design system proíbe.

#### 1.5 — Herói: ocupação de UTI e da rede

| | |
|---|---|
| **Colunas** | `ano_mes` contínuo, **Mês** |
| **Linhas** | `c_TaxaRede` e `c_TaxaUti` — as duas **no mesmo eixo** (arrastar a segunda sobre o eixo da primeira, gerando *Nomes de medidas*), **não** eixo duplo |
| **Marcas** | Linha. Cor = Nomes de medidas: rede `#2a78d6`, UTI `#eb6834`. Espessura da UTI 2,5px |
| **Eixo Y** | **Começa em zero**, fixo de 0 a 1,4 (140%) |
| **Referências** | linha em 1,0 rotulada "100% · capacidade esgotada"; faixas em `p_LimiarAtencao` e `p_LimiarCritico` (Distribuição de referência → faixa, preenchimento laranja 7% e 13%) |
| **Rótulos** | só na última marca de cada linha (Rótulo → Marcas para rotular → Fim da linha) |

O herói é o único gráfico que ignora `p_Visao`: mostrar as duas séries **é** o argumento.

Conferência: 2021 UTI **111,9%** contra rede **53,2%**; máximo mensal jun/2021 **131,9%**.

#### 1.6 — De onde veio a variação da ocupação

| | |
|---|---|
| **Colunas** | `YEAR(ano_mes)` discreto |
| **Linhas** | `c_IndiceCapacidade` e `c_IndiceDemanda`, mesmo eixo |
| **Marcas** | Linha. Capacidade `#2a78d6`, demanda `#eb6834` |
| **Eixo Y** | **base 100**, não zero — única exceção do sistema |
| **Referências** | linha constante em 100, tracejada, rotulada `<Ano base> = 100` |
| **Título** | `De onde veio a variação da ocupação · <Parâmetros.p_Visao>` |
| **Subtítulo** | **obrigatório**: "A distância entre as linhas não é folga de capacidade — é a variação da ocupação." |

> ⚠️ **Não renomear este gráfico para "capacidade × demanda".** As duas séries são indexadas
> cada uma contra a própria base, em unidades diferentes (leitos e diárias), então o ponto de
> cruzamento **não significa nada**. Ler "capacidade acima de demanda" como "sobra
> capacidade" está errado, e já foi lido assim. O que a distância codifica é a *variação* da
> ocupação. A ressalva no subtítulo não é decoração — é a correção de um defeito real.

Conferência, 2019 = 100: em 2023 rede capacidade **100,3** / demanda **103,1**; UTI
capacidade **121,1** / demanda **125,1**. Em 2021 a UTI é capacidade **99,6** / demanda
**146,4**.

#### 1.7 — Internações e permanência média, indexadas

Mesma construção do 1.6, com:

```
// c_IndiceInternacoes     Tabela (horizontal)
100 * ZN(SUM([total_internacoes])) / LOOKUP(ZN(SUM([total_internacoes])), FIRST())

// c_PermanenciaMedia      (de hospitalizacoes)
AVG([quantidade_dias_permanencia])

// c_IndicePermanencia     Tabela (horizontal)
100 * ZN([c_PermanenciaMedia]) / LOOKUP(ZN([c_PermanenciaMedia]), FIRST())
```

Permanência em `#8c8c89` cinza: é contexto, não alarme.

---

### Aba 2 · Território

#### 2.1 — Mapa coroplético

| | |
|---|---|
| **Marcas** | Mapa (polígono), campo espacial `Geometry` do GeoJSON |
| **Detalhe** | `codarea` |
| **Cor** | `c_Taxa`, paleta `V2 Sequencial Azul`, **um hue só** |
| **Contêiner** | **quadrado**, ~330 × 330px |
| **Camadas** | Mapa → Camadas: desligar tudo menos a base. Sem rótulo de cidade, sem estrada |

O contêiner é quadrado porque o RS é: a proporção do envelope é **1,03**. Numa faixa larga
sobraria ~800px vazios ou o estado sairia achatado.

Municípios sem leito ficam **em branco**, não em zero — em visão UTI isso é dois terços do
mapa, e é o achado: só 59 dos 225 municípios com leito têm UTI.

#### 2.2 — Dispersão leitos × ocupação

| | |
|---|---|
| **Colunas** | `c_Leitos` — **escala logarítmica** |
| **Linhas** | `c_Taxa` |
| **Detalhe** | `nome_municipio` |
| **Cor** | `c_Nivel` |
| **Tamanho** | maior para municípios acima do corte de leitos |
| **Contêiner** | **quadrado**, ~330 × 330px |
| **Referências** | linha horizontal na taxa do estado; linhas nos dois limiares; linha vertical no corte de leitos (100 na rede, 20 na UTI) |

Quadrado de propósito: dispersão codifica duas magnitudes comparáveis, e uma caixa larga diz
ao olho que a dispersão horizontal importa mais que a vertical — o que é uma afirmação sobre
o dado, não sobre o layout.

Os textos de leitura ficam **dentro do mesmo contêiner**, à direita do quadrado.

#### 2.3 — Os 12 municípios com mais leitos

| | |
|---|---|
| **Linhas** | `nome_municipio`, ordenado por `SUM([leito_dias_sus])` decrescente |
| **Colunas** | `c_Ocupado`, `c_Livre`, `c_Excedente` — **barra empilhada** via Nomes/Valores de medidas |
| **Marcas** | Barra. Cor por Nomes de medidas: Ocupado = `c_Nivel`; Livre = `#e4e4e1`; Excedente = `#eb6834` |
| **Filtro** | N Superiores = 12 por `SUM([leito_dias_sus])` |
| **Rótulo** | `c_Leitos` + `c_Taxa` no fim da barra |

Comprimento total = leitos; parte cheia = ocupação; o vazio **é** a capacidade livre. Uma
marca carrega as duas dimensões, então ninguém precisa segurar "quais são grandes" e "quais
estão apertados" em dois gráficos.

> Ordenar por `SUM([leito_dias_sus])` e não por `c_Leitos`: dá exatamente a mesma ordem
> (conferido) e evita ordenar por medida calculada, que o Tableau resolve depois do filtro
> de N Superiores.

---

### Aba 3 · Capacidade

#### 3.1 — Ocupação por tipo de leito

| | |
|---|---|
| **Linhas** | `tipo_leito_desc` (de `leitos`), ordenado por taxa decrescente |
| **Colunas** | taxa do tipo |
| **Marcas** | Barra. Cor: UTI em `#eb6834`, resto em `#2a78d6` |
| **Referência** | linha em 100% |

Numerador da enfermaria vem de `hospitalizacoes` por `tipo_leito_cnes`; o denominador de
`leitos` por `tipo_leito_desc`. **A linha da UTI não sai daí** — usa `dias_uti` sobre
`leito_dias_uti_sus`, porque no RS nenhuma internação é classificada como UTI em
`especialidade_leito` e o crosswalk devolveria zero.

Duas ressalvas obrigatórias na nota do gráfico:

1. **Hospital dia a ~18% não está ocioso** — gira dentro do mesmo dia, leito-dia é a unidade
   errada pra ele.
2. **"Complementar" não é UTI** — dos 2.404 leitos complementares de 2023 só 1.839 são
   UTI/UCO.

Conferência 2023: UTI 78,6% · cirúrgico 75,7% · clínico 70,4% · outras 66,3% · pediátrico
54,8% · obstétrico 36,8% · hospital dia 18,2%.

#### 3.2 — Leitos por tipo ao longo do tempo

Linhas por `tipo_leito_desc`, paleta `V2 Leitos` (**máximo 4 categorias + Outros** — acima
disso a leitura quebra). Agrupar o resto em "Outros" em `#8c8c89`.

Nunca desenhar `tipo_especialidade_leito_desc` como linha: são **64 combinações**. Aquilo é
barra ou drill-down.

#### 3.3 — Pacientes com 60 anos ou mais

```
// c_Share60
SUM(IF [idade_paciente] >= 60 THEN 1 ELSE 0 END) / COUNT([idade_paciente])
```

Somar um indicador 0/1 e dividir pela contagem, em vez de `COUNTD` com condicional: dá o
mesmo resultado, roda muito mais rápido sobre 3,7 milhões de linhas, e não depende de
`[Number of Records]`, que mudou de nome entre versões do Tableau.

Linha em `#2a78d6`. **O último ponto não é laranja** — recência não é alarme.

---

### Aba 4 · Custo

#### 4.1 — Gasto e internações, indexados

Mesma construção de 1.6, com `SUM([valor_aih])` e `SUM([total_internacoes])`. Gasto em
laranja: crescer acima do volume é o que pede atenção.

#### 4.2 — Volume e gasto por complexidade

Duas barras 100% empilhadas, `complexidade_desc` em Cor, alta complexidade em `#eb6834`.
O descasamento entre as duas barras **é** o gráfico.

> `complexidade_desc` vem grafado **"Méida Complexidade"** no dicionário da fonte. Corrigir
> só na exibição (alias), **nunca na chave de junção**.

#### 4.3 — Valor da AIH, média × mediana

Tabela de texto por ano: `SUM([valor_aih])`, `AVG([valor_aih])`, `MEDIAN([valor_aih])`.

**Colunas ordenáveis ligadas** (Nielsen — controle do usuário; é uma linha da orientação de
UX). Nota obrigatória: a distribuição é assimétrica, a mediana descreve melhor a internação
típica.

---

## 3. Onde o Tableau não faz o que o wireframe faz

Substituições aceitas, para ninguém perder tempo tentando:

| wireframe | Tableau | substituição |
|---|---|---|
| Barra excedente **hachurada** | não há preenchimento com padrão | laranja sólido com borda branca de 1px |
| Tour guiado de 6 passos | sem equivalente nativo | **aba "Comece aqui"** como primeira planilha do dashboard. Ver `docs/v2/orientation.md` §6 — a alternativa (corrente de contêineres mostrar/ocultar) ninguém consegue manter depois |
| Glossário com busca | sem busca em objeto de texto | contêiner flutuante com o texto completo + a linha do glossário em **dica de ferramenta** de cada métrica, que é onde ela chega sem exigir clique |
| Medidor de limiar no KPI | gráfico de marcador é eixo duplo | barra + duas linhas de referência constantes |
| Faixa de limiar sombreada | — | Distribuição de referência → Faixa, com preenchimento |
| Filtro "Visão" trocando medidas | parâmetro, não filtro | é o que a seção 1.2 faz; o Tableau chama de parâmetro, e ele **não** aparece na lista de filtros |

Se o relacionamento com o arquivo espacial der trabalho, o **plano B** é mapa de pontos por
centróide — `centroide` já vem em WKT nas três tabelas:

```
// c_Lon
FLOAT(SPLIT(REPLACE(REPLACE([centroide], "POINT(", ""), ")", ""), " ", 1))
// c_Lat
FLOAT(SPLIT(REPLACE(REPLACE([centroide], "POINT(", ""), ")", ""), " ", 2))
// c_Ponto
MAKEPOINT([c_Lat], [c_Lon])
```

É pior que o coroplético (bolha não mostra área, e cidade pequena some), então é plano B
mesmo — mas funciona sem conexão extra.

---

## 4. Antes de dar por pronto

- [ ] Roboto instalado e aplicado no nível da pasta de trabalho
- [ ] `Preferences.tps` copiado e Tableau reiniciado
- [ ] Relacionamentos, **não** junções — conferir que `SUM([total_internacoes])` dá
      **3.739.506** na visão estadual sem filtro. Se der mais, há fan-out
- [ ] Taxa estadual 2019–2023 = **55,8%**; 2023 = **60,0%**; UTI 2021 = **111,9%**
- [ ] Nenhuma taxa arrastada como `SUM([taxa_ocupacao_sus])` — sempre `c_Num / c_Den`
- [ ] Todo título com período dinâmico
- [ ] Nenhum subtítulo afirmando conclusão que o filtro possa desmentir
- [ ] Laranja só onde significa "precisa de atenção" — nunca "mais recente" nem "a mediana"
- [ ] Eixo em zero em toda taxa e toda barra; exceção só nos dois gráficos indexados
- [ ] Filtro de período aplicado às planilhas da aba inteira
- [ ] O aviso "a distância não é folga" presente no gráfico 1.6
- [ ] Botões de glossário, como usar e suporte no cabeçalho, nas quatro abas
- [ ] Cada aba cabe em 1200 × 800 **sem rolagem**
