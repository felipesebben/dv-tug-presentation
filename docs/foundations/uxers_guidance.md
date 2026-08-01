# Orientação dos UXers — refinamento sobre o deck Aurélien

Transcrição organizada de `references/uxers_guidance.pdf` (1 página, notas dos dois
UXers co-apresentadores após revisar *Learn Design Driven Data Visualization*).
Este documento **não substitui** o deck do Aurélien (`references/Learn_Design_Driven_Data_Visualization.pdf`,
já catalogado em `docs/v1/spec.md` seção 4) — é o **filtro de prioridade** que a
dupla aplicou por cima dele para esta apresentação específica: o que manter, o que
cortar, e que exemplos concretos (antes/depois) eles próprios querem usar no palco.

Onde este documento e o deck do Aurélien dizem coisas diferentes sobre o mesmo
princípio (ex.: o par de cores ruim para daltonismo), **este documento vence** — é a
camada de decisão mais recente. As referências `[p.NN]` no restante do repositório
continuam apontando pro deck do Aurélien; aqui as referências são pelo nome do
princípio, já que o PDF de origem não tem numeração de slide.

Os UXers dividiram a revisão em **três blocos**, cada um com princípios e, para a
maioria, um par `Ex. antes:` / `Ex. depois:`. Como o objetivo do dashboard V1 é
justamente capturar o **antes**, essa coluna é a mais usada no restante do repo — o
depois é o que a V2 demonstra ao vivo.

---

## 1. Fundamentos de Design

> Nota explícita dos UXers: **cortar a parte cognitiva** dos atributos pré-atentivos
> (a tabela categoria×quantidade do deck do Aurélien) **e focar em design** — ou
> seja, manter o conceito leve, sem tratá-lo como pilar central da apresentação.

**Gestalt** — como o cérebro agrupa elementos visuais naturalmente:

| Princípio | Ex. antes | Ex. depois |
|---|---|---|
| **Encerramento** (closure) | — (só o conceito: a mente completa o que os olhos veem) | — |
| **Proximidade** | Espaçamento entre botões de filtro do mesmo grupo é **igual** ao espaçamento entre grupos diferentes | Espaçamento entre botões do mesmo grupo é **menor** que o espaçamento entre grupos diferentes |
| **Similaridade** | Big numbers com formatos diferentes | Big numbers com o mesmo formato |
| **Região comum** | Filtros e big numbers/gráficos ocupando o **mesmo espaço** do header | Filtros no topo, abaixo big numbers, abaixo gráficos — regiões separadas |
| **Figura-fundo** | Dashboard e gráficos com a **mesma cor de fundo** | Dashboard com fundo cinza, gráficos com fundo branco |
| **Continuidade** (+ leitura F/Z) | Gráficos sem alinhamento horizontal/vertical claro (alturas e larguras muito diferentes) | Gráficos distribuídos em colunas e linhas claras |
| **Simetria** | Mosaico com larguras de coluna muito diferentes | Mosaico com larguras de coluna similares |
| **Ponto focal** | Barras da **mesma cor** em toda a página — nada se destaca | Barras cinzas em geral; quando o valor é relevante, destaque na cor primária |
| **Destino comum** | — (só o conceito: mesma direção indica mesmo propósito) | — |
| **Lei da simplicidade** (Prägnanz) | Muitas cores + diversidade de tipos de gráfico (pizza, **3D**, **bubble**) + grids com linhas **escuras** | Uma cor primária + cinza; gráficos de barra e linha; grids com linhas claras |

**Espaços brancos**
- Antes: card de gráfico sem espaçamento interno, margem pequena
- Depois: card de gráfico com espaçamento interno, margem pequena

**Alinhamento**
- Antes: header, filtros e cards não alinhados à esquerda e à direita
- Depois: header, filtros e cards alinhados à esquerda e à direita

---

## 2. Experiência do usuário

