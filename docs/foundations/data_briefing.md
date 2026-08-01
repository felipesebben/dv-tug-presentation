# Briefing para o time de UX — Dashboard de Ocupação Hospitalar (RS)

## Contexto

Este documento é o briefing de dados para a construção de um dashboard que será
usado em uma apresentação no Tableau User Group (TUG) sobre heurísticas de
gestalt/UX em design de dashboards. O plano é: a partir deste briefing, construir
uma primeira versão **propositalmente ruim** do dashboard; em seguida, dois
apresentadores de UX vão redesenhá-la, princípio a princípio, ao vivo (ou como
estudo de caso) durante a apresentação.

Este documento define **o que os dados permitem responder** e **quais perguntas
de negócio priorizamos** — a decisão de como visualizar (tipos de gráfico, cores,
layout) fica com o time de UX.

## Fonte e escopo dos dados

- **Fonte**: Base dos Dados (dados públicos do Ministério da Saúde/DATASUS, via BigQuery)
- **Internações hospitalares**: SIH-SUS (Sistema de Informações Hospitalares), registros de AIH reduzida
- **Capacidade de leitos**: CNES (Cadastro Nacional de Estabelecimentos de Saúde)
- **Recorte geográfico**: Rio Grande do Sul (RS) — não é uma amostra nacional
- **Recorte temporal**: 2019 a 2023 (dados mais recentes têm defasagem de ~6 meses na fonte)
- **Granularidade disponível**: hospital, município, mês

## Perguntas de negócio a explorar

### 1. Ocupação hospitalar ao longo do tempo (incluindo a pandemia de COVID-19)

O recorte 2019-2023 cobre o período pré-pandemia, a pandemia de COVID-19 e o
início da retomada — um arco narrativo relevante e reconhecível para a plateia.

- Como evoluiu a taxa de ocupação hospitalar mensal no RS entre 2019 e 2023?
- Houve um pico de ocupação nos períodos mais críticos da pandemia (2020-2021)? Como foi a recuperação depois?
- O número de internações e o tempo médio de permanência acompanharam essa curva?

### 2. Comparação geográfica (município / região de saúde)

- Quais municípios ou regiões do RS apresentam maior ou menor taxa de ocupação hospitalar?
- Há concentração de leitos e internações nos grandes centros (ex. Porto Alegre) frente ao interior do estado?
- Essa distribuição se relaciona com o tipo de leito disponível (municípios menores tendem a ter só leitos de baixa complexidade)?

### 3. Perfil demográfico dos pacientes internados

- Qual a distribuição etária das internações? Há grupos etários com padrões distintos (ex. pediátrico vs. idoso) ao longo do tempo ou da geografia?
- Como sexo e raça/cor se distribuem entre os pacientes internados?

### 4. Capacidade de leitos por tipo

- Como está distribuída a capacidade de leitos no RS por tipo (cirúrgico, clínico, complementar/UTI, obstétrico, pediátrico, hospital-dia)?
- Qual a proporção de leitos SUS frente ao total contratado?
- A capacidade por tipo mudou ao longo do tempo (ex. expansão de leitos de UTI durante a pandemia)?

### 5. Custo das internações (valor AIH)

- Qual o valor médio das internações e como varia por complexidade do procedimento?
- Como o custo total evoluiu ao longo do tempo?
- Há relação entre custo e tempo de permanência ou tipo de leito?

## Dados disponíveis (referência rápida)

Três tabelas finais, já tratadas e prontas para consumo:

| Tabela | Granularidade | Principais campos |
|---|---|---|
| `occupancy` | hospital × mês | `taxa_ocupacao`, `total_internacoes`, `total_dias_permanencia`, `leitos_total`, `leitos_sus`, geografia (`nome_municipio`, `nome_uf`, `nome_regiao`) |
| `hospitalizacoes` | internação individual | idade, sexo, raça/cor do paciente, tipo de internação, complexidade, valor da AIH, datas de internação/saída, geografia |
| `leitos` | hospital × mês × tipo de leito | tipo e especialidade do leito (descrição legível), quantidade total/SUS/contratado, geografia |

Todos os campos categóricos (tipo de internação, tipo de leito, complexidade etc.)
já vêm com descrição legível, não apenas o código numérico.

## Limitações importantes (para constar no dashboard)

- **Taxa de ocupação é uma aproximação**: calculada como dias de permanência
  somados ÷ (leitos × dias do mês). Não é uma medida pontual/instantânea de
  ocupação, e pode ultrapassar 100% (rotatividade de leitos dentro do mês,
  inconsistências de registro). O próprio DATASUS documenta essa limitação.
  Isso deve aparecer como nota no dashboard, não ser escondido.
- **Dados administrativos, não clínicos**: os registros existem para fins de
  faturamento e gestão do SUS, não para pesquisa clínica — estão sujeitos a
  inconsistências de preenchimento pelos estabelecimentos.
- **Recorte único de estado**: os números são específicos do RS e não podem
  ser generalizados para o Brasil.
- **Defasagem de dados**: a fonte pública tem ~6 meses de atraso; o dashboard
  não reflete o mês corrente.

## Próximos passos

1. Time de dados entrega este briefing + os dados tratados (arquivo `.hyper`)
2. Construção de uma primeira versão do dashboard, propositalmente sem cuidado
   com princípios de UX (muita informação, hierarquia confusa, gráficos
   inadequados, cores sem propósito)
3. Workshop de redesign com o time de UX, princípio a princípio (proximidade,
   similaridade, hierarquia visual, contraste, etc.), para a apresentação no TUG
