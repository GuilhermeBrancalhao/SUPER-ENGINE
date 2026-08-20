# Auditoria — VOL-54 INTEGRACAO-ERP (reauditoria)

- Data: 2026-08-20
- Volume: 54-INTEGRACAO-ERP (tipo ARQUITETURA)
- Auditor: modelo independente (Opus 5), reauditoria pós-correção

## Verificações executadas

| Comando | Saída resumida | Resultado |
|---|---|---|
| `python -m ferramentas.validar 54 --raiz ../acervo-controladoria` (de `acervo/`) | `ok: volume 54 sem violacoes` | Verde |
| `python -m pytest exemplos/54-integracao-erp -q` (de `acervo-controladoria/`) | `13 passed in 1.89s` | Verde |
| `python -m pytest exemplos/54-integracao-erp --collect-only -q` | `13 tests collected`; ordem conferida nome a nome | Verde na contagem, contradiz "Os 3 últimos, sobre `ler_csv()`" |
| `python -m pytest exemplos/45-conciliacao-contas -q` | `26 passed` (13+26 = 39) | Verde — confere com "39 testes" de `16-Roadmap.md` |
| CLI, console UTF-8: `python normalizar.py teste_bom.csv DIGIO --output out_a.xlsx` | fluxo completo, `✓` em todas as validações, `exit=0` | Verde — P6 corrigido |
| CLI, `chcp 1252` e `PYTHONIOENCODING=cp1252` | fluxo completo, `exit=0`, sem `UnicodeEncodeError` | Verde — `sys.stdout.reconfigure` funciona |
| Import direto do módulo (`from normalizar import Normalizador; n.ler_csv()`) com stdout cp1252 | `UnicodeEncodeError: '\U0001f4d6'` em `normalizar.py:67`; e `'\U0001f50d'` em `:204` | Falha residual: a correção vive só em `main()` |
| Leitura do XLSX gerado (`out_a.xlsx`) | `NUM_BANCO=999`, `NOM_BANCO=DIGIO`, `NUM_CONTRATO=NUM_PROPOSTA`, `VAL_BRUTO≠VAL_COMISSAO` | Verde — P2 e P7 corrigidos |
| Mesmo XLSX, coluna `DAT_CREDITO`: entrada `02/01/2026`, `03/01/2026` | saída `01/02/2026`, `01/03/2026` | **Falha nova: dia e mês trocados em silêncio** |
| CLI com CSV cujo dia é 15 (`15/01/2026`) | `ValueError: ❌ Não consegui detectar coluna de DATA`, `exit=1` | **Falha nova: aborta em qualquer arquivo de mês real** |
| Mutação só do cache `_series_numericas` + `n.validar()` | `True` com cache mutado, `False` mutando `df_processado` | Verde — P1 corrigido, não é mais tautológico |
| CSV com 3 colunas `comiss` (`% da Comissao`, `Vl Comiss Extra`, `Valor Comiss`) | `comissao='Vl Comiss Extra'`, `valor_bruto='Valor Comiss'` | Falha residual de P7: a 3ª coluna de comissão vaza para `VAL_BRUTO` |
| `grep -rn "ler_processado"` no volume e nos exemplos | nenhuma ocorrência | Falha residual de P10: arquivo órfão |
| `ls ../CHANGELOG.md` | existe na raiz `SUPER-ENGINE/` | Verde — item de `15-Checklist.md` agora aponta para caminho real |
| Links relativos de `18-Referencias-Cruzadas.md` (5) | todos resolvem | Verde |
| `grep -c "atualizado_em: 2026-08-04" *.md` | 18 de 18 seções | Falha menor: corpo cita edições de 2026-08-20 |

## Notas por seção