| Princípio | Ex. antes | Ex. depois |
|---|---|---|
| **Sobrecarga de escolhas** | Menu sidebar **e** topbar + filtros + outros botões pra clicar | Só sidebar **ou** topbar + filtros, sem botões extras |
| **Sempre insira contexto** | Big numbers e gráficos sem texto de apoio | Big numbers e gráficos com texto de apoio |
| **Métricas de vaidade** — os gráficos adicionam valor de verdade? | Gráfico com métrica que não leva a nenhuma decisão | Remove, ou substitui por gráfico que leva a uma decisão |
| **Nielsen — visibilidade do sistema** | Dashboard sem indicação de última atualização e origem dos dados | Dashboard com indicação de última atualização e origem dos dados |
| **Nielsen — combinar com o mundo real** (+ reconhecimento > recordação + Lei de Jakob) | Ícones e selos desconhecidos | Ícones e selos conhecidos |
| **Nielsen — controle do usuário e liberdade** | Tabela com colunas sem ordenamento | Tabela com colunas com ordenamento |
| **Nielsen — consistência e padrões** | Tipografia, tamanhos e espaçamentos diferentes | Mesma tipografia, mesmos tamanhos pra mesma função, mesmos espaçamentos |
| **Nielsen — prevenção de erros** | Drill-down que filtra o dashboard inteiro sem como voltar ao estado original sem resetar tudo | Drill-down com breadcrumb pra desfazer filtros |
| **Nielsen — flexibilidade e eficiência de uso** | *(em aberto — os UXers marcaram "?" pros dois lados; sem exemplo definido ainda)* | *(idem)* |
| **Nielsen — estética e design minimalista** | = Lei da simplicidade (ver acima) | = Lei da simplicidade |
| **Nielsen — ajuda a reconhecer/diagnosticar/recuperar de erros + documentação** | Dashboard sem glossário e sem botão de suporte | Dashboard com glossário e botão de suporte |
| **Lei de Hick** — limitar escolhas ajuda na decisão | Menu com 15 opções + 10 opções de filtro | Menu com 5 opções + 3 filtros + botão "mostrar mais filtros" (Pareto: 80% dos usuários só precisam de 20% das funcionalidades) |
| **Personas e User Journey** (+ scroll depth) | Um dashboard com todos os gráficos | Dashboards separados por perfil de análise |

---

## 3. Acessibilidade

| Princípio | Ex. antes | Ex. depois |
|---|---|---|
| **Dislexia + fontes pequenas** | Tipografia apertada, texto em caixa alta, fonte mínima **10px/6pt** | Tipografia respirada, evitar caixa alta, fonte mínima **14px/9pt** |
| **Daltonismo** | Destaques em **azul e vermelho** | Destaques em **verde e laranja** |
| **Contraste** | Variedade de cinzas com pouco contraste; cinza muito claro contra o fundo; botão com fundo escuro **e fonte escura** | Máximo de 3 tons de cinza com contraste, o mais claro ainda legível; botão com fundo escuro e fonte **clara** |
| **Cores** — limite de 3 a 5 cores, proporção 20% destaque / 30% cinzas / 70% branco-preto | Gráfico de categorias com uma cor diferente por categoria | Gráfico de categorias com a mesma cor em tons diferentes, ou cinza + uma cor de destaque |

> Nota: o par "azul e vermelho" como o pior caso de daltonismo é a chamada
> **específica dos UXers** para este projeto — o deck do Aurélien usa
> verde→vermelho como exemplo canônico [p.79]. Os dois pares são reais problemas
> de CVD; não são contraditórios, só ênfases diferentes. O V1 usa os dois (ver
> `docs/v1/spec.md` região E), um em cada mapa.

---

## 4. Top 5 UX Laws (imagem de referência anexa ao PDF)

O PDF inclui um cartão de referência ("TOP 5 UX LAWS") reforçando que, dos
princípios acima, estes cinco são os que os UXers tratam como **prioridade máxima**
— se o tempo de construção apertar, são os que não podem sair do V1/V2:

1. **Law of Proximity**
2. **Hick's Law**
3. **Law of Focus** (= ponto focal)
4. **Law of Simplicity** (= Prägnanz / lei da simplicidade)
5. **Jakob's Law** (= combinar com o mundo real / reconhecimento)

Isso importa porque, do inventário original em `docs/v1/spec.md` (baseado só
no Aurélien), a **Lei de Jakob não tinha nenhuma região dedicada** — é a lacuna mais
importante que este refinamento fecha (ver região **N** nova, seção 5 daquele
documento).

---

## 5. O que muda em relação ao inventário existente

Resumo prático para quem for direto ao `docs/v1/spec.md`/`.html` sem ler tudo
acima:

- **Cortar**: a tabela de atributos pré-atentivos deixa de ser um pilar — vira menção
  leve, não uma seção own-weight.
- **Adicionar** (lacunas reais no V1 anterior): Lei de Jakob (ícones desconhecidos),
  métrica de vaidade, heurísticas de Nielsen (visibilidade do sistema, controle do
  usuário, ajuda/documentação, consistência), Lei de Hick aplicada a um menu (não só
  a filtros), fonte mínima quantificada (10px/6pt), contraste botão escuro-sobre-escuro.
- **Afiar** (já existia, agora com exemplo mais preciso): região comum (filtro dentro
  do próprio header, não só "longe"), daltonismo (par azul-vermelho além do
  verde-vermelho), Prägnanz (nomeando 3D/bubble/grid escuro como violações
  específicas, não só "muitas cores").
- **Redistribuir**: o inventário antigo empilhava 4-5 princípios por região; este
  refinamento tenta manter **1 princípio primário + no máximo 1-2 secundários
  coerentes** por região, espalhando os três blocos (Fundamentos / UX / Acessibilidade)
  em vez de concentrar tudo em "Fundamentos de Design" — ver a tabela de mapeamento
  em `docs/v1/spec.md` seção 5.
