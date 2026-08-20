---
name: engine
description: Liga o modo ENGINE — motor de engenharia com ciclo em fases, elenco de agentes por papel e portas de segurança graduadas por risco. Use quando o pedido for "/engine", "/engine off", "/engine status", "ligar o motor", "desligar o motor", ou quando o usuário pedir para conduzir um trabalho de engenharia de ponta a ponta.
---

# ENGINE

Motor de engenharia persistente. O ciclo é sempre do motor: ferramenta externa (ECC,
superpowers) executa **dentro** de uma fase; nenhuma decide qual é a fase seguinte nem
quando o ciclo termina. Instrução direta do usuário sempre vence o motor.

## Verbos

| Pedido do usuário | O que fazer |
|---|---|
| `/engine <pedido>` | rode `ENGINE_RAIZ="$(pwd)" bash "${CLAUDE_PLUGIN_ROOT}/hooks/engine.sh" "${CLAUDE_PLUGIN_ROOT}/ferramentas/cli.py" ligar "<objetivo em uma frase>"` e entre em DESCOBERTA |
| `/engine off` | rode `ENGINE_RAIZ="$(pwd)" bash "${CLAUDE_PLUGIN_ROOT}/hooks/engine.sh" "${CLAUDE_PLUGIN_ROOT}/ferramentas/cli.py" desligar` e apresente o resumo do ciclo |
| `/engine status` | rode `ENGINE_RAIZ="$(pwd)" bash "${CLAUDE_PLUGIN_ROOT}/hooks/engine.sh" "${CLAUDE_PLUGIN_ROOT}/ferramentas/cli.py" status` e apresente a saída |
| `/engine <pedido> --dry` | rode `ENGINE_RAIZ="$(pwd)" bash "${CLAUDE_PLUGIN_ROOT}/hooks/engine.sh" "${CLAUDE_PLUGIN_ROOT}/ferramentas/cli.py" ligar "<objetivo em uma frase>" --dry` — use para um ciclo que só planeja e relata, sem escrever |
| `/engine retomar` | rode `ENGINE_RAIZ="$(pwd)" bash "${CLAUDE_PLUGIN_ROOT}/hooks/engine.sh" "${CLAUDE_PLUGIN_ROOT}/ferramentas/cli.py" retomar` e apresente o resumo de reentrada — use quando a sessão é nova mas o ciclo já existe |
| `/engine relatorio` | rode `ENGINE_RAIZ="$(pwd)" bash "${CLAUDE_PLUGIN_ROOT}/hooks/engine.sh" "${CLAUDE_PLUGIN_ROOT}/ferramentas/cli.py" relatorio ciclo` (ou `relatorio fase <FASE>`) e apresente a saída |
| em DESCOBERTA, logo depois de `ligar` | rode `… cli.py descoberta "<o pedido do usuário, com as palavras dele>"` — registra a entrevista e classifica a intenção |
| a CLI respondeu que a intenção é indeterminada | **não escolha**: apresente as candidatas ao usuário com opções clicáveis e rode de novo com `… cli.py descoberta "<pedido>" --intencao <INTENCAO>` |
| ver o que ainda falta na entrevista | rode `… cli.py descoberta status` — intenção, palpites pendentes (com a evidência), bloqueantes abertas (com a pergunta inteira e o motivo) e assumíveis |
| o usuário respondeu uma bloqueante | rode `… cli.py descoberta responder <ID> "<a resposta dele>"` |
| o `status` listou um palpite e o usuário confirmou | rode `… cli.py descoberta confirmar <PALPITE>` — aplica plataforma ou contexto, e **pode abrir um bloco inteiro de perguntas novas** |
| o usuário disse que o palpite está errado | rode `… cli.py descoberta recusar <PALPITE>` — tira da pendência sem aplicar nada |
| a entrevista é do SISTEMA (macro-DESCOBERTA), e não de um ciclo | acrescente `--programa` a qualquer um dos verbos acima: `… cli.py descoberta --programa "<pedido>"`, `… descoberta --programa status`, `… descoberta --programa responder <ID> "<resposta>"` |
| `/engine programa <objetivo>` | conduz um **sistema inteiro** como sequência de ciclos — ver a seção "O programa" |

