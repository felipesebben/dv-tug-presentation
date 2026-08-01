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
| `p_Medida` | string, lista | `Ocupação` · `Leitos` · `Internações` | **navegação do Panorama** — ver §C6 |
| `p_Visao` | string, lista | `Rede SUS` · `UTI` | **qual população está em foco** — Panorama e Território |
| `p_LimiarAtencao` | float | `0.85` | limiar de atenção |
| `p_LimiarCritico` | float | `0.95` | limiar crítico |

`p_Medida` e `p_Visao` fazem coisas diferentes, e confundi-los foi o erro de uma versão
anterior deste documento:

| parâmetro | responde | efeito |
|---|---|---|
| `p_Visao` | **qual população** está em foco | os KPIs passam a reportá-la, e nos gráficos ela vira a série azul (sujeito), com a outra em cinza (contexto) |
| `p_Medida` | **qual pergunta** se faz sobre ela | troca o herói e os dois gráficos de apoio |

Cada tile mostra **um número só** — o da população em foco. A comparação com a outra
acontece **no gráfico**, que é onde comparação pertence e onde ela já está sendo desenhada.
Trazer as duas para dentro do tile deixa o tile cheio e duplica o que o herói faz.

Território usa `p_Visao` e não tem seletor de medida: um mapa localiza uma população de cada
vez.

Os dois limiares são parâmetros de propósito: os valores vêm da literatura de crise de leito
(Bagust, Place & Posnett, *BMJ* 1999) e **não são alvo oficial da SES-RS nem do Ministério**.
Ficando em parâmetro, mudam num lugar só — inclusive ao vivo, se alguém na plateia
perguntar.

---

## 1. Campos calculados compartilhados

Criar todos antes de começar as planilhas. Nomes com prefixo para agruparem no painel de
dados.

### C1 · Filtro de período

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

### C2 · A troca de visão

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

### C3 · As duas séries do herói, e como a cor segue o foco

O herói mostra as duas populações ao mesmo tempo, então precisa das duas independentes da
visão:

```
// c_TaxaRede
SUM([dias_permanencia_sus]) / SUM([leito_dias_sus])

// c_TaxaUti
SUM([dias_uti]) / SUM([leito_dias_uti_sus])
```

**Mas plotar essas duas direto não funciona.** Com Nomes de medidas em Cor, cada medida
recebe uma cor fixa — e o que precisamos é que a cor siga `p_Visao`, não a identidade da
série. Não dá pra pintar "a que estiver em foco" com Nomes de medidas.

A saída é fazer a troca **no dado**, não na cor. Duas medidas derivadas, e aí sim cores
fixas:

```
// c_Foco        — a população em foco
IF [p_Visao] = "UTI" THEN [c_TaxaUti] ELSE [c_TaxaRede] END

// c_Contexto    — a outra, atrás
IF [p_Visao] = "UTI" THEN [c_TaxaRede] ELSE [c_TaxaUti] END
```

Plotar `c_Foco` e `c_Contexto`, e mapear em Nomes de medidas: **Foco → `#2a78d6` azul,
Contexto → `#8c8c89` cinza**, permanentemente. Trocar `p_Visao` troca quais números entram
em cada série, e a cor nunca precisa mudar — que é exatamente a regra "identidade vem da
seleção, o hue carrega só estado".

O mesmo par existe para as medidas de contagem:

```
// c_LeitosFoco / c_LeitosContexto        sobre leitos_uti_sus e leitos_sus
// c_InternacoesFoco / c_InternacoesContexto   sobre internacoes_com_uti e total_internacoes
```

Rótulos das séries: `IF [p_Visao] = "UTI" THEN "UTI" ELSE "Rede SUS" END` e o inverso, para
que a legenda diga qual é qual sem depender da cor.

### C4 · Nível de alerta

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

### C5 · Índice (2019 = 100)

Cálculo de tabela, não LOD — assim a base acompanha o filtro de período automaticamente:

```
// c_IndiceCapacidade     Calcular usando: Tabela (horizontal)
100 * ZN([c_Leitos]) / LOOKUP(ZN([c_Leitos]), FIRST())

// c_IndiceDemanda        Calcular usando: Tabela (horizontal)
100 * ZN([c_Num]) / LOOKUP(ZN([c_Num]), FIRST())
```

`LOOKUP(expr, FIRST())` devolve o valor da primeira marca da partição. Trocar o período
re-indexa sozinho.

