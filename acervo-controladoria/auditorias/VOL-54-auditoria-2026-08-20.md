# Auditoria — VOL-54 INTEGRACAO-ERP

- Data: 2026-08-20
- Volume: 54-INTEGRACAO-ERP (tipo ARQUITETURA)
- Auditor: modelo independente (Opus 5)

## Verificações executadas

| Comando | Saída resumida | Resultado |
|---|---|---|
| `python -m ferramentas.validar 54 --raiz ../acervo-controladoria` (de `acervo/`) | `ok: volume 54 sem violacoes` | Verde |
| `python -m pytest exemplos/54-integracao-erp -q` (de `acervo-controladoria/`) | `.......... 10 passed in 1.74s` | Verde |
| `python -m pytest exemplos/54-integracao-erp --collect-only -q` | `10 tests collected` — nomes conferidos um a um | Verde, mas contradiz "7 testes" citado em 3 seções |
| `python -m pytest exemplos/45-conciliacao-contas -q` | `23 passed` (logo 10+23 = 33, não "30") | Número do volume errado |
| `grep -io "santander\|itau\|itaú\|caixa\|bradesco\|nubank\|btg" -r exemplos/54-integracao-erp/tests/` | (nenhuma ocorrência) | Falha: item `[x]` do checklist sem respaldo |
| `len(Normalizador.COLUNAS_PADRAO)` | `36` | Verde — a alegação "36 colunas" confere |
| `python normalizar.py <csv> TESTE --output …` (CLI, console Windows cp1252) | `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4d6'` em `normalizar.py:67` | Falha: o uso por linha de comando documentado não roda |
| Execução instrumentada de `ler_csv → detectar_colunas → mapear_para_padrao → validar` | `ORIGEM E DESTINO IDENTICOS: True`; `NUM_BANCO: [nan, nan]`; `NOM_BANCO: [nan, nan]`; `VAL_BRUTO == VAL_COMISSAO` | Falha: validação de soma tautológica + colunas de banco vazias |

## Notas por seção

| Seção | Nota | Justificativa em uma frase |
|---|---|---|
| 01-Introducao | 9 | Separa com honestidade as duas superfícies e diz sem rodeio que o conector ERP é intenção; coerente com `_VOLUME.yml`. |
| 02-Objetivos | 7 | Boa divisão implementado/declarado, mas afirma que a soma de comissão é validada contra a origem — verifiquei que os dois lados da comparação são a mesma série. |
| 03-Escopo | 9 | Fronteira com `45-CONCILIACAO-CONTAS` argumentada por testabilidade, não por gosto, e o contrato de saída comum às duas rotas é a decisão certa. |
| 04-Arquitetura | 8 | `C4Context` válido, fechado, não vazio e seguido de prosa que explica a ausência de setas como decisão; erro de digitação `"Exporia"` em `Rel(erp, conector_erp, …)`. |
| 05-Diagramas | 8 | `sequenceDiagram` válido e a prosa explica por que a conversão precede o mapeamento — mas repete que `validar()` compara contra a origem. |
| 06-Fluxogramas | 9 | Árvore de desempate desenhada fielmente a `_escolher_valor_comissao()`, incluindo o caminho não coberto por teste, admitido explicitamente. |
| 07-Regras | 7 | Quatro das cinco regras têm teste correspondente real; a quinta ("validação que compare contra a origem") descreve algo que o código não faz. |
| 08-Modelos | 5 | É a seção do contrato de saída e omite três das onze colunas que `mapear_para_padrao()` preenche (`NUM_BANCO`, `NOM_BANCO`, `NUM_CONTRATO`), erra a contagem das vazias (26 versus 25 reais) e lista os mesmos campos como obrigatórios e como opcionais. |
| 09-Boas-Praticas | 6 | Boas práticas bem argumentadas, mas ancoradas em duas afirmações falsas: que `validar()` pega coluna errada com nome plausível, e que há em `12-Exemplos.md` um "caso ainda pendente". |
| 10-Anti-Patterns | 5 | Declara eliminado justamente o anti-pattern que o código ainda comete — comparar a soma de uma coluna com ela mesma — e afirma que os dois lados vêm de fontes independentes. |
| 11-Implementacao | 7 | Descrição fiel dos quatro métodos privados, porém apresenta como "pensado para uso via linha de comando" um caminho que falha no primeiro `print` no console da própria máquina. |
| 12-Exemplos | 9 | O bug de BOM UTF-8 está documentado de forma exemplar — causa raiz correta (não era o BOM, era o `sep` default aceitando 1 coluna em silêncio), correção e teste nomeado; nada escondido. |
| 13-Testes | 5 | Anuncia 10 testes, lista 9 itens, chama-os de "7 testes" duas vezes, erra a soma com o volume 45 (30 versus 33) e erra quais são "os 3 últimos". |
| 14-Metricas | 6 | Métricas bem escolhidas e honestas sobre 1 banco real de 40+, mas descreve o bug de BOM como "pendente" quando `12-Exemplos.md` e `15-Checklist.md` o dão por corrigido. |
| 15-Checklist | 4 | Formalmente completo e amarrado à Definição de PRONTO, mas marca `[x]` um teste contra seis bancos sintéticos do qual não existe nenhum vestígio na suíte. |
| 16-Roadmap | 6 | Boa leitura do que pode mudar (lista de padrões de nome), porém propaga a alegação dos seis bancos e a contagem de 7/30 testes. |
| 17-Conclusao | 6 | Síntese forte do padrão de engenharia, mas lista como pendências duas coisas que outras seções declaram feitas (BOM corrigido, mais de um banco testado). |
| 18-Referencias-Cruzadas | 7 | Todos os links relativos resolvem e a vizinhança em prosa justifica o `depende_de` vazio; o rótulo "os 7 testes" está errado. |