Os cinco verbos de `descoberta` — registrar, `status`, `responder`, `confirmar`, `recusar`
— são a **saída** da porta da descoberta. Nunca edite `.engine/estado.json` nem
`.engine/programa.json` à mão para destravar uma fase — a recusa do gate diz que nada foi
gravado justamente porque o conserto é responder, não remendar o arquivo. Registrar de novo
por cima de uma entrevista já respondida é recusado; para recomeçar do zero, `--forcar`.

**São DUAS entrevistas, em dois arquivos, e `--programa` diz qual.** Elas têm vidas
diferentes e por isso não moram juntas:

| | sem `--programa` | com `--programa` |
|---|---|---|
| de quem é | do **ciclo** em andamento | do **sistema** inteiro (a macro-DESCOBERTA da CONCEPCAO) |
| onde mora | `.engine/estado.json` | `.engine/programa.json` |
| que porta abre | `fase ANALISE` | `programa plano` (toda entrada em PLANO_MESTRE) |
| exige ciclo ligado | sim | **não** |
| sobrevive a `ligar` | não — cada ciclo faz a sua | **sim**, a todos eles |

Escolher errado não dá erro: grava a entrevista certa no arquivo errado e sobrescreve a que
estava lá. Antes de digitar, decida de quem é o pedido — do sistema ou do ciclo. **Cada
ciclo do programa faz a descoberta DELE**, mesmo o primeiro: a entrevista do sistema não
abre `fase ANALISE` de ciclo nenhum, e é assim de propósito — ela fala do todo, o ciclo
precisa do que é específico daquele pedaço.

**Palpite pendente não é resposta, e não some sozinho.** O que o motor infere do pedido
("app de celular" → MOBILE, "com pagamento" → LOJA_PAGAMENTOS) fica pendente com a
evidência que o produziu, e **não** vira eixo enquanto ninguém disser que sim. Leve cada
palpite ao usuário com a evidência, em opções clicáveis, e só então `confirmar` ou
`recusar`. Ignorar não é nenhuma das duas: enquanto o palpite estiver pendente, as
perguntas que ele destravaria não existem para o motor — e a porta pode abrir sem elas.

**Resposta de lacuna com opções declaradas tem de ser uma delas.** `onde_roda` aceita
`WEB`, `MOBILE`, `DESKTOP` ou `AUTOMACAO`, e não "no navegador": ela é a única lacuna
universal cuja resposta muda *quais outras perguntas existem*, e texto fora da lista
fecharia a lacuna sem ativar o ramo. A CLI recusa dizendo quais são as opções — leve-as ao
usuário, não reescreva a resposta dele por conta própria.

Essa é a forma que funciona **de qualquer diretório e em qualquer plataforma**, e é a
única que se deve usar. O diretório corrente é o do projeto do usuário, não o do plugin:
ali `python -m ferramentas.cli` falha com `ModuleNotFoundError: No module named
'ferramentas'`, porque o pacote do plugin não está no `sys.path`. E o interpretador nunca
é invocado por nome fixo: `hooks/engine.sh` — o mesmo lançador dos cinco hooks — detecta
em runtime `py` (Windows), `python3` ou `python`, o que existir no PATH; chamar `py`
direto quebraria em macOS/Linux, onde o Python Launcher não existe. (Não passe
`--travar-sem-python` aqui: essa flag é exclusiva do hook `PreToolUse`; para a CLI, o
lançador sem Python sai 0 em silêncio, que é o certo.) `${CLAUDE_PLUGIN_ROOT}` é
expandido pelo Claude Code para a raiz do plugin instalado, e `ENGINE_RAIZ` diz à CLI
qual é o projeto hospedeiro — o diretório corrente. Nunca troque de diretório para rodar
a CLI.

