---
volume: "45"
volume_nome: CONCILIACAO-CONTAS
tipo: ENGINE
secao: 15-Checklist
status: RASCUNHO
atualizado_em: 2026-08-03
---

# Checklist

Antes de considerar este volume pronto para uso em produção — não confundir com a Definição de
PRONTO do acervo, tratada em `16-Roadmap.md` e em `00-INTRODUCAO/Convencoes.md`:

- [x] Os cinco módulos existem, as funções de decisão são puras (sem I/O), `guarda`/`trilha`
      mutam só estado em memória, e todos têm teste próprio.
- [x] O teste de fluxo completo cobre a composição na ordem real de uso, incluindo o ramo de
      confiança MEDIA/BAIXA (não escreve) e a segunda execução (guarda nova, trilha antiga).
- [x] Cada invariante de `07-Regras.md` que o motor pode de fato violar tem teste que falha se
      for violada. "Título aberto sempre vence lançamento novo" não tem teste possível porque
      o motor não expõe função de criação de lançamento avulso — não há o que a regra proíba.
- [x] Nenhum módulo referencia banco, ERP, cliente ou credencial específicos.
- [x] Os três diagramas exigidos pelo tipo `ENGINE` (contexto, sequência, estados) existem e têm
      parágrafo descritivo logo depois.
- [x] Todo exemplo citado no volume existe como arquivo e tem teste correspondente.
- [ ] `depende_de` aponta para `43-CONTABILIDADE-BASICA`, `53-AUDITORIA-TRILHA` e
      `54-INTEGRACAO-ERP` assim que esses três volumes forem reescritos com o mesmo rigor —
      hoje fica vazio de propósito, ver `_VOLUME.yml`.
- [ ] Auditoria por outro modelo, com média maior ou igual a 8,0 e nenhuma seção abaixo de 6,
      registrada em `auditorias/`.
- [ ] Resultado registrado em `CHANGELOG.md` com a data do dia.

Os dois últimos itens são exatamente o que falta para o `status` no front-matter passar de
`RASCUNHO` para `PRONTO`, conforme a Definição de PRONTO deste acervo — os gates mecânicos
(estrutural e executável) já rodam verde, mas isso não substitui a auditoria de qualidade.