| Seção | Nota | Justificativa em uma frase |
|---|---|---|
| 01-Introducao | 9 | Continua separando com honestidade o implementado (CSV) do declarado (API de ERP), coerente com `_VOLUME.yml` e com o que o código faz. |
| 02-Objetivos | 8 | A promessa "validar a transformação contra a origem" passou a ser verdadeira e verificável, mas "detectar automaticamente a data" e "falhar de forma explícita" não se sustentam: a detecção de data falha pelo motivo errado em arquivo real. |
| 03-Escopo | 9 | Fronteira com `45-CONCILIACAO-CONTAS` argumentada por testabilidade e contrato de saída comum às duas rotas — nada a corrigir. |
| 04-Arquitetura | 9 | `C4Context` válido, fechado, seguido de prosa que explica a ausência de setas como decisão; `"Exporia"` corrigido para `"Exportaria"`. |
| 05-Diagramas | 7 | `sequenceDiagram` válido, mas a tese da seção ("`mapear_para_padrao()` nunca volta a ler `df_original`, para não duplicar a lógica de conversão") foi justamente invertida pela correção de `validar()`, e a etapa de conversão de data não aparece na sequência. |
| 06-Fluxogramas | 8 | Árvore fiel a `_escolher_valor_comissao()`, com o caminho frágil admitido — só não mostra que apenas uma candidata descartada é registrada, o que ainda vaza a terceira para `VAL_BRUTO`. |
| 07-Regras | 7 | Quatro regras têm teste real e a quinta deixou de descrever ficção, mas não existe regra alguma sobre parsing de data — a armadilha de dado real mais grave do volume hoje. |
| 08-Modelos | 6 | Contradição obrigatório/opcional e a contagem de 25 colunas vazias estão corrigidas e confirmadas na execução, porém a seção lista `DAT_CREDITO` entre os campos "que toda conciliação depende de ter certo" quando esse campo sai com dia e mês trocados. |
| 09-Boas-Praticas | 7 | As duas afirmações falsas saíram (BOM dado por corrigido, sem "caso pendente"), mas a seção diz que rodar sem `validar()` é aceitar risco enquanto a própria CLI ignora o retorno de `validar()` e salva o XLSX de todo jeito. |
| 10-Anti-Patterns | 8 | O bullet da soma tautológica agora descreve o que o código faz de fato (verificado mutando o cache), embora "escolher a primeira coluna sem desempate" ainda decida no empate de três candidatas e o `except:` nu enfraqueça o bullet de erro nomeado. |
| 11-Implementacao | 7 | Descrição fiel dos métodos privados e a alegação de uso via linha de comando agora executa de verdade, mas a seção não menciona a conversão de data, nem que `main()` ignora o resultado de `validar()`. |
| 12-Exemplos | 8 | Documentação exemplar do bug de BOM com teste que passa, só que afirma que o `encoding` padrão passou a `'utf-8-sig'` quando `main()` continua passando `'utf-8'` explicitamente. |
| 13-Testes | 6 | As três contagens (13, 26, 39) estão certas e foram conferidas por coleta, mas a lista tem 12 marcadores para 13 testes e "Os 3 últimos, sobre `ler_csv()`" contradiz a ordem real de coleta que verifiquei. |
| 14-Metricas | 8 | Métricas bem escolhidas e o estado do bug de BOM alinhado com as demais seções; a honestidade do "1 de 40+ bancos" se sustenta. |
| 15-Checklist | 7 | O `[x]` sem artefato virou `[ ]` com explicação — a correção mais importante do volume — e o item da CLI é verdadeiro e verificado, mas o item 1 afirma execução conferida contra CSV real de produção que a falha de data torna impossível para o arquivo de julho. |
| 16-Roadmap | 8 | Retrata corretamente as contagens verificadas e retrata a alegação dos seis bancos como não comprovada, em vez de repeti-la. |
| 17-Conclusao | 8 | Deixou de contradizer as outras seções sobre BOM e cobertura; ainda diz "validado contra a própria origem antes de ser aceito", garantia que a CLI não impõe. |
| 18-Referencias-Cruzadas | 8 | Os cinco links relativos resolvem, o rótulo "os 13 testes" agora está correto e a vizinhança em prosa justifica o `depende_de` vazio. |

media: 7.7

## Achados da auditoria anterior — status

