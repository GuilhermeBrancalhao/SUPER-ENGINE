# Auditoria — VOL-45 CONCILIACAO-CONTAS (reauditoria)

- Data: 2026-08-20
- Volume: 45-CONCILIACAO-CONTAS (tipo ENGINE)
- Auditor: modelo independente (Opus 5), reauditoria pós-correção

## Verificações executadas

| Comando | Saída resumida | Resultado |
|---|---|---|
| `python -m ferramentas.validar 45 --raiz ../acervo-controladoria` (de dentro de `acervo/`) | `ok: volume 45 sem violacoes`, exit 0 | Verde |
| `python -m pytest exemplos/45-conciliacao-contas -q` (de dentro de `acervo-controladoria/`) | `26 passed in 0.10s` | Verde |
| `python -m pytest ... --collect-only` | `26 tests collected` em 6 arquivos | Confere com 13-Testes ("vinte e seis"); **contradiz** 11-Implementacao ("vinte e três") |
| Mutação `BOILERPLATE = set()` (arquivo inteiro, suíte inteira) | `3 failed, 23 passed` — caem `test_boilerplate_e_load_bearing`, `test_boilerplate_nao_derruba_...` e `test_similaridade_zero_...` | **P1 corrigido de verdade**: o mecanismo agora é load-bearing |
| Reprodução manual do Caso 2 com e sem `BOILERPLATE` | `com boilerplate: T2` / `sem boilerplate: T1` | Confere com 12-Exemplos e com o docstring do teste |
| `grep "DEBIT"` em `casamento.py` | `"DEBIT"` presente no conjunto (diff de uma linha sobre HEAD) | **P2 corrigido** |
| Mutação: apagar o corte `if dia < data_inicial_conhecida: continue` em `ancora.py` | `26 passed` | **Mutante sobrevive**: a regra central do volume não tem teste que falhe se violada |
| Mutação: `limiar_similaridade` efetivamente desligado (`< 0.0`) | `26 passed` | **Mutante sobrevive**: o descarte por ambiguidade não tem teste |
| Mutação: remover o filtro `len(t) >= 4` de `_tokens()` | `26 passed` | **Mutante sobrevive** |
| Mutação: ramo `MEDIA` de `classificar()` passa a devolver `BAIXA` | `26 passed` | **Mutante sobrevive**: `MEDIA` nunca é produzida por nenhum teste |
| Mutação: guarda decidindo por `abs(valor)` isolado | `3 failed, 23 passed` | Mutante morto — confere com 13-Testes |
| Mutação: `trilha.registrar()` aceitando duplicata em silêncio | `3 failed, 23 passed` | Mutante morto |
| Mutação: `LIMIAR_HISTORICO_OCORRENCIAS >= 1` | `1 failed, 25 passed` | Mutante morto |
| `grep` por persistência em `trilha.py` | segue lista/set em memória, sem `open`/`json`/`sqlite` — e 11-Implementacao **agora diz isso** | **P3 corrigido** (por documentação honesta, o caminho mais barato) |
| `grep "MEDIA"` em `tests/` | só no dicionário de ordenação de `test_confianca.py` e no docstring de `test_fluxo_nao_escreve_quando_confianca_e_media_ou_baixa` | Nenhum teste assere `Confianca.MEDIA` |
| Conferência de todo nome `test_*` citado nas 18 seções contra a suíte | todos existem | Verde |
| `grep "puro/puras"` nas 18 seções | 10-Anti-Patterns segue afirmando "os cinco módulos deste volume são puros de propósito" | **P6 remanescente** numa seção não tocada |
| `grep` por `valor == 0` / "valor zero" nas 18 seções | nenhuma ocorrência | **P11 remanescente** |
| Links relativos de 18 e blocos `<!-- exemplo: -->` | todos resolvem | Verde |

## Notas por seção

