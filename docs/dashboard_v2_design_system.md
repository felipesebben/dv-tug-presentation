# Design system da V2

Os tokens e regras que a V2 usa. Existe para que "consistência" e "acessibilidade"
sejam **valores decididos uma vez**, não julgamentos repetidos folha a folha — que é
exatamente o pecado nº 27 da V1 (tipografia, tamanhos e espaçamentos diferentes pra
mesma função).

Base: bloco de **Acessibilidade** e **Lei da simplicidade** de `docs/uxers_guidance.md`,
que continua sendo o filtro de prioridade do projeto. Onde este documento acrescenta
número onde a orientação dava direção, o número está justificado abaixo.

Escopo: **modo claro apenas** — um dashboard Tableau não alterna tema.

---

## 1. Achado: o par verde + laranja não passa em daltonismo

`uxers_guidance.md` recomenda **"destaques em verde e laranja"** em vez de azul e
vermelho. Testado com simulação de CVD antes de adotar:

| par | ΔE protanopia | ΔE visão normal | veredito |
|---|---|---|---|
| verde `#008300` + laranja `#eb6834` | **3,2** | 31,0 | **reprovado** |
| azul `#2a78d6` + laranja `#eb6834` | **24,7** | 33,6 | aprovado |
| violeta `#4a3aa7` + amarelo `#eda100` | 41,0 | 45,9 | aprovado |

Alvo ≥ 8; abaixo de 6 é reprovação. Verde e laranja caem os dois no eixo de confusão
vermelho-verde: para um protanope, os dois viram o mesmo marrom-amarelado. Em visão
normal o par é ótimo (31,0) — é justamente o caso que passa despercebido em revisão
visual.

**Isto contradiz a orientação dos UXers**, que pela regra do projeto vence em conflito.
Mas a regra de prioridade é editorial, e aqui há medição. **Decisão pendente do Felipe**
— até lá o restante deste documento adota **azul + laranja**, que passa com folga e não
é o par azul-vermelho que os UXers queriam evitar. A recomendação original deles
(evitar azul+vermelho) continua respeitada.

> Vale como momento de palco: a dupla recomendou um par por intuição, e a simulação
> reprovou. "Rode o verificador, não confie no olho" é uma lição mais forte vinda de um
> erro próprio do que de um exemplo de livro.

---

## 2. Cores

Proporção alvo dos UXers: **20% destaque · 30% cinzas · 70% branco/preto**. Na prática:
cinza é o padrão, cor é exceção, e cor só aparece onde há um argumento.

### Destaque (2 cores, nunca mais)

| papel | hex | contraste vs card | uso |
|---|---|---|---|
| `--destaque` | `#2a78d6` | 4,42 | a série ou barra que sustenta o argumento |
| `--destaque-2` | `#eb6834` | 3,20 | apenas quando duas séries precisam coexistir (capacidade × demanda) |

### Cinzas (exatamente 3 — o teto dos UXers)

| papel | hex | contraste vs card | uso |
|---|---|---|---|
| `--grade` | `#e4e4e1` | 1,27 | linhas de grade, divisórias. Nunca texto |
| `--marca-neutra` | `#8c8c89` | 3,37 | marcas **não** destacadas — o padrão dos gráficos |
| `--texto-secundario` | `#5c5c5a` | 6,70 | rótulos de eixo, legendas, notas |

`--marca-neutra` foi escolhido em `#8c8c89` e não num cinza mais claro porque precisa
cruzar 3:1 contra o card branco — `#9a9a97` dá 2,82 e reprova. É a regra "o cinza mais
claro ainda tem que ser legível", com número.

### Superfícies (figura-fundo)

| papel | hex | |
|---|---|---|
| `--plano` | `#f4f4f2` | fundo do dashboard |
| `--card` | `#ffffff` | fundo de cada gráfico |
| `--tinta` | `#111110` | texto primário, números dos KPIs |

Fundo cinza com cards brancos é o par antes/depois de figura-fundo dos UXers, e é o que
substitui as bordas da V1: **separar por espaço e superfície, não por linha**.

### Rampa ordinal — tipos de leito

Categorias com **um hue em tons diferentes**, conforme a regra de cores dos UXers.
Substitui a paleta categórica de cor-por-categoria da V1.

`#86b6ef` → `#3987e5` → `#256abf` → `#184f95`, e `--marca-neutra` para "Outros".

Verificado: lightness monotônica, degraus ≥ 0,06, ponta clara em 2,11:1. Máximo de
**4 categorias + Outros** — acima disso a leitura quebra, e é a Lei de Hick aplicada a
cor.

### Rampa sequencial — mapa

Mesma família azul, `#cde2fb` → `#0d366b`, claro = baixo. **Um hue só.**

Isto mata o pecado nº 79 da V1 (paleta divergente verde→amarelo→vermelho num mapa de
magnitude). Divergente só se houver um ponto neutro real — taxa de ocupação não tem.