Se `ligar` recusar porque já existe um ciclo ativo, apresente o objetivo do ciclo em
andamento ao usuário e pergunte se quer retomá-lo ou recomeçar. Só acrescente `--forcar`
ao fim do comando de `ligar` se o usuário confirmar explicitamente que quer descartar o
ciclo em andamento.

## O ciclo

`DESCOBERTA → ⟨porta⟩ → ANALISE → [EVOLUCAO, se o projeto já existe] → PLANO → ⟨porta⟩ →
BUILD ⇄ TESTE → REVISAO → DOC → ENTREGA`

São as **duas** portas, e só elas — a primeira só para quando há lacuna bloqueante aberta,
a segunda para sempre. Ver "As duas portas", abaixo.

Avance de fase com `ENGINE_RAIZ="$(pwd)" bash "${CLAUDE_PLUGIN_ROOT}/hooks/engine.sh" "${CLAUDE_PLUGIN_ROOT}/ferramentas/cli.py" fase
<DESTINO>`. A CLI recusa transição fora do grafo — se ela recusar, a fase pretendida está
errada, não a máquina.

## As duas portas

O motor para para o usuário em **duas** portas, e só nelas. Elas param por motivos
diferentes, e por isso são duas: uma protege o que ainda não se sabe, a outra protege o
que já foi decidido. Parada que acontece fora delas deixa de ser sinal e vira ruído;
parada que falta entrega plano escrito sobre suposição.

**1. Porta da descoberta — para quando há lacuna BLOQUEANTE aberta.** Vale em
`DESCOBERTA → ANALISE` (no ciclo) e em **toda** entrada em `PLANO_MESTRE` (no programa,
onde a CONCEPCAO é a macro-DESCOBERTA) — tanto vindo de `CONCEPCAO` quanto de `DESVIO`,
que é o replanejamento. A CLI recusa a transição, imprime a pergunta inteira de
cada bloqueante com o predicado que a travou, e não grava nada. Leve essas perguntas ao
usuário e registre cada resposta com `descoberta responder <ID> "<resposta>"` — **com
`--programa` quando a recusa for de `programa plano`**, e a própria mensagem de recusa já
imprime o comando com a bandeira certa. Cada uma das duas portas cobra a SUA entrevista:
a do sistema não abre a fase de um ciclo, e a de um ciclo não abre o plano-mestre. **Sem
bloqueante aberta esta porta não para**: a transição passa direto, sem confirmação, sem
"posso seguir?". Ela não é uma parada por fase — é uma parada por dúvida que decide o
resto da entrevista.

**2. Porta do plano — para sempre, para o usuário aprovar a arquitetura.** Ao terminar
PLANO, apresente arquitetura, stack, estrutura e a justificativa de cada decisão, e
**espere** o usuário. No programa é a mesma porta um andar acima, ao fim do PLANO_MESTRE:
`programa aprovar` é o único verbo do motor que você nunca roda por conta própria. Esta
porta para mesmo sem dúvida nenhuma, porque o que está em jogo não é informação que falta
— é o usuário decidir se aceita o desenho antes de alguém construir em cima dele.

### A regra "não pergunte o que você pode decidir" continua valendo — e onde

`motores/materializar-ideia/SKILL.md` diz, e mantém:
**"Não pergunte o que você pode decidir"**, e "quando a ideia já vem com essas três coisas
claras, pule a pergunta e construa". A porta da descoberta **não** contradiz isso, e a
fronteira entre as duas frases é exatamente a regra de bloqueio de
`ferramentas/elicitacao/bloqueio.py`:

- **Lacuna ASSUMÍVEL — o motor decide, registra e segue.** É o território da regra do
  materializar-ideia. Framework, nome de tabela, biblioteca de ícone: decida, nomeie,
  siga. O que a decisão não pode ser é silenciosa — ela sai na lista de **decisões
  abertas**, com a pergunta inteira, em `descoberta status`. "Assumível" quer dizer *o
  motor segue sem perguntar*; nunca *o motor escolheu no lugar de alguém e não contou*.
