# Logos — marcas fictícias para o dashboard

Três marcas em SVG, criadas para o V1 do dashboard de ocupação hospitalar.

## ⚠️ São fictícias, e isso é proposital

Nenhuma delas reproduz a identidade visual de órgão público real — nem do SUS, nem do
Ministério da Saúde, nem do governo do RS, nem de nenhuma secretaria existente. São marcas
**inventadas** com aparência institucional genérica.

Isso não é excesso de zelo: o dashboard vai ser projetado numa apresentação pública como
exemplo de **design ruim**. Carimbar o brasão de um órgão real numa peça apresentada como
mal feita seria injusto com o órgão e desnecessário pro argumento. Os nomes dos *sistemas*
de dados no título (SIH/SUS, CNES, DATASUS) continuam reais — são as fontes dos dados,
citadas como referência, não branding.

## Os arquivos

| arquivo | marca (fictícia) | forma | cor |
|---|---|---|---|
| `logo-sed.svg` | SED — Secretaria Estadual de Dados | escudo + 3 barras ascendentes | `#17386B` navy |
| `logo-rede-saude.svg` | Rede Saúde Integrada | círculo + linha de pulso (ECG) | `#0E7C86` teal |
| `logo-painel.svg` | Painel+ | quadrado arredondado + rosca ~30% | `#5B3A9E` roxo |

Todas em `viewBox="0 0 64 64"`, sem dependência externa (sem fonte, sem imagem embutida,
sem `<style>`), então escalam pra qualquer tamanho e funcionam offline.

Cada uma tem **placa de cor própria** com o glifo em branco. Isso é de propósito: assim
funcionam sobre fundo claro, escuro ou sobre o degradê do banner do V1, sem precisar de
variante. Efeito colateral bem-vindo pro V1 — três placas de cores diferentes brigando
entre si sobre um degradê azul→roxo é exatamente o tipo de ruído visual que a região A
precisa demonstrar.

Cada glifo cita um tipo de gráfico diferente (barras, linha, rosca) — piada interna com
a "diversidade de tipos de gráfico" que os UXers marcam como pecado na região D.

## Uso no Tableau

O Tableau Desktop aceita SVG em objetos de imagem no dashboard (Objetos → Imagem). Aponte
direto pro arquivo neste diretório. Se a sua versão reclamar do SVG, exporte pra PNG em
2× ou 3× do tamanho final pra não serrilhar em tela de alta densidade.

## Uso no wireframe

`docs/v1/wireframe.html` **não** referencia estes arquivos — ele traz os mesmos
três SVGs embutidos inline. É duplicação consciente: o wireframe precisa ser um arquivo
único que funcione sozinho (e como artifact publicado), sem caminhos relativos que quebrem.
**Se editar uma marca aqui, replique lá** — busque por `logo-svg` no HTML.
