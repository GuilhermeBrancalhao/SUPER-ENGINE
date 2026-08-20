---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 12-Exemplos
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Exemplos Práticos

## Caso real — DIGIO, janeiro/2026 (`110075 02.01.csv`)

O CSV tem 29 colunas, duas delas casando com o padrão `comiss`: "% da
Comissão" (percentual) e "Valor Comiss" (o valor pago, como texto
`'886,39'`). A versão original de `normalizar.py` escolhia a primeira que
aparecesse na ordem das colunas do CSV — nesse arquivo, o percentual — e a
validação de soma "batia" mesmo assim: como `is_numeric_dtype` excluía
texto com vírgula, só sobravam colunas numéricas vazias como candidatas, e
a soma de uma coluna 100% vazia dá `0,00` por padrão do pandas.

Corrigido, o script escolhe "Valor Comiss", converte `'886,39'` → `886.39`,
e a soma das 14 linhas do arquivo bate em `6.762,97` — conferida à mão
contra o CSV original. Reproduzido em
[`test_escolhe_valor_comissao_e_nao_o_percentual`](../exemplos/54-integracao-erp/tests/test_normalizar.py)
e
[`test_mapeamento_grava_valor_correto_nao_o_percentual`](../exemplos/54-integracao-erp/tests/test_normalizar.py).

## Segundo bug real, corrigido em 2026-08-04: BOM UTF-8 e coluna única silenciosa

O mesmo banco, arquivo de julho (`DIGIO - 110075 01.07.csv`), tem BOM UTF-8 (`\xef\xbb\xbf`) no
início e separador `;`. A causa raiz não era o BOM em si — o parser do pandas já descarta o BOM
sozinho — era `ler_csv()` só acionar a detecção de separador quando `pd.read_csv` lançava
exceção. Ler esse arquivo com separador `,` (o default, sem `sep` explícito) não lança nada:
`pandas` aceita a linha inteira como uma única coluna e devolve normalmente. O arquivo virava 2
colunas em vez de ~29, em silêncio total — nenhuma exceção, nenhum aviso.

Corrigido comparando o número de colunas resultante contra o mínimo plausível (mais de 1) depois
da leitura, não só capturando exceção: se sobrar 1 coluna e o separador não foi forçado pelo
usuário, `ler_csv()` reexecuta a detecção por contagem de ocorrência do caractere (`;`, `,` ou
`\t`) na primeira linha, e relê com o separador achado. `encoding` padrão também passou de
`'utf-8'` para `'utf-8-sig'`, mais correto para arquivo que pode ou não ter BOM. Reproduzido em
`test_ler_csv_com_bom_e_separador_ponto_e_virgula_nao_fica_em_1_coluna`.

## Por que este caso específico, e não um sintético inventado

O caso do DIGIO entrou neste volume porque foi reproduzido rodando o script contra o arquivo de
produção real, não porque foi montado para ilustrar o ponto. A diferença importa: um cenário
sintético provaria só que a lógica de desempate funciona no papel; o CSV real provou, além
disso, que a causa raiz era mais profunda do que parecia — o problema não era só a ordem das
colunas, era o parsing numérico brasileiro escondendo a coluna certa antes mesmo do desempate
entrar em jogo.
