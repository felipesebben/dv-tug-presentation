# Dashboard V2 — especificação do "depois"

Documento de construção da **versão correta** do dashboard de ocupação hospitalar
(RS, 2019-2023). A V1 existe para ser desmontada; esta existe para mostrar o que sobra
quando cada decisão é tomada de propósito.

Entrada: `data/refined/sih_cnes_rs.hyper` (extrato regenerado — ver §7)
Tokens: `docs/v2/design_system.md` — **não redefina cor, fonte ou espaçamento
aqui**, use os papéis de lá
Saída: `tableau/dashboard_v2.twb`, **quatro abas**

> Espelha a estrutura de `docs/v1/spec.md` de propósito, pra que os dois documentos
> possam ser lidos lado a lado. Onde a V1 tem um placar de 46 pecados, esta tem a §6:
> o mapa de qual decisão daqui responde a qual pecado de lá.

---

## 1. Regras do jogo

1. **Toda métrica precisa levar a uma decisão do usuário.** Se não leva, sai. Não é
   economia de espaço — é a regra da métrica de vaidade dos UXers.
2. **Cinza é o padrão; cor é exceção.** Se tudo está destacado, nada está.
3. **A resposta antes da interação.** A aba 1 responde à pergunta principal sem que
   ninguém clique em nada. Filtro é refinamento, nunca pré-requisito.
4. **Um argumento por tela.** Cada aba tem uma frase que ela prova. Se não dá pra
   escrever essa frase, a aba não está pronta.
5. **A ressalva fica visível.** Taxa de ocupação é aproximação; isso aparece na tela,
   não numa nota de rodapé que ninguém lê.

---

## 2. Persona e pergunta

**Analista da Secretaria Estadual da Saúde (RS), montando pleito de recursos federais.**

Não aloca verba federal — **constrói a evidência que a pede**. Isso decide tudo o que
vem abaixo: cada aba é um passo do argumento, e o dashboard inteiro é um documento de
defesa que se atualiza sozinho.

A sequência que ele precisa percorrer:

| # | pergunta | aba |
|---|---|---|
| 1 | A rede está sob pressão, e está piorando? | **Panorama** |
| 2 | Onde? | **Território** |
| 3 | Que tipo de leito está faltando? | **Capacidade** |
| 4 | Quanto custa, e quanto custaria? | **Custo** |

Perguntas do briefing que **não** viram aba: perfil demográfico (§3 do briefing). Sexo e
raça/cor não informam alocação de leito e virariam decoração aqui. Idade sobrevive, mas
como **evidência dentro da aba Capacidade**, não como tela própria — a população
internada envelheceu (45,4 → 46,9 anos; 34,1% → 36,7% com 60+ entre 2019 e 2023), e isso
é argumento de demanda futura.

---

## 3. A frase de cada aba

Escritas antes de qualquer gráfico. Se um gráfico não ajuda a provar a frase da sua aba,
ele não entra.

| aba | a frase que ela prova |
|---|---|
| **Panorama** | "A demanda voltou 3,1% acima do patamar pré-pandemia; a capacidade SUS voltou ao mesmo patamar de 2019. 2023 é o ano mais pressionado da série." |
| **Território** | "A pressão está concentrada na região metropolitana, onde também está a capacidade — o interior tem folga que não é transferível." |
| **Capacidade** | "A expansão da pandemia foi quase toda de UTI e foi desfeita; leito pediátrico e obstétrico encolheram de forma permanente." |
| **Custo** | "10,8% das internações consomem 36% do gasto. Alta complexidade é onde o recurso federal faz diferença." |

---

## 4. Layout

Quatro abas, **1200 × 800 px cada** — cabe numa tela de 1080p sem rolagem. A V1 tinha
2600px de altura; a diferença não é estética, é a diferença entre ler e caçar.

Estrutura repetida nas quatro (Lei de Jakob — a segunda aba não deve precisar ser
aprendida):