| Seção | Nota | Justificativa em uma frase |
|---|---|---|
| 01-Introducao | 9 | Enuncia as cinco decisões recorrentes e justifica com precisão por que o volume não é o 43, sem prosa de enchimento. |
| 02-Objetivos | 9 | Cinco objetivos verificáveis, cada um amarrado a um módulo e a um teste nomeado que de fato existe na suíte. |
| 03-Escopo | 9 | A correção de pureza é exata e melhor que a formulação original — nomeia as quatro funções de decisão, admite as duas que mutam memória e explica por que a distinção é a fronteira que importa. |
| 04-Arquitetura | 9 | `C4Context` válido, fechado e seguido de prosa que explica a fronteira (não legenda), com justificativa real para o desacoplamento dos cinco módulos. |
| 05-Diagramas | 6 | O `sequenceDiagram` foi corrigido bem (orquestrador como chamador único, `data_inicial_conhecida` na assinatura), mas a seção troca uma afirmação falsa por outra: diz que `test_fluxo_nao_escreve_quando_confianca_e_media_ou_baixa` "testa exatamente este ramo" quando o teste assere `titulo is None` e `BAIXA`, e afirma que o outro teste cobre "um ramo diferente" quando os dois cobrem o mesmo ramo `SemTitulo`. |
| 06-Fluxogramas | 6 | `stateDiagram-v2` completo e bem narrado, mas não foi tocado: `VerificandoDuplicata` continua consultando só `guarda.ja_registrado()` antes de `Escrito`, a barreira que 11 mesma chama de volátil, e a seção não cita o novo teste de segunda execução que existiria para sustentá-la. |
| 07-Regras | 8 | Cinco invariantes com o mecanismo do erro que cada uma evita e teste nomeado, mas duas delas ("título aberto vence", agora honestamente declarada intestável em 15, e a âncora que caminha para frente) não têm teste que falhe se violadas. |
| 08-Modelos | 8 | Fiel ao código em todos os tipos, defaults e no `CENTAVO = 0.005`, com a concordância corrigida; segue documentando só as dataclasses, sem o contrato de `achar_ancora` que P9 pedia nesta seção. |
| 09-Boas-Praticas | 9 | Seis práticas com o porquê e duas não óbvias ("pendência é sucesso do desenho", "testar a ordem de chamada"), e é a seção que enunciou corretamente a pureza antes de 03 e 15 serem corrigidas. |
| 10-Anti-Patterns | 7 | Cada anti-pattern traz o mecanismo real da falha, mas a seção não foi incluída na correção de P6 e reintroduz sozinha a contradição que 03 e 15 fecharam: "os cinco módulos deste volume são puros de propósito". |
| 11-Implementacao | 6 | A nota de correção sobre a trilha é exemplar — separa contrato de durabilidade e nomeia a responsabilidade de quem compõe —, mas a mesma seção reescrita em 2026-08-20 continua abrindo com "vinte e três testes" contra os 26 reais e contra o que 13-Testes diz. |
| 12-Exemplos | 8 | Caso 2 foi reescrito com dado que de fato depende do desconto, cita o teste load-bearing correto e a narração truncada desapareceu — verificado por mutação, não por leitura. |
| 13-Testes | 6 | As contagens agora conferem e a nota de atualização é honesta, mas a tese central da seção — toda regra de 07 tem teste que falha se violada — é refutada por quatro mutantes sobreviventes, e o bloco `<!-- exemplo: -->` segue apontando para um módulo, não para um arquivo de teste. |
| 14-Metricas | 8 | O argumento novo sobre computabilidade é válido dentro da máquina de estados desenhada, mas ele revela sem comentar que escrita aprovada por humano não entra na trilha — o que contradiz a trilha ser a única fonte sobre "já processado". |
| 15-Checklist | 6 | Os itens 1 e 3 ficaram honestos e bem redigidos, mas o item 2 é `[x]` para "cobre o ramo de confiança MEDIA/BAIXA" quando nenhum teste chega a `MEDIA` e o ramo sobrevive à mutação — voltou a se autocertificar num ponto refutável. |
| 16-Roadmap | 8 | Três lacunas concretas com o motivo de cada uma esperar e os limiares nomeados como pontos de calibração; a fronteira de `t.valor == 0` continua sem casa em nenhuma seção. |
| 17-Conclusao | 8 | Sintetiza os cinco princípios generalizáveis e é honesta sobre o `RASCUNHO`, sem introduzir afirmação nova que precise de prova. |
| 18-Referencias-Cruzadas | 8 | Tabela de vizinhança com a relação exata de cada volume, links que de fato resolvem hoje e navegação interna com ordem justificada. |

media: 7.7

## Achados da auditoria anterior — status

