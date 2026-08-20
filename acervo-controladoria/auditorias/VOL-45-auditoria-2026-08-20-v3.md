# Auditoria — VOL-45 CONCILIACAO-CONTAS (3ª rodada)

- Data: 2026-08-20
- Volume: 45-CONCILIACAO-CONTAS (tipo ENGINE)
- Auditor: modelo independente (Opus 5), 3ª rodada

## Verificações executadas

| Comando / técnica | Saída literal | Resultado |
|---|---|---|
| `python -m ferramentas.validar 45 --raiz ../acervo-controladoria` (de `acervo/`) | `ok: volume 45 sem violacoes`, `EXIT=0` | Verde |
| `python -m pytest exemplos/45-conciliacao-contas -q` (de `acervo-controladoria/`) | `30 passed in 0.10s` | Verde |
| `python -m pytest ... --collect-only -q` | `30 tests collected in 0.05s`, 6 arquivos | Confere com `11-Implementacao` ("trinta"); **contradiz** `13-Testes` ("Vinte e seis") |
| **M1** — apagar `if dia < data_inicial_conhecida: continue` de `ancora.py` | `1 failed, 29 passed` — cai `test_dia_anterior_a_data_inicial_conhecida_e_ignorado_mesmo_batendo_por_coincidencia` | **Mutante MORTO** (sobrevivia na rodada 2) |
| **M2a** — remover o bloco `if similaridade(...) < limiar_similaridade: return None` | `2 failed, 28 passed` — caem `test_limiar_similaridade_e_load_bearing` e `test_filtro_de_token_curto_e_load_bearing` | **Mutante MORTO** (sobrevivia) |
| **M2b** — `limiar_similaridade: float = 0.0` (default desligado) | `2 failed, 28 passed` — os mesmos dois | **Mutante MORTO** |
| **M3** — remover `len(t) >= 4` de `_tokens()` | `1 failed, 29 passed` — cai `test_filtro_de_token_curto_e_load_bearing` | **Mutante MORTO** (sobrevivia) |
| **M4** — ramo `MEDIA` de `classificar()` devolve `BAIXA` | `1 failed, 29 passed` — cai `test_fluxo_nao_escreve_quando_confianca_e_media` | **Mutante MORTO** (sobrevivia — era o achado mais grave da rodada 2) |
| Reprodução do caso do teste MEDIA fora da suíte | `sim = 0.7077`; `classificar(Evidencia(False, 0.71)) == Confianca.MEDIA` | O docstring ("similaridade 0.71", entre 0.6 e 0.85) **confere com o corpo**, e o corpo confere com o nome |
| **M5** — `melhor = melhor or Ancora(...)` (âncora mais antiga vence) | `1 failed, 29 passed` | Mutante morto |
| **M6** — `CENTAVO = 100.0` | `1 failed, 29 passed` | Mutante morto |
| **M7** — `tolerancia_valor: float = 0.0` | `1 failed, 29 passed` | Mutante morto |
| **M8** — comentar `candidatos.sort(key=similaridade...)` | `2 failed, 28 passed` | Mutante morto |
| **M9** — `LIMIAR_HISTORICO_DOMINANCIA = 0.0` | `30 passed` | **MUTANTE SOBREVIVE — novo** |
| **M10** — `normalizada()` descarta a contraparte | `1 failed, 29 passed` | Mutante morto |
| Restauro pós-mutação (`diff` contra backup dos três módulos + `sed -n 23p guarda.py`) | `RESTAURO OK`, `30 passed` | Volume devolvido intacto; nada editado |
| `grep dominancia` em `tests/` | 4 ocorrências, todas com `dominancia_historica` ≥ 0.85 ou = 0.0 acompanhada de `ocorrencias_historicas` = 0/1 | Nenhum teste isola a dominância; confirma M9 |
| Cruzamento de **todo** nome `test_*` citado nas 18 seções contra `--collect-only` | 1 nome citado inexistente: `test_fluxo_nao_escreve_quando_confianca_e_media_ou_baixa` (`05-Diagramas.md:47`) | Citação morta (o teste foi renomeado nesta rodada) |
| `grep -i "puro\|puras"` nas 18 seções | só `03-Escopo.md:42-45` e `15-Checklist.md:15`, ambos na formulação precisa ("as funções de *decisão* são puras") | `10-Anti-Patterns.md` **não** contém mais a afirmação errada |
| Leitura integral de `06-Fluxogramas.md` | `stateDiagram-v2` com `ConsultandoTrilha` antes de `VerificandoDuplicata` + prosa citando `test_segunda_execucao_...` | Corrigido; mas o §"caminho de decisão" (linha 52) segue dizendo `Classificado` → `VerificandoDuplicata` |
| `grep "valor == 0"` / "valor zero" nas 18 seções | nenhuma ocorrência | Remanescente |
| Links relativos de `18-Referencias-Cruzadas.md` (7 links, teste de existência de arquivo) | 7/7 `OK` | Verde |
| `grep atualizado_em` nas 18 seções | `2026-08-03` em **todas as 18** | Falso em 11 seções cujo corpo declara edição em 2026-08-20 |