| Achado | Status | Evidência desta reauditoria |
|---|---|---|
| P1 — validação de soma tautológica | **Corrigido** | `validar()` recalcula via `_para_numerico(self.df_original[...])` (linhas 417-419). Mutei `n._series_numericas["Valor Comiss"]` para `[9999.99, 9999.99]` e `validar()` seguiu `True`; mutei `df_processado['VAL_COMISSAO']` para `[1.0, 1.0]` e devolveu `False`. Não é mais a mesma referência nos dois lados. |
| P2 — `NUM_BANCO`/`NOM_BANCO` saem `NaN` | **Corrigido** | `df_processado` nasce com `index=self.df_original.index` (linhas 348-350). No XLSX gerado pela CLI: `NUM_BANCO=999`, `NOM_BANCO=DIGIO` nas duas linhas. |
| P3 — `[x]` dos seis bancos sintéticos sem evidência | **Corrigido** | `15-Checklist.md` traz o item como `[ ]` e registra explicitamente que a auditoria não achou vestígio; `16-Roadmap.md` faz o mesmo em vez de propagar a alegação. É a correção mais honesta do lote. |
| P4 — estado do bug de BOM contado de duas formas | **Corrigido** | "corrigido em 2026-08-04" agora em `09-Boas-Praticas.md`, `12-Exemplos.md`, `14-Metricas.md`, `15-Checklist.md` e `17-Conclusao.md`; nenhuma seção diz mais "pendente". |
| P5 — contagem de testes errada | **Corrigido em parte** | 13/26/39 conferem com a coleta real. Restam três erros dentro de `13-Testes.md`: 12 marcadores para 13 testes (`test_para_numerico_preserva_coluna_ja_numerica` não tem marcador); "Os 3 últimos, sobre `ler_csv()`" — na ordem de coleta os de `ler_csv` são o 10º, 11º e 12º e o 13º é `test_validar_trava_se_coluna_de_comissao_ficar_vazia`, em memória; e "eram 10 antes da auditoria que adicionou os três últimos desta lista" aponta para os três últimos marcadores, que são os antigos de `ler_csv`, não os três novos (que são o 7º, 8º e 9º da lista). |
| P6 — CLI documentada não executa | **Corrigido em parte** | `python normalizar.py teste_bom.csv DIGIO --output out.xlsx` completou com `exit=0` tanto em console UTF-8 quanto sob `chcp 1252` e sob `PYTHONIOENCODING=cp1252`. Residual: a correção está só em `main()`; importar o módulo e chamar `ler_csv()` com stdout cp1252 ainda estoura `UnicodeEncodeError` em `normalizar.py:67` (reproduzido) — e nenhum dos 13 testes exercita `executar()` ou `main()`, então o gate verde continua sem cobrir o caminho de uso documentado. |
| P7 — `VAL_BRUTO` duplica `VAL_COMISSAO` | **Corrigido em parte** | O caso relatado não ocorre mais: `ja_usadas` exclui `comissao` e `pcl_comissao` (linhas 285-288) e `test_valor_bruto_nao_reusa_a_coluna_ja_escolhida_como_comissao` cobre. Residual descrito em N-3 abaixo: com três candidatas `comiss`, só uma descartada é registrada e a terceira vira `VAL_BRUTO`. |
| P8 — contradição obrigatório/opcional em `08-Modelos.md` | **Corrigido** | `VAL_BRUTO` e `VAL_BASE_COMISSAO` aparecem só na lista de opcionais; a contagem "outras 25 colunas" confere (36 menos os 11 campos que `mapear_para_padrao()` preenche no caso completo — a execução com dois campos não detectados devolveu 27 colunas vazias, exatamente 25+2). |
| P9 — typo `"Exporia"` no `C4Context` | **Corrigido** | `Rel(erp, conector_erp, "Exportaria dado via API")`. |
| P10 — exemplo órfão e `CHANGELOG.md` inexistente | **Corrigido em parte** | O item de `15-Checklist.md` agora diz "raiz de `SUPER-ENGINE/`, não existe changelog próprio dentro de `acervo-controladoria/`", e o arquivo existe lá. Residual: `exemplos/54-integracao-erp/ler_processado.py` continua sem ser citado por nenhuma seção, sem teste, e com caminho de rede `Z:\COMISSÃO\...` fixo no código. |

Balanço: dos dez achados, seis foram fechados por completo e quatro parcialmente. Nenhum dos quatro residuais é a reintrodução do problema original — são cauda, não recaída. As correções de código são reais e os testes novos têm dente (o de P1 é o melhor dos três: falha se alguém voltar a ler o cache).

## Problemas encontrados (novos ou remanescentes)

