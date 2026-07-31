# Camada de orientação da V2 — tour, "como usar" e glossário

> **Por que existe.** Fecha a última linha aberta de `docs/uxers_guidance.md` (bloco
> Experiência do Usuário, Nielsen — *ajuda a reconhecer/diagnosticar/recuperar de erros +
> documentação*): **"dashboard sem glossário e sem botão de suporte → dashboard com
> glossário e botão de suporte"**. É requisito com fonte, não ideia nova.
>
> **E ganhou uma segunda função.** A revisão de 29/07/2026 tirou dos subtítulos toda
> afirmação editorial, porque um subtítulo que afirma conclusão é desmentido pelo primeiro
> filtro que o usuário aplica. As conclusões não deixaram de ser verdadeiras nem de ser
> importantes — elas mudaram de lugar. **Este é o lugar.** Sem esta camada, a V2 troca um
> defeito (título que mente) por outro (dashboard que não explica nada).

Três peças, especificadas juntas porque se sobrepõem muito: o tour ensina a ordem de
leitura, o "como usar" responde perguntas de mecânica, o glossário define os números. A
mesma frase serve às três em contextos diferentes, então cada frase vive **num** lugar e é
referenciada nos outros.

---

## 1. Regra de procedência: o glossário não é fonte de verdade

`docs/metrics_dictionary.md` é a **definição-de-record** de todo número do projeto. O
glossário aqui é o **subconjunto voltado ao usuário** dele — linguagem de quem lê o
dashboard, não de quem o constrói.

| | `metrics_dictionary.md` | glossário (esta camada) |
|---|---|---|
| público | quem constrói as planilhas | quem lê o dashboard |
| conteúdo | SQL exato, grão, validações, todas as armadilhas | o que o número significa e a ressalva que muda a leitura |
| tamanho | ~700 linhas | 16 verbetes, 2–4 linhas cada |
| em conflito | **vence** | corrige-se |

**Nunca acrescente aqui uma definição que não exista lá.** Se um número precisa de
verbete e não está no dicionário, o caminho é escrever no dicionário primeiro. Duas fontes
de verdade sobre o que uma métrica mede é exatamente o problema que a V1 demonstra por
ausência.

---

## 2. Botão de suporte — o que "suporte" quer dizer aqui

A linha dos UXers pede "botão de suporte". Num dashboard interno de secretaria isso não é
um chat de atendimento; é **um caminho claro para uma pessoa** quando o dado não fecha.
Três destinos, nesta ordem de probabilidade de uso:

1. **"Como usar"** — mecânica: o que cada aba responde, como o filtro age, como ler o
   índice.
2. **"Glossário"** — "esse número quer dizer o quê?".
3. **"Falar com quem mantém"** — quem responde por este painel, e o que informar ao pedir
   ajuda (aba, filtro aplicado, número que pareceu errado). É o que transforma "o dashboard
   está errado" em um relato reproduzível.

Os três ficam **no cabeçalho, sempre visíveis, sempre no mesmo lugar** — não num rodapé
que ninguém rola até. Custam três botões, e a Lei de Hick se paga porque nenhum deles é
uma escolha analítica: são saídas de emergência.

---

## 3. Tour guiado — 6 passos

Aparece na primeira visita como **convite não-modal** ("primeira vez aqui? ver o tour"),
não como modal que sequestra a tela. Modal de boas-vindas é o padrão que todo mundo fecha
sem ler, e fechá-lo sem ler é pior que não ter tour: ensina o usuário a descartar ajuda.
Pode ser reaberto a qualquer momento pelo cabeçalho.

O tour ensina **ordem de leitura**, que é a única coisa que um dashboard de quatro abas não
consegue dizer sozinho.

| # | Alvo | O que ensina |
|---|---|---|
| 1 | — | **Para que serve.** Este painel existe para montar um pleito de recurso federal: mostrar que a rede SUS do RS está sob pressão e onde. Não decide alocação; produz a evidência que a pede. |
| 2 | gráfico herói | **O achado.** UTI e rede em cima do mesmo eixo. Entre 2019 e 2021 a rede *caiu* e a UTI *subiu* a 111,9%. Quem olhasse só a média teria concluído que 2021 foi mais folgado que 2019. |
| 3 | faixa de KPIs | **Todo número tem período.** Cada tile diz de que recorte ele fala. Se o filtro muda, o tile muda — e diz que mudou. |
| 4 | barra de filtros | **Dois controles mudam tudo na aba.** *Período* — e "pandemia" não é um recorte de data qualquer, é o intervalo em que as duas taxas andam em direções opostas. *Visão* troca a população entre rede e UTI; em UTI dois terços do mapa ficam em branco. |
| 5 | abas | **A ordem de leitura.** Panorama (o quê) → Território (onde) → Capacidade (que tipo de leito) → Custo (quanto). Cada aba responde uma pergunta e passa a próxima adiante. |
| 6 | cabeçalho | **Onde pedir ajuda.** Glossário para os números, "como usar" para a mecânica, e uma pessoa para o resto. |

