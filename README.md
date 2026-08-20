# ENGINE

Um motor de engenharia persistente para o [Claude Code](https://claude.com/claude-code),
empacotado como plugin.

## O problema que ele resolve

Um "modo de engenharia" para o Claude Code costuma ser tentado como **um prompt longo** colado
numa skill. Isso não funciona, e o motivo é mecânico e não estético: a skill carrega **uma
única vez**, no turno em que é invocada. A cada mensagem seguinte o texto afunda no contexto,
perde peso relativo, e na primeira compactação desaparece. Na prática você observa um
comportamento excelente por três ou quatro turnos, seguido de regressão silenciosa ao padrão —
sem nenhum aviso de que o modo caiu.

O ENGINE troca texto por **estado em disco**. O ciclo vive em `.engine/estado.json` no projeto
onde você trabalha, e um hook `UserPromptSubmit` relê esse arquivo e reinjeta um cartão de no
máximo 40 linhas **a cada turno**. Não é o texto de nenhuma skill que sustenta o modo; é o
hook.

## O que ele faz

**Um ciclo de fases** que uma máquina acompanha, não uma instrução que o modelo pode esquecer:

```
DESCOBERTA → ANÁLISE → [EVOLUÇÃO, se o projeto já existe] → PLANO → ⟨porta⟩
  → BUILD ⇄ TESTE → REVISÃO → DOC → ENTREGA
```

Transição fora desse grafo é recusada em código. A **porta** depois do PLANO é a única parada
obrigatória por fase: o motor apresenta arquitetura, stack e a justificativa de cada decisão, e
espera.

**Nove papéis**, despachados por fase — `descobridor`, `cartografo`, `arquiteto`, `designer`,
`implementador`, `testador`, `revisor`, `sentinela`, `documentador`. Só o `implementador` tem
escrita ampla; quem revisa não conserta em silêncio, e essa garantia é estrutural (o `revisor`
não recebe ferramenta de execução), não uma instrução que ele possa contrariar.

**Doze cartões de tecnologia**, carregados sob demanda conforme a stack detectada no projeto.
Tecnologia nova custa um arquivo de ~60 linhas, não um agente novo.

**Seis motores consultáveis**, de duas naturezas diferentes: cinco motores de critério
próprios, em `motores/` — `revisar-codigo`, `otimizar-performance`, `arquitetar-sistema`,
`materializar-ideia`, `diagramar` —, mais `gauntlet-loop`, uma **entrada-ponteiro** para uma
skill externa (instalada à parte no ambiente de quem conduz o ciclo, não mantida por este
repositório) que, consultada em REVISAO e DOC, acrescenta crítica cega contra barra externa
quando o entregável já passa em teste e critério funcional mas a qualidade em si precisa ser
medida. O cartão de cada turno lista os motores consultáveis da fase atual (nome +
`description` do `SKILL.md` de cada um):

| Fase | Motores consultáveis |
|---|---|
| PLANO | `arquitetar-sistema`, `materializar-ideia` |
| EVOLUÇÃO | `arquitetar-sistema` |
| BUILD | `materializar-ideia`, `revisar-codigo` |
| REVISÃO | `revisar-codigo`, `otimizar-performance`, `gauntlet-loop` |
| DOC | `diagramar`, `gauntlet-loop` |

Fora de DESCOBERTA e ANÁLISE, o hook também analisa o `git diff` local e, quando o padrão do
código pede um motor específico, acrescenta a sugestão ao cartão.

**Volumes de conhecimento PRONTO**, detectados dinamicamente — nenhuma lista hardcoded no
código. Todo diretório em `volumes/prontos/<NOME>/` entra no cartão como consultável se o seu
`_VOLUME.yml` declara `status: PRONTO` (qualquer outro status fica de fora; sem `_VOLUME.yml`,
vale o fallback: basta ter `README.md` ou capítulos `.md`). O resumo mostrado vem do campo
`escopo:` do `_VOLUME.yml`, senão da primeira linha não-vazia do `README.md`. Criar um volume
novo não exige mudar código nenhum — a descoberta usa cache com TTL de 300 s.

**Quem escreve esses volumes mora aqui também**, em `acervo/` — a plataforma de engenharia de
projetos de IA, com o seu contrato legível por máquina, os seus três gates e os seus 42
volumes. `volumes/prontos/` deixou de ser cópia mantida à mão e passou a ser **artefato
derivado**: quem gera é `ferramentas/sincronizar.py`, a partir do `status` que o acervo declara.

```bash
py -m ferramentas.sincronizar --verificar   # a cópia está em dia com o acervo?
py -m ferramentas.sincronizar               # regenera
```

Não edite nada dentro de `volumes/prontos/`: a próxima sincronização sobrescreve, e o teste
`test_a_copia_do_plugin_esta_em_dia` reprova a suíte se os dois lados divergirem. Foi
exatamente essa deriva que motivou a unificação — a cópia chegou a carregar `31-TESTING`
marcado `PRONTO` enquanto a fonte dizia `RASCUNHO`, e a nunca entregar `03-DISCOVERY`, que era
`PRONTO` de verdade.

As duas suítes rodam separadas, porque cada uma tem o seu próprio pacote `ferramentas`:

```bash
py -m pytest                  # motor  — 844 testes
cd acervo && py -m pytest     # acervo — 789 testes
```

**Um classificador de risco** que roda antes de cada ação:

| Nível | O que acontece |
|---|---|
| `travado` | bloqueia e pede confirmação humana |
| `rastreado` | executa, e aparece no relatório da fase |
| `livre` | executa em silêncio |

## A decisão de projeto que mais importa

**Comando de shell nunca é `livre`** — ou trava, ou é rastreado. Só operação de arquivo pode
ser livre.

Isso não foi a intenção original. O classificador nasceu como uma lista de proibições, e sete
rodadas de revisão adversarial encontraram doze contornos — cada rodada achava outro:
`bash -c "rm"`, `echo $(rm -rf)`, quebra de linha depois de um `echo`, `cmd /c del`,
`git -c core.fsmonitor=./script status`, `git diff --output=`.

A causa é estrutural, não descuido: **cada comando de shell é ele próprio uma linguagem**, com
aspas, substituição, apelidos e variantes por plataforma. Enumerar o que é perigoso não
termina. Então o default foi invertido — o que não é comprovadamente inócuo é auditado, e um
teste (`test_nenhum_comando_de_shell_e_livre`) trava essa política contra reintrodução
acidental.

O mesmo raciocínio produziu a família **R9**: escrita em `.engine/` é travada, porque sem ela
gravar `{"ativo": false}` no estado desligava os dois hooks — o motor não protegia o próprio
painel de controle. Uma auditoria adversarial posterior acrescentou mais três famílias pelo
mesmo caminho: **R10** (escrita em caminho de execução persistente — `.git/hooks/`,
`.claude/`, init de shell — que a política de "arquivo novo é livre" deixava invisível),
**R11** (destruição de dados sem verbo de apagar: `truncate`, `dd of=`, `robocopy /MIR`,
`format`) e **R12** (comando acima do teto de 20.000 caracteres **trava** em vez de ser
analisado — travar é o lado certo do erro, porque varrer as famílias sobre um comando
gigante era um vetor de negação de serviço por regex). A lista fechada hoje vai de R1 a R12;
a seção 5 da especificação documenta cada uma com o vetor que a motivou.

## Requisitos

- [Claude Code](https://claude.com/claude-code).
- Python 3.11+, alcançável no PATH como `py` (Windows), `python3` ou `python` — o lançador
  (`hooks/engine.sh`) tenta os três, nessa ordem.
- **No Windows, [Git Bash](https://git-scm.com/downloads/win)** (instalado junto com o Git para
  Windows). Os cinco hooks usam a forma shell do `hooks.json`, que no Windows roda em Git Bash;
  sem ele, o Claude Code cai para PowerShell, onde `hooks/engine.sh` — um script bash — não
  executa.

Se nenhum interpretador Python for encontrado no PATH, o hook `PreToolUse` (o classificador de
risco) **trava toda ação de ferramenta de propósito**, com uma mensagem em stderr explicando o
motivo. Isso é comportamento desejado, não defeito: um gate de segurança que não consegue rodar
tem que bloquear, nunca liberar em silêncio. Os outros quatro hooks (`UserPromptSubmit`,
`PostToolUse`, `PreCompact`, `Stop`), em contraste, saem em silêncio quando não acham Python —
eles nunca podem atrapalhar o turno do usuário.

## Instalação

```bash
git clone https://github.com/AlphaContabilidade/planejamento-do-motor-de-revisao-de-codigo.git ENGINE
```

Depois, dentro do Claude Code (use o **caminho absoluto**; caminho relativo tem bug conhecido):

```bash
/plugin marketplace add C:\caminho\completo\para\ENGINE
```

```bash
/plugin install engine@engine-marketplace
```

Escolha escopo **user** para o plugin valer em todos os seus projetos. Abra uma janela nova —
plugin só carrega no início da sessão.

Confirme com:

```bash
claude plugin details engine
```

Você deve ver `Skills (2)`, `Agents (9)` e `Hooks (5)`.

## Uso

```bash
/engine:engine <o que você quer construir>
```

O motor entra em DESCOBERTA, e a partir daí o cartão de estado aparece a cada turno.

| Comando | Efeito |
|---|---|
| `/engine:engine <pedido>` | liga o motor e cria o ciclo |
| `/engine:engine <pedido> --dry` | ciclo em modo seco: planeja e relata, **não escreve nada** |
| `/engine:engine status` | fase, ciclo, decisões, arquivos tocados, pendências |
| `/engine:engine relatorio` | relatório do ciclo (ou de uma fase) a partir da trilha |
| `/engine:engine retomar` | reconstrói o estado numa sessão nova |
| `/engine:engine off` | desliga e gera o relatório do ciclo |

O modo seco é o jeito de conhecer o motor sem risco: ele percorre as fases, apresenta o
plano e relata, mas o classificador de risco rebaixa toda escrita para travada.

## Testes

Três suítes, e desde 2026-08-04 as três rodam na CI (`.github/workflows/suites.yml`)
a cada push — antes disso não havia CI nenhuma, e "os testes passam" era uma
afirmação sobre a última vez que alguém os rodou à mão.

```bash
py -m pytest                                   # motor          — 844 testes
cd acervo && py -m pytest                      # acervo         — 789 testes
py -m pytest acervo-controladoria/exemplos     # controladoria  —  33 testes
```

O motor usa **apenas a biblioteca padrão do Python** — nenhuma dependência de
runtime, porque o plugin se instala em projetos alheios e não pode arrastar
dependência junto. O acervo tem as dele declaradas em `acervo/requirements-dev.txt`.

Além delas, dois scripts de aceite disparam os hooks de verdade como subprocesso:

```bash
python aceite/verificar_familias.py
python aceite/simular_turnos.py
```

## Estado

**Fases 1 e 2 completas**, mescladas em `master`. Estão no repositório e cobertos por testes:
`ferramentas/` (configuração, classificador de risco, máquina de fases, detecção de stack,
trilha, relatório e a CLI), os cinco hooks (`PreToolUse`, `UserPromptSubmit`, `PostToolUse`,
`PreCompact`, `Stop`), a skill, os nove papéis, os doze cartões e o empacotamento como plugin.

**O que já foi observado em sessão real.** Em 2026-07-31 o plugin foi instalado e rodou
dentro de uma sessão real do Claude Code, e três coisas foram observadas — não simuladas:
o hook `UserPromptSubmit` injetou o cartão `== ENGINE ativo ==` no contexto do turno; o
hook `PreToolUse` travou um `git push` pela família R2 (inclusive o push do próprio
código-fonte deste projeto); e o mesmo hook travou um `python -c` pela família R8 — um
falso positivo, corrigido depois: a string `'EXEC(ruim)'` casava `\bexec\(` porque o
padrão era compilado sem distinguir maiúsculas. Isso prova que o **mecanismo** funciona
numa sessão real; não é uma declaração de vitória.

**Durabilidade: por que ela vale.** A pergunta "o modo sobrevive à compactação?" era tratada
como empírica, e ficava em aberto porque o motor nunca tinha atravessado uma sessão longa com
compactação de verdade. Ela não é empírica. É consequência de uma propriedade do hook que
injeta o cartão:

> o cartão é função **apenas do disco** (`.engine/`, config, projeto), e de nada que a
> compactação possa destruir.

A compactação descarta contexto e reescreve a transcrição. `hooks/engine_contexto.py` lê do
evento **uma única chave: `cwd`** — nunca `transcript_path`, `session_id`, mensagens ou
qualquer coisa derivada do contexto. Não existindo leitura, não existe caminho pelo qual a
compactação altere a saída. `test_o_cartao_nao_depende_de_nada_que_a_compactacao_destroi`
trava isso na árvore sintática do hook: acrescentar uma leitura de `transcript_path` — ideia
natural, para enriquecer o cartão com o histórico — deixa a suíte vermelha no mesmo commit.

Em cima dessa razão, `ferramentas/tests/test_durabilidade_compactacao.py` exerce a propriedade
com os hooks reais rodando como subprocesso: compactação em **todo** limite de turno (contra
uma execução de controle sem compactação nenhuma, cartão a cartão), dez compactações seguidas,
compactação em cada fase do ciclo, `PreCompact` **morto no meio da escrita**, e `PreCompact`
concorrente com uma transição de fase de outra sessão.

**O que continua não observado**, e não é o que esses testes afirmam: uma sessão real do
Claude Code atravessando auto-compactação. O que sobra de resíduo, porém, é o **contrato do
Claude Code** (disparar `PreCompact`, preservar o `cwd`), não o motor.

**Desde então: Fase 4 e dois programas reais, com prova por execução.** O motor
ganhou uma camada acima do ciclo — `programa`, que encadeia uma sequência de
ciclos com dependência, porta única de aprovação e aceite de sistema — ver
`docs/specs/2026-08-05-engine-fase-4-programa.md` e `aceite/fase-4.md`. Sobre
essa camada rodaram dois programas de verdade: o primeiro ligou o catálogo de
37 lacunas de elicitação (que existia como exemplo didático no acervo,
desligado da máquina) aos dois gates de fase — hoje é `descoberta`/`programa
descoberta` neste README; o segundo trocou o veredito de ciclo de **digitado**
(`programa aceite <C> ok`) para **decidido pelo código de saída** de um
comando real (`programa verificar <C>`), com prova em `aceite/fase-5.md`: um
projeto-cobaia (calculadora de folha CLT) onde um ciclo reprovou de verdade,
bloqueou o dependente, e só o conserto seguido de nova verificação destravou o
programa. Isso substitui a frase abaixo — os cenários de aceite com
projeto-cobaia deixaram de ser pendência.

Também pendente: os quatro cenários de aceite com projetos-cobaia da Fase 3
original (instalação e ciclo único de ponta a ponta numa sessão real, fora
deste repositório). O lançador
(`hooks/engine.sh`) tem suíte automatizada (`ferramentas/tests/test_lancador.py`) cobrindo os
cenários de PATH via subprocesso, mas **nunca rodou numa máquina macOS ou Linux de verdade** —
só sob Git Bash no Windows, onde a forma shell também roda.

## Documentação

| | |
|---|---|
| Especificação de desenho (Fases 1-3) | `docs/specs/2026-07-30-engine-design.md` |
| Especificação do modo PROGRAMA (Fase 4) | `docs/specs/2026-08-05-engine-fase-4-programa.md` |
| Plano de implementação | `docs/plans/` |
| Histórico e decisões | `CHANGELOG.md` |
| Registros de aceite | `aceite/` (`fase-1` a `fase-5`) |

A especificação explica cada decisão com a alternativa que foi descartada e a razão. Se você
for mexer no classificador de risco, leia a seção 5 antes — ela documenta por que a política
atual é a que é, e sete rodadas de revisão estão por trás dela.

## Licença

MIT. Veja [LICENSE](LICENSE).