**N1 — `DAT_CREDITO` troca dia por mês em silêncio, e aborta a execução em qualquer arquivo de mês real (grave, novo). `exemplos/54-integracao-erp/normalizar.py`, `mapear_para_padrao()` linhas 362-364 e `detectar_colunas()` linhas 257-268; afeta `08-Modelos.md`, `07-Regras.md`, `13-Testes.md`.**
`pd.to_datetime(self.df_original[col])` é chamado sem `dayfirst=True` nos dois lugares. Consequências verificadas rodando a CLI:
- CSV com `Data Base` = `02/01/2026` e `03/01/2026` (2 e 3 de janeiro, formato brasileiro) produziu `DAT_CREDITO` = `01/02/2026` e `01/03/2026` no XLSX. Dia e mês trocados, sem exceção, sem aviso, e a validação de soma passa igual porque não olha data. O exemplo DIGIO do próprio `MODELO_UNIVERSAL.md` (`01/07/2026`) cai nesse caso: sai como 7 de janeiro.
- CSV com `15/01/2026` fez a CLI morrer: `pd.to_datetime` levanta `ValueError`, o `except:` nu da linha 267 engole, nenhuma coluna de data é aceita e `detectar_colunas()` termina em `ValueError: ❌ Não consegui detectar coluna de DATA`, `exit=1`. Qualquer arquivo de comissão cobrindo um mês inteiro tem dia maior que 12.

Ou seja: para dado real, o script ou corrompe a data ou não roda. `08-Modelos.md` lista `DAT_CREDITO` entre os "campos sempre preenchidos por `mapear_para_padrao()`, que toda conciliação depende de ter certo" — é a chave temporal que `45-CONCILIACAO-CONTAS` consome. Nenhum dos 13 testes toca `DAT_CREDITO`, nenhuma seção menciona parsing de data, e este é exatamente o tipo de erro silencioso sobre dado brasileiro que `07-Regras.md` e `10-Anti-Patterns.md` afirmam ser a razão de existir do volume. Pesa também sobre a alegação de `15-Checklist.md` de execução conferida à mão contra o CSV real de julho do DIGIO (`01.07`): com esta falha, aquele arquivo não pode ter atravessado `mapear_para_padrao()` com data correta.

**N2 — `except:` nu na detecção de data transforma erro de formato em "coluna não encontrada". `normalizar.py:267`; contradiz `10-Anti-Patterns.md` (último bullet) e `09-Boas-Praticas.md` (quarto parágrafo).**
`10-Anti-Patterns.md` declara eliminado o padrão de "tratar toda coluna não encontrada como um único erro genérico", argumentando que `detectar_colunas()` nomeia o campo que faltou. Só que aqui o campo *existe* e o problema é de formato — a mensagem `"Não consegui detectar coluna de DATA"` desinforma. E `09-Boas-Praticas.md` instrui a tratar `ValueError` de `detectar_colunas()` como mudança de layout do banco e "investigar o CSV primeiro, antes de tocar no código de detecção": exatamente o conselho que faria alguém perder horas no CSV enquanto o defeito é do código.

**N3 — com três candidatas a comissão, a terceira vaza para `VAL_BRUTO` e a escolha volta a depender da ordem das colunas. `normalizar.py`, `_escolher_valor_comissao()` (só devolve `outros[0]`) e `detectar_colunas()` linha 285; afeta `06-Fluxogramas.md` e `10-Anti-Patterns.md`.**
Reproduzido com `% da Comissao`, `Vl Comiss Extra` (500/600) e `Valor Comiss` (886,39/109,48): resultado `comissao='Vl Comiss Extra'`, `pcl_comissao='% da Comissao'`, `valor_bruto='Valor Comiss'`. Dois problemas num só caso — `ja_usadas` só conhece duas colunas, então a terceira coluna de comissão é gravada como valor bruto; e entre duas candidatas que ambas casam com `valor`/`vl` o desempate cai na primeira da ordem do CSV, que é o anti-pattern que `10-Anti-Patterns.md` dá por eliminado. O caso é mais raro que o relatado em P7 e o teste novo não o cobre.

**N4 — a CLI salva o XLSX mesmo quando `validar()` reprova. `normalizar.py`, `main()` linhas 514-515; contradiz `09-Boas-Praticas.md` e `17-Conclusao.md`.**
`normalizador.validar()` é chamado e o retorno é descartado; `salvar_xlsx()` roda em seguida e o processo sai com `0`. As divergências só aparecem como texto em `stdout` sob o título "Avisos de validação". `09-Boas-Praticas.md` diz que "rodar sem chamar `validar()` depois de `mapear_para_padrao()` é aceitar o risco que o próprio script foi desenhado para eliminar" e `17-Conclusao.md` fala de "resultado validado contra a própria origem antes de ser aceito" — chamar e ignorar é o mesmo risco com aparência de garantia. Note-se que `executar()` também não trata o `False`.