## Notas por seção

| Seção | Nota | Justificativa |
|---|---|---|
| 01-Introducao | 9 | Enuncia as cinco decisões recorrentes e justifica por que o volume não é o 43; nenhuma afirmação verificável está errada. |
| 02-Objetivos | 9 | Cinco objetivos amarrados a módulo e a teste nomeado — todos os nomes citados existem na suíte de 30. |
| 03-Escopo | 9 | A formulação de pureza é exata (nomeia as quatro funções de decisão, admite as duas que mutam memória) e é a redação que 10 passou a espelhar. |
| 04-Arquitetura | 9 | `C4Context` válido com prosa que explica a fronteira e justifica o desacoplamento; nada refutável. |
| 05-Diagramas | 7 | O `sequenceDiagram` está correto e a prosa sobre o ramo MEDIA/BAIXA agora é **substantivamente verdadeira** (M4 morre), mas a seção cita como prova um teste que não existe mais: o nome foi trocado por `..._e_media` e a citação não acompanhou. |
| 06-Fluxogramas | 8 | A correção é real e boa: duas barreiras em sequência, com prosa que explica por que a ordem importa e cita o teste que sustenta. Perde ponto porque a subseção da própria página continua descrevendo a transição antiga (`Classificado` → `VerificandoDuplicata`), contradizendo o diagrama recém-corrigido logo acima. |
| 07-Regras | 9 | Cinco invariantes com o mecanismo do erro que cada uma evita; a precisão nova sobre o escopo da trilha (só escrita ALTA automática) fecha R6 nomeando a fronteira em vez de estreitá-la em silêncio, e quatro das cinco invariantes agora têm mutante que morre. |
| 08-Modelos | 8 | Fiel ao código em todos os tipos, defaults e no `CENTAVO = 0.005`; segue sem o contrato de `achar_ancora`, que 05 documenta. |
| 09-Boas-Praticas | 8 | Seis práticas com o porquê, duas delas não óbvias; "nenhuma das cinco funções faz chamada de rede" é contagem que 03 abandonou ao nomear quatro funções de decisão mais dois métodos. |
| 10-Anti-Patterns | 9 | A afirmação de pureza foi removida e substituída por texto que distingue mutação em memória de I/O externo, consistente com 03/09/15; cada anti-pattern segue trazendo o mecanismo real da falha. |
| 11-Implementacao | 8 | A contagem foi corrigida para "trinta" e confere com `--collect-only`, e a nota de processo ("nunca repetir o número aqui sem conferir") é a resposta certa ao achado; a seção mantém "ocorrências **e** dominância acima dos limiares" quando metade dessa conjunção sobrevive à mutação (M9). |
| 12-Exemplos | 9 | Os três casos batem com o código, o Caso 2 depende de fato do desconto (verificado por M-boilerplate na rodada 2 e por M8 aqui) e os testes citados existem. |
| 13-Testes | 5 | É a seção cujo trabalho é ser exata sobre a suíte, e é a que ficou fora da correção: abre em "Vinte e seis testes" contra 30 coletados, contradizendo `11-Implementacao` na mesma rodada em que 11 foi consertada; o inventário "O que cada arquivo cobre" não menciona nenhum dos quatro testes novos; a tese de fechamento ("cada regra de 07 tem teste que falha se violada") segue refutada por M9; e o `<!-- exemplo: ... casamento.py -->` continua apontando para um módulo numa seção sobre testes. |
| 14-Metricas | 8 | O argumento de computabilidade da métrica de falso positivo fecha, e agora se apoia numa fronteira que 07 nomeia explicitamente — a lacuna de R6 deixou de ser silenciosa. |
| 15-Checklist | 8 | Os itens 2 e 3 passaram de autocertificação refutável a afirmação verificada: o ramo MEDIA é coberto (M4 morre) e a segunda execução também; o item 3 ainda é levemente amplo demais por causa de M9. |
| 16-Roadmap | 8 | Três lacunas concretas com o motivo de cada uma esperar e os limiares nomeados como pontos de calibração; a fronteira de `t.valor == 0` continua sem casa em nenhuma seção. |
| 17-Conclusao | 8 | Sintetiza os princípios generalizáveis e é honesta sobre o `RASCUNHO`, sem introduzir afirmação nova que precise de prova. |
| 18-Referencias-Cruzadas | 8 | Tabela de vizinhança com a relação exata de cada volume e 7/7 links resolvendo hoje. |