---

## 4. "Como usar" — conteúdo

### O que cada aba responde

| aba | pergunta | frase que ela prova |
|---|---|---|
| **Panorama** | A rede está sob pressão? | A pressão existe e está concentrada na UTI — o agregado a esconde. |
| **Território** | Onde? | A folga é do interior e não é transferível: capacidade ociosa num município de 8 leitos não absorve a demanda de Porto Alegre. |
| **Capacidade** | Que tipo de leito? | UTI e cirúrgico são os tensionados; a expansão da pandemia foi de UTI e foi desfeita. |
| **Custo** | Quanto, e onde vai? | O gasto cresce mais rápido que o volume, e o descolamento é a alta complexidade. |

### Como os filtros agem

- **Período** vale para a **aba inteira** — todos os gráficos e todos os KPIs. Não há filtro
  que valha só para um gráfico: era exatamente o defeito da V1, onde 8 de 11 filtros
  atingiam alvos diferentes sem dizer quais.
- Trocar o período **recalcula** cada taxa como `soma dos dias ÷ soma dos leito-dias` no
  recorte novo. Não é média das médias — o que significa que a taxa de um recorte de dois
  anos não é a média das taxas dos dois anos, e está certo assim: um mês com mais leitos
  pesa mais.
- **Região intermediária** (8) fica visível; **região de saúde** (30) fica atrás de "mais
  filtros". As duas são geografia real, de granularidades diferentes: região de saúde é a
  unidade de planejamento do SUS, região intermediária é recorte do IBGE.
- Quando um filtro está fora do padrão, aparece **como desfazer**. (Nielsen — prevenção de
  erros; a linha dos UXers pede breadcrumb para desfazer filtro.)

### A visão rede × UTI

Um controle troca a **população de que a aba trata** — KPIs, mapa, dispersão e barras
passam a falar de UTI em vez da rede inteira. Não é conveniência: em visão UTI o Território
responde uma pergunta que a visão rede não consegue fazer — **onde a terapia intensiva
simplesmente não existe**. Só 87 dos 270 hospitais e **59 dos 225 municípios** com leito têm
alguma UTI SUS, então dois terços do mapa ficam em branco, e esse branco é o achado.

Disponível em Panorama e Território, que são as abas onde "ocupação" é a métrica principal.
Capacidade compara os tipos de leito entre si e Custo trata de gasto, então lá o controle
seria inerte — e filtro que não faz nada é o defeito que tiramos da V1.

As duas linhas do gráfico herói **continuam mostrando rede e UTI juntas** em qualquer
visão, porque a comparação entre elas é o argumento inteiro.

### O gráfico da tesoura: a distância **não** é folga

Este é o ponto mais fácil de ler errado no painel inteiro, e já foi lido errado — a pergunta
que originou esta seção foi exatamente "se a UTI chegou a 111,9% em 2021, por que a demanda
não passou da capacidade no gráfico?".

**A resposta curta:** passou — na UTI. Em 2021, indexando a 2019 = 100:

| | capacidade | demanda |
|---|---|---|
| rede | 106,0 | 96,5 |
| **UTI** | **99,6** | **146,4** |

A visão de rede esconde porque **UTI era 6,5% dos leitos SUS em 2021**. Os outros 93,5% são
enfermaria, e esvaziaram quando as eletivas foram suspensas. O agregado é uma média
ponderada dominada pela parte que ficou quieta.

**A resposta longa, que é a que importa:** mesmo na visão de rede, ler "linha de capacidade
acima da linha de demanda" como "sobra capacidade" está **errado**. As duas séries são
indexadas cada uma contra a *própria* base de 2019, em unidades diferentes — leitos e
diárias. Capacidade em 106 e demanda em 96,5 quer dizer "a capacidade cresceu 6% e a
demanda caiu 3,5%, cada uma em relação a si mesma". Não diz nada sobre folga absoluta. A
folga absoluta é a taxa de ocupação: 53,2%.