**N5 — `main()` passa `encoding='utf-8'`, não o `'utf-8-sig'` que `12-Exemplos.md` diz ter virado padrão. `normalizar.py:506`; afeta `12-Exemplos.md`.**
A seção registra que "`encoding` padrão também passou de `'utf-8'` para `'utf-8-sig'`", e `ler_csv()` de fato tem esse default — mas a CLI o sobrescreve com `'utf-8'` pelo `default=` do `argparse`. Verificado: rodando a CLI contra um CSV com BOM e `;`, a saída foi `1 coluna e implausivel, detectando separador... ';'`, isto é, o arquivo só foi lido certo pela rede de proteção secundária, não pelo `utf-8-sig`. Funciona hoje por acidente de defesa em profundidade; o texto descreve um caminho que a CLI não usa.

**N6 — resíduo de P6: a proteção de encoding só existe em `main()`.**
Reproduzido: `from normalizar import Normalizador; n.ler_csv()` com stdout em cp1252 levanta `UnicodeEncodeError` em `normalizar.py:67` (`📖`) e, se aquele passar, em `:204` (`🔍`). Qualquer consumidor que importe a classe em vez de chamar a CLI — o caminho que `04-Arquitetura.md` pressupõe quando fala de `45-CONCILIACAO-CONTAS` consumindo o contrato — herda o defeito. A correção certa é ASCII nos `print` ou logging, não `reconfigure` no ponto de entrada.

**N7 — resíduo de P5 dentro de `13-Testes.md`** (marcador faltando, "Os 3 últimos" e "os três últimos desta lista" errados) e **resíduo de P10** (`ler_processado.py` órfão, sem teste, com caminho `Z:\` fixo, ao lado do item `[x]` "Todo exemplo citado no volume existe como arquivo e tem teste correspondente" em `15-Checklist.md`). Detalhados na tabela de status acima.

**N8 — `atualizado_em: 2026-08-04` nas 18 seções, enquanto o corpo de sete delas descreve edições de 2026-08-20.** `grep -c` confere 18 de 18. O front-matter é campo de contrato (`contrato.json`, `campos_frontmatter`) e passa no validador porque a data é sintaticamente válida — mas a seção que diz "atualizado em 2026-08-20" no texto e `2026-08-04` no cabeçalho registra o próprio estado errado, defeito que `17-Conclusao.md` diz querer evitar.

## Veredicto

Requer revisão

Média 7,7 (abaixo de 8,0), embora nenhuma seção fique abaixo de 6 — a segunda condição do critério é cumprida, a primeira não. Os gates 1 e 2 da Definição de PRONTO estão verdes (`ok: volume 54 sem violacoes`, `13 passed`) e o `status: RASCUNHO` no front-matter continua correto: o critério 3 de `00-INTRODUCAO/Convencoes.md` não é atendido por esta auditoria.

O trabalho de correção é real e não cosmético. As quatro mudanças de código foram verificadas rodando: a validação de soma deixou de comparar a mesma série consigo mesma e o teste novo prova isso pelo caminho certo (mutar o cache não muda o resultado, mutar o processado reprova); `NOM_BANCO` sai preenchido no XLSX; `VAL_BRUTO` não reusa mais a coluna de comissão; a CLI documentada roda de ponta a ponta em console cp1252. E o `[x]` sem artefato dos seis bancos foi desmarcado com a explicação junto, o que é a melhor evidência de que a auditoria anterior foi lida como crítica e não como lista de aparências a corrigir. Cinco seções subiram de nota por deixarem de afirmar coisa que o código não fazia.

O que reprova não é nenhum dos dez achados anteriores. É `DAT_CREDITO`: um campo que `08-Modelos.md` declara essencial ao consumidor sai com dia e mês trocados quando o dia é menor ou igual a 12, e derruba a execução inteira com a mensagem de erro errada quando é maior — ou seja, em praticamente todo arquivo mensal real de banco. Nenhum dos 13 testes olha esse campo e nenhuma das 18 seções menciona parsing de data. É a mesma classe de defeito que o volume elegeu como sua tese — silêncio sobre dado real brasileiro — em cima do único campo temporal do contrato de saída, e é o que separa este volume de aprovado.