---

## 3. Tipografia

Mínimo dos UXers: **14px / 9pt**. O Tableau trabalha em pt.

| papel | tamanho | peso | cor |
|---|---|---|---|
| Número de KPI | 28pt | bold | `--tinta` |
| Rótulo de KPI | 10pt | regular | `--texto-secundario` |
| Título de gráfico | 12pt | bold | `--tinta` |
| Subtítulo / contexto | 10pt | regular | `--texto-secundario` |
| Eixo, legenda, rótulo | **9pt** | regular | `--texto-secundario` |
| Nota de rodapé | 9pt | regular | `--texto-secundario` |

Seis tamanhos, cada um com uma função. **Nada abaixo de 9pt. Nada em caixa alta** —
caixa alta destrói o contorno da palavra, que é o que a leitura por forma usa (bloco de
dislexia dos UXers). Uma família só.

---

## 4. Espaçamento e layout

Grade de **8px**. Todo espaçamento é múltiplo de 8.

| espaço | valor |
|---|---|
| Interno do card | 16px |
| Entre itens do mesmo grupo | 8px |
| Entre grupos diferentes | 24px |
| Entre seções | 40px |

A relação **8 < 24** é a Lei da Proximidade em número: o espaço dentro do grupo tem que
ser visivelmente menor que o espaço entre grupos. Na V1 os dois eram iguais — foi
exatamente o exemplo "antes" que os UXers deram.

Alinhamento: tudo se alinha a uma grade de colunas. Cabeçalho, filtros e cards
compartilham a mesma margem esquerda e direita. Larguras de coluna semelhantes
(simetria); alturas iguais na mesma linha (continuidade).

**Filtros**: no máximo 3 visíveis, no topo, **junto do que controlam** — e não os 11
espalhados por 6 lugares da V1. O resto vai atrás de "mais filtros" (Lei de Hick).

---

## 5. Regras de gráfico

**Formas permitidas:** barra, linha, mapa, big number. Ponto/dispersão só com
justificativa.

**Proibidas:** pizza e rosca (V1 tinha três), 3D, bubble, eixo duplo.

> O eixo duplo merece nota: a série temporal da V1 é um eixo duplo sincronizado, e como
> os dois eixos medem a mesma coisa na mesma escala, ele não mente. Ainda assim a V2 não
> usa nenhum. Para comparar duas medidas de escalas diferentes — capacidade × demanda —
> a resposta é **indexar as duas a 2019 = 100** e plotar num eixo só. É o que transforma
> o gráfico-tesoura no argumento do pleito, em vez de duas escalas que o leitor tem que
> reconciliar de cabeça.

**Eixo Y começa em zero** em toda barra e em toda série de taxa.

**Grade**: horizontal apenas, `--grade`, hairline. Sem grade vertical, sem borda no
card, sem fundo de plotagem.

**Ordenação**: toda barra categórica sai ordenada por valor, nunca alfabética — a menos
que a categoria tenha ordem natural (mês, faixa etária). Tabela com colunas ordenáveis
(controle do usuário, Nielsen).

**Destaque**: barras em `--marca-neutra`; só o que sustenta o argumento recebe
`--destaque`. Uma barra colorida numa série cinza carrega mais significado que doze
barras coloridas.

**Rótulos diretos** no fim da linha ou na barra destacada, em vez de legenda, quando há
≤ 2 séries. Nunca um número em cima de todo ponto.

**Contexto obrigatório** (Nielsen, visibilidade do estado do sistema): todo gráfico tem
título que diz o que ele mostra, e o dashboard traz fonte, recorte e data da última
atualização — a região J da V1 era um rodapé vazio.

---

## 6. Aplicação no Tableau

As paletas ficam em `tableau/Preferences.tps`, que precisa ser copiado para
`Documentos/Meu repositório do Tableau/Preferences.tps` e o Tableau reiniciado. Assim as
três paletas aparecem nomeadas no seletor de cores em vez de serem coladas hex a hex.

Onde cada coisa é definida:

| token | onde no Tableau |
|---|---|
| Cores de série | Marcas → Cor → Editar cores → paleta `V2 · destaque` |
| Tipos de leito | paleta `V2 · leitos` (ordinal) |
| Mapa | paleta `V2 · sequencial azul` |
| Fundo do dashboard | Dashboard → Sombreamento → `#f4f4f2` |
| Fundo do card | Contêiner → Sombreamento → `#ffffff` |
| Espaçamento | Layout → Espaçamento externo, múltiplos de 8 |
| Grade | Formatar → Linhas → Linhas de grade `#e4e4e1`, zero linhas verticais |
| Fontes | Formatar → Fonte da pasta de trabalho, mínimo 9pt |

Formatar **no nível da pasta de trabalho** (Formatar → Pasta de trabalho) antes de
formatar folha a folha. É o que impede a V2 de recair na inconsistência que a V1
demonstra.