| # | Achado | Status | Evidência desta auditoria |
|---|---|---|---|
| P1 | Teste de boilerplate não load-bearing | **Corrigido** | Esvaziar `BOILERPLATE` derruba 3 testes, incluindo o citado por 11 e 12; reprodução manual mostra o vencedor mudando de `T2` para `T1`. |
| P2 | `BOILERPLATE` sem `DEBIT` | **Corrigido** | `"DEBIT"` presente em `casamento.py`. |
| P3 | Trilha descrita como persistente | **Corrigido** | 11-Implementacao passou a dizer que é memória de processo e que durabilidade é de quem compõe — o caminho 2 da sugestão anterior, aplicado com o contrato da fronteira explícito. |
| P4 | Máquina de estados nunca consulta a trilha antes de escrever | **Parcial (só o teste)** | `test_segunda_execucao_com_guarda_nova_e_trilha_antiga_nao_reescreve` existe e é real, mas `06-Fluxogramas.md` não mudou uma linha: o diagrama segue com a guarda volátil como única barreira pré-escrita, e nem cita o novo teste. |
| P5 | Item `[x]` refutável no checklist | **Parcial** | O item 3 foi reformulado com honestidade (invariante intestável nomeada), mas o item 2 assumiu o lugar do refutável: afirma cobertura do ramo `MEDIA`, que não existe. |
| P6 | "São puros" contraditório | **Parcial** | 03 e 15 corrigidos com precisão; 10-Anti-Patterns ficou de fora e mantém a afirmação errada. |
| P7 | Sequência com módulo chamando módulo | **Corrigido** | Todas as setas partem de `Op`; a prosa explicita que nenhuma seta parte de `Cas`/`Conf`/`Grd`/`Tri`. |
| P8 | Teste do ramo MEDIA/BAIXA cobre outro ramo | **Cosmético** | O teste novo assere `titulo is None` (ramo `SemTitulo`, o mesmo do antigo) e `Confianca.BAIXA`; seu próprio docstring diz o contrário do corpo ("HÁ título candidato e o casamento ACHA um par"). Mutar o ramo `MEDIA` para `BAIXA` deixa a suíte verde: o ramo continua sem cobertura, e agora com duas seções afirmando que tem. |
| P9 | Assinatura de `achar_ancora` incompleta | **Corrigido em 05, não em 08** | `05-Diagramas.md` traz os quatro parâmetros e explica o papel de `data_inicial_conhecida`; `08-Modelos.md` segue sem o contrato da função. |
| P10 | Métrica de falso positivo não computável | **Corrigido com ressalva** | O argumento por invariante fecha para escrita automática; a ressalva nova é que decisão humana escrita não entra em `trilha.historico()`, e ninguém diz onde ela entra. |
| P11 | Defeitos menores | **Parcial** | "a degradação segura" e a "padaria" do Caso 2 corrigidos; `<!-- exemplo: casamento.py -->` em 13-Testes e a fronteira de `t.valor == 0` seguem como estavam. |

## Problemas encontrados (novos ou remanescentes)

**R1 — O ramo `MEDIA` não é exercitado por teste nenhum, e três seções afirmam que é.**
Mutando `confianca.py` para que o ramo `MEDIA` devolva `BAIXA`, a suíte fecha em `26 passed`.
Nenhum teste da suíte assere `Confianca.MEDIA` (grep confirma: a única ocorrência em código de
teste é o dicionário de ordenação de `test_confianca.py`). Ainda assim `05-Diagramas.md` diz que
`test_fluxo_nao_escreve_quando_confianca_e_media_ou_baixa` "testa exatamente este ramo",
`13-Testes.md` lista "os dois caminhos em que o motor decide não escrever" como cobertos, e
`15-Checklist.md` marca `[x]`. O teste em questão assere `titulo is None` — ou seja, é o ramo
`SemTitulo` de novo, o mesmo do teste que ele deveria complementar — e classifica uma evidência
montada à mão como `BAIXA`. É o achado P8 com nome novo, e agravado: antes uma seção errava,
agora três.

**R2 — Contradição de contagem entre 11 e 13, na seção que foi reescrita.**
`11-Implementacao.md` linha 12: "com vinte e três testes ao lado". `13-Testes.md` linha 14:
"Vinte e seis testes em seis arquivos (atualizado em 2026-08-20)". A suíte coleta 26. O tipo de
afirmação é exatamente o que a auditoria anterior penalizou em 11 — número verificável em um
comando — e a seção recebeu edição nesta rodada sem que a primeira frase fosse conferida.

**R3 — Quatro mutantes sobrevivem, e a regra central do volume é um deles.**
Apagar `if dia < data_inicial_conhecida: continue` de `achar_ancora` deixa a suíte verde. Esse é
o corte que materializa "caminhar para frente a partir de um saldo passado conhecido", a regra
que 01, 02, 07, 10, 12 e 17 apresentam como o principal aprendizado do volume — e que
`05-Diagramas.md` acabou de ser corrigido para destacar. Também sobrevivem o desligamento de
`limiar_similaridade` (o descarte por ambiguidade que 11 descreve como decisão de projeto) e a
remoção do filtro `len(t) >= 4`. Isso refuta diretamente a tese de fechamento de `13-Testes.md`.
Nota de crédito: guarda, trilha e limiar de histórico mataram seus mutantes corretamente.

