---
tecnologia: ui-ux-producao
detectar: ["**/*.tsx", "**/*.jsx", "**/*.vue", "**/*.html", "**/*.css"]
papeis: [arquiteto, designer, implementador, revisor]
versao: 2026-08-20
---

## Relação com os outros dois pontos de qualidade de UI
Este cartão é **complementar** a `cartoes/ui-ux.md`, não substituto: `ui-ux.md` cobre o piso
de acessibilidade (WCAG AA, foco de teclado, alvo de toque) — condição necessária, mas não
suficiente para qualidade de produção. Este cartão ensina o que fazer para o nível acima do
piso. O motor `gauntlet-loop` (consultável em REVISÃO/DOC) é o terceiro ponto: ele **mede**
contra referência externa por crítica cega — não ensina o que fazer, só aponta se o resultado
bateu a barra. Os três não se sobrepõem: piso (`ui-ux`) → construção (este cartão, em BUILD) →
medição (`gauntlet-loop`, em REVISÃO/DOC).

## Convenções
- Sistema de design mínimo com **papel semântico**, não valor cru: `cor-acao-primaria`, não
  "azul"; `espaco-secao`, não "24px". Trocar o valor não deveria exigir caçar cada uso.
- Motion tem propósito: duração e easing existem para comunicar causa e efeito (o que acabou
  de mudar, para onde o foco foi), nunca como decoração. Ausência de motion é uma opção válida;
  motion inconsistente entre telas da mesma aplicação não é.
- Densidade de informação calibrada ao contexto real de uso, não a um padrão genérico de
  "espaçoso é sempre melhor": um dashboard de controladoria lido por quem já conhece o domínio
  pede tabela densa e escaneável, não cards grandes com muito respiro — o padrão errado aqui é
  copiar o visual de landing page para uma tela de trabalho repetitivo.
- Vazio, erro e sucesso são **estados desenhados**, com texto específico do que aconteceu e da
  próxima ação possível — nunca o texto genérico que o framework gera por padrão.

## Armadilhas
- Hierarquia visual que depende de legenda para ser lida — se o usuário precisa de uma
  explicação ao lado para entender o que é mais importante na tela, a hierarquia falhou.
- Motion com timing copiado de outra tela sem considerar a diferença de contexto (uma transição
  de 300ms que funciona num modal pequeno fica arrastada numa lista de 200 linhas).
- Estado vazio tratado como "não vai acontecer" — em dado real de controladoria, lista vazia
  (nenhuma divergência, nenhum lançamento no período) é um resultado esperado e frequente, não
  uma exceção.
- Copiar densidade de referência visual (Dribbble, template SaaS) sem considerar que quem usa
  a tela é a mesma pessoa todo dia, muitas vezes por dia — otimizar para primeira impressão
  em vez de uso repetido.

## Checklist de review
- [ ] Hierarquia visual é legível sem legenda.
- [ ] Motion (se existe) tem duração/easing consistentes entre telas equivalentes da mesma
      aplicação, e comunica causa e efeito.
- [ ] Densidade de informação foi calibrada para o padrão de uso real (frequência, quem usa),
      não copiada de referência genérica.
- [ ] Estados vazio, erro e sucesso têm texto específico da situação e da próxima ação.
- [ ] Antes de considerar pronto, avaliar se vale rodar `gauntlet-loop` (motor consultável em
      REVISÃO/DOC) para medir o resultado contra uma barra externa.