media: 8.2

## Achados de rodadas anteriores — status

| # | Achado (rodada 2) | Status | Evidência desta auditoria |
|---|---|---|---|
| R1 | Ramo `MEDIA` não exercitado; três seções afirmavam que era | **Corrigido, e verificado por mutação** | `test_fluxo_nao_escreve_quando_confianca_e_media` faz `casar()` achar T1 de verdade, deriva a evidência da MESMA similaridade (0.7077, conferido fora da suíte) e assere `MEDIA`; mutar o ramo para `BAIXA` derruba exatamente esse teste. Docstring, nome e corpo concordam — o defeito de redação que era o pior da rodada 2 desapareceu. |
| R2 | Contradição de contagem entre 11 e 13 | **Migrou de seção** | 11 foi corrigida para "trinta" (confere) e ganhou nota de processo; `13-Testes.md:14` ficou em "Vinte e seis". A contradição não foi fechada, trocou de lado. |
| R3 | Quatro mutantes sobreviventes (corte de data, limiar, token curto, MEDIA) | **Corrigido: os quatro morrem** | M1, M2a, M2b, M3 e M4 acima. Os três testes novos são load-bearing de verdade, não decorativos — cada um derruba a suíte quando o mecanismo é desligado. |
| R4 | `06-Fluxogramas.md` não acompanhou o teste de segunda execução | **Corrigido (com resíduo)** | Diagrama tem `ConsultandoTrilha` antes de `VerificandoDuplicata`, prosa explica por que a ordem importa e cita o teste. Resíduo: a subseção seguinte não foi atualizada e descreve a transição antiga. |
| R5 | "Os cinco módulos são puros de propósito" em 10 | **Corrigido** | A frase não existe mais; o texto substituto distingue mutação em memória de I/O externo e remete a 03/09. |
| R6 | Trilha não registra decisão humana, métrica dependia disso em silêncio | **Corrigido** | `07-Regras.md:37-42` nomeia o escopo da garantia e atribui o segundo rastro a quem compõe o motor — a fronteira ficou declarada, no mesmo padrão da nota de persistência de 11. |
| R7 | Remanescentes menores | **Parcial** | `<!-- exemplo: casamento.py -->` em 13, fronteira de `t.valor == 0` ausente de 07/16, `08-Modelos` sem o contrato de `achar_ancora` e "as cinco funções" em 09 seguem todos como estavam. |