**R4 — `06-Fluxogramas.md` não acompanhou a correção.**
O teste de segunda execução foi escrito e é bom — inclusive documenta no docstring por que a
guarda isolada mentiria. Mas a máquina de estados que ele deveria sustentar continua com
`VerificandoDuplicata --> Escrito: guarda.ja_registrado() = false` como único portão, e a seção
não menciona trilha em nenhuma transição pré-escrita. Quem lê 06 e 07 na sequência ainda encontra
a mesma incoerência que motivou P4.

**R5 — P6 sobreviveu em 10-Anti-Patterns.**
"Os cinco módulos deste volume são puros de propósito" (linha 40) contra `09-Boas-Praticas.md`
("Só `trilha.registrar()` e `guarda.registrar()` têm efeito colateral") e contra a nova redação
de 03 e 15. Correção aplicada por busca de seção, não por busca de afirmação.

**R6 — A trilha não registra decisão humana, e a métrica nova depende disso sem dizer.**
O argumento acrescentado a `14-Metricas.md` está certo: se só ALTA chega a `registrar()`, todo
registro é escrita automática. A consequência não dita é que a baixa aprovada por um operador
(o destino de `PendenciaHumana`, que 04 e 06 tratam como saída legítima do motor) não deixa
rastro na trilha — logo a próxima execução não sabe que ela ocorreu, apesar de `07-Regras.md`
declarar a trilha "a única fonte de verdade sobre já processado". Ou a fronteira é nomeada como
está a de persistência em 11, ou a invariante de 07 é mais estreita do que a seção afirma.

**R7 — Remanescentes menores.** `13-Testes.md` continua declarando
`<!-- exemplo: exemplos/45-conciliacao-contas/casamento.py -->` numa seção sobre testes.
A fronteira de `t.valor == 0` em `casar()` (tolerância colapsa a zero e só um movimento de valor
exatamente zero casa) segue sem menção em 07 ou 16. `08-Modelos.md` não documenta o contrato de
`achar_ancora`. `09-Boas-Praticas.md` fala de "as cinco funções", contagem que 03 abandonou.
`test_fluxo_nao_escreve_quando_confianca_e_media_ou_baixa` tem docstring que contradiz o próprio
corpo — o pior defeito de redação possível num teste, porque quem lê o nome e o docstring acredita
numa cobertura que o corpo não entrega.

## Veredicto

Requer revisão

As correções são reais onde foram feitas, e três delas são de qualidade acima da sugestão que as
motivou: o teste de boilerplate agora morre por mutação em duas direções (verificado, não
acreditado), a nota sobre a trilha em 11 separa contrato de durabilidade com honestidade que
melhora o volume, e a nova redação de 03 sobre pureza é mais precisa do que a que 09 já tinha.
`media` subiu de 7,5 para 7,7.

O que ainda reprova é o padrão: a correção foi aplicada onde a auditoria anterior apontou o dedo,
não onde a afirmação vive. `10-Anti-Patterns.md` guardou o erro de pureza porque não estava na
lista; `11-Implementacao.md` foi reescrita no fim e manteve o número errado na primeira linha;
`06-Fluxogramas.md` ganhou o teste mas não o diagrama. E o caso mais grave é P8/R1: o teste novo
tem o nome do ramo certo, um docstring que descreve o ramo certo, e um corpo que testa o ramo
errado — e três seções passaram a citá-lo como prova. Uma correção que faz o volume afirmar com
mais confiança algo que continua falso é pior que o achado original. Somando: `media: 7.7` (< 8,0)
e cinco seções em 6, falham os dois critérios do item 3 da Definição de PRONTO de
`00-INTRODUCAO/Convencoes.md`. `status: RASCUNHO` no front-matter continua correto.

Para a próxima rodada, o caminho mais curto para 8,0 é curto de verdade: escrever um teste que
faça `casar()` devolver título E `classificar()` devolver `MEDIA`, assertando que guarda e trilha
não são tocadas (fecha R1, 05, 13 e o item 2 de 15); acrescentar a `test_ancora.py` um dia de
saldo anterior a `data_inicial_conhecida` que só passa se o corte existir (fecha o mutante de R3);
trocar "vinte e três" por "vinte e seis" em 11; apagar "os cinco módulos são puros de propósito"
de 10; e inserir a consulta à trilha na máquina de estados de 06.
