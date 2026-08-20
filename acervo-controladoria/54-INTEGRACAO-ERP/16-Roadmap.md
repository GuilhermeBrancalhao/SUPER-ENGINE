---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 16-Roadmap
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Roadmap

## O que este volume ainda não cobre

Conector de API de ERP (SAP, Oracle, Omie, IFS) — hoje só intenção declarada, sem nenhum caso
real que justifique a implementação, já que nenhum banco de comissão trabalhado neste projeto
expõe API.

Teste contra CSVs de outros bancos — hoje só DIGIO (real) está testado. Um item de checklist
anterior afirmava padrões sintéticos de SANTANDER/ITAÚ/CAIXA/BRADESCO/NUBANK/BTG; auditoria de
2026-08-20 não achou vestígio desses testes na suíte real, e o item foi corrigido (ver
`15-Checklist.md`). Isso continua pendente de verdade, não resolvido. Um CSV real de um banco
novo pode revelar peculiaridades que teste sintético nenhum previu — como aconteceu com o DIGIO,
que revelou tanto o bug de parsing numérico brasileiro quanto o de coluna única silenciosa.

## O que este volume assume que pode mudar

A lista de padrões de nome usada na detecção (`comiss`, `commission`, `incentiv`, `fee` para
comissão; `data`, `date`, `dt.` para data; e assim por diante) é hoje uma lista fixa em código.
Conforme mais bancos passarem pelo script, é provável que apareça um nome de coluna que nenhum
padrão atual cobre — nesse momento, a lista cresce, e o teste correspondente registra o caso
novo, seguindo o mesmo padrão que corrigiu o bug do percentual.

## Dívida técnica registrada, não deste volume especificamente

Os 49 testes de `acervo-controladoria/exemplos/` (os 18 deste volume mais os 31 de
`45-CONCILIACAO-CONTAS`) não são coletados por nenhuma suíte automática de `pytest` — ver
`13-Testes.md`. Resolver isso é do repositório como um todo, não deste volume isolado, mas fica
registrado aqui porque afeta diretamente a confiança que se pode ter em "os testes passam".
