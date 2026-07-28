# Dashboard V1 — especificação do "antes" (propositalmente ruim)

Documento de construção da **primeira versão** do dashboard de ocupação hospitalar (RS,
2019-2023). Esta versão é ruim de propósito: ela existe para ser destruída ao vivo pelos
dois apresentadores de UX no TUG, princípio a princípio.

Entrada: `docs/data_briefing.md` + `data/refined/sih_cnes_rs.hyper`
Saída: um workbook Tableau (`tableau/dashboard_v1.twb`, exportado como `.twbx` pra
compartilhar — ver `tableau/README.md`) com **uma única aba de dashboard**.

Referência dos princípios: *Learn Design Driven Data Visualization* — Aurélien Vautier /
Dataviz Clarity, CC BY-NC-ND 4.0. O PDF fica em `references/` (fora do versionamento).
As referências `[p.NN]` neste documento apontam para os slides do deck.

> **Este é o documento de projeto, não o inventário do que existe.** A V1 foi construída e
> diverge desta especificação em alguns pontos — com destaque para o **eixo Y da série
> temporal, que ficou automático** em vez de fixado em 0,26–0,34, e para o **escopo dos
> filtros**, aplicado de forma aproximada. O registro do artefato real é
> **`docs/dashboard_v1_as_built.md`**; onde os dois discordarem, o *as-built* descreve o
> workbook e este documento descreve a intenção. A argumentação daqui continua sendo o
> material de redesign.

---

## Refinamento dos UXers — leia antes da seção 1

A dupla de UX revisou o deck do Aurélien e devolveu `docs/uxers_guidance.md`: um
filtro de prioridade sobre o mesmo material, dividido em três blocos —
**Fundamentos de Design**, **Experiência do usuário**, **Acessibilidade** — cada um
com pares antes/depois. Esta versão do documento incorpora esse filtro:

- Cada região do wireframe (seção 5) agora carrega **1 princípio primário + no
  máximo 1-2 secundários coerentes**, em vez das 4-5 violações empilhadas da
  primeira passada — objetivo explícito dos UXers: **não virar caricatura**.
- Os três blocos estão espalhados pelo wireframe, não concentrados em "Fundamentos
  de Design": **N** e **I** carregam Experiência do Usuário, **E** é a região-âncora
  de Acessibilidade, o resto segue primariamente Fundamentos de Design (Gestalt).
- Região nova: **N — barra de navegação**. A Lei de Jakob (reconhecer > lembrar)
  não tinha nenhum lugar dedicado na primeira passada, e é uma das "Top 5 UX Laws"
  que os UXers marcaram como prioridade máxima (junto com Proximidade, Lei de Hick,
  Ponto Focal e Prägnanz — todas já cobertas em outras regiões).
- A tabela de atributos pré-atentivos (seção 4.1) permanece como referência, mas os
  UXers pediram pra **cortar seu peso cognitivo** — não é mais tratada como pilar
  organizador do documento.

Onde este refinamento e o deck do Aurélien divergem no mesmo princípio (ex.: o par
de cores mais hostil a daltonismo — verde/vermelho pro Aurélien, azul/vermelho pros
UXers), `uxers_guidance.md` vence por ser a camada de decisão mais recente; o V1 usa
os dois, um em cada mapa da região E, porque ambos são problemas reais de CVD.

---

## 1. Regras do jogo

Um "dashboard ruim" de apresentação só funciona se for **plausível**. Se virar caricatura,
a plateia ri e não se reconhece. Se for sutil demais, ninguém enxerga do fundo da sala.
As regras abaixo mantêm esse equilíbrio:

1. **Os números têm que estar certos.** Nada de dado inventado ou errado. O que está
   quebrado aqui é o *design*, não a pipeline. A única exceção é a seção 9 do deck
   (uso enganoso), onde a mentira é de **apresentação** — eixo truncado, escala, ordenação —
   e não de cálculo.
2. **Todo pecado tem que ser reversível ao vivo.** Cada violação da lista da seção 7 precisa
   ter uma correção demonstrável em Tableau em menos de 2 minutos. Se não dá pra consertar
   no palco, não entra.
3. **Nada de erro bobo de digitação nosso.** Rótulo trocado ou número quebrado tira o foco
   do argumento — a plateia vai discutir o bug, não o princípio. (Exceção autorizada: o
   `complexidade_desc` da fonte vem com "Méida Complexidade", com typo. Esse a gente
   **mantém**, porque ele ilustra "confiabilidade do dado é parte da narrativa" [p.69].)
4. **1 princípio primário por região da tela, no máximo 1-2 secundários coerentes.**
   Empilhar cinco violações soltas no mesmo gráfico impede a dupla de UX de isolar um
   princípio de cada vez — e vira caricatura. Ver o mapa por região refinado na seção 5.
5. **O dashboard tem que carregar.** Lento é ótimo (é o argumento da seção 10 do deck),
   travado não é — a demo tem que rodar.

---

## 2. O que a V1 "quer" ser (a persona do erro)

Vale escrever isso no slide de abertura da apresentação, porque explica *por que* o
dashboard ficou assim — e todo mundo na plateia já viveu isso:

> "A Secretaria pediu um **painel gerencial integrado** de ocupação hospitalar.
> Perguntamos quem usa: *'todo mundo'*. Perguntamos o que precisa responder:
> *'a gente quer ver tudo'*. Levantamos 30 indicadores numa reunião de uma hora.
> Ninguém desenhou nada antes de abrir o Tableau."

Isso ataca de saída o deck em três pontos:

- **"Cockpit" é desistir do perímetro** [p.112] → daí vem a abundância de dados [p.113]
  que o usuário vai ter que filtrar depois [p.114].
- **Produto feito pra todo mundo é produto pra ninguém** [p.91].
- **Mudar de ferramenta não muda a cabeça** [p.94] — o Tableau não salva ninguém de pular
  a etapa de *Define*.

A V1 não tem persona, não tem pergunta única e não tem processo. Todo o resto decorre disso.

---

## 3. Layout da página

**Tamanho fixo: 1200 × 2600 px.** Isso é intencional: força rolagem em qualquer tela.
O deck cita a NN/g — a atenção cai 68% depois da primeira dobra [p.90] — então tudo que
realmente responde à pergunta de negócio vai **abaixo da dobra**.

A ordem de leitura está deliberadamente invertida: o topo (o imóvel mais caro da tela,
onde os padrões F e Z começam [p.86]) recebe o conteúdo de menor valor; a série temporal
de ocupação — o insight de verdade, a pergunta nº 1 do briefing — fica no rodapé.

O rail lateral corre a **altura inteira** da página (como em qualquer app de BI real), e a
appbar corre o topo da coluna de conteúdo — os dois menus visíveis ao mesmo tempo.

```
┌──────┬─────────────────────────────────────────────────────────────────────────────┐
│ ▤    │ SES/RS · BI Corporativo / Assistência / Ocupação Hospitalar   ▤ ▤ ▤ ▤ ▤     │ N
│ ▤ r  ├─────────────────────────────────────────────────────────────────────────────┤
│ ▤ a  │ [logo] PAINEL GERENCIAL DE MONITORAMENTO ESTRATÉGICO INTEGRADO      [logo]  │ A
│ ▤ i  │        DE OCUPAÇÃO HOSPITALAR — SIH/SUS × CNES — RS — 2019 A 2023   [logo]  │
│ ▤ l  │        v1.4_FINAL_rev2_ok                     (fundo em degradê azul→roxo)  │
│ ▤    ├─────────────────────────────────────────────────────────────────────────────┤
│ 12×  │  ← a partir daqui, as regiões B..J empilham dentro da coluna de conteúdo     │
│ (FS) │                                                                             │
└──────┴─────────────────────────────────────────────────────────────────────────────┘
  rail de altura inteira (12 ícones, item ativo marcado, avatar no pé)
  + appbar no topo do conteúdo (+5 ícones) = 17 destinos, nenhum de "ajuda"
```