media: 6.8

## Problemas encontrados

**P1 — Validação de soma é tautológica (grave). `exemplos/54-integracao-erp/normalizar.py`, `validar()`, "Validação 1", contradiz `10-Anti-Patterns.md`, `09-Boas-Praticas.md`, `07-Regras.md` e `02-Objetivos.md`.**
`total_original = self._series_numericas[self.deteccoes['comissao']].sum()` e `VAL_COMISSAO` foi atribuído em `mapear_para_padrao()` a partir *dessa mesma série*. Execução instrumentada devolveu `ORIGEM E DESTINO IDENTICOS: True`. A comparação não pode falhar por escolha errada de coluna — só por desalinhamento de índice. `10-Anti-Patterns.md` afirma o contrário nestas palavras: "os dois lados vierem de fontes independentes — aqui, o CSV original e o resultado mapeado, nunca a mesma referência de coluna repetida". A única checagem com dente real é a guarda `isna().all()`. O volume vende como resolvido o anti-pattern que ele mesmo nomeia.

**P2 — `NUM_BANCO` e `NOM_BANCO` saem vazias (`NaN`). `normalizar.py`, `mapear_para_padrao()`.**
`self.df_processado = pd.DataFrame(columns=self.COLUNAS_PADRAO)` cria o frame com zero linhas; as atribuições escalares `df_processado['NUM_BANCO'] = 999` e `['NOM_BANCO'] = self.nome_banco` não geram linha, e quando as séries reais entram depois, as duas colunas viram `NaN`. Verificado: `NOM_BANCO: [nan, nan]` mesmo passando `'DIGIO'` como nome do banco. O comentário `# Placeholder` no código sequer surte efeito. Nenhuma seção menciona isto, e `08-Modelos.md` apresenta o `PROCESSADO` como o contrato que `45-CONCILIACAO-CONTAS` consome.

**P3 — Item `[x]` do checklist sem nenhuma evidência. `15-Checklist.md`, sexto item; repetido em `16-Roadmap.md`.**
"Testado contra mais de um banco — … testados em 2026-08-04 contra padrões sintéticos de SANTANDER, ITAÚ, CAIXA, BRADESCO, NUBANK e BTG (6 total …), todos passaram." O grep por esses seis nomes em `exemplos/54-integracao-erp/tests/` não retorna nada, e a suíte tem 10 testes, todos rastreáveis a outros comportamentos. Como `17-Conclusao.md` ainda diz "falta cobertura contra mais de um banco", a hipótese mais provável é que o item foi marcado sem o trabalho existir.