> **Cuidado com o grão, porque isto muda a fórmula.** Nos gráficos anuais (as tesouras de
> apoio) a primeira marca *é* o primeiro ano, e `LOOKUP(..., FIRST())` está certo. No herói,
> que é mensal, a primeira marca é **janeiro** — sazonalmente baixo, e indexar por ele
> superestimaria todo ponto seguinte. Lá a base é a **média do primeiro ano**, com
> `WINDOW_AVG` — ver §1.2, na seção 2.

### C6 · O seletor de KPI — Panorama inteiro depende disto

A faixa de KPIs **é** a navegação do Panorama. Sempre há exatamente um tile selecionado, e
ele decide qual pergunta os gráficos respondem sobre a população que `p_Visao` colocou em
foco. A estrutura da comparação nunca muda — foco contra a outra população —, então a tese
do painel vira um enquadramento aplicado três vezes.

**Ação de parâmetro** em cada tile: Dashboard → Ações → Alterar parâmetro, ao *selecionar*
a marca, alvo `p_Medida`, campo de origem = o rótulo da medida daquela planilha.
Em "Limpar seleção", escolher **Manter valor atual** — nunca "Definir como" —, porque uma
seleção vazia deixaria a aba sem gráfico nenhum.

Isso exige um campo na planilha do tile para a ação carregar. Não existe dimensão comum
entre os três tiles, então cada planilha ganha uma constante própria:

```
// d_MedidaOcupacao      (na planilha do tile de ocupação)     "Ocupação"
// d_MedidaLeitos        (na planilha do tile de leitos)       "Leitos"
// d_MedidaInternacoes   (na planilha do tile de internações)  "Internações"
```

Arrastar a constante para **Detalhe** na planilha correspondente e usá-la como campo de
origem da ação. O realce do tile ativo compara o parâmetro com ela:

```
// c_TileSelecionado   — realce do tile ativo
[p_Medida] = ATTR([d_MedidaOcupacao])     // idem nas outras duas, cada uma com a sua
```

**O realce precisa ser inequívoco**, porque com visibilidade dinâmica os gráficos que um
tile controla não estão na tela enquanto ele não é escolhido.

E precisa ser **figura-fundo, não cor**: seleção é cromo de interface, não dado. Pintar o
tile selecionado de azul faz o azul significar "valor de rede" *e* "este tile está
selecionado" no mesmo tile — a colisão exata que a regra de paleta existe pra impedir.
Então: tiles não selecionados recuados sobre o plano `#eceae7`, o selecionado num card
branco elevado com régua lateral em `--tinta` e rótulo em peso 600. Mesmo mecanismo que o
design system já usa pra separar card de fundo, e não custa cor nenhuma.

**Visibilidade dinâmica dos contêineres** (Tableau 2022.3+, você tem 2026.1): cada grupo de
gráficos de apoio fica num contêiner cujo "Controlar visibilidade usando valor" aponta para
um booleano:

```
// c_MostrarOcupacao        [p_Medida] = "Ocupação"
// c_MostrarLeitos          [p_Medida] = "Leitos"
// c_MostrarInternacoes     [p_Medida] = "Internações"
```

> O campo precisa ser booleano e retornar **um único valor** na planilha do contêiner —
> normalmente se cria como calculado a partir do parâmetro, sem referência a campo da fonte,
> o que garante isso. Se o Tableau recusar o campo na lista, é quase sempre porque ele está
> agregado ou depende de uma dimensão da visão.

**O herói nunca é escondido.** Ele muda de medida, mas continua na tela em todos os três
estados: é o gráfico que justifica o painel existir, e escondê-lo em dois estados de três
seria otimizar o layout perdendo o argumento.

#### As três medidas, e por que o eixo muda

A série em foco é sempre a **azul**; a outra fica **cinza** atrás dela. Trocar `p_Visao`
troca qual é qual — identidade vem da seleção, não do hue.

| medida | séries | eixo | por quê |
|---|---|---|---|
| **Ocupação** | taxa em foco × taxa da outra | **zero**, com faixas de limiar | taxas dividem a unidade, então comparam em absoluto |
| **Leitos** | leitos em foco × leitos da outra | **índice, base 100** | 1.837 contra 21.838 — no mesmo eixo absoluto a série menor vira uma linha no chão |
| **Internações** | internações em foco × as da outra | **índice, base 100** | 342.929 contra 3.739.506, mesma razão |

A base do índice é a **média do primeiro ano selecionado**, não o primeiro mês. Janeiro é
sazonalmente baixo; indexar por ele superestimaria todo ponto seguinte, e a média anual é o
que os números documentados usam.