**O ponto de cruzamento não significa nada.** O que a distância vertical codifica é a
*variação* da ocupação: `demanda ÷ capacidade × taxa-base` reproduz a taxa exatamente
(146,4 / 99,6 × 76,1% = 111,9%).

Por isso o gráfico se chama **"de onde veio a variação da ocupação"** e não "capacidade ×
demanda". O valor dele é decomposição — dizer que a ocupação subiu porque a demanda subiu, e
não porque a capacidade encolheu, que é o que a linha de ocupação sozinha não conta. A
ressalva está escrita no subtítulo, na tela.

> Vale de palco: este erro estava no nosso próprio painel corrigido, e foi encontrado por
> uma pergunta de leitor, não por revisão de design. Mesma família do denominador errado da
> V1 — conta certa respondendo pergunta que ninguém fez.

### Alvos de ocupação — 85% e 95%

O painel marca **85% como atenção** e **95% como crítico**, nas duas visões.

- **Vêm de onde:** 85% é a "regra de ocupação" da literatura de crise de leito (Bagust,
  Place & Posnett, *BMJ* 1999). **Não é alvo oficial da SES-RS nem do Ministério** — precisa
  de validação clínica antes de virar padrão na apresentação.
- **A rede não cruza, e isso é a informação.** No estado a rede fica em 60,0%; a UTI passou
  dos dois limiares em 2020–21. A régua é a mesma nas duas para que o leitor tenha um
  modelo mental só.
- **Só taxa tem alvo.** Leitos e internações não recebem limiar: alvo implica direção que se
  persegue, e ninguém tem meta de quantas pessoas adoecem.

### Como ler o gráfico indexado — a parte que precisa de explicação

Dois gráficos usam índice: capacidade × demanda, e internações × permanência.

**O problema que o índice resolve:** comparar 21.838 leitos com 4,78 milhões de dias de
permanência num gráfico só é impossível — a série menor vira uma linha reta no chão. Índice
põe as duas na mesma escala: cada série vira "quanto mudou desde o ano-base", e o ano-base
vale 100.

**Como ler:** 100 = igual ao ano-base. 103,1 = 3,1% acima. 87,9 = 12,1% abaixo. **A
distância entre as duas linhas é a leitura** — não o nível de nenhuma delas.

**Por que o eixo começa em 100 e não em zero**, contrariando a regra do próprio design
system: num índice, **100 *é* o zero** — é o ponto onde nada mudou. Um eixo de zero
comprimiria a faixa de 88 a 106 nos 6% de cima da altura e apagaria justamente o efeito que
o gráfico existe para mostrar. A regra do eixo zerado continua valendo para **toda taxa e
toda barra** — inclusive para o gráfico herói, que é de taxas e por isso começa em zero.

> Vale dizer em voz alta na apresentação: esta é a única exceção do sistema, ela é
> declarada, e a linha de base está desenhada na tela. Exceção anotada é decisão de
> projeto; exceção silenciosa é o eixo truncado da V1.

### Por que a ocupação passa de 100%

A taxa é `dias de permanência ÷ (leitos × dias do mês)` — a aproximação que o próprio
DATASUS documenta. Dois motivos fazem ela passar de 100%, e nenhum é erro de conta:

1. **Rotatividade dentro do mês** — dois pacientes podem usar o mesmo leito no mesmo dia.
2. **O cadastro de leitos é uma foto mensal** — se a capacidade real subiu no meio do mês,
   o denominador está desatualizado.

Na UTI de junho de 2021 isso deu **131,9%**, e é leitura correta: a demanda passou da
capacidade cadastrada. Não se corrige — se legenda.

---

## 5. Glossário — 16 verbetes

Cada verbete: o que é, e a ressalva que muda a leitura. Referências entre parênteses
apontam para a seção de `metrics_dictionary.md` que manda.