O empilhamento das demais regiões, dentro da coluna de conteúdo:

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ [logo] PAINEL GERENCIAL DE MONITORAMENTO ESTRATÉGICO INTEGRADO DE     [logo][logo] │ A
│        OCUPAÇÃO HOSPITALAR — SIH/SUS × CNES — RS — 2019 A 2023                     │
│        v1.4_FINAL_rev2_ok                          (fundo em degradê azul→roxo)    │
├────────────────────────────────────────────────────────────────────────────────────┤
│ [Ano▾] ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐            │ B
│        │30,8% ││3739506││22.6M ││107,9 ││6545187││6,05% ││ 228  ││ 287  │ 8 cores  │
│        │ TAXA ││Intern.││ dias ││leitos││ R$   ││óbito ││munic.││hosp. │ 8 tam.   │
│        └──────┘└──────┘└──────┘└──────┘└──────┘└──────┘└──────┘└──────┘            │
│        filtro e KPIs no mesmo espaço do header — "região comum" quebrada           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ FILTROS  [Faixa de valor ▾][Motivo de saída ▾]   → controlam a DISPERSÃO (G), abaixo │ I·1
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ██ TABELÃO — 228 municípios × 60 meses × 6 medidas ██  (grid escuro, sem ordenação) │ C
│ (container de 300px de altura, scroll interno, fundo = mesmo cinza do resto da      │
│  página — nenhum contraste de card)                                                 │
├──────────────────────┬──────────────────────┬──────────────────────────────────────┤
│  PIZZA (estilo 3D)   │  ROSCA               │  PIZZA                               │ D
│  58 especialidades   │  Sexo (2 fatias)     │  Raça/cor (6 fatias)                 │
│  de leito (57+NULL)  │  + % com 4 casas     │  incl. "Sem Informação"              │
│  legenda 58 itens,   │                      │  sem explicação                      │
│  fonte 10px          │                      │                                      │
├──────────────────────┴───────────┴──────────────────────────────────────────────────┤
│ REFINAR  [Complexidade ▾ (escuro/escuro)][Caráter ▾]  → controlam IDADE (F1) e G     │ I·2
├──────────────────────────────────┬──────────────────────────────────────────────────┤
│  MAPA 1 — taxa de ocupação       │  MAPA 2 — nº de internações                     │ E
│  paleta verde→vermelho           │  paleta azul→vermelho                           │
│  (dois mapas competindo pelo mesmo olhar, 9 passos cada)                            │
├──────────────────────────────────┼──────────────────────────────────────────────────┤
│  BARRAS — idade 0 a 99           │  BARRAS — municípios em ordem ALFABÉTICA        │ F
│  (100 barras, uma por idade)     │  rótulos rotacionados 90°, nenhuma barra        │
│                                   │  destacada (Porto Alegre igual às demais)       │
├──────────────────────────────────┴──────────────────────────────────────────────────┤
│ LEITOS  [Tipo de leito ▾][Especialidade ▾]  → controlam a PIZZA D1, MUITO acima      │ I·3
├─────────────────────────────────────────────────────────────────────────────────────┤
│  DISPERSÃO — valor AIH × dias de permanência                                       │ G
│  (3,7 mi de marcas espremidas em 1200 × 180 px)                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~  DOBRA APROXIMADA DA TELA (1080p)  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ PACIENTE  [Sexo ▾][Raça/cor ▾]  → controlam as ROSCAS D2/D3, MUITO acima            │ I·4
├─────────────────────────────────────────────────────────────────────────────────────┤
│  SÉRIE TEMPORAL — taxa de ocupação mensal 2019-2023                                │ H
│  (o insight de verdade, enterrado; eixo Y automático → não construído)              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ FILTROS GLOBAIS  [Município ▾ (228)][Hospital ▾ (287)]                              │ I·5
│ → controlam TABELÃO (C), MAPAS (E) e BARRAS (F2) — todos muito acima                 │
│ 10 filtros em 5 blocos, nenhum perto do que controla; +17 ícones no menu (N)         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                    (rodapé vazio — sem fonte, sem data)              │ J
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Inventário de princípios utilizáveis (referência)

Este é o catálogo dos princípios do deck que dá pra **aplicar** (na V2) ou **violar de
propósito** (na V1) neste dashboard. Ele também é a **chave das referências `[p.NN]`** que
aparecem no resto do documento — quando a especificação diz `[p.85]`, é este slide.

O deck separa duas famílias que trabalham juntas [p.36]: **atributos pré-atentivos** trazem
clareza (destacam *um* ponto), **princípios de Gestalt** organizam a complexidade (agrupam
*muitos*). O resto são regras de carga cognitiva, contexto, layout, honestidade e performance.

> Este inventário é só o deck do Aurélien — os princípios que vêm do refinamento dos
> UXers (Lei de Jakob, heurísticas de Nielsen, métrica de vaidade, Lei de Hick aplicada
> a menu) estão em `docs/uxers_guidance.md`, não aqui. Os UXers também pediram pra
> **cortar o peso cognitivo** da seção 4.1 abaixo — ela fica como referência, mas não é
> mais tratada como pilar organizador do wireframe (seção 5).

### 4.1. Atributos pré-atentivos — "ímãs de atenção"

O que o cérebro processa **antes** de prestar atenção [p.20-21]. A tabela de eficácia [p.22]
é a mais útil do deck inteiro, porque diz qual atributo serve pra **categoria** (dimensão) e
qual serve pra **quantidade** (medida):

| Atributo | Bom pra categoria | Bom pra quantidade |
|---|---|---|
| Cor (matiz) | **Alto** | Baixo |
| Cor (intensidade) | Médio | **Alto** |
| Tamanho | Médio | **Alto** |
| Forma | **Alto** | Baixo |
| Posição | **Alto** | **Alto** |
| Orientação | Médio | Baixo |
| Largura | Baixo | Médio |
| Comprimento | Baixo | **Alto** |
| Agrupamento | Médio | Baixo |
| Enclausuramento | Médio | Baixo |

Leitura prática: **matiz para categorias, posição/comprimento/intensidade para quantidades.**
Quase todo pecado de cor da V1 é usar matiz (o mais forte) como enfeite, e sobrar nada pra
destacar o que importa.

### 4.2. Princípios de Gestalt — "organizar o caos"

| Princípio | Slide | Em uma frase |
|---|---|---|
| Fechamento (Closure) | p.25 | A mente completa o que o olho começa (não precisa de grade fechada) |
| Proximidade | p.26 | Perto = relacionado |
| Similaridade | p.27 | Formas iguais sinalizam função igual |
| Região comum | p.28 | Um recorte compartilhado une elementos |
| Ponto focal | p.29 | Leve o olho pro que mais importa |
| Figura-fundo | p.30 | Contraste separa o sujeito do cenário |
| Destino comum | p.31 | Direção compartilhada implica propósito compartilhado |
| Prägnanz | p.32 | A clareza nasce da forma mais simples |
| Continuação | p.33 | O fluxo guia a atenção naturalmente |
| Simetria | p.34 | Lados equilibrados trazem ordem |

### 4.3. Carga cognitiva — "não fritar o circuito"

