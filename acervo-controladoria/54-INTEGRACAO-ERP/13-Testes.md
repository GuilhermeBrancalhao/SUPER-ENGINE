---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 13-Testes
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Testes

18 testes em `exemplos/54-integracao-erp/tests/test_normalizar.py` (atualizado em 2026-08-20,
terceira rodada de correção; eram 16 na segunda rodada, 13 na primeira, 10 antes disso). Na
ordem real de coleta (`pytest --collect-only` — nunca repetir o número aqui sem conferir):

1. Conversão de formato brasileiro
2. Coluna já numérica passa direto
3. dtype `str` nativo do pandas recente (não é `object` clássico)
4. Coluna 100% vazia não vira candidata
5. Desempate correto entre "% da Comissão" e "Valor Comiss"
6. Mapeamento grava o valor certo em `VAL_COMISSAO`, não o percentual
7. `NUM_BANCO`/`NOM_BANCO` são preenchidos de fato (não saem `NaN`)
8. `VAL_BRUTO` não reusa a mesma coluna já escolhida como `VAL_COMISSAO`
9. `validar()` recalcula do CSV original, não compara um cache com ele mesmo
10. `DAT_CREDITO` não troca dia por mês (`dayfirst=True`), inclusive dia > 12
11. Terceira coluna candidata a comissão não vaza para `VAL_BRUTO`
12. `executar()` sinaliza reprovação de `validar()` no retorno, não só via print
13. CSV com BOM UTF-8 e separador `;` não fica em 1 coluna silenciosa (bug do
    arquivo de julho do DIGIO, corrigido em 2026-08-04)
14. CSV sem BOM com separador `;` continua funcionando (guarda de regressão)
15. CSV com separador `,` continua funcionando (guarda de regressão)
16. `validar()` trava quando a coluna de comissão fica vazia
17. CLI real (subprocess) sai com código 2 quando `validar()` reprova — achado de 3ª auditoria:
    o teste 12 cobria só o retorno de `executar()`, nunca o `sys.exit(2)` de `main()`
18. CLI real (subprocess) repassa `--sep`/`--encoding` a `ler_csv()` — achado de 3ª auditoria:
    as duas flags eram parseadas e descartadas em silêncio

Os testes 1-11 são unitários, sem I/O de arquivo (constroem o `DataFrame` em memória). O teste
12 grava CSV e XLSX em `tmp_path` (achado da 3ª auditoria — a frase anterior desta seção dizia
o contrário). Os testes 13-15, sobre `ler_csv()`, também usam `tmp_path` para escrever um CSV
temporário. O 16º testa `validar()`, não `ler_csv()`, mas também usa `tmp_path`. Os testes 17 e
18 rodam a CLI de verdade via `subprocess`, não chamam a classe direto.

## Dívida conhecida: nenhuma suíte automática coleta estes testes

`acervo-controladoria/exemplos/` não é alcançado por `pytest` na raiz do motor (que só coleta o
pacote `ferramentas` de lá) nem por `pytest` de dentro de `acervo/` (que coleta o pacote dele).
Os 18 testes deste volume, junto com os 31 de `45-CONCILIACAO-CONTAS`, passam hoje porque
alguém rodou `python -m pytest acervo-controladoria/exemplos -q` manualmente — não por garantia
mantida pelo repositório, registrado como dívida em `acervo-controladoria/ESTADO.md`.

Cada um dos 18 testes existe porque reproduz um comportamento que já quebrou de verdade (os
oito mais recentes, achados de três rodadas de auditoria em 2026-08-20), não porque cobre uma
linha de código por obrigação — a lista de bugs reais em `10-Anti-Patterns.md` tem
correspondência direta com a lista de testes aqui, e essa correspondência é intencional: um
teste sem bug real por trás tende a virar manutenção sem valor, e um bug real sem teste
correspondente tende a voltar sem aviso na próxima mudança.