| termo | definição | ressalva |
|---|---|---|
| **Taxa de ocupação SUS (rede)** | Dias de permanência de pacientes SUS ÷ (leitos SUS × dias do período). | Denominador é **só leito SUS**. Dividir por todos os leitos mede demanda SUS contra capacidade que o paciente SUS não pode ocupar — é o erro que a V1 comete (§4). |
| **Taxa de ocupação de UTI** | Diárias de UTI ÷ (leitos de UTI/UCO × dias do período). | Numerador vem do contador próprio de diárias de UTI, não da especialidade do leito — no RS **nenhuma** internação é classificada como UTI naquele campo (§4.3). |
| **Leitos SUS** | Média mensal de leitos cadastrados no CNES como SUS. | Média mensal, não total acumulado. São 77,1% dos leitos cadastrados no RS. |
| **Internações (AIH)** | Contagem de autorizações de internação hospitalar. | **Não é contagem de pacientes.** Uma pessoa internada três vezes conta três (§2). |
| **Dias de permanência** | Soma das diárias de internação. | É o numerador da taxa de ocupação. Não é "dias por paciente". |
| **Permanência média** | Dias de permanência ÷ internações. | Cai quando a rede gira mais rápido, o que pode ser bom (eficiência) ou ruim (alta precoce) — o número sozinho não distingue. |
| **Índice (base = 100)** | Cada série reescalada para que o ano-base valha 100. | Lê-se a **distância entre as linhas**, não o nível. O eixo começa em 100 porque num índice 100 é o zero (ver §4). |
| **Complementar** | Categoria do CNES que agrupa UTI, unidade coronariana, cuidados intermediários e isolamento. | **Não é sinônimo de UTI.** Em 2023, 1.839 dos 2.404 leitos complementares são UTI/UCO; o resto é cuidado intermediário e isolamento (§4.4). |
| **Tipo de leito** | Classificação do CNES em 7 categorias. | O SIH classifica internação em 13 especialidades no RS, vocabulário diferente. A taxa por tipo usa um crosswalk documentado e é aproximação (§4.4). |
| **Hospital dia** | Leito de internação que não pernoita. | Marca ~18% de ocupação **e não está ocioso**: gira dentro do mesmo dia, então leito-*dia* é a unidade errada para ele. Não compare com os outros tipos (§4.4). |
| **Complexidade** | Média ou alta, conforme a tabela de procedimentos do SUS. | O dicionário da fonte grafa "Méida Complexidade"; corrigido só na exibição, nunca na chave de junção. |
| **Valor da AIH** | Valor aprovado da autorização, em reais nominais. | É **valor aprovado, não custo real**, e **não está corrigido pela inflação** — somar 2019 com 2023 direto subestima o começo da série. Distribuição assimétrica: use a mediana (§2). |
| **Região de saúde / Região intermediária** | 30 e 8 agrupamentos de municípios, respectivamente. | Região de saúde é a unidade de planejamento do SUS; região intermediária é recorte estatístico do IBGE. Não são hierarquia uma da outra. |
| **Ocupação acima de 100%** | A taxa pode passar de 100%. | Rotatividade de leito dentro do mês e cadastro mensal de capacidade. Leitura válida: a demanda passou da capacidade cadastrada (§"Ocupação acima de 100%"). |
| **Alvo de ocupação (85% / 95%)** | 85% marca atenção, 95% crítico — mesma régua na rede e na UTI. | Vem da "regra de ocupação" (Bagust, Place & Posnett, *BMJ* 1999). **Não é alvo oficial da SES-RS nem do Ministério.** A rede fica em 60% e nunca cruza — isso é a informação. Só taxa tem alvo. |
| **Visão: rede × UTI** | Troca a população de que a aba trata. | A UTI é 8,4% dos leitos e existe em 59 dos 225 municípios com leito; em visão UTI dois terços do mapa ficam em branco, e essa ausência é o achado. |

---

## 6. O que isto vira no Tableau

O wireframe implementa a camada com sobreposições em HTML. No workbook, o equivalente:

| peça | como no Tableau |
|---|---|
| Botões do cabeçalho | Objeto **Botão de navegação** ou **Mostrar/ocultar contêiner** (um contêiner flutuante por painel) |
| "Como usar" e Glossário | Contêiner flutuante com objeto **Texto**, oculto por padrão, botão X para fechar |
| Tour guiado | Sem equivalente nativo. Opções: (a) uma **aba "Comece aqui"** como primeira planilha do dashboard — mais simples e o que recomendamos; (b) sequência de contêineres mostrar/ocultar encadeados, frágil de manter |
| "Falar com quem mantém" | Objeto **Botão** com ação de URL (`mailto:`) |
| Desfazer filtro | Botão com ação **Redefinir filtros**, visível ao lado dos filtros |
| Tooltip por métrica | Dica de ferramenta da planilha, com a linha do glossário do número — é onde o glossário chega sem exigir clique |

A recomendação (a) para o tour existe porque um tour encadeado em contêineres
mostrar/ocultar é exatamente o tipo de construção que ninguém consegue manter depois. Uma
aba "Comece aqui" entrega 80% do valor — ordem de leitura e o que cada aba responde — e
sobrevive à próxima pessoa que abrir o workbook.