| Conceito | Slide | Em uma frase |
|---|---|---|
| Carga intrínseca | p.42 | A dificuldade natural do próprio dado — difícil de reduzir |
| Carga extrínseca | p.43, p.46 | Esforço desperdiçado por design ruim — **é a que a gente corta** |
| Carga germânica (germane) | p.44-45 | Esforço que ajuda a entender — dá pra aumentar de leve pra baixar a intrínseca |
| "Peso no olho, não no cérebro" | p.47 | Stephen Few: boa dataviz tira o esforço do cérebro e põe nos olhos |
| "Nada a tirar" | p.48 | St. Exupéry: perfeição é quando não há mais o que remover |
| Zona Pokémon | p.50 | Cor é pra destacar, não pra encher |
| Cor da marca | p.51 | Nem sempre usar a cor da marca é boa ideia |
| Detalhes somam | p.52 | Pequenos deslizes acumulam |
| Hierarquia de texto | p.53 | Nem todo elemento tem a mesma importância |
| Tipografia | p.54 | 8 pecados: fonte decorativa, ilegível, baixo contraste, tamanhos inconsistentes, bold demais, itálico demais, CAIXA ALTA, ligaduras decorativas |
| Sobrecarga de escolha | p.55-56 | Opções demais = indecisão ou escolha ruim |

### 4.4. Contexto e elementos de apoio — "usuário antes do dado"

| Conceito | Slide | Em uma frase |
|---|---|---|
| Sempre dar contexto | p.59 | Número sozinho quase nunca conta a história |
| Nome do produto | p.61 | Um bom projeto merece um bom nome (que declare a pergunta) |
| Ilusão de sucesso | p.62 | Seu produto de dados está mesmo agregando valor? |
| Desenhar para o erro | p.63 | Projete para os enganos, não reze pra evitá-los |

### 4.5. Qual produto para qual público — "dashboard ≠ relatório"

| Conceito | Slide | Em uma frase |
|---|---|---|
| Dashboard × Analytics × Report | p.71 | Cada um tem público, frequência e interatividade diferentes |
| The Classic / Export Master / Nightmare | p.72-74 | Arquétipos — a V1 é um "Export Master" travestido de dashboard |
| Matriz produto × necessidade | p.75 | Decisão, exploração, comparação, storytelling → produtos diferentes |
| Confiança sustenta a narrativa | p.69 | A narrativa vale o que vale a qualidade declarada do dado |

### 4.6. Layout claro — "usuário feliz"

| Conceito | Slide | Em uma frase |
|---|---|---|
| Dislexia | p.78 | 5-15% da população; fontes simples e texto espaçado |
| Daltonismo | p.79 | ~8% dos homens, 0,5% das mulheres — nunca dependa só de cor |
| Tabela de acessibilidade | p.80 | ~20% dos usuários podem ter dificuldade; soluções por problema |
| Data-ink ratio (Tufte) | p.81 | Proporção da tinta que mostra dado vs. tinta total |
| Limite de 3-5 tons | p.82 | Incluindo a cor da fonte |
| Evitar bandeiras | p.83 | Bandeiras sequestram a atenção pré-atentiva |
| Livro embaralhado | p.84 | Ordem do layout = ordem da leitura |
| Filtro perto do alvo | p.85 | Sempre próximo do gráfico que ele controla |
| Padrão F / Z | p.86 | Denso = F, visual = Z; do agregado/importante para o detalhe |
| Margens / respiro | p.87 | Segmente com espaço vazio, não com borda |
| Alinhamento | p.88 | Alinhamento consistente cria harmonia |
| Estilos misturados | p.89 | Misturar estilos confunde e quebra o fluxo |
| Rolagem | p.90 | NN/g: o foco cai 68% depois da primeira dobra |
| Para todos = pra ninguém | p.91 | Produto para todo mundo não serve a ninguém |

### 4.7. Uso enganoso — "provar qualquer coisa, até o errado"

| Conceito | Slide | Em uma frase |
|---|---|---|
| Eixo truncado | p.103 | Só com um motivo muito bom, a serviço do dado |
| Cor redundante | p.104 | Dobrar a altura da barra com cor é desnecessário |
| Rótulo rotacionado | p.105 | "Não sei por que meu pescoço dói ultimamente" |
| Dispersão espremida | p.106 | Retangular só pra "caber no dashboard" distorce |
| Coleção de enganos | p.107 | Catálogo de gráficos que mentem |
| Cherry-picking (Tufte) | p.108 | A maior ameaça à credibilidade é o dado escolhido a dedo |

### 4.8. Performance e reatividade — "a fundação, não o bônus"

| Conceito | Slide | Em uma frase |
|---|---|---|
| Carga e resposta rápidas | p.111 | Não são bônus — são a base de um bom produto |
| Síndrome do cockpit | p.112 | Ao dizer "cockpit" você já desistiu do perímetro |
| Abundância de datasets | p.113 | O cockpit puxa fontes de dados demais |
| Usuário filtra tudo | p.114 | ...que o usuário vai ter que filtrar no fim |
| Personae | p.116 | Ajudam a customizar, delimitar escopo e entender o fluxo |
| Desafie a necessidade | p.119 | Deixe-os laser-focados em 1 objetivo |

---

## 5. Mapa de princípios por região do dashboard

Enquanto o **Placar de pecados** (seção 7) é a lista plana pra riscar ao vivo, este mapa é a
lente **por região da tela**: para cada bloco do wireframe (seção 3), quais princípios estão
em jogo e — o mais importante pro workshop — **para onde a virada aponta**. Depois do
refinamento dos UXers (`uxers_guidance.md`), cada região carrega **1 princípio primário +
no máximo 1-2 secundários coerentes** — não a pilha de 4-5 violações da primeira passada — e
cada uma está etiquetada com o bloco a que pertence: **FD** (Fundamentos de Design), **UX**
(Experiência do Usuário) ou **A11** (Acessibilidade). Referências `[p.NN]` são do deck do
Aurélien; `[UXers]` vêm de `docs/uxers_guidance.md`.

### N — Barra de navegação *(região nova · bloco UX)*
- **Sobrecarga de escolhas** [UXers]: rail lateral **e** appbar ao mesmo tempo, mais filtros e
  botões extras — o antes literal do exemplo deles. Não há regra nenhuma que explique o que
  mora em qual dos dois menus.
- **Lei de Hick** [UXers]: 12 ícones no rail + 5 na appbar = 17 opções de menu antes mesmo
  de chegar nos 10 filtros da região I.
- **A moldura competente é parte do pecado**: o rail tem altura inteira, item ativo marcado
  e avatar no rodapé — parece um app de BI de verdade. É justamente por parecer profissional
  que ninguém questiona os 17 destinos. Esse é o ponto pedagógico da região: o problema não é
  "feio", é **caro de usar**.
- **Lei de Jakob** [UXers]: nenhum ícone usa o glifo padrão do setor (filtro não é um funil,
  exportar não é uma seta pra baixo) — o usuário decifra em vez de reconhecer. Era a lacuna
  mais importante do inventário antigo: nenhuma região cobria a Lei de Jakob, uma das
  "Top 5 UX Laws" que os UXers marcaram como prioridade máxima.
- **Ajuda ausente** [UXers]: 17 ícones, nenhum é "?" ou "ajuda"/glossário.
- **A virada**: um menu só (rail OU appbar), ícones padrão do setor com rótulo, ícone de ajuda visível
  — Lei de Hick e Lei de Jakob resolvidas na mesma reforma.

### A — Banner de título · bloco FD
- **Figura-fundo** [p.30]: o degradê azul→roxo é o "figura" da tela; o dado devia ser.
- **Hierarquia de texto** [p.53] + **Tipografia** [p.54]: 3 tamanhos na mesma frase, CAIXA
  ALTA em tudo, entreletra esticada, baixo contraste. A fonte é **Arial** — o pecado nunca
  foi a fonte ser feia, é **não haver escala**. Ver a nota da seção 6.