**P4 — Estado do bug de BOM contado de duas formas incompatíveis.**
Corrigido em `12-Exemplos.md` ("corrigido em 2026-08-04") e em `15-Checklist.md` ("corrigido em 2026-08-04, coberto por 3 testes"); pendente em `14-Metricas.md` ("um com o bug de BOM pendente"), `17-Conclusao.md` ("falta corrigir o bug conhecido de BOM UTF-8") e `09-Boas-Praticas.md` ("o caso ainda pendente descrito em `12-Exemplos.md`"). A verificação decide a favor de "corrigido": `test_ler_csv_com_bom_e_separador_ponto_e_virgula_nao_fica_em_1_coluna` existe e passa. Três seções estão desatualizadas. Registro, a favor do volume, que o pedido de auditoria pergunta se o bug está documentado e não escondido — está, e bem documentado.

**P5 — Contagem de testes errada em quatro lugares. `13-Testes.md`, `16-Roadmap.md`, `18-Referencias-Cruzadas.md`.**
São 10 testes (coleta conferida). `13-Testes.md` abre com "10 testes", lista 9 marcadores, e depois fala de "os 7 testes deste volume" e "cada um dos 7 testes"; `16-Roadmap.md` diz "os 30 testes … (os 7 deste volume mais os 23 de `45-CONCILIACAO-CONTAS`)" — 10+23 = 33; `18-Referencias-Cruzadas.md` rotula o arquivo como "os 7 testes". Ainda em `13-Testes.md`: "Os 3 últimos, sobre `ler_csv()`" — na ordem real de coleta os testes de `ler_csv` são o 7º, 8º e 9º, e o último é `test_validar_trava_se_coluna_de_comissao_ficar_vazia`, que é em memória.

**P6 — O uso por linha de comando documentado não executa. `11-Implementacao.md` ("pensado para uso via linha de comando"), `05-Diagramas.md` (participante `normalizar.py (linha de comando)`).**
`python normalizar.py <csv> TESTE --output <xlsx>` morre em `normalizar.py:67` com `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4d6'` no console Windows cp1252 — antes de ler uma linha do CSV. Os emojis dos `print` só funcionam com `PYTHONIOENCODING=utf-8`. Nenhum dos 10 testes exercita `executar()` nem o `main()`, então o gate verde não cobre o único modo de uso que o volume descreve.

**P7 — `VAL_BRUTO` pode duplicar `VAL_COMISSAO` em silêncio. `normalizar.py`, `detectar_colunas()`; afeta `08-Modelos.md`.**
Num CSV com `% da Comissao` e `Valor Comiss`, a coluna `Valor Comiss` foi detectada simultaneamente como `comissao` e como `valor_bruto`, e o resultado saiu com `VAL_BRUTO == VAL_COMISSAO`. `08-Modelos.md` diz que `VAL_BRUTO` "só é preenchido quando `detectar_colunas()` encontra uma coluna correspondente", sem dizer que a mesma coluna pode ser reaproveitada por dois campos — exatamente o tipo de silêncio que `07-Regras.md` afirma combater.

**P8 — Contradição obrigatório/opcional dentro de `08-Modelos.md`.**
`VAL_BRUTO`, `VAL_BASE_COMISSAO` e `DSC_SITUACAO_BANCO` aparecem sob "Campos que toda conciliação depende de ter certo" e, três parágrafos depois, sob "Campos opcionais, presentes só quando o banco fornece". Contagem também errada: as colunas não preenchidas são 25, não "as outras 26".

**P9 — Erro de digitação no `C4Context`. `04-Arquitetura.md`.**
`Rel(erp, conector_erp, "Exporia dado via API")` — "Exporia" por "Exporia/Exporta". Não quebra a renderização; é o único defeito que encontrei nos diagramas, que no restante são válidos, fechados, não vazios e seguidos de prosa explicativa, como o `contrato.json` exige para `ARQUITETURA` (`C4Context` + `sequenceDiagram`).