```
┌─────────────────────────────────────────────────────────────┐
│ Ocupação hospitalar SUS · RS                    [abas]      │  cabeçalho 64px
│ Fonte: SIH-SUS + CNES · 2019-2023 · atualizado em __/__     │
├─────────────────────────────────────────────────────────────┤
│ [Ano ▾]  [Macrorregião ▾]  [+ mais filtros]                 │  filtros 48px
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   herói — o gráfico que prova a frase da aba                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│   apoio 1              │   apoio 2                          │
├─────────────────────────────────────────────────────────────┤
│ Taxa de ocupação = dias de permanência ÷ (leitos SUS ×      │  ressalva
│ dias do mês). Aproximação — pode passar de 100%.            │
└─────────────────────────────────────────────────────────────┘
```

**Máximo 3 filtros visíveis**, sempre no mesmo lugar, sempre no topo, aplicando à aba
inteira. `Ano` e `Macrorregião` em todas; o terceiro varia por aba. O resto atrás de
"+ mais filtros" (Lei de Hick).

---

## 5. Especificação por aba

Fonte de todas as medidas: `docs/foundations/metrics_dictionary.md` §4.1 e §4.2. **A taxa é sempre
`SUM(dias_permanencia_sus) / SUM(leito_dias_sus)`** — nunca `AVG(taxa_ocupacao_sus)`.

### Aba 1 · Panorama

**KPIs — 4 tiles, formato idêntico** (contra os 8 tiles em 8 estilos da V1):

| tile | valor 2023 | detalhe |
|---|---|---|
| Taxa de ocupação SUS | **60,0%** | delta vs 2019 (+1,6 p.p.) |
| Leitos SUS | **21.838** | delta vs 2019 (+0,3%) |
| Dias de permanência | **4,78 mi** | delta vs 2019 (+3,1%) |
| Internações | **804.504** | delta vs 2019 (+4,3%) |

Número em 28pt, rótulo em 10pt acima, delta em 9pt abaixo. Delta com seta e sinal —
nunca cor sozinha carregando o sentido. Um tile é `--acento` (a taxa); os outros três
em `--tinta`.

**Herói — capacidade × demanda, indexadas a 2019 = 100.** Linha, eixo único, 60 meses.

| | 2019 | 2020 | 2021 | 2022 | 2023 |
|---|---|---|---|---|---|
| Leitos SUS (índice) | 100 | 102,3 | 106,0 | 100,8 | **100,3** |
| Dias de permanência (índice) | 100 | 87,9 | 96,5 | 99,7 | **103,1** |

Duas séries: capacidade em `--serie`, demanda em `--acento`. Rótulo direto no fim de
cada linha, sem legenda. Anotação vertical discreta em março/2020. **Eixo Y começando
em zero** — a tesoura continua legível, e é justamente o contraste com a V1.

> Este é o gráfico que a V1 não tem. Não é um gráfico "melhor": é o único que responde
> à pergunta do briefing, porque o argumento não está no nível de nenhuma das duas
> séries, está na distância entre elas.

**Apoio 1 — taxa mensal.** Linha única, `--serie`, eixo de zero a 100%, faixa
sombreada em `--grade` entre mín e máx do mês. Mínimo 23,1% (mai/2020), máximo 35,4%
(nov/2023) na escala antiga; recalcular na escala SUS ao construir.

**Apoio 2 — permanência média.** 6,02 dias (2019) → 5,95 (2023). Praticamente estável,
e é isso que o gráfico precisa dizer: **a pressão não vem de internações mais longas,
vem de mais internações.** Um número com uma frase serve melhor que um gráfico.

### Aba 2 · Território

**Herói — mapa coroplético, taxa SUS por município.** Rampa `V2 Sequencial Azul`, um
hue, claro = baixo. Sem segundo mapa competindo (a V1 tinha dois lado a lado).

