---
volume: "45"
volume_nome: CONCILIACAO-CONTAS
tipo: ENGINE
secao: 12-Exemplos
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Exemplos

## Caso 1 — fechamento correto com lançamento tardio

Um saldo inicial de 1000 é conhecido em 1º de janeiro. O único saldo de banco disponível é o do
dia 5, em 1050. Sem nenhum movimento registrado, `achar_ancora` não encontra fechamento — o
resíduo de 50 não bate com nada. Assim que um movimento de +50 com data de registro igual ao dia
5 é incluído (mesmo que esse movimento só tenha chegado à base dias depois), a âncora fecha
exatamente no dia 5. O caso está reproduzido em
[`../exemplos/45-conciliacao-contas/tests/test_ancora.py`](../exemplos/45-conciliacao-contas/tests/test_ancora.py),
no teste `test_lancamento_com_data_retroativa_fecha_o_dia_correto_quando_chega`, e ilustra a regra
central de `07-Regras.md`: o que importa é a data do fato, não a data em que o dado chegou.

## Caso 2 — boilerplate engana o casamento se não for descontado

Um título aberto (T1, errado) carrega o prefixo genérico bancário inteiro — "PAGAMENTO
RECEBIMENTO TRANSFERENCIA TARIFA COMPRA NACIONAL DEBITO CREDITO CARTAO BANCO LTDA" — seguido do
nome real do fornecedor (padaria); outro título (T2, correto) tem só o nome real do fornecedor
(farmácia), sem boilerplate nenhum. O movimento bancário chega com o mesmo prefixo genérico de
T1 seguido do nome da farmácia. Comparando o texto bruto (sem descontar vocabulário genérico),
o movimento parece muito mais parecido com T1 — o prefixo compartilhado, sendo enorme, domina a
métrica de similaridade e supera de longe a diferença real de nome. Descontando o vocabulário
genérico antes de comparar — o que `casar()` faz por padrão — sobra só o nome real de cada lado,
e o casamento correto (farmácia, T2) vence. `test_boilerplate_e_load_bearing`
(`../exemplos/45-conciliacao-contas/tests/test_casamento.py`) prova isso na prática: esvaziar o
conjunto de boilerplate muda o vencedor de T2 para T1, confirmando que o desconto realmente
decide o resultado — achado de auditoria de 2026-08-20, que encontrou a versão anterior deste
teste citando boilerplate como prova sem de fato depender dele.

## Caso 3 — dois valores redondos iguais, uma é duplicata e a outra não

Duas transferências de exatamente 1000, mesmo valor com sinal, para a mesma contraparte, no
mesmo dia: a segunda é bloqueada pela guarda, porque a chave completa (data + valor + contraparte)
já foi vista. Duas transferências de 1000 para a mesma contraparte em dias diferentes: nenhuma é
bloqueada, porque a chave é composta e a data diverge. O caso existe porque decidir por valor
isolado — um erro real de implementação em motores mais simples — bloquearia a segunda situação
por engano, negando uma transação legítima. Ver `test_valores_redondos_repetidos_em_dias_diferentes_nao_sao_duplicata`
e `test_mesma_chave_completa_e_bloqueada` em
[`../exemplos/45-conciliacao-contas/tests/test_guarda.py`](../exemplos/45-conciliacao-contas/tests/test_guarda.py).

Os três casos, e a composição completa dos cinco módulos numa única passagem, estão narrados de
ponta a ponta em `test_fluxo_completo.py`, citado em `13-Testes.md`.