#### O que cada medida revela — conferido, e cada uma é uma história diferente

| | rede | UTI |
|---|---|---|
| **Ocupação** 2021 | caiu a **53,2%** | subiu a **111,9%** |
| **Leitos** 2021 | cresceu a **106,0** | ficou parada em **99,6** |
| **Leitos** 2023 | voltou a **100,3** | cresceu a **121,1** |
| **Internações** 2020 | caiu a **87,6** | subiu a **112,5** |

A linha de leitos é a mais forte para um pleito: o RS **expandiu leito geral durante a
pandemia enquanto a UTI ficou parada, e só ampliou UTI depois**. A resposta de capacidade
intensiva chegou após a emergência.

#### Gráficos de apoio por medida

| medida | apoio 1 | apoio 2 |
|---|---|---|
| Ocupação | tesoura da **UTI** (capacidade × demanda) | tesoura da **rede** — lado a lado mostram os dois mecanismos opostos de 2020–21 num relance |
| Leitos | UTI como fatia da rede (7,0% → 8,4%) | leitos por tipo ao longo do tempo |
| Internações | % das internações que usaram UTI (7,6% → 9,0%) | volume × permanência média, indexados |

### C7 · Decomposição da barra de capacidade

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

A aba inteira depende do seletor de §C6. Construir os tiles primeiro, depois a ação de
parâmetro, e só então os gráficos — assim dá pra testar a troca antes de haver o que
esconder.

#### 1.1 — A faixa de KPIs (três tiles, e eles são o menu)

Três planilhas, tipo **Texto**, uma por medida. Cada uma mostra **um número só** — o da
população que `p_Visao` colocou em foco. A comparação com a outra acontece no gráfico
abaixo, que já a está desenhando; trazê-la para dentro do tile enche o tile e duplica o
herói.

| tile | medida (na visão em foco) | medidor |
|---|---|---|
| **Ocupação** | `c_Taxa` | barra + 2 linhas de referência |
| **Leitos** | `c_Leitos` | minigráfico |
| **Internações** | `c_Internacoes` | minigráfico |

```
// c_Internacoes    internações da visão corrente
IF [p_Visao] = "UTI" THEN SUM([internacoes_com_uti]) ELSE SUM([total_internacoes]) END
```

**Só o tile de ocupação recebe medidor e nível.** Leitos e internações são contagens: um
alvo ali implicaria que alguém dirige quantas pessoas adoecem. O nível segue a população em
foco — em visão UTI o tile marca *atenção* a 86,1%, em visão rede marca *sob controle* a
55,8%.

Realce do selecionado: **figura-fundo, nunca cor de dado** — ver §C6. Cursor de mão.

Rodapé de cada tile: `<Parâmetros.p_Visao> · <Parâmetros.p_Periodo>`, para que o número
nunca fique ambíguo sobre de que população e de que recorte ele fala.

#### 1.2 — Herói: a mesma comparação, na medida selecionada

Uma planilha por medida (três), cada uma num contêiner com visibilidade dinâmica ligada ao
`c_Mostrar*` correspondente. **O herói nunca fica escondido** — sempre há exatamente um
dos três na tela.

| | ocupação | leitos / internações |
|---|---|---|
| **Colunas** | `ano_mes` contínuo, Mês | idem |
| **Linhas** | `c_TaxaUti` e `c_TaxaRede`, mesmo eixo | índices das duas séries, mesmo eixo |
| **Eixo Y** | **zero** a 1,4 | **base 100** |
| **Referências** | faixas em `p_LimiarAtencao` e `p_LimiarCritico`; linha em 100% | linha constante em 100 |

**Cor, e esta é a correção de 01/08/2026:** a série **em foco é azul** (o sujeito) e a
outra é **cinza** (o contexto). Trocar `p_Visao` troca qual é qual. Nenhuma das duas é
laranja: laranja fica só para a faixa de limiar, e o alarme passa a ser *uma linha azul
entrando numa faixa laranja*, que só acontece quando é verdade. Antes a UTI era laranja por
identidade, então UTI a 40% continuava gritando alarme.

Base do índice: **média do primeiro ano selecionado**, não o primeiro mês. Em cálculo de
tabela:

```
// c_IndiceFoco        Calcular usando: Tabela (horizontal)
100 * ZN([c_LeitosFoco]) / WINDOW_AVG(ZN([c_LeitosFoco]), FIRST(), FIRST() + 11)

// c_IndiceContexto    idem, sobre [c_LeitosContexto]
```

