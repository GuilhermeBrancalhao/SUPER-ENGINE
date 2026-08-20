# Auditoria — VOL-54 INTEGRACAO-ERP (3ª rodada)

- Data: 2026-08-20
- Volume: 54-INTEGRACAO-ERP (tipo ARQUITETURA)
- Auditor: modelo independente (Opus 5), 3ª rodada

## Verificações executadas

| Comando / verificação | Saída literal resumida | Resultado |
|---|---|---|
| `python -m ferramentas.validar 54 --raiz ../acervo-controladoria` (de `acervo/`) | `ok: volume 54 sem violacoes` | Verde |
| `python -m pytest exemplos/54-integracao-erp -q` | `16 passed in 2.82s` | Verde |
| `python -m pytest exemplos/54-integracao-erp --collect-only -q` | `16 tests collected`; ordem conferida nome a nome contra a lista de `13-Testes.md` | Verde — os 16 itens e a ordem batem exatamente |
| `python -m pytest exemplos/45-conciliacao-contas -q` | `30 passed` | **Contradiz `13-Testes.md` e `16-Roadmap.md`, que dizem 26** |
| `python -m pytest exemplos --collect-only -q` | `46 tests collected` | **Contradiz "42 testes" de `16-Roadmap.md`** |
| CLI ponta a ponta, CSV com BOM, `;`, dia > 12 (`15/01/2026`, `02/01/2026`, `31/07/2026`) | fluxo completo, 4 validações `✓`, `exit=0` | Verde — N1 corrigido |
| Leitura do XLSX gerado | `DAT_CREDITO` = `15/01/2026`, `02/01/2026`, `31/07/2026`; `NUM_BANCO=999`; `NOM_BANCO=DIGIO`; `VAL_BRUTO=10000` ≠ `VAL_COMISSAO=886.39`; 36 colunas, 26 vazias | Verde — dia preservado, dia > 12 não aborta |
| CSV que reprova `validar()` (comissão negativa) | `⚠️ 1 comissões negativas`; XLSX salvo; `exit=2` | Verde — N4 corrigido |
| CSV com data em ISO (`2026-01-15`) | `DAT_CREDITO` correto, com `UserWarning` do pandas sobre `dayfirst` | Verde funcional |
| CSV com formatos de data misturados na mesma coluna (`03/01/2026`, `15/01/2026`, `2026-01-20`) | `ValueError: ❌ Não consegui detectar coluna de DATA`, `exit=1` | **Falha residual de N2: erro de formato reportado como coluna ausente** |
| CSV com 3 colunas `comiss` (`% da Comissao`, `Vl Comiss Extra` 500/600, `Valor Comiss` 886,39/109,48) | `comissao='Vl Comiss Extra'`, `pcl='% da Comissao'`, `valor_bruto='Valor Bruto'` (não vaza) — mas `Valor Comiss` é descartada em silêncio e `validar()` devolve `True` | Vazamento corrigido; **mis-seleção por ordem de coluna permanece** |
| Mutação só do cache `_series_numericas` + `validar()` | `True` com cache mutado; `False` mutando `df_processado` (`1045.87 → 3.0`) | Verde — P1 segue corrigido |
| Import direto da classe com `PYTHONIOENCODING=cp1252` | fluxo completo sem `UnicodeEncodeError`, `validar() == True` | Verde — N6 corrigido |
| CLI com `--sep "\|" --encoding latin-1` | flags aceitas e **silenciosamente ignoradas**: `executar()` chama `ler_csv()` sem argumentos | **Achado novo (N9)** |
| `grep -rn "ler_processado"` no volume | nenhuma ocorrência; `ler_processado.py` mantém `Z:\COMISSÃO\...` fixo na linha 5 | Falha residual de P10 |
| `atualizado_em` × menções a `2026-08-20` no corpo | 11 seções em `2026-08-20`, 7 em `2026-08-04`; toda seção que cita `2026-08-20` no corpo tem o cabeçalho em `2026-08-20` | Verde — N8 corrigido |
| 5 links relativos de `18-Referencias-Cruzadas.md` | todos os arquivos existem | Verde |

## Notas por seção