**Apoio 1 — ranking dos 15 maiores municípios por leitos SUS**, barra horizontal
ordenada por taxa. Barras em `--marca-neutra`; as acima de 85% em `--acento`.
Rótulo direto no fim de cada barra. Âncoras 2023:

| município | leitos SUS | taxa |
|---|---|---|
| Porto Alegre | 281 | **80,6%** |
| Sapucaia do Sul | 209 | 73,4% |
| São Leopoldo | 212 | 65,8% |
| Canoas | 273 | 65,1% |
| Rio Grande | 211 | 64,5% |

**Apoio 2 — a distribuição.** Mediana municipal 37,2%, máximo 90,9%, 225 municípios,
só 2 acima de 85%. Histograma simples com a mediana marcada.

> A tensão que o mapa sozinho esconde: o interior tem folga, mas folga em município de
> 8 leitos não absorve demanda de Porto Alegre. O texto de apoio precisa dizer isso —
> caso contrário o mapa sugere uma redistribuição que não existe.

**Terceiro filtro da aba:** `Município`.

### Aba 3 · Capacidade

**Herói — leitos SUS por tipo, 2019-2023.** Área empilhada ou linhas múltiplas, paleta
`V2 Leitos` (4 tons + Outros). Média mensal estadual:

| tipo | 2019 | 2021 | 2023 | leitura |
|---|---|---|---|---|
| Clínico | 8.857 | 9.362 | 9.382 | estável |
| Cirúrgico | 4.373 | 3.914 | 4.028 | não recuperou |
| **Complementar (UTI)** | **2.168** | **3.743** | **2.404** | +73% no pico, desfeito |
| Pediátrico | 2.255 | 1.979 | 1.984 | −12% permanente |
| Obstétrico | 1.971 | 1.819 | 1.735 | −12% permanente |
| Outras especialidades | 2.722 | 2.726 | 2.518 | — |
| Hospital dia | 298 | 326 | 331 | — |

Sete tipos, teto de 4 + Outros: mantenha **Clínico, Cirúrgico, Complementar,
Pediátrico**; o resto agrupa em Outros (`--marca-neutra`). Complementar recebe
`--acento` — é a série que carrega o argumento.

Pico real de UTI: **4.106 leitos** (2021) contra 2.188 em 2019. Anotar no gráfico.

**Apoio 1 — envelhecimento.** Idade média 45,4 → 46,9; 60+ de 34,1% para 36,7%. Duas
barras, ou um slope. É a evidência de demanda futura.

**Apoio 2 — proporção SUS.** 77,1% dos leitos cadastrados são SUS. Contexto para o
denominador, e responde à pergunta 4 do briefing.

**Terceiro filtro da aba:** `Tipo de leito`.

### Aba 4 · Custo

**Herói — gasto total e nº de internações por ano**, indexados a 2019 = 100, eixo único.

| ano | internações | gasto (R$ mi) | médio | **mediana** |
|---|---|---|---|---|
| 2019 | 771.568 | 1.131,6 | 1.466,65 | 639,08 |
| 2020 | 675.603 | 1.186,7 | 1.756,45 | 689,11 |
| 2021 | 709.893 | **1.567,3** | 2.207,87 | 731,46 |
| 2022 | 777.938 | 1.298,3 | 1.668,85 | 679,86 |
| 2023 | **804.504** | 1.361,3 | 1.692,09 | 688,20 |

2021 custou 38% mais que 2019 com **menos** internações — alta complexidade da COVID.

> **Use a mediana, não a média.** Média R$ 1.692 contra mediana R$ 688 em 2023: a
> distribuição é fortemente assimétrica, e a média descreve mal a internação típica.
> Onde a média aparecer, ela vem rotulada como média e acompanhada da mediana.

**Apoio 1 — concentração por complexidade (2023):**

| complexidade | internações | % | gasto (R$ mi) | % | médio |
|---|---|---|---|---|---|
| Média | 717.574 | 89,2% | 868,0 | 63,8% | 1.209,59 |
| **Alta** | 86.930 | **10,8%** | **493,3** | **36,3%** | 5.674,93 |