**P10 — Arquivo de exemplo órfão e referência a `CHANGELOG.md` inexistente neste acervo.**
`exemplos/54-integracao-erp/ler_processado.py` existe e não é citado por nenhuma seção do volume nem coberto por teste. E o último item de `15-Checklist.md` ("registrado em `CHANGELOG.md`") aponta para um arquivo que não existe em `acervo-controladoria/` — só na raiz `SUPER-ENGINE/`.

## Sugestões concretas de melhoria

1. Tornar a validação de soma real: em `validar()`, recalcular `total_original` a partir de `self.df_original[self.deteccoes['comissao']]` reconvertido, ou melhor, comparar contra a soma de *todas* as candidatas descartadas para detectar troca de coluna. Depois reescrever a terceira bala de `10-Anti-Patterns.md` para descrever o que o código passa a fazer — hoje o texto descreve uma intenção, não o comportamento.
2. Corrigir `mapear_para_padrao()` para atribuir `NUM_BANCO`/`NOM_BANCO` depois de o frame ter linhas (ou construir o frame já com o índice de `df_original`), e adicionar um teste que afirme `NOM_BANCO` igual ao nome passado. Documentar em `08-Modelos.md` que `NUM_BANCO` é placeholder e que `NUM_CONTRATO` é hoje uma cópia de `NUM_PROPOSTA`.
3. Desmarcar o item dos seis bancos em `15-Checklist.md` até que os testes existam, ou escrever os seis testes sintéticos e citá-los pelo nome na seção — um `[x]` sem artefato é pior que um `[ ]` honesto, e é a única falha deste volume que contraria a tese que ele defende sobre si mesmo.
4. Passar uma revisão de consistência de estado: atualizar `09-Boas-Praticas.md`, `14-Metricas.md` e `17-Conclusao.md` para "BOM corrigido em 2026-08-04", e substituir todo "7 testes"/"30 testes" por "10"/"33" em `13-Testes.md`, `16-Roadmap.md` e `18-Referencias-Cruzadas.md`. Corrigir também "Os 3 últimos" para nomear os três testes de `ler_csv()`.
5. Trocar os emojis dos `print` por texto ASCII (ou envolver a saída com `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` no `main()`), e adicionar um teste que invoque `executar()` de ponta a ponta com `tmp_path` — isso fecha simultaneamente P6 e a lacuna de cobertura do único caminho de uso documentado.
6. Impedir que a mesma coluna seja detectada como `comissao` e `valor_bruto` (excluir as já atribuídas das candidatas seguintes), e registrar o caso como regra em `07-Regras.md` com teste próprio.
7. Citar `ler_processado.py` em `11-Implementacao.md` com teste correspondente, ou removê-lo de `exemplos/`; e ajustar o item de `CHANGELOG.md` em `15-Checklist.md` para o caminho que existe.
8. Corrigir `"Exporia"` para `"Exportaria"` no `C4Context` de `04-Arquitetura.md` — a forma condicional é a correta, já que o conector não existe.

## Veredicto

Requer revisão

Média 6,8 (abaixo de 8,0) e cinco seções abaixo de 6 (`08-Modelos` 5, `10-Anti-Patterns` 5, `13-Testes` 5, `15-Checklist` 4, mais `09-Boas-Praticas`, `14-Metricas`, `16-Roadmap` e `17-Conclusao` em 6 no limite). Os dois gates mecânicos da Definição de PRONTO estão verdes e o `status: RASCUNHO` no front-matter continua correto — o critério 3 de `00-INTRODUCAO/Convencoes.md` não é atendido por esta auditoria. O volume é bem escrito e a honestidade declarada sobre "ERP é intenção, CSV é implementado" se sustenta em quase todo o texto; o que reprova não é inflar o escopo de integração ERP, é o inverso — afirmar garantias sobre a parte que *está* implementada (validação contra a origem, cobertura de seis bancos, contagem de testes) que a execução do código não confirma.