- **Lacuna BLOQUEANTE — o motor para.** É bloqueante quando, e só quando, dispara um
  destes três predicados:
  - **B1 — responder muda quais outras perguntas existem.** Decidir sozinho aqui não é
    decidir: é escolher um ramo da entrevista no escuro, e as perguntas do ramo certo
    nunca chegam a ser feitas.
  - **B2 — a lacuna é universal**, sem gatilho: não existe caso em que ela seja
    dispensável. É o mesmo critério que impede uma especificação de se declarar completa.
  - **B3 — sem a resposta não se escreve critério de aceite falsificável** para nenhum
    ciclo do plano. Decidido sozinho, o aceite passa a ser aquilo que o próprio motor
    escolheu conseguir cumprir.

Nos três, "decidir por conta própria" não devolve ao usuário o trabalho que ele delegou —
devolve a ele um resultado sobre outra pergunta. Repare que as três coisas que a Fase 1 do
materializar-ideia manda perguntar (quem usa e para quê, a ação central, a restrição dura)
são bloqueantes por B2 e B3: a própria skill que proíbe perguntar o supérfluo manda
perguntar exatamente essas. As duas regras dizem a mesma coisa por lados opostos —
**pergunte o que muda o rumo, decida o resto e escreva o que decidiu.**

E "pule a pergunta e construa" continua literal: quando o pedido **já traz** as respostas
bloqueantes, registre-as com `descoberta responder` e siga. A porta abre porque a lacuna
foi respondida, não porque foi dispensada.

## O programa — sistemas inteiros, não um ciclo

Um ciclo entrega **um** trabalho de engenharia. Um sistema de alta complexidade é uma
**sequência** de ciclos com dependências, e é isso que o modo PROGRAMA conduz.

`CONCEPCAO → PLANO_MESTRE → ⟨porta⟩ → EXECUCAO → ACEITE_SISTEMA → CONCLUIDO`

De `EXECUCAO` sai também `DESVIO`, e de `DESVIO` volta-se a `EXECUCAO` (retomar) ou a
`PLANO_MESTRE` (replanejar, com as duas portas de novo). Qualquer estado vivo sai para
`ABORTADO`, o segundo terminal — desistência declarada, que não se confunde com
`CONCLUIDO`.

Todos os comandos abaixo usam o mesmo prefixo dos demais verbos
(`ENGINE_RAIZ="$(pwd)" bash "${CLAUDE_PLUGIN_ROOT}/hooks/engine.sh"
"${CLAUDE_PLUGIN_ROOT}/ferramentas/cli.py" …`), aqui abreviado como `CLI`.

| Pedido | O que fazer |
|---|---|
| `/engine programa <objetivo>` | `CLI programa "<objetivo em uma frase>"` — abre em CONCEPCAO |
| conduzir a macro-DESCOBERTA | `CLI descoberta --programa "<o pedido do usuário, com as palavras dele>"` e responda as bloqueantes com `CLI descoberta --programa responder <ID> "<resposta>"` — **não** precisa de ciclo ligado |
| decompor | escreva o plano num JSON e rode `CLI programa plano <arquivo.json>` |
| `/engine programa status` | `CLI programa status` |
| fechar um ciclo | `CLI programa verificar <CICLO>` — roda o comando de aceite e registra o veredito do código de saída |
| `/engine programa retomar` | `CLI programa retomar` — sessão nova, programa que já existe |

**O critério de aceite de cada ciclo é COMANDO, não só prosa.** Cada item de `ciclos` traz
`{"id", "objetivo", "depende_de", "aceite", "comando_de_aceite"}`. `aceite` é a afirmação
falsificável que o usuário lê na porta P1; `comando_de_aceite` é a linha de comando que a
verifica, e quem decide o veredito é o **código de saída** dela — 0 passa, qualquer outro
reprova. Plano em que algum ciclo não traga `comando_de_aceite` é **recusado**: frase não
se executa, e veredito sem execução é opinião. Um `programa.json` gravado antes desta
regra continua carregando inteiro; a exigência vale para o plano novo, na hora de propô-lo
— inclusive ao **replanejar**, e nesse caso um ciclo cujo comando mude (ou que só tinha
prosa) volta a `PENDENTE`, porque o verde antigo prova outro critério.