(Trocar `c_LeitosFoco` por `c_InternacoesFoco` na medida de internações.)

> Se o recorte tiver menos de 12 meses, trocar o `+ 11` pelo número de meses do primeiro
> ano selecionado, ou indexar por `LOOKUP(..., FIRST())` e aceitar a base de um mês só. A
> média anual é a que bate com os números documentados.

#### 1.3 — Os dois gráficos de apoio, por medida

Seis planilhas ao todo, em três contêineres de visibilidade dinâmica.

| medida | apoio 1 | apoio 2 |
|---|---|---|
| **Ocupação** | tesoura da **UTI** — `c_IndiceCapacidade` × `c_IndiceDemanda` sobre leitos e diárias de UTI | tesoura da **rede**, idem sobre a rede |
| **Leitos** | UTI como fatia da rede: `SUM([leitos_uti_sus]) / SUM([leitos_sus])`, por ano | leitos por tipo ao longo do tempo (paleta `V2 Leitos`, 4 + Outros) |
| **Internações** | % que usou UTI: `SUM([internacoes_com_uti]) / SUM([total_internacoes])` | volume × permanência média, indexados |

As **duas tesouras lado a lado** são o melhor momento da aba: mostram os dois mecanismos
opostos de 2020–21 num relance — a rede ganhando capacidade enquanto a demanda caía, a UTI
com capacidade parada enquanto a demanda explodia.

Nas duas, a nota é obrigatória: **"A distância entre as linhas não é folga de capacidade —
é a variação da ocupação."** As séries são indexadas cada uma contra a própria base, em
unidades diferentes, então o cruzamento não significa nada. Ver §C5.

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

Mesma construção indexada da §C5, com `SUM([valor_aih])` e `SUM([total_internacoes])`.

Gasto em laranja é uma das duas únicas exceções à regra "laranja só onde há limiar": aqui
não há régua, mas o gasto crescer acima do volume **é** a condição que o pleito discute, e é
acionável. Está anotado aqui de propósito, para não virar precedente — se aparecer uma
terceira exceção, é sinal de que a regra virou opinião.

#### 4.2 — Volume e gasto por complexidade

Duas barras 100% empilhadas, `complexidade_desc` em Cor: **alta complexidade em `#2a78d6`
azul (é o sujeito), média em `#8c8c89` cinza (é o contexto)**. O descasamento entre as duas
barras **é** o gráfico, e ele se lê pelo comprimento — não precisa de cor de alarme.

> Correção de revisão: antes a alta complexidade era laranja, o que é laranja marcando
> **categoria** — justamente o que a regra proíbe. O gráfico não perde nada: a
> desproporção entre 10,8% das internações e 36,3% do gasto está no tamanho das faixas.

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
| Filtro "Visão" trocando medidas | parâmetro, não filtro | é o que a §C2 faz; o Tableau chama de parâmetro, e ele **não** aparece na lista de filtros |
| KPI clicável como menu | ação de parâmetro + visibilidade dinâmica | nativo desde 2022.3 — funciona, mas o realce do tile é responsabilidade sua: sem ele o usuário não descobre que dá pra clicar, e os gráficos escondidos ficam invisíveis para sempre |

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
- [ ] **`p_Visao` e `p_Medida` fazem coisas diferentes** — trocar a visão muda os *números*
      dos tiles e qual série é azul; trocar o tile muda *quais gráficos* aparecem. Se um
      deles não fizer nada, ou se um tile mostrar as duas populações, os dois se
      confundiram de novo
- [ ] **Sempre exatamente um tile de KPI selecionado** — inclusive depois de clicar fora.
      Se "Limpar seleção" estiver como "Definir como", a aba fica sem gráfico nenhum
- [ ] Trocar de tile muda os dois gráficos de apoio, e o herói continua na tela nos três
      estados
- [ ] **Laranja só marca condição, nunca categoria.** UTI é azul quando é o sujeito e
      cinza quando é contexto — nunca laranja por ser UTI. Nas medidas de contagem, onde
      não há limiar para romper, **não deve haver laranja nenhum nos gráficos**
- [ ] Eixo em zero em toda taxa e toda barra; exceção só nos dois gráficos indexados
- [ ] Filtro de período aplicado às planilhas da aba inteira
- [ ] O aviso "a distância não é folga" presente **nas duas tesouras** (§1.3)
- [ ] Botões de glossário, como usar e suporte no cabeçalho, nas quatro abas
- [ ] Cada aba cabe em 1200 × 800 **sem rolagem**
