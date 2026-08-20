---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 08-Modelos
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Modelos de Dados

## O modelo `PROCESSADO` (36 colunas)

Documentado em `MODELO_UNIVERSAL.md`. Nasce de comparar o CSV nativo de um
banco (DIGIO) com a planilha `PROCESSADO` já conferida contra o banco real.
Campos sempre preenchidos por `mapear_para_padrao()`, que toda conciliação depende de ter certo:

- `NUM_BANCO` — placeholder fixo (`999`) até existir um catálogo real de códigos de banco.
- `NOM_BANCO` — o nome passado na linha de comando/construtor, sempre igual em todo o arquivo.
- `NUM_PROPOSTA` — identificador único da operação, chave de casamento contra o sistema.
- `NUM_CONTRATO` — hoje é cópia de `NUM_PROPOSTA` (não há campo de contrato distinto no CSV
  nativo); documentado assim para quem for consumir a coluna não assumir um valor independente.
- `VAL_COMISSAO` — o valor pago pelo banco, não o percentual. É o campo que
  o bug real (ver `12-Exemplos.md`) escolhia errado.
- `DAT_CREDITO` — data de crédito, sempre presente no CSV nativo dos bancos testados até aqui.

## Por que detecção automática, e não mapeamento manual por banco

Com 40+ bancos e sem API, mapear coluna a coluna por banco não escala, e
cada mudança de layout do banco quebraria o mapeamento manual em silêncio.
`normalizar.py` detecta a coluna certa por padrão de nome (`comiss`, `data`,
`prop`) mais validação de tipo/unicidade, e falha explicitamente
(`ValueError`) quando não acha comissão, data ou proposta — errar em
silêncio aqui é conciliação errada depois.

## Campos opcionais, presentes só quando o banco fornece

`PCL_COMISSAO`, `VAL_BRUTO` e `VAL_BASE_COMISSAO` só são preenchidos quando
`detectar_colunas()` encontra uma coluna correspondente — nem todo banco expõe as três (e,
desde 2026-08-20, `VAL_BRUTO` nunca reusa a mesma coluna já escolhida como `VAL_COMISSAO`, ver
`10-Anti-Patterns.md`). `DSC_SITUACAO_BANCO` e `TIPO_COMISSAO_BANCO` seguem a mesma regra. As
outras 25 colunas do modelo `PROCESSADO` (código de loja, unidade de empresa, parcela diferida,
entre outras) não são preenchidas por `normalizar.py` hoje — ficam como colunas vazias no XLSX
final, reservadas para quando alguma fonte de dado real precisar delas, e documentadas em
`MODELO_UNIVERSAL.md` como parte do contrato de saída mesmo sem uso atual.
