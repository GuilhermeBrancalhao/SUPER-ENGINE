# Auditoria — VOL-45 CONCILIACAO-CONTAS

- Data: 2026-08-20
- Volume: 45-CONCILIACAO-CONTAS (tipo ENGINE)
- Auditor: modelo independente (Opus 5)

## Verificações executadas

| Comando | Saída resumida | Resultado |
|---|---|---|
| `python -m ferramentas.validar 45 --raiz ../acervo-controladoria` (de dentro de `acervo/`) | `ok: volume 45 sem violacoes` | Verde |
| `python -m pytest exemplos/45-conciliacao-contas -q` (de dentro de `acervo-controladoria/`) | `....................... 23 passed in 0.08s` | Verde |
| `python -m pytest exemplos/45-conciliacao-contas -q --collect-only` | `23 tests collected` em 6 arquivos | Confere com o "vinte e três testes" de 11 e 13 |
| Mutação: `casamento.BOILERPLATE = set()` e rodar o caso do Caso 2 | `casar` ainda escolhe `T2` — o teste continuaria passando | **Falha de verificação**: o teste citado como prova do boilerplate não é load-bearing |
| Mutação: guarda decidindo por `abs(valor)` isolado | dia diferente passa a ser bloqueado por engano → teste falharia | Confere com a afirmação de 13-Testes.md |
| `grep` por persistência em `trilha.py` | nenhum `open`/`json`/`sqlite`/`Path` — lista em memória | **Contradiz** 11-Implementacao.md ("registro persistente que sobrevive entre execuções") |
| Existência dos 5 módulos, dos 6 arquivos de teste e dos links relativos de 18 | todos existem e resolvem | Verde |

## Notas por seção

| Seção | Nota | Justificativa em uma frase |
|---|---|---|
| 01-Introducao | 9 | Enuncia as cinco decisões recorrentes e justifica com precisão por que o volume não é o 43, sem prosa de enchimento. |
| 02-Objetivos | 9 | Cinco objetivos verificáveis, cada um amarrado a um módulo e a um teste nomeado que de fato existe na suíte. |
| 03-Escopo | 7 | Fronteiras e destinos excelentes, mas afirma que "todas as cinco funções públicas são puras, sem efeito colateral" quando há mais de cinco funções públicas e duas delas mutam estado — como 09 mesma admite. |
| 04-Arquitetura | 9 | `C4Context` válido, fechado e seguido de prosa que explica a fronteira (não legenda), com justificativa real para o desacoplamento dos cinco módulos. |
| 05-Diagramas | 6 | Os dois diagramas são válidos e bem explicados, mas o `sequenceDiagram` põe módulo chamando módulo (contradizendo 04), omite da assinatura de `achar_ancora` justamente o parâmetro que encarna a regra central, e cita como prova do ramo MEDIA/BAIXA um teste que nunca chega a chamar `classificar()`. |
| 06-Fluxogramas | 7 | `stateDiagram-v2` completo e bem narrado, com testes reais na segunda metade, mas a máquina consulta apenas a guarda volátil antes de escrever, nunca a trilha, contradizendo a invariante de 07. |
| 07-Regras | 8 | Cinco invariantes com o mecanismo do erro que cada uma evita e teste nomeado, exceto "título aberto vence lançamento novo", que não tem como falhar porque o motor não tem função de criação. |
| 08-Modelos | 8 | Fiel ao código em todos os tipos, defaults e no `CENTAVO = 0.005`, e justifica a duplicação deliberada de `Movimento`; omite `data_inicial_conhecida` do contrato de `achar_ancora`. |
| 09-Boas-Praticas | 9 | Seis práticas com o porquê e duas delas não óbvias ("pendência é sucesso do desenho", "testar a ordem de chamada"), e é a seção que enuncia corretamente o que 03 e 15 erram sobre pureza. |
| 10-Anti-Patterns | 9 | Cada anti-pattern traz o mecanismo real da falha e o teste que a barra, com o caso do ERP que limpa o boleto sustentando a decisão de projeto mais importante do volume. |
| 11-Implementacao | 5 | Três afirmações verificáveis são falsas: o boilerplate não está "provado" (suíte fica verde com o mecanismo desligado), a trilha não é persistente (é lista em memória), e `BOILERPLATE` não contém `DEBIT`, o token exato do exemplo-vitrine. |
| 12-Exemplos | 6 | Casos 1 e 3 são exatos e rastreáveis, mas o Caso 2 se apoia inteiramente no teste não load-bearing e sua narração está truncada ("um posto de padaria"). |
| 13-Testes | 6 | Contagens e a afirmação sobre a mutação da guarda conferem, mas a tese central da seção — toda regra tem teste que falha se violada — é falsa para pelo menos duas regras, e a seção declara `ancora.py` como seu exemplo em vez de um arquivo de teste. |
| 14-Metricas | 8 | Cinco métricas com definição, fonte e a decisão que cada uma habilita, incluindo o alvo zero de falso positivo; a de falso positivo, porém, não é computável a partir de `historico()`, que não carrega o nível de confiança. |
| 15-Checklist | 5 | Acionável e honesto no que falta, mas dois itens marcados `[x]` são refutáveis por quem audita — "os cinco módulos são puros" e "cada invariante tem teste que falha se violada" — e um checklist que se autocertifica errado é pior que um item ausente. |
| 16-Roadmap | 8 | Três lacunas concretas com o motivo de cada uma esperar, ordem de cobertura justificada e os limiares nomeados como pontos de calibração futura. |
| 17-Conclusao | 8 | Sintetiza os cinco princípios generalizáveis e é honesta sobre o `RASCUNHO`, sem introduzir afirmação nova que precise de prova. |
| 18-Referencias-Cruzadas | 8 | Tabela de vizinhança com a relação exata de cada volume, lista de links que de fato resolvem hoje e navegação interna com ordem justificada. |

