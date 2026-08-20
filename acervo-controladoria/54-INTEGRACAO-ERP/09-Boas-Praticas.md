---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 09-Boas-Praticas
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Boas Práticas

**Nunca confiar em heurística de detecção sozinha — sempre validar contra a origem.** Detectar
a coluna certa por padrão de nome é probabilístico, não uma garantia; `validar()` existe
justamente porque a detecção pode acertar o nome e ainda assim o resultado estar errado (foi o
que aconteceu no bug real de `12-Exemplos.md`, onde a coluna escolhida "parecia" certa pelo
nome). Rodar sem chamar `validar()` depois de `mapear_para_padrao()` é aceitar o risco que o
próprio script foi desenhado para eliminar.

**Preferir desempate por nome antes de magnitude.** Nome de coluna é estável entre execuções do
mesmo banco — o layout do CSV não muda a cada arquivo. Magnitude pode enganar quando os valores
de comissão são pequenos e caem, por coincidência, na mesma faixa 0-100 que um percentual real.
`_escolher_valor_comissao()` só recorre a magnitude depois que nome já não decide, exatamente
pela ordem de confiabilidade descrita em `06-Fluxogramas.md`.

**Guardar o percentual descartado em `PCL_COMISSAO`, em vez de simplesmente ignorá-lo.** A
informação continua útil como checagem cruzada — se `PCL_COMISSAO * VAL_BASE_COMISSAO` divergir
muito de `VAL_COMISSAO`, é sinal de que a detecção escolheu a coluna errada, mesmo que a
validação de soma tenha passado por outro motivo.

**Tratar `ValueError` de `detectar_colunas()` como sinal de mudança de layout do banco, nunca
como bug do script.** O banco mudou o CSV (renomeou coluna, removeu campo) é a explicação mais
provável quando a detecção falha num banco que já funcionava antes — investigar o CSV primeiro,
antes de tocar no código de detecção.

**Rodar contra CSV real de produção antes de confiar num banco novo.** Um teste sintético, como
os de `test_normalizar.py`, prova a lógica de decisão — mas não reproduz peculiaridade real de
encoding, separador ou BOM que só aparece no arquivo de fato exportado pelo banco, como o caso
do DIGIO descrito em `12-Exemplos.md` (já corrigido em 2026-08-04, mas que só apareceu porque
alguém rodou contra o arquivo real).