**Como conduzir a EXECUCAO.** Em laço, até não haver mais ciclo elegível:

1. `CLI programa proximo` — diz qual ciclo ligar, qual é o critério de aceite dele e qual
   comando o verifica.
2. `CLI ligar "<objetivo daquele ciclo>"` e conduza o ciclo **normalmente**, com todas as
   fases, papéis e gates de sempre. O programa não muda nada dentro do ciclo — inclusive a
   DESCOBERTA: cada ciclo faz a sua, com `CLI descoberta "<o que este ciclo entrega>"` (sem
   `--programa`). A entrevista do sistema continua guardada e intacta no
   `.engine/programa.json`; `ligar` não a toca.
3. Ao chegar em ENTREGA, `CLI programa verificar <CICLO>`. **Você não digita veredito
   nenhum**: o motor roda o `comando_de_aceite` declarado, imprime o comando, o código de
   saída e a saída, e registra `CONCLUIDO` se o código for 0 e `REPROVADO` se não for. O
   verbo sai 0 quando aprova e 1 quando reprova, e comando e código de saída ficam na
   trilha.
4. `CLI desligar` e volte ao passo 1.

**O veredito digitado só resta ao plano antigo.** `CLI programa aceite <CICLO> ok` (ou
`falhou`) continua existindo porque um `programa.json` gravado antes do aceite executável
não tem comando a rodar — mas agora exige `--porque "<motivo>"`, e o motivo vai para a
trilha. Se o ciclo tem `comando_de_aceite`, use `verificar`: digitar veredito onde há
comando declarado é justamente a opinião do modelo que o motor existe para não aceitar.
`programa verificar` sobre um ciclo sem comando é **recusado** — o motor não inventa a
linha que ninguém declarou.

Quando `proximo` disser que todos concluíram, rode o aceite de sistema declarado no plano,
e então `CLI programa sistema ok` (ou `falhou`). Aceite vermelho devolve o programa para
EXECUCAO — nada é dado como concluído.

**As duas portas, no programa.** São as mesmas de sempre, um andar acima. A **porta da
descoberta** guarda toda entrada em `PLANO_MESTRE` — `CONCEPCAO → PLANO_MESTRE` e
`DESVIO → PLANO_MESTRE`: `programa plano` é recusado enquanto houver lacuna bloqueante
aberta na macro-DESCOBERTA, com a mesma mensagem e a mesma saída (`descoberta --programa
status` e `descoberta --programa responder`). A **porta do plano-mestre** vem depois: ao
terminar o PLANO_MESTRE, apresente a decomposição inteira, com dependências e critérios de
aceite, e **espere**. `programa aprovar` é o único verbo do motor que **você nunca roda por
conta própria** — só o usuário autoriza, dizendo-o explicitamente. É a **última** parada do
programa: depois dela os ciclos encadeiam sozinhos.

**Quando parar no meio.** Só por desvio, e só por um destes quatro motivos:
`stack-fora-do-plano`, `dependencia-nao-prevista`, `aceite-inalcancavel`,
`escopo-fora-do-declarado`. Rode `CLI programa desviar <motivo> "<detalhe>"`, apresente o
conflito e espere. Fora disso não pergunte: parada que sempre acontece deixa de ser sinal.