media: 7.5

## Problemas encontrados

**P1 — O teste citado como prova do desconto de boilerplate não prova nada.**
`11-Implementacao.md` ("provado em `test_boilerplate_nao_derruba_a_identificacao_de_fornecedores_diferentes`") e `12-Exemplos.md` (Caso 2). Esvaziando `BOILERPLATE` por completo — isto é, deletando o mecanismo inteiro que a seção existe para defender — `casar()` continua escolhendo `T2` e o teste continua verde. O motivo é que a descrição do movimento é *idêntica* à contraparte de T2: na comparação bruta T2 marca 1.0 e T1 marca 0.727, então o vencedor correto já sai por diferença de texto cru. O teste confirma o caminho feliz; não captura o erro que a regra existe para evitar.

**P2 — `BOILERPLATE` não contém `DEBIT`, o token do próprio exemplo-vitrine.**
`exemplos/45-conciliacao-contas/casamento.py` tem `"DEBITO"` no conjunto, mas não `"DEBIT"`. Os tokens sobreviventes do movimento do Caso 2 são `{DEBIT, FARMACIA, SAUDE}` e os de T1 são `{DEBIT, PADARIA, CENTRAL}` — o boilerplate que `11-Implementacao.md` afirma ser descontado permanece nos dois lados inflando a similaridade. (`BOA` também cai, mas por outra razão: a regra de `len(t) >= 4`.)

**P3 — A trilha é descrita como persistente e não é.**
`11-Implementacao.md`: "a trilha é o registro persistente que sobrevive entre execuções" e "a trilha como o registro que a próxima execução consulta". `trilha.py` é uma `list` e um `set` em memória, sem nenhuma escrita em disco. Como consequência, a garantia de idempotência entre execuções que `07-Regras.md` declara ("a trilha local é a única fonte de verdade sobre já processado") não existe no código entregue: reiniciar o processo zera as duas camadas.

**P4 — A máquina de estados nunca consulta a trilha antes de escrever.**
`06-Fluxogramas.md` vai de `VerificandoDuplicata` (só `guarda.ja_registrado()`) para `Escrito` e só então para `RegistradoNaTrilha`. `07-Regras.md` diz que a trilha "é consultada antes de qualquer índice remoto" e `11-Implementacao.md` diz que a guarda "pode ser reconstruída do zero a cada execução (memória volátil)". Juntando as três: no fluxo desenhado, a única barreira consultada antes da escrita é a volátil. Não há teste de segunda execução (guarda nova, trilha já com a chave, não escrever) — o cenário que motiva a existência da trilha é o único não coberto.