- **Marcas** [p.81]: três logos fictícios de tamanhos e alinhamentos diferentes, cada um
  com placa de cor própria competindo com o degradê — data-ink gasto em quem assina.
- **Nome do produto** [p.61] + **Cockpit** [p.112]: "Painel Gerencial Integrado v1.4" é
  literalmente o nome da síndrome.
- **A virada**: um nome que declara a **pergunta** ("A ocupação hospitalar do RS voltou ao
  patamar pré-pandemia?"), escala tipográfica de 3 níveis, caixa alta só onde for título,
  uma marca só e discreta, fundo neutro que deixa o número virar sujeito — Prägnanz [p.32]
  é o único luxo que vale gastar aqui.

### B — Faixa de KPIs · bloco FD (primário) + UX (secundário)
- **Similaridade** [p.27]: 8 estilos gritam "somos 8 coisas diferentes" quando são 8 cartões
  de mesma função.
- **Região comum** [UXers]: o filtro Ano mora dentro do mesmo bloco visual dos KPIs — o antes
  literal do exemplo deles ("filtros e big numbers ocupando o mesmo espaço do header").
- **Métrica de vaidade** [UXers]: nem todo KPI leva a uma decisão — "228 municípios" é
  interessante, mas não muda a ação de ninguém.
- **Contexto** [p.59]: nenhum KPI tem meta, variação ou período — o par "6,05 dias / 6,05%"
  prova o custo de omitir a unidade.
- **A virada**: um estilo só de tile; filtro fora do bloco de KPIs (região comum própria,
  como a região I); cortar ou substituir o KPI de vaidade por algo acionável; cada número
  com sua comparação.

### C — Tabelão · bloco FD (primário) + UX (secundário)
- **Prägnanz** [p.32] + **carga extrínseca** [p.43]: ~82 mil células são ruído, não
  informação.
- **Figura-fundo** [UXers]: o fundo do container é o mesmo cinza do resto da página — nada
  sinaliza "isto é um card separado" (o antes literal deles, aplicado ao dashboard inteiro,
  mais visível aqui por ser o maior bloco).
- **Grid escuro** [UXers]: linhas de grade escuras em vez de claras — o oposto do "depois"
  deles pra Prägnanz.
- **Nielsen — controle do usuário** [UXers]: colunas sem nenhum controle de ordenação.
- **A virada**: se a tabela é mesmo necessária, ela é um **relatório separado** [p.75], não a
  capa; se ficar, fundo branco contra o cinza da página, grid claro, colunas ordenáveis.

### D — Gráficos circulares (pizzas) · bloco FD (primário) + A11 (secundário)
- **Prägnanz** [p.32]: 58 fatias não têm forma simples — 40 delas ficam abaixo de 1%.
- **Diversidade de tipos de gráfico** [UXers]: a pizza de especialidades ganha tratamento
  pseudo-3D — o antes literal deles ("pizza, 3D, bubble" na mesma tela).
- **Fonte mínima** [UXers, Acessibilidade]: a legenda de 58 itens roda a 10px — abaixo do
  mínimo de 14px/9pt que eles definem pra dislexia/legibilidade.
- **Contexto** [p.59]: a fatia `NULL` e o "Sem Informação" (11%) sem nota tratam ausência de
  dado como categoria real.
- **A virada**: 2D, mesmo tipo de gráfico (barra ordenada) com a mesma paleta pros três
  (similaridade, [p.27]); fonte de legenda ≥14px; nota explicando a ausência de dado.

### E — Mapas concorrentes · bloco A11 (região-âncora de Acessibilidade)
- **Daltonismo** [p.79] + [UXers]: Mapa 1 usa verde→vermelho (o exemplo canônico do
  Aurélien), Mapa 2 usa azul→vermelho (o exemplo específico dos UXers) — os dois piores
  pares pra daltonismo, lado a lado, cada um coberto uma vez.
- **Limite de 3-5 tons** [p.82]: 9 passos em cada mapa inventam uma precisão que não existe.
- **A virada**: paleta segura de 4 níveis nos dois; **destino comum** [p.31] — se contam a
  mesma geografia, um mapa-herói com detalhe on-demand em vez de dois competindo.

### F — Barras mal feitas · bloco FD (primário)
- **Continuidade** [p.33] + [UXers]: municípios em ordem alfabética, não por valor — quebra
  o fluxo de leitura.
- **Ponto focal** [UXers]: nenhuma barra tem destaque de cor — Porto Alegre (23% do estado)
  se perde tão bem quanto qualquer outro município, o antes literal deles ("barras da mesma
  cor em toda a página").
- **Cor redundante** [p.104]: cada barra com uma cor arbitrária — decorativo, não codifica
  nada, e nem isso ajuda a achar Porto Alegre.
- **Rótulo rotacionado** [p.105]: 90° nos municípios — "meu pescoço dói".
- **A virada**: ordenar por valor, barra horizontal, cinza em geral com destaque de cor
  primária só na barra relevante [UXers] — a Lei do Foco resolvida numa tacada.

### G — Dispersão espremida · bloco FD (só Aurélien — fora do refinamento dos UXers)
- **Dispersão retangular** [p.106]: 1200×180 px achata a relação real entre valor e
  permanência.
- **Performance** [p.111]: 3,7 mi de marcas é a planilha que sozinha derruba a demo.
- **A virada**: agregar (por faixa de valor/complexidade) resolve performance **e** revela o
  padrão; devolver a proporção a ~1:1 (**simetria**, [p.34]).
- *Nota*: este bloco não aparece em `uxers_guidance.md` — mantido porque sozinho sustenta o
  argumento de performance da seção 10 do deck, e é barato de cortar ao vivo se o tempo
  apertar (ver seção 8).

### H — Série temporal (o herói enterrado) · bloco FD (hero — sem mudanças)
- ~~**Eixo truncado** [p.103]: o eixo Y fixado em 0,26-0,34 é a mentira central — transforma
  uma variação real de ~7 p.p. em colapso e pico.~~ **Não construído** — o eixo da V1 é
  automático. Ver `docs/dashboard_v1_as_built.md` §3.
- **Rolagem** [p.90] + **scroll depth** [UXers, personas]: o insight que responde à pergunta
  nº 1 do briefing está no rodapé.
- **Destino comum** [p.31]: 287 linhas sobrepostas (espaguete) se movem juntas sem comunicar
  nada.
- **Contexto** [p.59] + **"sempre insira contexto"** [UXers]: a pandemia — o arco narrativo
  inteiro — não está marcada.
- **A virada**: este é o **ponto focal** [p.29, UXers "Law of Focus"] que devia abrir a tela
  (F/Z, [p.86]); eixo em zero + 1-3 séries destacadas + anotação do evento respondem à
  pergunta em 3 segundos.

### I — Filtros espalhados · bloco UX (primário) + A11 (secundário)

> **Mudou:** os 10 filtros não estão mais empilhados num rodapé. Ninguém faz isso de
> propósito — e um erro que ninguém comete não ensina nada. Agora estão **espalhados em 5
> blocos** ao longo da página, que é o que acontece de verdade: filtros vão sendo encaixados
> onde couber, em épocas diferentes, por gente diferente, e ninguém volta pra reorganizar.

- **Proximidade** [UXers]: agora o pecado é **estrutural**, não de espaçamento — **nenhum**
  bloco fica perto do que controla:

  | bloco | onde está | o que controla | onde isso está |
  |---|---|---|---|
  | Faixa de valor · Motivo de saída | logo abaixo dos KPIs | dispersão G | bem abaixo |
  | Complexidade · Caráter | entre D e E | idade F1, dispersão G | abaixo |
  | Tipo de leito · Especialidade | entre F e G | pizza D1 | **muito acima** |
  | Sexo · Raça/cor | abaixo da dobra | roscas D2/D3 | **muito acima** |
  | Município · Hospital | rodapé | tabelão C, mapas E, barras F2 | espalhados acima |

- **Lei de Hick** [UXers]: 10 filtros + 17 ícones da região N = 27 escolhas antes de olhar
  um gráfico — e agora **pior**, porque estão espalhados: não dá pra ver quantos são sem
  rolar a página inteira, então nem a contagem o usuário consegue fazer.
- **Similaridade** [p.27]: cinco blocos, cinco estilos (fundo, forma do chip, rótulo).
  Parecem cinco funcionalidades diferentes; fazem exatamente a mesma coisa.
- **Contraste** [UXers, Acessibilidade]: o chip "Complexidade" usa fundo escuro com fonte
  escura — quase ilegível.
- **A virada**: **um** bloco de filtros globais na região comum do topo, com 3-5 opções e
  "mostrar mais" [Lei de Hick, UXers]; o que for específico de um gráfico fica **encostado
  nele**; espaçamento menor dentro do mesmo tema do que entre temas; contraste mínimo AA em
  todo chip.

### J — Rodapé sem ressalvas · bloco UX (Nielsen)
- **Nielsen — visibilidade do sistema** [UXers]: nenhuma indicação de origem dos dados nem
  de última atualização — o antes literal do exemplo deles.
- **A virada**: fonte + data de atualização reais, perto do número que qualificam
  (proximidade, [p.26]) — dá **credibilidade** [p.69], não é letra miúda.
- *Nota*: a passada anterior deste documento usava uma data de atualização enganosa
  (14/03/2024) como exemplo de cherry-picking por omissão [p.108]. Fica registrado aqui como
  variante — mas não construído junto com "nenhuma data", já que as duas coisas se
  contradizem (não dá pra faltar uma data E mentir sobre ela ao mesmo tempo).

---

## 6. Especificação por planilha

Prioridade: **P0** = essencial pra demo (construir primeiro), **P1** = reforça o argumento,
**P2** = só se sobrar tempo. Com as P0 já dá pra fazer a apresentação inteira.

### N. Barra de navegação — P0 *(região nova)*

| | |
|---|---|
| **Objeto** | Um rail lateral vertical de **altura inteira** (esquerda, ~56px) + uma appbar horizontal no topo da coluna de conteúdo — os dois visíveis ao mesmo tempo. O banner A e as demais regiões ficam **dentro** da coluna à direita do rail, não abaixo de uma faixa de navegação |
| **Rail** | 12 ícones sem rótulo de texto, glifos inventados (não usar funil pra filtro, não usar seta-pra-baixo pra exportar, não usar engrenagem pra config), separadores agrupando 4+4+4, um item com estado ativo, avatar do usuário no rodapé |
| **Appbar** | +5 ícones, também sem rótulo, alinhados à direita; à esquerda um breadcrumb (`SES/RS · BI Corporativo / Assistência / Ocupação Hospitalar`). Nenhum ícone de ajuda/"?"/glossário em nenhum dos dois menus |

> **Importante — a moldura tem que parecer boa.** Uma tira vertical de botões flutuando
> acima do título não é um erro que exista no mundo real; é caricatura, e a plateia
> descarta. O rail de altura inteira, com item ativo e avatar, é o que times de verdade
> entregam. O pecado não está no acabamento, está na **contagem** (17 destinos) e no
> **vocabulário** (glifos que ninguém reconhece). Fazer isso parecer profissional é o que
> força a plateia a *procurar* o problema em vez de rir dele.

**Pecados**: sobrecarga de escolhas [UXers] — rail **e** appbar juntos, mais filtros e
botões; Lei de Hick [UXers] — 17 opções de menu antes mesmo dos 10 filtros da região I; Lei
de Jakob [UXers] — ícones que o usuário tem que decifrar, não reconhecer; ajuda ausente
[UXers] — nenhum dos 17 ícones é de suporte/glossário.

---

### A. Banner de título — P0

| | |
|---|---|
| **Objeto** | Objeto de texto + 3 imagens |
| **Texto** | `PAINEL GERENCIAL DE MONITORAMENTO ESTRATÉGICO INTEGRADO DE OCUPAÇÃO HOSPITALAR — SIH/SUS × CNES — RS — 2019 A 2023` / segunda linha: `v1.4_FINAL_rev2_ok` |
| **Formato** | **Arial** (não fonte decorativa — ver nota abaixo), tudo em CAIXA ALTA, entreletra esticada, 3 tamanhos diferentes na mesma frase, fundo em degradê azul→roxo, texto cinza-claro sobre o degradê |
| **Imagens** | 3 marcas **fictícias** de `assets/logos/` (`logo-sed.svg`, `logo-rede-saude.svg`, `logo-painel.svg`), em tamanhos e alinhamentos diferentes, cada uma com placa de cor própria brigando com o degradê |

> **Por que Arial e não Papyrus.** A primeira versão usava fonte manuscrita/decorativa. Isso
> era caricatura: ninguém publica um painel de secretaria em Papyrus, então a plateia ri e
> **não se reconhece** — viola a regra 1 da seção 1. O pecado tipográfico de verdade,
> aquele que todo mundo comete, é **não ter escala**: três tamanhos arbitrários na mesma
> frase, caixa alta em tudo, entreletra esticada pra "preencher", e cinza-claro sobre
> degradê. Em Arial isso continua ruim — e agora ruim de um jeito que a plateia reconhece
> do próprio trabalho. O argumento fica mais forte, não mais fraco.

> **Marcas fictícias, de propósito.** Nenhum logo reproduz identidade visual de órgão real.
> Carimbar o brasão de uma secretaria de verdade numa peça apresentada publicamente como
> mal feita seria injusto com o órgão e desnecessário pro argumento. Ver
> `assets/logos/README.md`. Os nomes dos *sistemas* no título (SIH/SUS, CNES) seguem reais —
> são as fontes dos dados, citadas, não branding.

**Pecados**: nome de "cockpit" [p.112]; caixa alta + ausência de escala tipográfica + baixo
contraste + tamanhos inconsistentes [p.54]; sem hierarquia de texto [p.53]; título que não
diz nada sobre o dado; data-ink gasto em degradê e em três marcas desencontradas [p.81].

---

### B. Faixa de 8 KPIs — P0

| | |
|---|---|
| **Fonte de dados** | `hospitalizacoes` + `occupancy` |
| **Marca** | 8 planilhas separadas, tipo Texto, mais o filtro `Ano` **dentro do mesmo container** — sem separação de região comum entre filtro e KPI |

Os oito números (todos reais, conferidos contra os dados):

| # | KPI | Valor | Formato proposital |
|---|---|---|---|
| 1 | Taxa de ocupação média | ~30,8% | `30,8%` |
| 2 | Total de internações | 3.739.506 | `3739506` (sem separador) |
| 3 | Dias de permanência | 22.616.421 | `22616421` |
| 4 | Leitos (média mensal) | 107,9 | `107,9` |
| 5 | Valor total AIH | R$ 6.545.187.195,36 | `6545187195,36` (sem R$, sem abreviação) |
| 6 | Taxa de óbito | 6,05% | `0,0605` |
| 7 | Municípios | 228 | `228` |
| 8 | Hospitais | 287 | `287` |

Cada tile com **cor de fundo diferente** (vermelho, laranja, amarelo, verde, ciano, azul,
roxo, rosa), **tamanho de fonte diferente** e **borda diferente** (sólida / tracejada /
sombra / nenhuma). Nenhum tile tem comparação, meta, variação ou período de referência.

> Detalhe delicioso e verdadeiro: permanência média (6,05 dias) e taxa de óbito (6,05%)
> dão o mesmo número. Colocados lado a lado sem unidade explícita, a plateia não consegue
> saber qual é qual — é o argumento de "contexto" [p.59] servido de graça.

**Pecados**: similaridade quebrada — elementos de mesma função com formas diferentes [p.27];
região comum quebrada — filtro Ano no mesmo espaço dos KPIs [UXers]; métrica de vaidade —
"Municípios" não leva a nenhuma decisão [UXers]; número sem contexto [p.59]; formatos
inconsistentes; cor usada sem propósito codificador.

---

### C. Tabelão — P0

| | |
|---|---|
| **Fonte** | `occupancy` |
| **Linhas** | `nome_municipio`, `id_estabelecimento_cnes` |
| **Colunas** | `ano_mes` (mês contínuo, 60 colunas) + Medidas |
| **Medidas** | `taxa_ocupacao`, `total_internacoes`, `total_dias_permanencia`, `leitos_total`, `leitos_sus`, `AVG(taxa_ocupacao)` |
| **Container** | Altura fixa 300 px com barra de rolagem interna; fundo do container igual ao cinza de fundo da página inteira (sem contraste de card) [UXers] |
| **Formato** | Todos os números com 4 casas decimais; grade completa em cinza **escuro** [UXers]; colunas sem controle de ordenação [UXers]; sem realce de nada |

Posição: **topo da página**, ocupando o espaço mais valioso da tela.

**Pecados**: "The Export Master" [p.73] — confundir dashboard com relatório [p.71];
sobrecarga extrínseca [p.43]; Prägnanz [p.32]; figura-fundo — sem separação visual do resto
da página [UXers]; Nielsen — controle do usuário, sem ordenação [UXers].

---

### D. Três gráficos circulares — P0

**D1 — Pizza de especialidade de leito**
`tipo_especialidade_leito_desc` em Cor + `SUM(quantidade_total)` em Ângulo, com **efeito 3D**
(bisel/sombra) aplicado — a diversidade de tipos de gráfico que os UXers citam
explicitamente ("pizza, 3D, bubble" na mesma tela) [UXers].
São **57 categorias distintas** na base, mais o `NULL` → **58 fatias**, das quais 40 ficam
abaixo de 1%. Legenda à direita com os 58 itens, fonte **10px** [UXers, abaixo do mínimo de
14px/9pt]. Rótulo de percentual com 4 casas nas fatias.
Manter a categoria `NULL` (41.796 leitos) sem tratamento — só a fatia sem nome.

**D2 — Rosca de sexo**
Duas categorias (Feminino 2.065.368 / Masculino 1.674.138) num donut, 2D. Rótulos `55,2310%` e `44,7690%`.

**D3 — Pizza de raça/cor**
Seis fatias, 2D, incluindo `Sem Informação` (410.050 = 11% do total) sem nenhuma nota
explicando que é ausência de preenchimento e não uma categoria.

Os três lado a lado, **com paletas diferentes entre si** — só D1 ganha o tratamento 3D, D2/D3
ficam 2D, reforçando a inconsistência de tipos.

**Pecados**: Prägnanz — 58 fatias sem forma simples [p.32]; diversidade de tipos de gráfico —
pizza 2D, pizza 3D e rosca na mesma linha [UXers]; fonte mínima na legenda, 10px [UXers];
ângulo é péssimo pra comparação quantitativa [p.22]; ausência de contexto sobre o dado
faltante [p.59].

---

### E. Dois mapas concorrentes — P1

| | |
|---|---|
| **Fonte** | `occupancy`, com `nome_municipio` como papel geográfico |
| **Mapa 1** | Cor = `AVG(taxa_ocupacao)`, paleta divergente **verde→amarelo→vermelho** [par ruim segundo o Aurélien, p.79] |
| **Mapa 2** | Cor = `SUM(total_internacoes)`, paleta **azul→vermelho**, 9 passos [par ruim segundo os UXers] |

Lado a lado, mesmo tamanho, mesmo peso visual, legendas sem título (só `AVG(taxa_ocupacao)`).
Sem tratamento para os municípios sem hospital (228 de 497 municípios do RS têm dado).

**Pecados**: daltonismo — dois pares ruins diferentes, um por mapa (verde/vermelho [p.79],
azul/vermelho [UXers]); mais de 3-5 níveis de sombreamento [p.82].

---

### F. Duas barras mal feitas — P1

**F1 — Idade**: `idade_paciente` como **dimensão discreta** (não binned) em Colunas,
`CNTD(registros)` em Linhas → 100 barras, uma por idade de 0 a 99. Rótulos de eixo
ilegíveis. Cor variando por idade (gradiente sem sentido).

> Conferido: `idade_paciente` vai de 0 a 99 e **não** há empilhamento artificial no topo
> (97 → 1.889 registros, 98 → 1.343, 99 → 951, decrescendo normalmente). O problema aqui
> é só de design — 100 barras onde caberiam 6 faixas etárias.

**F2 — Municípios**: `nome_municipio` em Colunas, `SUM(total_internacoes)` em Linhas,
**ordenados alfabeticamente**, todos os 228, rótulos rotacionados a **90°**, cada barra de
uma cor **arbitrária — nenhuma barra recebe destaque**, nem Porto Alegre. Porto Alegre
(848.764 internações) fica perdido no meio do alfabeto e sem cor de destaque, apesar de
sozinho representar 23% do estado — o antes literal do exemplo dos UXers ("barras da mesma
cor em toda a página", sem realce pro valor relevante).

**Pecados**: ponto focal — nenhuma barra destacada [UXers]; rótulo vertical = "não sei por
que meu pescoço dói" [p.105]; ordenação que destrói a continuidade/fluxo do olhar [p.33];
cor como enfeite, não como código [p.104]; o dado mais importante escondido pela ordenação.

---

### G. Dispersão espremida — P2

`AVG(valor_aih)` × `AVG(quantidade_dias_permanencia)`, marca = círculo, detalhe no nível
do registro individual (3,7 mi de marcas), num container de **1200 × 180 px**.
Sem transparência, sem linha de tendência, sem tratamento dos outliers
(valor AIH vai de R$ 0,00 a R$ 198.575,01, contra uma média de R$ 1.750,28).

**Pecados**: dispersão retangular só pra "caber no dashboard" — o deck é explícito nisso [p.106]; sobreposição total das marcas; e o principal argumento da seção 10: esta planilha sozinha destrói a performance [p.111]. *(Fora do refinamento dos UXers — só Aurélien; é a primeira a cortar se o tempo apertar, ver seção 8.)*

---

### H. A série temporal (enterrada) — P0

Este é o gráfico que **responde à pergunta nº 1 do briefing**, e é o mais maltratado:

| | |
|---|---|
| **Fonte** | `occupancy` |
| **Colunas** | `ano_mes` (mês contínuo) |
| **Linhas** | `AVG(taxa_ocupacao)` |
| **Detalhe** | `id_estabelecimento_cnes` → **287 linhas sobrepostas** (espaguete) |
| **Eixo Y** | ~~**Fixado em 0,26 – 0,34**~~ → **não construído**, o eixo da V1 é automático |
| **Posição** | Abaixo da dobra, no final da página |

> **Divergência de construção.** O eixo truncado **não foi implementado** — ver
> `docs/dashboard_v1_as_built.md` §3. O parágrafo abaixo descreve a intenção de projeto e o
> raciocínio do pecado; ele não descreve o workbook. Na V1 construída a série aparece
> inteira (23,13% em maio/2020 a 35,40% em nov/2023) e o gráfico ainda é um eixo duplo
> sincronizado — espaguete de 287 hospitais atrás, média estadual grossa por cima.

O eixo truncado seria a mentira central da V1. As médias anuais reais são:

| Ano | Taxa média |
|---|---|
| 2019 | 31,8% |
| 2020 | 26,8% |
| 2021 | 29,8% |
| 2022 | 32,3% |
| 2023 | 33,5% |

Uma variação real de ~7 pontos percentuais. Com o eixo fixado em 0,26–0,34, 2020 vira um
**colapso de fundo de escala** e 2023 vira um pico histórico. Nada foi calculado errado —
só o eixo mente.

Sem anotação de nenhum evento. A pandemia — o arco narrativo inteiro do recorte 2019-2023 —
não aparece marcada em lugar nenhum.

**Pecados**: ~~eixo truncado sem justificativa [p.103]~~ *(não construído)*; o conteúdo mais importante abaixo da dobra [p.90]; livro cortado em 80 pedaços e embaralhado [p.84]; "common fate" mal usado — 287 linhas se movendo juntas não comunicam nada [p.31]; ausência de elemento de contexto/anotação [p.59].

---

### I. Filtros espalhados — P0

**11 filtros**, em **6 lugares diferentes** da página. Nenhum deles no lugar certo.

| # | bloco (estilo) | filtros | posição no layout | controla | distância |
|---|---|---|---|---|---|
| 0 | dentro dos KPIs | `Ano` | região B | tudo | região comum quebrada |
| 1 | faixa cinza | `Faixa de valor`, `Motivo de saída` | entre **B** e **C** | dispersão G | bem abaixo |
| 2 | branco, chip arredondado | `Complexidade`, `Caráter da internação` | entre **D** e **E** | idade F1, dispersão G | abaixo |
| 3 | faixa azulada | `Tipo de leito`, `Especialidade` | entre **F** e **G** | pizza D1 | **muito acima** |
| 4 | caixa com borda | `Sexo`, `Raça/cor` | **abaixo da dobra**, antes de H | roscas D2/D3 | **muito acima** |
| 5 | rodapé cinza | `Município`, `Hospital` | fim da página (região I) | tabelão C, mapas E, barras F2 | espalhados acima |

> **Divergência de construção.** A coluna "controla" acima é a intenção. Na V1 construída o
> escopo é **aproximado**: `Caráter` e `Hospital` ficaram **globais** (controlam tudo), e
> `Motivo de saída` / `Faixa de valor` alcançam também o tabelão. O escopo real está em
> `docs/dashboard_v1_as_built.md` §2. O pecado de proximidade continua válido em 8 dos 11
> filtros — para demonstrar ao vivo, use `Município`, `Tipo de leito` ou `Sexo`, que têm
> alvo único e distante.

> **Por que não todos no rodapé.** Era assim na primeira versão, e é irreal: ninguém empilha
> 10 filtros no pé da página de propósito. Um erro que ninguém comete não gera
> reconhecimento na plateia — quebra a regra 1 da seção 1. O padrão real é este:
> filtros encaixados **onde couber**, conforme foram pedidos, em épocas diferentes, por
> pessoas diferentes, e ninguém nunca volta pra reorganizar. Espalhar também **fortalece**
> o pecado de proximidade: em vez de "estão longe de tudo", vira "cada um está longe
> especificamente do que controla" — que é demonstrável ao vivo, filtro por filtro.

Todos como lista de múltipla seleção, mostrando todos os valores (município tem 228 itens;
motivo de saída, 27; especialidade, 58), **sem botão de aplicar** — cada clique redispara a
consulta inteira. Dentro de cada bloco o espaçamento é **uniforme**, sem agrupar por tema
[UXers]. Os 5 blocos têm **estilos visuais diferentes entre si** (fundo, forma do chip,
rótulo) — parecem funcionalidades distintas, mas fazem a mesma coisa [p.27]. O chip
`Complexidade` usa fundo escuro com fonte escura — quase ilegível [UXers,
Acessibilidade/contraste].

**Pecados**: proximidade — nenhum bloco perto do que controla [UXers]; Lei de Hick — 10
filtros + 17 ícones da região N, sem "mostrar mais", e agora nem contáveis sem rolar a
página [UXers]; similaridade — 5 estilos pra mesma função [p.27]; filtro longe do alvo
[p.85]; contraste — chip escuro sobre escuro [UXers]; sem botão de aplicar = reatividade
destruída [p.111].

---

### J. Rodapé vazio — P0

```
(nada — nem fonte, nem data de atualização)
```

O antes literal do exemplo dos UXers pra "Nielsen — visibilidade do sistema": *"dashboard
sem indicação de última atualização e origem dos dados"*. O briefing (`docs/data_briefing.md`,
seção "Limitações importantes") lista quatro ressalvas que **deveriam** estar no dashboard.
Nenhuma aparece, e nem a fonte dos dados:

1. A taxa de ocupação é uma aproximação (dias de permanência ÷ leitos × dias do mês) —
   e **57 registros da base passam de 100%**, chegando a **187,8%**. Esse valor aparece cru
   na tabela (C) e no mapa (E), sem nota em lugar nenhum explicando se é erro, rotatividade
   ou bug — "desenhar para o erro" [p.63] ao contrário.
2. São dados administrativos de faturamento, não clínicos.
3. Recorte de um único estado — não generalizável.
4. Defasagem de ~6 meses na fonte.

> *Variante registrada, não construída*: a primeira passada deste documento usava uma data
> de atualização **enganosa** ("Atualizado em 14/03/2024", a data de extração, sugerindo
> dado fresco quando o mais recente é de dez/2023) como exemplo de cherry-picking por
> omissão [p.108]. É um pecado real e mais sutil — mas contradiz "nenhuma data", então fica
> de fora desta versão; pode virar uma V1.1 ou um contraste ao vivo com esta ("olha como o
> mesmo rodapé pode mentir de duas formas diferentes").

**Pecados**: Nielsen — visibilidade do sistema, zero indicação de origem/atualização
[UXers]; contexto ausente [p.59]; confiança na narrativa depende da qualidade declarada do
dado [p.69].

---

## 7. Placar de pecados

Checklist para o workshop. A dupla de UX pode ir riscando ao vivo — cada linha é um round.
(Para a leitura por região da tela, ver a seção 5.)

| # | Princípio violado | Deck | Onde está | Correção na V2 |
|---|---|---|---|---|
| 1 | Proximidade | p.26 | Filtros (I) longe dos alvos | Filtro junto do gráfico que ele controla |
| 2 | Similaridade | p.27 | KPIs (B) com 8 estilos | Um só estilo de tile para função igual |
| 3 | Região comum | p.28 | Nada agrupado, tudo com borda | Agrupar por espaço vazio, não por borda |
| 4 | Ponto focal | p.29 | Tabelão + 2 mapas competindo | Um único herói na tela |
| 5 | Figura-fundo | p.30 | Degradê no banner (A); tabelão (C) com fundo igual ao da página [UXers] | Fundo neutro, dado em primeiro plano; card com contraste |
| 6 | Destino comum | p.31 | 287 linhas espaguete (H) | Agregar; destacar 1-3 séries |
| 7 | Prägnanz | p.32 | Tabelão (C); pizza de 58 fatias em estilo 3D (D1) [UXers] | Simplificar até o essencial; 2D só |
| 8 | Continuidade | p.33 | Barras em ordem alfabética (F2) | Ordenar por valor |
| 9 | Fechamento / Simetria | p.25, p.34 | Grade completa, alinhamento caótico | Remover grade; alinhar em grid |
| 10 | Atributos pré-atentivos | p.22 | Cor (matiz) usada pra quantidade | Intensidade/posição pra quantitativo |
| 11 | Sobrecarga extrínseca | p.43, p.46 | Tabelão, 3 pizzas, 100 barras | Cortar o que não responde à pergunta |
| 12 | Zona Pokémon | p.50 | 8 cores nos KPIs, barras arco-íris | Paleta de 3-5 tons |
| 13 | Hierarquia de texto | p.53 | Banner com 3 tamanhos, tudo em caps | Escala tipográfica de 3 níveis |
| 14 | Tipografia | p.54 | Caps em tudo, 3 tamanhos sem escala, entreletra esticada, baixo contraste (a fonte é Arial — o problema é a falta de escala) | Escala tipográfica de 3 níveis, caps só em título, contraste AA |
| 15 | Sobrecarga de escolha / Lei de Hick | p.55, UXers | Nav (N): 17 ícones de menu; filtros (I): 10, sem "mostrar mais" | Menu de 5 + filtros de 3 + "mostrar mais" (Pareto) |
| 16 | Contexto ausente | p.59 | KPIs (B) sem comparação, meta ou período | Cada KPI com sua comparação |
| 17 | Nome do produto | p.61, p.112 | "Painel Gerencial Integrado v1.4" | Nome que declara a pergunta |
| 18 | Desenhar para o erro | p.63 | 187% de ocupação aparece crua na tabela (C) e no mapa (E), sem nota em lugar nenhum | Nota de método + tratamento de outlier |
| 19 | Produto errado | p.71, p.73 | Tabelão dentro de um dashboard | Dashboard ≠ relatório: separar |
| 20 | Daltonismo (par 1) | p.79 | Mapa 1 verde→vermelho (E) | Paleta segura, testada |
| 21 | Data-ink ratio | p.81 | Grade, bordas, sombras, degradê | Remover tudo que não é dado |
| 22 | 3-5 tons | p.82 | Mapa com 9 passos | Reduzir a 4 níveis |
| 23 | Layout embaralhado | p.84 | Insight no rodapé, tabela no topo | Ordem = importância |
| 24 | Filtro perto do alvo | p.85 | (I) | Reposicionar |
| 25 | Padrão F/Z | p.86 | Ordem invertida | Alto→baixo em agregação e importância |
| 26 | Margens / respiro | p.87 | Zero margem, bordas em tudo | Espaço vazio como separador |
| 27 | Alinhamento | p.88 | Logos e tiles desalinhados | Grid consistente |
| 28 | Estilos misturados | p.89 | 3 paletas diferentes nas pizzas | Um sistema visual só |
| 29 | Rolagem | p.90 | 2600 px de altura | Caber numa tela |
| 30 | Feito pra todo mundo | p.91 | Sem persona | Definir persona única |
| 31 | Processo pulado | p.94, p.99 | Abriu o Tableau primeiro | Define → Design → Develop |
| 32 | ~~Eixo truncado~~ **não construído** | p.103 | Eixo Y da região H ficou automático | — (nada a corrigir na V2) |
| 33 | Cor redundante | p.104 | Barras coloridas por barra | Cor só pra destacar |
| 34 | Rótulo vertical | p.105 | Municípios a 90° (F2) | Barras horizontais |
| 35 | Dispersão espremida | p.106 | (G) em 1200×180 | Proporção ~1:1 |
| 36 | Cherry-picking / ordenação | p.108 | Porto Alegre (23%) escondido pela ordem alfabética (F2) | Ordenar por valor, destacar o relevante |
| 37 | Performance | p.111 | 3,7 mi de marcas, 10 filtros | Agregar na fonte |
| 38 | Síndrome do cockpit | p.112-114 | 30 indicadores numa tela | 1 objetivo, 1 tela |
| 39 | Lei de Jakob | UXers | Nav (N): ícones fora do padrão do setor | Ícones padrão, reconhecíveis |
| 40 | Ajuda ausente | UXers | Nav (N): 17 ícones, nenhum de ajuda/glossário | Botão de ajuda/glossário visível |
| 41 | Métrica de vaidade | UXers | KPI "Municípios" (B) não leva a nenhuma decisão | Cortar ou trocar por métrica acionável |
| 42 | Nielsen — controle do usuário | UXers | Tabelão (C) sem ordenação de coluna | Colunas ordenáveis |
| 43 | Nielsen — visibilidade do sistema | UXers | Rodapé vazio (J): sem fonte, sem data | Fonte + data de atualização visíveis |
| 44 | Fonte mínima | UXers | Legenda da pizza D1, 10px | Mínimo 14px/9pt |
| 45 | Contraste | UXers | Chip "Complexidade" (I): fundo e fonte escuros | Fundo escuro + fonte clara |
| 46 | Daltonismo (par 2) | UXers | Mapa 2 azul→vermelho (E) | Verde→laranja |

---

## 8. Ordem de construção sugerida

Se o tempo apertar, esta ordem garante uma demo completa mesmo parando na metade:

1. **Fonte de dados** — conectar `data/refined/sih_cnes_rs.hyper` como **uma única fonte de
   dados do Tableau**, com as três tabelas ligadas por **Relacionamentos** (não Joins
   físicos) em `id_estabelecimento_cnes` + `ano_mes`. `hospitalizacoes` e `leitos` estão em
   grãos diferentes (internação individual vs. hospital×mês×tipo de leito) — um join físico
   entre elas faria fan-out (multiplicaria linhas). `occupancy` já vem pré-agregada por
   hospital×mês e funciona como a tabela "segura" pra KPIs/mapa/série temporal. Relacionar
   (não juntar) é o que garante que os filtros funcionem em cascata pelas três tabelas na V1
   — a V2 é quem decide se separa por persona/assunto. Não renomear nenhum campo
   (`taxa_ocupacao`, `id_estabelecimento_cnes` cru na interface já é um pecado a mais, e de
   graça).
2. **P0 primeiro**: N (nav) → A (banner) → B (KPIs) → C (tabelão) → D (pizzas) → H (série
   temporal com eixo truncado) → I (filtros) → J (rodapé). Isso já cobre a maior parte do
   placar (seção 7).
3. **P1**: E (mapas) → F (barras).
4. **P2**: G (dispersão) — deixar por último, porque é a que mais pesa. Se travar a demo,
   cortar sem dó; o argumento de performance se sustenta só com os filtros e o menu de N.
5. **Montagem**: layout em modo *Tiled* onde couber, mas com objetos flutuantes
   desalinhados de propósito nos logos e nos KPIs.
6. **Tooltips**: não editar nenhuma. O padrão do Tableau (`AVG(taxa_ocupacao): 0,3081`)
   já expõe nome de campo técnico pro usuário final.

---

## 9. Registrar o "antes" para a apresentação — *fora de escopo*

Esta seção previa capturar prints da página inteira e da primeira dobra, cronometrar carga
e resposta de filtro, e gravar um teste de usabilidade.

**Retirada do escopo deste repositório.** A divisão de trabalho é: aqui os dashboards são
construídos e documentados; a dupla de UX cuida da apresentação e dos materiais dela,
incluindo a captura do "antes". A pasta `docs/assets/v1/` não foi criada e não é esperada.

---

## 10. Próximos passos

1. ~~Construir a V1 no Tableau conforme esta especificação~~ — **feito**, com as divergências
   registradas em `docs/dashboard_v1_as_built.md`
2. ~~Capturar os artefatos da seção 9~~ — fora de escopo (ver seção 9)
3. Workshop de redesign com a dupla de UX, usando o placar da seção 7 (lista) e o mapa da
   seção 5 (por região) como roteiro — lendo o *as-built* junto, para não redesenhar contra
   pecados que não foram construídos (item 32)
4. Produzir a V2 e documentar o *depois* em `docs/dashboard_v2_spec.md`