## Problemas encontrados (novos ou remanescentes)

**N1 — `13-Testes.md` ficou com o número errado, no mesmo ciclo em que 11 ficou com o certo.**
`11-Implementacao.md:12` diz "trinta testes" e acerta; `13-Testes.md:14` diz "Vinte e seis testes
em seis arquivos (atualizado em 2026-08-20)". A suíte coleta 30. Pior: 11 ganhou a instrução
correta ("nunca repetir o número aqui sem conferir contra `pytest --collect-only`") e 13, que é a
seção de referência para onde 11 manda o leitor buscar a contagem por arquivo, não foi conferida.
O inventário de 13 também está defasado em conteúdo, não só em número: descreve `test_ancora.py`
por três casos (tem quatro) e `test_casamento.py` sem o teste de limiar e sem o de token curto —
ou seja, os três testes que fecharam R3 não aparecem na seção que existe para catalogá-los.

**N2 — `05-Diagramas.md` cita um teste que não existe mais.**
Linha 47: `test_fluxo_nao_escreve_quando_confianca_e_media_ou_baixa`. Esse nome foi substituído
por `test_fluxo_nao_escreve_quando_confianca_e_media` justamente nesta rodada. O cruzamento de
todos os nomes `test_*` das 18 seções contra `--collect-only` acusa esse único órfão. A afirmação
que ele sustenta ("testa exatamente este ramo") passou de falsa a verdadeira — mérito real da
correção —, mas aponta para um alvo inexistente, e o gate mecânico não pega isso.

**N3 — Mutante novo: `LIMIAR_HISTORICO_DOMINANCIA` não é load-bearing.**
Baixar `LIMIAR_HISTORICO_DOMINANCIA` de `0.8` para `0.0` deixa a suíte em `30 passed`. A promoção
a `ALTA` por histórico forte é uma conjunção — volume **e** dominância —, e `11-Implementacao.md`,
`06-Fluxogramas.md` e o comentário de `confianca.py` ("Exige volume E dominancia") todos afirmam
as duas metades. Só a metade do volume tem prova: `test_ocorrencia_isolada_nao_vira_regra` fixa
`ocorrencias_historicas`, e nenhum teste passa dominância baixa com ocorrências altas. É o mesmo
tipo de lacuna que R3 apontou, num limiar que R3 não tinha listado — o que sugere que a rodada 2
foi tratada como lista de itens a fechar, não como método a repetir sobre o resto do módulo.

**N4 — `06-Fluxogramas.md` contradiz o próprio diagrama corrigido.**
Linha 52, na subseção "O caminho de decisão de confiança em detalhe": "A transição de
`Classificado` para `VerificandoDuplicata` só acontece sob duas condições". No diagrama reescrito
(linhas 20-24), `Classificado` transita para `ConsultandoTrilha`; `VerificandoDuplicata` só é
alcançado depois. A correção acertou o diagrama e a prosa imediatamente abaixo dele, e não releu
a página inteira.

**N5 — `atualizado_em: 2026-08-03` nas 18 seções, incluindo as 11 editadas em 2026-08-20.**
`06-Fluxogramas.md` traz no corpo "**Duas barreiras distintas, nesta ordem — correção de auditoria
em 2026-08-20**" com front-matter de 03/08; o mesmo vale para 03, 05, 07, 10, 11, 12, 13, 14 e 15,
que citam "auditoria de 2026-08-20" no texto. O campo é um dos seis exigidos pelo contrato e o
validador só checa a presença, não a veracidade — é exatamente a classe de defeito que este acervo
foi montado para não ter: metadado verde que mente sobre o estado do arquivo.