**P5 — Item de checklist marcado `[x]` que a auditoria refuta.**
`15-Checklist.md`, item 3: "Cada invariante de `07-Regras.md` tem pelo menos um teste que falha se for violada." Falso para duas invariantes: o desconto de boilerplate (ver P1) e "título em aberto sempre vence lançamento novo", que não tem teste possível porque o motor não expõe nenhuma função de criação de lançamento avulso — não há o que a regra proíba, logo não há o que testar.

**P6 — "São puros" dito de forma contraditória em três seções.**
`03-Escopo.md` ("todas as cinco funções públicas ... são puras ... sem efeito colateral de I/O") e `15-Checklist.md` ("são puros (sem I/O)") contra `09-Boas-Praticas.md` ("Só `trilha.registrar()` e `guarda.registrar()` têm efeito colateral"). 09 está certa; 03 e 15 estão erradas, e 03 ainda erra a contagem — as funções públicas dos cinco módulos são nove, não cinco.

**P7 — `05-Diagramas.md` atribui orquestração a `confianca.py`.**
O `sequenceDiagram` tem `Cas-->>Conf`, `Conf->>Grd` e `Conf->>Tri`, ou seja, a confiança chamando guarda e trilha. `04-Arquitetura.md` afirma o oposto: "nenhum módulo conhece os outros quatro por importação direta — a composição acontece em quem chama". O chamador não é participante do diagrama, e é ele quem faz essas chamadas em `test_fluxo_completo.py`.

**P8 — O teste citado para o ramo MEDIA/BAIXA cobre outro ramo.**
`05-Diagramas.md` cita `test_fluxo_nao_escreve_quando_confianca_e_baixa` como cobertura de "quando a confiança fica em MEDIA ou BAIXA, o fluxo nunca chega a guarda ou trilha". O teste só faz `casar()` devolver `None` e assertar isso — nunca chama `classificar()`. É o ramo `SemTitulo`, não o ramo `Classificado → PendenciaHumana`. O ramo de confiança insuficiente não tem cobertura ponta-a-ponta.

**P9 — A assinatura de `achar_ancora` no diagrama omite o parâmetro que carrega a regra.**
`05-Diagramas.md` escreve `achar_ancora(saldo, movimentos, saldos_banco)`; a real é `achar_ancora(saldo_inicial_conhecido, data_inicial_conhecida, movimentos, saldos_banco)`. `data_inicial_conhecida` é exatamente o que materializa "caminhar para frente a partir de um saldo passado conhecido". `08-Modelos.md` também não o documenta.

**P10 — A métrica de falso positivo não é computável do modelo entregue.**
`14-Metricas.md` define a fonte como "cruzamento entre a trilha (`trilha.historico()`) e o registro de reversões". `RegistroTrilha` tem `chave`, `usuario`, `quando`, `acao`, `detalhe` — nenhum campo de confiança. Não há como separar, no histórico, o que foi escrito com ALTA do que foi escrito por decisão humana, que é a divisão que a métrica exige.

**P11 — Defeitos menores.** `08-Modelos.md`: "a degradação seguro" (concordância). `12-Exemplos.md`: "um posto de padaria" — os dados do teste são `PADARIA CENTRAL` e `FARMACIA BOA SAUDE`. `13-Testes.md` declara `<!-- exemplo: exemplos/45-conciliacao-contas/ancora.py -->` numa seção sobre testes, onde o exemplo natural seria um arquivo de teste. `casamento.py`: com `t.valor == 0`, a tolerância `abs(t.valor) * tolerancia_valor` colapsa para zero e só um movimento de valor exatamente zero casa — comportamento não descrito em nenhuma seção.

## Sugestões concretas de melhoria