**Depois do desvio, há dois caminhos.** `CLI programa retomar` volta a EXECUCAO com o
mesmo plano; `CLI programa plano <arquivo.json>` **replaneja** — e replanejar volta a
passar pelas duas portas, na ordem. Pela porta da descoberta primeiro: os quatro motivos
de desvio são, um a um, a constatação de que a macro-DESCOBERTA não previu o que
apareceu, então reveja a entrevista do sistema (`CLI descoberta --programa status`) e
responda o que o desvio abriu antes de propor. Ela **continua lá**, com as respostas de
quando o programa começou, por mais ciclos que tenham sido ligados no meio; se algum
motivo do desvio a tornou obsoleta, reabra com `CLI descoberta --programa "<pedido
revisto>" --forcar` e refaça — mas isso é decisão, não obrigação da máquina. Pela porta do plano
depois: a decomposição nova precisa da aprovação do usuário como qualquer outra. O
veredito dos ciclos já fechados **sobrevive** ao replanejamento quando o `id` e o
critério de aceite continuam os mesmos — replanejar não desfaz trabalho aceito, nem
absolve trabalho reprovado. Reescreveu o critério de aceite de um ciclo? Ele volta a
PENDENTE, porque o veredito antigo era sobre outra afirmação.

**Um ciclo reprovado bloqueia os dependentes** — é o desenho, não um defeito. Corrija,
rode `CLI programa reabrir <CICLO>` e verifique de novo: só o comando saindo 0 fecha o
ciclo.

**Desistir do programa inteiro.** `CLI programa abortar` encerra em `ABORTADO`, que é um
desfecho **diferente** de `CONCLUIDO`: este último só existe depois de um aceite de
sistema verde. A decomposição e a trilha ficam preservadas, e o abort entra na trilha.
Abortado **não** libera a pasta: abrir outro programa por cima continua exigindo
`--forcar`. É um verbo destrutivo — desfaz inclusive um plano-mestre que o usuário
aprovou na porta —, então trate-o como os outros destrutivos: pergunte antes.

Os gates de risco R1–R9 valem **idênticos** em modo programa. Autonomia de processo não é
autonomia de risco: com ninguém olhando, o gate vale mais, não menos.

## Conhecimento — o backlog que aprende com os relatórios

`CLI conhecimento {atualizar|status|revisar [ID]|pipeline|aprovar <ID>|rejeitar
<ID> [motivo]|editar <ID> <novo_texto>}`. Camada separada dos ciclos e do
programa: lê os relatórios já produzidos, extrai lacuna (achado crítico/alto
que se repete) e propõe inserção de trecho em cartão real — nunca aplica
sozinha. `atualizar` gera o backlog de lacunas a partir do relatório do ciclo
atual; `revisar` (sem ID) lista as propostas de merge pendentes, com ID e
confiança; `revisar <ID>` mostra o detalhe de uma proposta específica —
trecho atual do cartão ao lado do texto sugerido; `aprovar`/`rejeitar`/`editar`
decidem o destino de uma proposta pontual; `pipeline` roda `atualizar` e a
geração de propostas em sequência e resume o que restou pendente. Nada aqui
edita cartão sem `aprovar` — é o mesmo princípio da porta do plano, um andar
abaixo: o motor propõe, o humano decide o que vira conhecimento permanente.

## Papéis

Despache o subagente do papel correspondente à fase (`agents/`). Antes de despachar, leia
os cartões de `cartoes/` relevantes à stack e passe o conteúdo ao subagente.

| Fase | Papel |
|---|---|
| DESCOBERTA | `descobridor` |
| ANALISE / EVOLUCAO | `cartografo` |
| PLANO | `arquiteto` (e `designer`, quando houver direção visual a decidir) |
| BUILD | `implementador` |
| TESTE | `testador` |
| REVISAO | `revisor` e `sentinela` |
| DOC | `documentador` |

## Quando o hook travar uma ação

O hook de risco devolve `[R<n>] ação travada`. Não tente de novo por outro caminho, não
contorne com outra ferramenta. Apresente ao usuário **o que pretende fazer e o impacto**, e
peça confirmação com opções clicáveis.

## Invariantes

Valem em toda fase, e o hook de contexto os relembra a cada turno:

1. Nunca afirmar sucesso sem ter olhado.
2. Nunca ajustar o teste para o código passar.
3. Nunca inventar arquivo, API, número ou regra de negócio.
4. Nunca tocar em item fora do escopo declarado do ciclo.
5. Toda decisão técnica sai com a justificativa junto.