Duas barras 100% empilhadas, uma de volume e uma de gasto. O descasamento entre elas
**é** o gráfico.

**Apoio 2 — custo médio por dia de permanência**, ligando custo e ocupação.

> ⚠ **Erro de dado a corrigir na exibição:** `complexidade_desc` vem como
> `"Méida Complexidade"` (typo na origem) e `" Alta Complexidade"` (espaço à esquerda).
> Criar um campo calculado com os rótulos corretos — não exibir cru, e não corrigir na
> origem, que é dado público.

**Terceiro filtro da aba:** `Complexidade`.

---

## 6. Mapa de correções — qual pecado da V1 cada decisão responde

Roteiro do workshop. Colunas 1-2 vêm do placar da §7 de `docs/v1/spec.md`.

| # V1 | pecado | correção na V2 |
|---|---|---|
| 1 | Proximidade — filtros longe do alvo | 3 filtros, topo, escopo da aba inteira |
| 2 | Similaridade — 8 KPIs em 8 estilos | 4 tiles, formato idêntico |
| 3 | Região comum — tudo com borda | Cards brancos sobre plano cinza, zero bordas |
| 4 | Ponto focal — tabelão e 2 mapas competindo | Um herói por aba; um mapa só |
| 5 | Lei de Hick — 11 filtros, 17 ícones | 3 filtros + "mais filtros"; sem barra de ícones |
| 27 | Consistência — tipografia por folha | Formatação no nível da pasta de trabalho |
| 29 | Rolagem — 2600px | 800px, sem rolagem |
| 30 | Sem persona | Analista da SES montando pleito (§2) |
| 33 | Cor redundante — uma cor por categoria | Cinza padrão, `--acento` só no argumento |
| 34 | Rótulo vertical a 90° | Barras horizontais na aba 2 |
| 35 | Dispersão espremida 1200×180 | Dispersão cortada |
| 36-38 | Pizzas | Cortadas — nenhuma pizza na V2 |
| 79 | Mapa divergente verde-amarelo-vermelho | Rampa sequencial de um hue |
| — | Denominador errado (só no dicionário) | Taxa SUS ponderada, 30,8% → 55,8% |

O item **32 (eixo truncado) não entra** — não chegou a ser construído na V1. Ver
`docs/v1/as_built.md` §3.

> A linha mais importante é a última, e ela **não** é um item do placar: o pecado que
> nenhum princípio de design pega. A V1 podia ter sido linda e ainda estaria dividindo
> demanda SUS por leito privado. Vale abrir ou fechar a apresentação com isso.

---

## 7. Ordem de construção

1. **Extrato** — já regenerado com as colunas SUS (§4.1 do dicionário). Verificado:
   taxa estadual 0,5585, 38 linhas nulas, `taxa_ocupacao` da V1 intacta.
2. **Paleta** — copiar `tableau/Preferences.tps` para o repositório do Tableau e
   reiniciar, **antes** de criar qualquer folha.
3. **Formatação da pasta de trabalho** — fonte, tamanhos e linhas de grade em
   *Formatar → Pasta de trabalho*, antes da primeira folha. É o que impede a
   inconsistência da V1 de voltar por acúmulo.
4. **Campos calculados**, uma vez, nomeados: `Taxa de ocupação SUS`, `Índice
   capacidade`, `Índice demanda`, `Complexidade (rótulo)`.
5. **Aba 1**, completa e revisada, antes de começar a 2 — a estrutura dela é o gabarito
   das outras três.
6. Abas 2, 3, 4.
7. **Aba 1 de novo**, depois que as outras existirem. Sempre sobra coisa pra tirar.

Se o tempo apertar: as abas 1 e 2 sozinhas sustentam a demonstração. A 4 é a que mais
depende de dado com ressalva (média × mediana) e a primeira que eu cortaria.
