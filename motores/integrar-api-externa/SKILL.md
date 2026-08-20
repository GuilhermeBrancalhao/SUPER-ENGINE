---
name: integrar-api-externa
description: Motor de integração com sistema externo (ERP, banco, serviço de terceiro) via API ou export de arquivo. Use quando o pedido envolver consumir dados de um ERP (Omie e afins), sincronizar com sistema de terceiro, ou tratar exportação de dado externo cujo formato muda entre fornecedores/períodos. Cobre autenticação, paginação, normalização de coluna variável, rate limit e idempotência de reprocessamento. Não é cartão de um ERP específico (ERP único demais para virar convenção estável) — para um ERP usado repetidamente, o cartão específico é candidato a ser criado depois, com âncora de arquivo real.
---

# Motor de integração com sistema externo

Sistema externo muda sem avisar: campo renomeado, coluna reordenada no export, limite de
taxa reduzido, formato de data trocado. Este motor trata a integração como fronteira
instável por padrão, não como contrato confiável só porque "sempre foi assim".

## Duas formas de integração, tratamento diferente

1. **API real** (endpoint HTTP, autenticação, resposta estruturada) — cobre autenticação,
   paginação e rate limit abaixo.
2. **Export de arquivo** (CSV/Excel baixado manualmente ou por rotina, sem API) — é o caso
   mais comum quando o fornecedor não expõe API (documentado como realidade recorrente em
   `acervo-controladoria/54-INTEGRACAO-ERP`: dezenas de bancos/fintechs de comissão não têm
   API, só export). Aqui o problema não é autenticação, é **normalização de coluna variável**
   abaixo.

## Autenticação e sessão (quando há API)

- Credencial nunca em código-fonte nem em log — vem de variável de ambiente ou arquivo de
  configuração fora do controle de versão.
- Token com expiração: a integração precisa renovar sozinha, não falhar esperando alguém
  rodar de novo manualmente.

## Paginação

Toda API de listagem real pagina. Assumir que a primeira página é a resposta inteira é o
defeito mais comum e mais silencioso — passa despercebido quando o volume de teste é menor
que uma página, e só aparece em produção quando o volume cresce.

## Normalização de coluna variável

O caso central de `acervo-controladoria/54-INTEGRACAO-ERP` (`normalizar.py`, testado contra
40+ bancos): cada fornecedor nomeia e ordena colunas diferente, e o mesmo fornecedor muda o
formato entre exportações (ex.: BOM UTF-8 presente numa exportação e ausente noutra do mesmo
banco). A normalização precisa:
- Casar coluna por conteúdo/posição semântica, não por índice fixo.
- Tratar variação de encoding (BOM presente/ausente) explicitamente, não assumir um único
  encoding para sempre.
- Falhar de forma visível (erro claro) quando uma coluna esperada não aparece — nunca seguir
  em frente com dado ausente tratado como zero ou vazio sem sinalizar.

Antes de escrever normalização nova, ler `acervo-controladoria/54-INTEGRACAO-ERP` (quando
`PRONTO`) — o padrão já testado ali cobre a maior parte dos casos reais de banco brasileiro.

## Rate limit

Toda API de terceiro tem limite de chamadas por período, documentado ou não. Reprocessar sem
throttling na primeira falha por limite é o caminho mais rápido para o fornecedor bloquear a
integração inteira, não só a chamada que falhou.

## Idempotência de reprocessamento

Rodar a integração duas vezes sobre o mesmo período não pode duplicar dado do lado de cá.
Isso normalmente significa: chave de identificação do registro externo é preservada e usada
para decidir "já processei isto" antes de gravar de novo — não um `TRUNCATE` seguido de
reimportação total como única estratégia de idempotência (funciona, mas é caro e apaga
histórico de auditoria de quando cada registro chegou).

## Referências

- `acervo-controladoria/54-INTEGRACAO-ERP` — normalização de CSV bancário real, testada.
- `acervo/16-INTEGRATION` — contrato versionado, idempotência e tolerância a falha entre
  fronteiras de sistema, de forma genérica.
- `acervo/25-API-ARCHITECT` — contrato exposto a cliente, versionamento, erros consistentes
  (mais relevante quando O PRÓPRIO PROJETO expõe uma API, não quando consome uma externa).

## Checklist antes de considerar pronto

- [ ] Credencial não está em código-fonte nem aparece em log.
- [ ] Paginação está tratada — testado com volume que exige mais de uma página, não só com
      dado de amostra pequeno.
- [ ] Normalização de coluna casa por conteúdo/posição semântica, não por índice fixo.
- [ ] Variação de encoding entre exportações do mesmo fornecedor está tratada, não assumida.
- [ ] Falha por coluna ausente é visível, não silenciosamente tratada como vazio.
- [ ] Reprocessar o mesmo período não duplica dado do lado de cá.