| Seção | Nota | Justificativa em uma frase |
|---|---|---|
| 01-Introducao | 9 | Continua separando o implementado (CSV) do declarado (API de ERP) com honestidade, coerente com `_VOLUME.yml` e com o que o código faz de fato. |
| 02-Objetivos | 9 | "Validar contra a origem" e "falhar de forma explícita" agora se sustentam na execução; só a mensagem de erro em caso de formato de data misto ainda não é o campo certo. |
| 03-Escopo | 9 | Fronteira com `45-CONCILIACAO-CONTAS` argumentada por testabilidade e contrato de saída comum às duas rotas — nada a corrigir. |
| 04-Arquitetura | 9 | `C4Context` válido e fechado, seguido de prosa que explica a ausência de setas como decisão, mais a justificativa de não unificar os dois componentes. |
| 05-Diagramas | 7 | `sequenceDiagram` válido e bem comentado, e a tese "`mapear_para_padrao()` não relê `df_original` para os campos monetários" está correta como escrita — mas a conversão de data, que foi o defeito central desta rodada, não aparece em nenhuma etapa da sequência, e o passo `validar()` não mostra que ele agora recalcula da origem. |
| 06-Fluxogramas | 7 | A árvore é fiel à cascata de `_escolher_valor_comissao()`, porém o nó "só uma tem 'valor'/'vl'" esconde que, com duas candidatas casando, a decisão cai em `nao_percentuais[0]` — ordem de coluna — e reproduzi isso escolhendo `Vl Comiss Extra` em vez de `Valor Comiss`. |
| 07-Regras | 9 | Seis regras, todas com teste real que citei e coletei, e a nova regra de data descreve com precisão os dois sintomas (troca silenciosa para dia ≤ 12, `ValueError` para dia > 12) e a exigência da mesma opção nos dois pontos de parse. |
| 08-Modelos | 9 | `DAT_CREDITO` deixou de ser uma promessa falsa — sai correto no XLSX gerado — e a contagem "outras 25 colunas" confere (execução com um campo não detectado devolveu 26 vazias, exatamente 25+1). |
| 09-Boas-Praticas | 8 | A contradição sobre `validar()` sumiu (a CLI agora sai com 2), mas o parágrafo que manda tratar `ValueError` de `detectar_colunas()` como mudança de layout "nunca como bug do script" continua mandando investigar o CSV no caso em que o defeito é do parse. |
| 10-Anti-Patterns | 7 | O bullet da soma tautológica está verificado, porém "escolher a primeira coluna que casa, sem desempate" é dado como eliminado e eu o reproduzi com três candidatas, e "erro genérico para coluna não encontrada" segue contradito pela mensagem de DATA em erro de formato. |
| 11-Implementacao | 7 | Descrição fiel dos métodos privados, mas a seção descreve `executar()` com o contrato antigo — "sai com código 1" — sem citar o retorno `(saida, validado)`, o exit code 2, a conversão de data, nem a proteção de encoding movida para o topo do módulo, tudo mudado nesta rodada. |
| 12-Exemplos | 8 | Documentação exemplar do bug de BOM, e a afirmação sobre o `encoding` padrão finalmente é verdadeira nos dois lugares (`ler_csv()` e `argparse`); a rede de proteção descrita como o conserto é a que de fato agiu na minha execução. |
| 13-Testes | 6 | Os 16 nomes e a ordem de coleta conferem item a item — o melhor trabalho de correção da seção — mas ela erra duas coisas novas: `45-CONCILIACAO-CONTAS` tem 30 testes coletados, não 26, e "os 12 primeiros são unitários, sem I/O de arquivo" é falso porque o 12º grava CSV e XLSX em `tmp_path`. |
| 14-Metricas | 8 | Métricas bem escolhidas e alinhadas com as outras seções; a honestidade do "1 de 40+ bancos" continua se sustentando. |
| 15-Checklist | 8 | Os quatro `[x]` novos foram todos verificados rodando (dayfirst nos dois pontos, exit 2, terceira coluna, encoding no topo do módulo) e o `[ ]` dos seis bancos segue desmarcado com explicação; o `[x]` "todo exemplo citado existe e tem teste" ainda convive com `ler_processado.py` órfão e com `Z:\` fixo. |
| 16-Roadmap | 7 | Retrata com honestidade o que falta e não repete a alegação dos seis bancos, mas o número que ela existe para registrar está errado: são 46 testes em `exemplos/` (16 + 30), não 42. |
| 17-Conclusao | 8 | "Resultado validado contra a própria origem antes de ser aceito" agora tem lastro — `validar()` recalcula do CSV e o exit code separa salvo de salvo-validado — embora o XLSX continue sendo gravado na reprovação, o que a seção não menciona. |
| 18-Referencias-Cruzadas | 9 | Os cinco links relativos resolvem, o rótulo "os 16 testes" está correto e a vizinhança em prosa justifica o `depende_de` vazio. |

media: 8.0

## Achados de rodadas anteriores — status

| Achado | Status | Evidência desta auditoria |
|---|---|---|
| N1 — `DAT_CREDITO` troca dia por mês; aborta para dia > 12 | **Corrigido** | `dayfirst=True` nas duas chamadas (`normalizar.py:278` na detecção, `:384-386` na gravação). CLI rodada com `15/01/2026`, `02/01/2026` e `31/07/2026`: `exit=0` e XLSX com as três datas idênticas à entrada. Coberto por `test_dat_credito_nao_troca_dia_por_mes`, que inclui dia 15 explicitamente. |
| N2 — `except:` nu vira "coluna não encontrada" | **Corrigido em parte** | O `except:` nu virou `except (ValueError, TypeError)` (`:282`), o que estreita o silêncio. Mas o sintoma de fundo permanece: coluna de data com formatos misturados (`03/01/2026`, `15/01/2026`, `2026-01-20`) ainda morre com `ValueError: ❌ Não consegui detectar coluna de DATA` e `exit=1` — a coluna existe, o problema é de formato, e a mensagem manda o leitor para o lugar errado, exatamente como `09-Boas-Praticas.md` instrui. |
| N3 — terceira coluna de comissão vaza para `VAL_BRUTO` / escolha por ordem | **Corrigido em parte** | O vazamento acabou: `ja_usadas = set(candidatos_comissao.keys()) | {...}` (`:303-305`) e reproduzi com o CSV de três colunas — `valor_bruto` foi para `Valor Bruto` legítimo, e `None` quando não havia. A metade restante segue viva: entre `Vl Comiss Extra` (500/600) e `Valor Comiss` (886,39/109,48) o código escolheu a primeira pela ordem, gravou 500/600 em `VAL_COMISSAO`, descartou `Valor Comiss` inteira e `validar()` devolveu `True`. Pior: o teste novo usa exatamente esse `DataFrame` e só afirma `deteccoes["valor_bruto"] is None`, sem afirmar nada sobre `deteccoes["comissao"]` — a escolha errada está dentro do teste, não asseverada. |
| N4 — CLI salva o XLSX e sai 0 mesmo com `validar()` reprovando | **Corrigido** | `executar()` devolve `(saida, validado)` (`:513`) e `main()` faz `sys.exit(2)` (`:538`). CSV com comissão negativa: `⚠️ 1 comissões negativas`, XLSX gravado (decisão deliberada e documentada no docstring) e `exit=2`. Verificado também que erro real ainda sai 1 e sucesso 0 — três códigos distintos. |
| N5 — `main()` passa `encoding='utf-8'` contra o texto de `12-Exemplos.md` | **Corrigido no texto, agravado no mecanismo** | O `default=` do `argparse` é `'utf-8-sig'` (`:531`), alinhado com `ler_csv()` e com a seção. Só que `executar()` chama `self.ler_csv()` sem argumentos: nem `--encoding` nem `--sep` chegam ao leitor. Ver N9 — o texto ficou verdadeiro por coincidência de defaults, e as duas flags da CLI são inertes. |
| N6 — proteção de encoding só em `main()` | **Corrigido** | O `sys.stdout.reconfigure` está no nível de import (`:26-27`). `PYTHONIOENCODING=cp1252 python -c "from normalizar import Normalizador; ..."` completou os quatro passos e `validar()` devolveu `True`, sem `UnicodeEncodeError`. |
| N7 — resíduo de `13-Testes.md` e `ler_processado.py` órfão | **Corrigido em parte** | Os erros de marcador e de "os 3 últimos" foram resolvidos: conferi os 16 itens da lista contra `--collect-only` um a um, ordem inclusive, e batem. `ler_processado.py` continua sem citação em nenhuma seção, sem teste e com `xlsx_path = r"Z:\COMISSÃO\..."` fixo na linha 5, ao lado do `[x]` de `15-Checklist.md`. E `13-Testes.md` trocou os erros antigos por dois novos — ver P1 abaixo. |
| N8 — `atualizado_em: 2026-08-04` em 18 de 18 seções | **Corrigido** | 11 seções em `2026-08-20`, 7 em `2026-08-04`, e o cruzamento `grep -c "2026-08-20"` mostra que nenhuma seção cita a data nova no corpo mantendo a antiga no cabeçalho. O front-matter voltou a descrever o próprio estado. |

Balanço: dos oito achados, cinco fechados por completo e três parcialmente. O achado grave da rodada 2 — `DAT_CREDITO` — está resolvido pelo caminho certo (a mesma opção nos dois parses, mais teste que inclui dia > 12), e verifiquei isso rodando a CLI de ponta a ponta e abrindo o XLSX, não lendo o diff.

## Problemas encontrados (novos ou remanescentes)

**P1 — as contagens de teste de outro volume estão erradas, e a afirmação sobre I/O nos 12 primeiros é falsa (novo). `13-Testes.md` linha 44 e `16-Roadmap.md` linha 35.**
`13-Testes.md` diz "os 16 testes deste volume, junto com os 26 de `45-CONCILIACAO-CONTAS`", e `16-Roadmap.md` diz "os 42 testes de `acervo-controladoria/exemplos/` (os 16 deste volume mais os 26 de `45`)". Coletado agora: `exemplos/45-conciliacao-contas` tem **30** testes (`30 passed`, `30 tests collected`) e `exemplos/` inteiro tem **46**. A aritmética das duas seções é consistente com si mesma e errada quanto ao fato — o número foi atualizado nesta rodada para o valor de ontem. É a mesma classe de defeito que `17-Conclusao.md` diz querer evitar: a seção de registro registrando o estado errado. Some-se a isso "Os 12 primeiros são unitários, sem I/O de arquivo (constroem o `DataFrame` em memória)": o 12º é `test_executar_reporta_exit_code_diferente_quando_validacao_reprova`, que escreve `real.csv` e `saida.xlsx` em `tmp_path` — grava dois arquivos em disco, incluindo um XLSX.

**P2 — resíduo de N3: com três candidatas a comissão, a coluna de comissão real é descartada em silêncio e a validação aprova. `normalizar.py`, `_escolher_valor_comissao()` linhas 184-210; afeta `06-Fluxogramas.md`, `10-Anti-Patterns.md`, `13-Testes.md`.**
Reproduzido com `% da Comissao` (3,0), `Vl Comiss Extra` (500/600) e `Valor Comiss` (886,39/109,48): `VAL_COMISSAO` saiu 500/600, `Valor Comiss` não foi para lugar nenhum, e `validar()` devolveu `True` — porque `validar()` recalcula a soma da coluna que a detecção escolheu, e por desenho (o próprio comentário nas linhas 435-437 admite isso) não julga a escolha. Como as duas candidatas casam com `vl`/`valor`, o filtro `com_valor` não reduz a uma, e a decisão final cai em `nao_percentuais[0]`, isto é, na ordem das colunas do CSV — o anti-pattern que `10-Anti-Patterns.md` declara eliminado. O teste novo (`test_terceira_coluna_de_comissao_nao_vaza_para_valor_bruto`) usa esse mesmo `DataFrame` e afirma apenas `valor_bruto is None`, deixando a escolha errada passar sem asserção.

**P3 — resíduo de N2: erro de formato de data continua sendo reportado como coluna ausente. `normalizar.py:277-283` e `:349`; afeta `09-Boas-Praticas.md` e `10-Anti-Patterns.md`.**
Com formatos misturados na mesma coluna, `pd.to_datetime(..., dayfirst=True)` levanta, o `except (ValueError, TypeError)` engole, nenhuma coluna de data é aceita e a execução termina em `❌ Não consegui detectar coluna de DATA`, `exit=1`. O caso é bem mais raro que o dia > 12 da rodada anterior, mas a mensagem segue apontando para o campo errado — e `09-Boas-Praticas.md` transforma isso em conselho ativo ("investigar o CSV primeiro, antes de tocar no código de detecção").

**P4 — `--sep` e `--encoding` são aceitos pela CLI e nunca chegam a `ler_csv()` (novo). `normalizar.py`, `executar()` linha 501 e `main()` linhas 530-536; afeta `11-Implementacao.md` e `12-Exemplos.md`.**
`executar()` chama `self.ler_csv()` sem argumentos; `args.sep` e `args.encoding` são parseados e descartados. Verificado: `python normalizar.py teste_dia15.csv DIGIO --sep "|" --encoding latin-1` ignorou as duas e completou normalmente pelo caminho de auto-detecção. Duas consequências: a mensagem `"Não consegui detectar separador. Use --sep"` (`:66`) instrui o usuário a usar uma flag que não faz nada, e o ramo `if separador: raise` de `ler_csv()` é inalcançável pela CLI. O texto de `12-Exemplos.md` sobre o `encoding` padrão só é verdadeiro porque os dois defaults coincidem hoje.

**P5 — o teste que cobre o exit code não testa o exit code. `tests/test_normalizar.py:186-198`; afeta `13-Testes.md`.**
`test_executar_reporta_exit_code_diferente_quando_validacao_reprova` faz `monkeypatch.setattr(n, "validar", lambda: False)` e afirma `validado is False` — testa o retorno de `executar()`, não `main()` nem o `sys.exit(2)`, e como `validar()` está substituída, também não prova que uma reprovação real produz `False`. O comportamento existe (verifiquei `exit=2` na CLI, com CSV de comissão negativa), mas nenhum teste da suíte o exerce, e o nome do teste promete mais do que ele afirma. Vale também notar que `test_dat_credito_nao_troca_dia_por_mes` recebe `tmp_path` e não usa.

**P6 — resíduo de P10: `ler_processado.py` órfão, sem teste, com caminho de rede fixo. `exemplos/54-integracao-erp/ler_processado.py:5`; afeta `15-Checklist.md`.**
`grep -rn "ler_processado"` no volume e nos exemplos: zero ocorrências fora dos próprios relatórios de auditoria. O arquivo carrega `xlsx_path = r"Z:\COMISSÃO\DOCS - WORK BANK 2026\DIGIO\07 - JULHO\PROCESSADOS\DIGIO - 110075 01.07 - EDITADO.xlsx"` — não roda em nenhuma máquina sem esse mapeamento — e convive com o `[x]` "Todo exemplo citado no volume existe como arquivo e tem teste correspondente". O item é literalmente verdadeiro (o arquivo não é citado), o que é a forma mais fraca de estar certo.

**P7 — `import normalizar` reconfigura o `stdout` do processo hospedeiro (menor, novo). `normalizar.py:26-27`; afeta `11-Implementacao.md`.**
A correção de N6 é eficaz, mas resolve o problema no lugar de fora: um módulo importável muda o encoding e o `errors` do `sys.stdout` do processo que o importa, efeito colateral global que atinge `45-CONCILIACAO-CONTAS` ou qualquer consumidor do contrato. O comentário no código reconhece o achado da auditoria mas não o trade-off; a saída sem efeito colateral seria ASCII nos `print` ou `logging`. O `traceback` de `executar()` vai para `stderr`, que não é reconfigurado — nas minhas execuções ele saiu com mojibake (`N�o consegui`) enquanto o `stdout` saiu correto, na mesma tela.

## Veredicto

Aprovado

Média 8,0 (igual ao mínimo) e nenhuma seção abaixo de 6 — as duas condições do critério estão cumpridas, a segunda com folga (a menor nota é 6, em `13-Testes.md`). Os gates 1 e 2 da Definição de PRONTO estão verdes (`ok: volume 54 sem violacoes`, `16 passed`). Registro que a aprovação é por margem zero: qualquer uma das duas seções de contagem valendo um ponto menos reprovaria o volume.

O que mudou de verdade nesta rodada foi o defeito que reprovou a anterior. `DAT_CREDITO` está correto pelos dois lados do parse, com a mesma opção nos dois lugares — que era a exigência real, não um detalhe de forma — e confirmei rodando a CLI contra CSV com BOM, separador `;` e dia 15 e dia 31, abrindo o XLSX resultante e comparando as três datas com a entrada. `07-Regras.md` documenta o caso descrevendo os dois sintomas em vez de mencionar a opção, e o teste inclui dia > 12 explicitamente, que é o que impede a reintrodução. O exit code passou a distinguir três estados, a proteção de encoding cobre quem importa a classe, e o vazamento da terceira coluna de comissão fechou. As oito seções que eu subi ou mantive alto subiram porque pararam de afirmar coisa que o código não faz.

O que segura o volume no limite é a mesma classe de problema em outra roupa. Duas seções afirmam contagens de teste erradas — 26 testes em `45-CONCILIACAO-CONTAS` quando são 30, 42 no acervo quando são 46 — e essas contagens foram justamente o que esta rodada disse ter atualizado; uma delas afirma ainda que os 12 primeiros testes não tocam disco quando o 12º grava um XLSX. Somam-se a mis-seleção de coluna de comissão que sobrevive dentro do próprio teste novo sem ser asseverada, o teste de exit code que não testa exit code, e duas flags de CLI que existem, são documentadas indiretamente e não fazem nada. Nenhum desses derruba dado de produção como `DAT_CREDITO` derrubava; todos são o volume errando sobre si mesmo, que é o defeito que ele elegeu como tese. Antes de gravar `PRONTO`, valeria recontar `45-CONCILIACAO-CONTAS`, ligar `--sep`/`--encoding` a `ler_csv()` e fazer o teste das três candidatas afirmar qual coluna foi escolhida.
