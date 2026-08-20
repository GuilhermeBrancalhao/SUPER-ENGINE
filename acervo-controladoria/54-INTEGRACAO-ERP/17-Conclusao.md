---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 17-Conclusao
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Conclusão

Este volume registra duas rotas de "trazer dado externo para dentro" convergindo no mesmo
contrato de saída — o modelo `PROCESSADO` de 36 colunas. A rota real hoje é a de arquivo:
`normalizar.py` lê o CSV nativo de um banco sem API, detecta automaticamente qual coluna é
comissão, data e proposta por padrão de nome mais validação de tipo, e produz um resultado
validado contra a própria origem antes de ser aceito. A rota de API de ERP (SAP, Oracle, Omie,
IFS) permanece só intenção — nenhuma linha de código deste volume fala com um ERP hoje.

O que o leitor deve levar embora não é o script em si, é o padrão que o motivou a existir:
converter formato numérico antes de filtrar por tipo, nunca depois; nunca deixar coluna vazia
virar candidata só porque o dtype é numérico; desempatar por nome antes de recorrer a magnitude;
e validar todo resultado contra a origem antes de aceitá-lo, porque detecção automática é
probabilística e o próprio caso real do DIGIO provou que ela pode escolher a coluna errada sem
nenhum sinal visível se ninguém verificar a soma.

O volume está estruturalmente mais completo do que quando a auditoria de 2026-08-04 o classificou
como "parcial" com 41 violações — a citação de teste incorreta foi corrigida, e as 18 seções
foram reescritas com prosa real em vez de esqueleto herdado de outro domínio. Ainda assim, o
`status` no front-matter permanece `RASCUNHO`: falta cobertura real contra mais de um banco (o
bug de BOM UTF-8 já está corrigido desde 2026-08-04 — outras seções deste volume ainda diziam o
contrário até a auditoria de 2026-08-20 corrigir a inconsistência), e falta a auditoria por
outro modelo exigida pela Definição de PRONTO em `00-INTRODUCAO/Convencoes.md`. Gravar `PRONTO`
antes disso mentiria sobre
o próprio estado do acervo, exatamente o defeito que motivou remover os dez volumes esqueleto que
existiam ao lado deste.