**N6 — Remanescentes de R7, intactos.** `13-Testes.md:22` declara
`<!-- exemplo: exemplos/45-conciliacao-contas/casamento.py -->` numa seção sobre testes (aponta
para módulo, não para arquivo de teste). A fronteira de `t.valor == 0` em `casar()` — com valor
zero a tolerância colapsa e só um movimento de valor exatamente zero casa — segue sem menção em
07 ou 16. `08-Modelos.md` segue sem o contrato de `achar_ancora`. `09-Boas-Praticas.md:15` segue
em "as cinco funções", contagem que 03 substituiu por quatro funções de decisão mais dois métodos.

## Veredicto

Requer revisão

Esta rodada é qualitativamente diferente das duas anteriores: as correções não são cosméticas e
não são acreditadas — foram verificadas por mutação, uma por uma. Os quatro mutantes que
sobreviviam morrem agora, e o mais grave deles morre pelo motivo certo: o novo teste do ramo
MEDIA faz `casar()` encontrar um título de verdade, deriva a evidência da mesma similaridade que
o casamento produziu (0.7077, reproduzido fora da suíte) e assere que guarda e trilha não são
tocadas — nome, docstring e corpo finalmente dizem a mesma coisa, que era o defeito mais sério da
rodada 2. As oito mutações adicionais que apliquei por conta própria (âncora mais antiga, CENTAVO
frouxo, tolerância zero, sem ordenação por similaridade, guarda sem contraparte) morreram todas.
A suíte deixou de ser decorativa. `06` ganhou o diagrama que faltava e `07` nomeou a fronteira da
trilha em vez de estreitar a invariante em silêncio — as duas melhores correções do lote.
`media` subiu de 7,7 para 8,2, e o critério de média está cumprido pela primeira vez.

O que reprova é uma seção só, e pelo mesmo padrão das duas rodadas anteriores: a correção foi
aplicada onde a auditoria apontou o dedo, não onde a afirmação vive. `11-Implementacao.md` foi
consertada e recebeu até a regra de processo certa; `13-Testes.md`, que é a seção de referência
para a contagem e o catálogo da suíte, ficou com "vinte e seis" contra 30, sem os três testes
novos no inventário e com a mesma tese de fechamento que um mutante novo (M9, dominância
histórica) refuta. `05` cita um teste renomeado nesta rodada, `06` contradiz o diagrama que
acabou de corrigir três parágrafos abaixo, e as 18 seções carregam `atualizado_em: 2026-08-03`
enquanto onze delas falam de "correção de 2026-08-20" no corpo. Nenhum desses é um erro de
raciocínio — todos são falta de uma releitura de página inteira depois da edição.

Somando: `media: 8.2` (≥ 8,0, primeiro critério cumprido) mas `13-Testes` em 5 (< 6), o que
reprova pelo segundo critério do item 3 da Definição de PRONTO de
`00-INTRODUCAO/Convencoes.md`. `status: RASCUNHO` no front-matter continua correto.

O caminho para a aprovação é o mais curto das três rodadas, e é todo de edição de texto mais um
teste: trocar "Vinte e seis" por "trinta" em `13-Testes.md` e acrescentar ao inventário os quatro
testes novos; escrever em `test_confianca.py` um caso com `ocorrencias_historicas=6` e
`dominancia_historica=0.3` assertando que não vira `ALTA` (mata M9 e torna verdadeira a tese de
fechamento de 13 e o item 3 de 15); corrigir o nome do teste citado em `05-Diagramas.md:47`;
trocar `VerificandoDuplicata` por `ConsultandoTrilha` em `06-Fluxogramas.md:52`; e atualizar
`atualizado_em` nas seções que foram de fato editadas. Feito isso, nenhuma seção fica abaixo de 6
e a média sobe.