1. **Reescrever o teste de boilerplate para ser load-bearing.** Fazer a descrição do movimento *não* ser idêntica à contraparte vencedora — por exemplo, movimento `"COMPRA NACIONAL DEBITO FARMACIA BOA SAUDE MATRIZ"` contra títulos `"COMPRA NACIONAL DEBITO PADARIA CENTRAL LTDA"` e `"FARMACIA BOA SAUDE"`. Aí o prefixo compartilhado domina a comparação bruta, T1 ganha sem o desconto, e o teste passa a falhar se `BOILERPLATE` for esvaziado. Verificar a nova versão exatamente como esta auditoria verificou: zerando o conjunto e confirmando que o teste fica vermelho.
2. **Acrescentar `DEBIT` (e as variantes truncadas que aparecerem em extrato real) ao conjunto `BOILERPLATE`**, ou trocar a comparação exata por prefixo/radical. Enquanto `DEBIT` sobrevive, o exemplo-vitrine do volume demonstra o contrário do que afirma.
3. **Resolver a questão da persistência da trilha escolhendo um dos dois caminhos, e dizer qual.** Ou `trilha.py` ganha persistência real (um `registrar`/`carregar` sobre arquivo append-only, mantendo a pureza dos outros quatro módulos) e o volume passa a ter a garantia que declara; ou `11-Implementacao.md` para de chamá-la de persistente e passa a dizer que a persistência é responsabilidade de quem compõe, com o contrato dessa fronteira explícito. A segunda é mais barata e igualmente honesta — a atual é a única inaceitável.
4. **Inserir a consulta à trilha antes da escrita na máquina de estados de `06-Fluxogramas.md`**, com um estado de verificação em duas camadas (trilha para o histórico entre execuções, guarda para o lote corrente), e escrever o teste que hoje não existe: trilha já com a chave, guarda recém-instanciada, motor não escreve.
5. **Adicionar ao fluxo completo o teste que 05 promete**: um movimento que *casa* mas classifica como MEDIA, assertando que `guarda.registrar` e `trilha.registrar` não são chamados. Renomear o teste atual para `test_fluxo_para_em_pendencia_quando_nao_ha_titulo`, que é o que ele faz.
6. **Corrigir `03-Escopo.md` e o primeiro item de `15-Checklist.md`** para a formulação que `09-Boas-Praticas.md` já usa: as funções de *decisão* são puras; `guarda.registrar()` e `trilha.registrar()` mutam estado em memória por desenho, e é isso que permite testar sem mock.
7. **Desmarcar o item 3 de `15-Checklist.md`** até que P1 e a invariante de título aberto tenham teste real — ou reformular a invariante para algo que o motor possa violar, já que ele não cria lançamento. Um checklist de volume ENGINE só vale se cada `[x]` sobreviver a quem não escreveu o volume.
8. **Acrescentar `confianca: Confianca` (ou um campo equivalente em `detalhe`) a `RegistroTrilha`**, sem o que a métrica de falso positivo de `14-Metricas.md` — declarada como "a métrica de segurança" — não tem como ser produzida.
9. **Ajustar o `sequenceDiagram` de 05** para incluir o orquestrador como participante e mover as setas `Conf->>Grd` e `Conf->>Tri` para ele, alinhando o diagrama com o desacoplamento que 04 defende e com o que `test_fluxo_completo.py` realmente faz. Na mesma passada, completar a assinatura de `achar_ancora` com `data_inicial_conhecida` no diagrama e em `08-Modelos.md`.
10. **Documentar a fronteira de `t.valor == 0` em `07-Regras.md` ou `16-Roadmap.md`** e corrigir os defeitos de redação de P11.

## Veredicto

Requer revisão

Os dois gates mecânicos estão verdes e o volume é, na maior parte, escrito com rigor real — 07, 09 e 10 são seções que um leitor usaria em produção, e a suíte tem testes genuinamente load-bearing (o da guarda foi verificado por mutação e falha corretamente). O que reprova não é falta de substância: é que três afirmações verificáveis do volume não sobrevivem à verificação (P1, P2, P3), que a garantia de idempotência entre execuções — razão de existir da trilha, e o ponto mais forte da argumentação do volume — não está implementada nem coberta (P3, P4), e que o checklist da seção 15 certifica como feito exatamente um dos itens que esta auditoria refutou (P5). Com `media: 7.5` e duas seções em 5 (11-Implementacao e 15-Checklist), falham os dois critérios da Definição de PRONTO de `00-INTRODUCAO/Convencoes.md`. O `status: RASCUNHO` no front-matter continua sendo a descrição correta do estado do volume.
