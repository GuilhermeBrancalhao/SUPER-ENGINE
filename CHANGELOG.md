# Changelog - AI Engineering Motor (ENGINE)

**Version**: 4.0.0  
**Status**: ✅ Production Ready

---

## 2026-08-20 — Dois volumes de acervo-controladoria alcançam PRONTO

`45-CONCILIACAO-CONTAS` e `54-INTEGRACAO-ERP` passam de `RASCUNHO` para `PRONTO`
(gates 1-3 da Definição de PRONTO cumpridos: validação mecânica, `pytest`, e
auditoria formal por modelo independente com `media ≥ 8,0` e nenhuma seção
`< 6`). Três rodadas de auditoria independente (Opus 5) encontraram bugs reais
de código a cada rodada, não só de documentação — corrigidos por mutação
verificada, não por leitura:

- `45-CONCILIACAO-CONTAS`: teste do ramo `Confianca.MEDIA` reescrito para
  exercer o ramo de verdade (era cosmético — testava o ramo `BAIXA` com nome e
  docstring do `MEDIA`); mutantes mortos para corte de data da âncora, limiar
  de similaridade, filtro de token curto e dominância histórica fraca; suíte
  final com 31 testes. Auditorias em
  `acervo-controladoria/auditorias/VOL-45-auditoria-2026-08-20{,-v2,-v3}.md`.
- `54-INTEGRACAO-ERP`: `DAT_CREDITO` corrigido para não trocar dia por mês
  (`dayfirst=True` nos dois pontos de parse); exceção genérica de data
  estreitada; terceira coluna candidata a comissão deixou de vazar para
  `VAL_BRUTO`; `executar()`/`main()` passaram a propagar reprovação de
  `validar()` como exit code distinto (2); flags `--sep`/`--encoding` da CLI,
  antes aceitas e ignoradas em silêncio, agora chegam a `ler_csv()`; suíte
  final com 18 testes. Auditorias em
  `acervo-controladoria/auditorias/VOL-54-auditoria-2026-08-20{,-v2,-v3}.md`.

Suíte completa de `acervo-controladoria/exemplos/` (49 testes) e
`ferramentas.validar` para os dois volumes verificados verdes antes do
registro.

---

## 2026-08-04 (3) — O cartão de contexto só funcionava no repositório do autor

### 1. Duas raízes tratadas como uma (o defeito mais grave desta série)

`hooks/engine_contexto.py` procurava `motores/*/SKILL.md` e `volumes/prontos/` a
partir da raiz do **projeto hospedeiro**. Essas duas árvores viajam dentro do
**plugin**. Como `raiz_do_ciclo()` devolve sempre o projeto do usuário, em
qualquer projeto que não fosse este repositório a seção `📚 Volumes PRONTO`
**não aparecia** e os motores saíam sem descrição.

Dito com todas as letras: **os 42 volumes empacotados pelo `sincronizar.py` eram
entregues e nunca lidos**. A funcionalidade nunca funcionou em produção — só na
máquina de quem a escreveu.

O que escondeu isso por tanto tempo: o parâmetro se chamava `raiz`, ambíguo o
bastante para os dois papéis, e **todos os testes existentes codificavam a
suposição errada** (criavam `motores/` e `volumes/prontos/` dentro do `tmp_path`
que passavam como "projeto"). A suíte validava o cartão num mundo onde o bug não
existia. `ferramentas/cli.py` sempre fez certo, passando as duas raízes
explicitamente — era o hook que estava fora do padrão.

Correções: parâmetro renomeado para `raiz_plugin` (o nome ambíguo é o que
permitiu o erro), `principal()` passa `config.raiz_plugin()`. Trava: três testes
que rodam o hook **real como subprocesso** contra um projeto hospedeiro
temporário — único jeito de medir o comportamento de produção.

### 2. Efeito dominó: o aviso de configuração era sempre cortado

`_com_avisos` empilhava avisos no fim e cortava em `linhas[:teto]`. Funcionava
por sobra de espaço enquanto o cartão vinha quase vazio; com o cartão cheio
(defeito 1 corrigido), **todo aviso caía no corte**. Um teste já existente
apontava isso e passava apenas por causa do outro bug.

Agora os avisos entram antes do rodapé e o **corpo** cede espaço. Cabeçalho e
rodapé continuam inegociáveis.

### 3. Bypass de R8 por escape de aspas

`_dividir_segmentos` não tratava `\"`. Em
`bash -c "python -c \"import shutil; shutil.rmtree('/dados')\""` a aspa escapada
era lida como fim da string, o `;` seguinte virava separador, e a expressão
perigosa nunca cabia inteira num segmento: **R8 saía `rastreado` no lugar de
`travado`**. Medido antes de corrigir. A contrabarra agora escapa fora de aspas e
dentro de aspas duplas — não dentro de aspas simples, onde o shell não tem
escape.

### 4. R5 era assimétrica entre ferramenta e shell

`Write(config.py, "AKIA…")` travava pelo corpo; `echo 'AKIA…' >> config.py`
saía `rastreado`, porque no shell R5 só olhava o **nome** do alvo. A assimetria
fazia do shell o caminho fácil para contornar a regra que existe para segredo não
virar commit. Fechada, com contraprova de falso positivo junto.

### 5. Cadeado quebrado e mesmo assim negado a quem quebrou

Quebrar um cadeado abandonado não dava direito a uma tentativa: a checagem de
prazo vinha logo depois e derrubava quem tinha acabado de quebrar. Com `espera`
curta, o erro reportava ocupação de um cadeado que já não existia, e o benefício
ia para o processo seguinte.

### 6. Três volumes PRONTO sem escopo

`03-DISCOVERY`, `07-PROMPT-ENGINE` e `12-MEMORY` viajavam no plugin sem `escopo`
nem `README.md` — o cartão os listava como `"Volume 07-PROMPT-ENGINE"`, nome
pelado. Escopo preenchido na FONTE, condensado do próprio `03-Escopo.md` de cada
volume (nada inventado). A trava exige escopo de todo volume que viaja, não dos
que estão em rascunho.

### 7. Menores

- Percentual da sugestão do `AnalisadorDiff` dividia o score do vencedor pelo
  `max` — e o vencedor **é** o max, então dizia `(100%)` sempre. Agora é
  participação no total.
- `_extrair_diffs_locais` removido: stub que devolvia `""` fingindo cobrir um caso.
- `test_lancador.py` passava ou falhava conforme o `PYTHONIOENCODING` herdado do
  shell — media o locale da máquina, não o lançador. Codificação fixada nas duas
  pontas.
- Docstrings citavam `ferramentas/status.py` como se fosse do motor; esse arquivo
  só existe em `acervo/ferramentas/status.py`.

Motor: 466 → **478** testes. Toda correção provada por mutação.

---

## 2026-08-04 (2) — O arquivo único ganha cadeado, e a durabilidade deixa de ser aposta

Duas armadilhas que o `CLAUDE.md` e o `README.md` registravam como conhecidas-e-não-resolvidas.

### 1. `.engine/estado.json` é arquivo único — colisão entre sessões

**O defeito.** Toda mutação do motor era **ler → alterar → gravar** em três passos soltos. Duas
sessões do Claude Code na mesma pasta produziam *lost update*: a segunda lia antes de a primeira
gravar, e a gravação da segunda apagava o que a primeira acabara de escrever. Não era corrupção
— `gravar` sempre foi atômico. Era pior: o estado final era JSON perfeitamente válido, só que
**sem a transição de fase que a CLI já tinha confirmado ao usuário na tela**. O contorno
documentado era humano: "não ligar o motor em pasta com mais de uma sessão aberta".

**A correção.** `estado.cadeado` — `.engine/estado.lock` criado com `O_CREAT | O_EXCL`, a única
primitiva de exclusão entre processos que funciona igual no Windows e no POSIX usando só a
biblioteca padrão (`fcntl.flock` não existe no Windows, `msvcrt.locking` não existe fora dele, e
o motor não pode ganhar dependência de runtime). Cadeado abandonado é quebrado por idade
(30 s): dono morto travaria o motor para sempre naquela pasta, que é um modo de falhar pior do
que a corrida.

Em cima dele, `estado.atualizar(raiz, mutador)`, que **relê de dentro da seção crítica**. É esse
detalhe que mata o defeito: com o cadeado só na gravação, a segunda sessão ainda gravaria por
cima com dados velhos. Os cinco sítios de mutação foram roteados por ele — `cli.py` (ligar e
fase), `engine_gate.py`, `engine_salvar.py` e `estado.registrar_diff` —, e
`test_nenhum_gravar_fora_do_estado` trava a regra: nenhum módulo de produção chama
`estado.gravar` direto.

**Um defeito extra, achado pela mutação.** Removendo o cadeado de propósito para provar que o
teste de regressão não era decorativo, os processos concorrentes não perderam escrita: eles
**quebraram**, com `PermissionError` (`WinError 32`). `gravar` usava um temporário de nome fixo
(`estado.json.tmp`), disputado por todos os escritores. O temporário passou a levar o pid.

`ferramentas/tests/test_estado_concorrente.py` (8 testes) reproduz a corrida com **seis
subprocessos de verdade**, não threads — a exclusão é entre processos, e o GIL mascararia o que
precisa aparecer. Uma barreira de relógio faz os seis disputarem no mesmo instante; sem ela, o
custo de arranque do interpretador espalharia as tentativas e o teste passaria por acidente.

### 2. Durabilidade sob compactação

**O que estava escrito.** "O motor nunca atravessou uma sessão longa com compactação de verdade
[...] trate 'sobrevive à compactação' como projeto, não como fato observado."

**O erro estava na pergunta.** A durabilidade não é empírica. Ela é consequência de uma
propriedade verificável do hook que injeta o cartão:

> o cartão é função **apenas do disco**, e de nada que a compactação possa destruir.

`hooks/engine_contexto.py` lê do evento **uma única chave: `cwd`**. Nunca `transcript_path`,
`session_id`, mensagens ou contexto — que é exatamente o que a compactação destrói. Não
existindo leitura, não existe caminho pelo qual a compactação altere a saída.

`test_o_cartao_nao_depende_de_nada_que_a_compactacao_destroi` trava isso na árvore sintática do
hook (não por substring: prosa citando "contexto" não pode reprovar). Acrescentar uma leitura de
`transcript_path` — ideia natural, para enriquecer o cartão com o histórico — deixa a suíte
vermelha no mesmo commit. Provado por mutação.

`ferramentas/tests/test_durabilidade_compactacao.py` (8 testes) exerce a propriedade com os
hooks reais como subprocesso, indo além do turno 10 de `aceite/simular_turnos.py`: compactação
em **todo** limite de turno contra uma execução de controle (cartão a cartão), dez compactações
seguidas, compactação em cada fase do ciclo, `PreCompact` **morto no meio da escrita**, ciclo
desligado que não pode ressuscitar, e — onde os dois defeitos deste commit se encontram —
`PreCompact` concorrente com uma transição de fase de outra sessão. O PreCompact era o pior
lugar possível para um *lost update*: dispara quando o contexto vai ser descartado, então o que
ele apagasse do estado não sobrava em lugar nenhum.

**O que continua não observado**, e os testes não afirmam: uma sessão real do Claude Code
atravessando auto-compactação. O resíduo, porém, passou a ser o contrato do Claude Code
(disparar `PreCompact`, preservar o `cwd`) — não o motor.

Suíte do motor: 450 → **466**.



Uma revisão do repositório encontrou dois scripts em `ferramentas/` que ninguém citava —
nem doc, nem CHANGELOG, nem teste — e que destruíam conteúdo real se rodados:

| Script | O que fazia |
|---|---|
| `gerar_volumes_conteudo.py` | `write_text` incondicional em `acervo/{02..42}/*.md`: **702 arquivos de 39 volumes PRONTO** substituídos por stubs de dez linhas |
| `gerar_volumes_controladoria.py` | recriava os 12 esqueletos removidos no dia anterior — e apontava para `acervo/`, não para `acervo-controladoria/` |

O primeiro era o pior, porque o dano passava pela porta: os volumes atingidos são `PRONTO`,
então a sincronização seguinte levaria os stubs para dentro do plugin, e
`test_a_copia_do_plugin_esta_em_dia` continuaria **verde** — a cópia estaria fiel à fonte
destruída. O segundo recarimbava `tipo: PROCESSO` nos doze volumes, que é exatamente o defeito
de metadado que a `ESTADO.md` da controladoria identifica como causa das 420 violações
mascaradas.

**O que mudou**

- Os dois foram removidos por `git rm` — recuperáveis pelo histórico, mesmo tratamento dado aos
  10 volumes-esqueleto.
- `test_nenhum_modulo_do_motor_escreve_no_acervo` — a trava. Nenhum módulo de `ferramentas/`
  além de `sincronizar.py` pode combinar a palavra `acervo` com uma chamada de escrita.
  Provada por mutação: restaurar `gerar_volumes_conteudo.py` deixa a suíte vermelha.
- `.github/workflows/suites.yml` — **a primeira CI deste repositório.** Até aqui as três suítes
  só rodavam à mão, o que deixava a invariante central (`volumes/prontos/` é derivado)
  sustentada por disciplina humana — que é o que ela existe para substituir. Três jobs: motor
  (450) + `sincronizar --verificar`, acervo (789), controladoria (33) + gate estrutural. Só
  Windows, de propósito: é a única plataforma em que os hooks e o lançador foram verificados de
  fato, e um job Linux vermelho na estreia ensinaria a ignorar vermelho.
- Os **33 testes de `acervo-controladoria/exemplos/` deixaram de ser órfãos.** Nenhuma das duas
  suítes os coletava; agora o job `controladoria` os roda a cada push.
- `acervo/requirements-dev.txt` — o acervo não declarava dependência nenhuma. Os 789 testes
  passavam por causa de pacotes instalados na máquina do autor (`starlette`, `pydantic`,
  `httpx`); numa máquina limpa a coleta quebrava.
- 9 testes de `codigo_generators/` **pulam** em vez de reprovar quando o SDK `anthropic` está
  indisponível. Estavam vermelhos porque o pacote, embora instalado, tinha uma dependência
  transitiva ausente (`sniffio`) — e o erro não dizia isso. Suíte que nasce vermelha por
  dependência ausente ensina a ignorar vermelho, que é a mesma patologia do falso positivo do
  classificador.
- Contagens de teste corrigidas no `README.md` (dizia 436 e 455), no `CLAUDE.md` (455) e na
  `ESTADO.md` da controladoria (dizia 30 testes; são 33).



O motor e a plataforma que produz os volumes de conhecimento eram dois repositórios, e o motor
carregava uma **cópia manual** dos volumes em `volumes/prontos/`. A cópia derivou, e a medição
foi o que motivou a unificação:

| Sintoma | O que estava acontecendo |
|---|---|
| `31-TESTING` | na cópia com `status: PRONTO`; na fonte, `RASCUNHO` — o cartão de contexto carregava rascunho como conhecimento pronto |
| `03-DISCOVERY` | `PRONTO` na fonte, **nunca** chegou na cópia |
| `07-PROMPT-ENGINE` | 5 arquivos com conteúdo diferente da fonte |
| `12-MEMORY` | 3 arquivos com conteúdo diferente da fonte |

**O que mudou**

- `acervo/` — a plataforma inteira (302 arquivos), importada com o histórico preservado a
  partir do seu repositório público (`bf95c57`). Ela continua sendo a dona dos volumes.
- `ferramentas/sincronizar.py` — gera `volumes/prontos/` a partir de `acervo/`, incluindo
  apenas o que a fonte declara `PRONTO`. `--verificar` só compara e devolve 1 se divergiu.
- `ferramentas/tests/test_sincronizar.py` — a porta. `test_a_copia_do_plugin_esta_em_dia` roda
  contra o repositório real; editar um byte de `volumes/prontos/` deixa a suíte vermelha
  (provado por mutação). As outras reproduzem de propósito cada forma de deriva já observada.
- `volumes/_catalogo.md` passou a ser gerado, para não virar o próximo arquivo mantido à mão.
- `pytest.ini` — a raiz coleta só a suíte do motor. Os dois pacotes `ferramentas` (o do motor e
  o do acervo) colidem numa sessão única de pytest; o acervo roda de dentro de `acervo/`.

**Correção que apareceu no caminho:** `shutil.which("bash")` devolvia, no Windows sem WSL, o
stub da Microsoft Store — que responde a `which` mas imprime "instale uma distro" em UTF-16 e
sai 1 sem ler o script. Os 17 testes de `test_lancador.py` falhavam por isso, e não por defeito
do lançador. `hooks/engine.sh` já descartava esse stub para o Python; a mesma regra faltava no
teste.

**Suítes:** 449 (motor) + 455 (acervo) = 904 testes verdes.

**O que a unificação NÃO fez:** não renomeou o repositório, não reapontou o plugin e não mexeu
no manifesto — o acervo entrou dentro do motor, e não o contrário.

---

## 2026-07-31 — Primeira execução em sessão real do Claude Code

O plugin foi instalado e rodou dentro de uma sessão real do Claude Code — o item "instalação
real do plugin" deixado explicitamente não verificado pela Fase 2 está fechado. Três coisas
foram **observadas**, não simuladas:

- O hook `UserPromptSubmit` injetou o cartão `== ENGINE ativo ==` no contexto do turno.
- O hook `PreToolUse` travou um `git push` pela família R2 — inclusive o push do próprio
  código-fonte deste projeto.
- O mesmo hook travou um `python -c` pela família R8. Era um falso positivo, corrigido
  depois: a string `'EXEC(ruim)'` casava `\bexec\(` porque o padrão era compilado sem
  distinguir maiúsculas.

Isso prova que o **mecanismo** funciona numa sessão real, e nada além disso. O que continua
sem prova é a **durabilidade**: o motor nunca atravessou uma sessão longa com compactação de
verdade (`aceite/simular_turnos.py` simula vinte turnos e uma compactação chamando os hooks
reais, mas simulação não é sessão), e o lançador nunca rodou numa máquina macOS ou Linux
real.

Junto com a instalação, a skill foi corrigida no mesmo espírito dos hooks:
`skills/engine/SKILL.md` mandava invocar a CLI com `py` direto — o Python Launcher, que só
existe no Windows — enquanto os cinco hooks já passavam pelo lançador. Todas as invocações
da skill agora passam por `hooks/engine.sh` (sem `--travar-sem-python`: essa flag é
exclusiva do `PreToolUse`; para a CLI, sair 0 em silêncio quando não há Python é o certo).

## 2026-07-31 — Auditoria adversarial: três famílias novas (R10–R12) e a guerra aos falsos positivos

Quatro revisores adversariais rodaram em paralelo, cada um sobre uma superfície: o
lançador (`hooks/engine.sh`), o classificador (`ferramentas/risco.py`), os hooks e os
módulos de dados (`estado.py`, `trilha.py`, `config.py`). Suíte: **280 → 388 testes
verdes**; `aceite/verificar_familias.py` ganhou os casos de R10, R11 e R12 e a seção 5
da especificação foi atualizada.

Os achados que mais importaram, com o vetor concreto de cada um:

- **A caixa do nome derrotava a família do painel de controle.** `Write` em
  `.ENGINE/estado.json` saía `livre` — o filesystem do Windows não distingue
  maiúsculas, então era o mesmo arquivo real, e gravar `{"ativo": false}` nele
  desligava o motor inteiro sem travar nem aparecer no relatório. `_sob_painel`
  passou a comparar componente por componente ignorando a caixa (`.engineering`
  segue de fora).
- **Escrita de arquivo novo em qualquer ponto do disco era livre.** A política
  "arquivo novo é livre" não olhava PARA ONDE: `Write .git/hooks/pre-commit` ou
  `.claude/settings.json` instalava execução persistente — código arbitrário rodando
  a cada commit ou a cada sessão — como um inocente arquivo novo. Nasce a família
  **R10** (hooks de git, `.claude/`/`.vscode/`/`.idea/`, init de shell, perfil do
  PowerShell, `Startup`, `crontab`, `.gitconfig`, `authorized_keys`), que trava
  dentro ou fora da raiz; e arquivo novo fora da raiz do projeto deixou de ser livre.
- **ReDoS quadrática travava a sessão.** Os quantificadores ilimitados das famílias
  (`[^\n]*`) retrocediam sobre comando repetitivo: um comando de 6.400 repetições
  (32 mil caracteres) prendia o classificador por 7,7 s na medição da auditoria
  (5,7 s reproduzidos nesta máquina) — e o `PreToolUse` roda a cada ação. Todo
  quantificador virou janela limitada (`{0,200}`) e nasceu a família **R12**: comando
  acima do teto de 20.000 caracteres **trava** sem ser analisado, porque travar é o
  lado certo do erro — o humano confirma um comando anômalo em vez de a sessão
  congelar tentando entendê-lo. Junto entrou a família **R11** (destruição sem verbo
  de apagar: `truncate -s`, `dd of=`, `robocopy /MIR`, `format`, `wsl --unregister`,
  `reg delete /f`, truncamento por `>` puro), que a família de deleção nunca via.
- **O cartão de estado imprimia segredo cru no contexto a cada turno.** A trilha já
  redigia credencial (`trilha.redigir`), mas o cartão — que volta ao contexto do
  modelo TODO turno — imprimia o objetivo e as decisões sem redação nenhuma. Agora
  todo texto vindo do estado passa pela MESMA redação da trilha (por referência, não
  por cópia: duas listas de padrões divergem na primeira vez que uma ganha um padrão
  novo), e redige ANTES de cortar — token truncado ainda é reconhecível.
- **`novo_ciclo` sobrescrevia estado corrompido em silêncio.** Um `estado.json`
  ilegível era tratado como inexistente e o ciclo novo gravava por cima, destruindo a
  evidência. Agora o arquivo corrompido é preservado com renomeação
  (`estado.corrompido-<carimbo>.json`) antes de qualquer escrita.

**A mesma quantidade de trabalho foi para o outro lado do erro: os falsos positivos.**
`pip install -r requirements.txt` travava como instalação global, `pytest -k token`
travava como acesso a segredo (o argumento `token` casava `*token*`), `grep 'DELETE
FROM' log.txt` travava como SQL destrutivo — os três hoje saem `rastreado`. Isso não é
conforto, é defeito de segurança: falso positivo frequente treina o humano a aprovar no
automático, e aprovação no automático anula o gate inteiro. Cada afrouxamento é
estreito e comentado no código com o caso que o motivou (lookahead para `-r`/`-e`/`.`,
primeiro token de ferramenta de busca, identificador sensível a caixa em `_PY_PERIGO`).

**Um bug foi introduzido durante a correção — e pego pela própria suíte.** O filtro do
stub da Microsoft Store no lançador (o `python` falso de `WindowsApps`) precisava
comparar sem distinguir caixa, e a primeira versão fazia isso com o binário externo
`tr`. Com PATH restrito — exatamente o cenário que o lançador existe para aguentar — o
`tr` some, a substituição falhava em silêncio e o filtro parava de filtrar. Corrigido
com classe de caracteres em glob POSIX puro, sem depender de binário nenhum; o teste de
PATH controlado é o que denunciou.

## 2026-07-31 — Hooks portáteis (Windows/macOS/Linux)

`hooks/hooks.json` lançava os cinco hooks pela forma exec do Claude Code com
`"command": "py"` — o Python Launcher, que só existe no Windows. Em macOS/Linux
o hook falhava ao iniciar, silenciosamente: sem interpretador, o classificador
de risco (`PreToolUse`) simplesmente não rodava, e nada avisava disso.

- **`hooks/engine.sh` (novo).** Lançador bash que decide o interpretador em
  runtime: tenta `py`, `python3`, `python`, nessa ordem, usando só `command -v`
  (nunca executa o candidato para sondar — o `PreToolUse` dispara a cada
  chamada de ferramenta, e sondar custaria latência em todas elas). Descarta
  qualquer caminho que contenha `WindowsApps` — o stub que o Windows registra
  quando não há Python instalado, que abre a Microsoft Store em vez de rodar
  código; confirmado nesta própria máquina (`command -v python3` resolve para
  o stub, `py` resolve para um Python de verdade). Achado o interpretador,
  `exec` troca o processo do shell pelo dele, repassando stdin/stdout/stderr e
  o código de saída intactos — só ele decide se a ação é bloqueada (`exit 2`).
  Com a flag `--travar-sem-python` (usada só no `PreToolUse`) e nenhum Python
  encontrado, sai `2` com mensagem explicando que o gate de segurança não está
  protegendo nada; sem a flag (os outros quatro hooks), sai `0` em silêncio —
  eles nunca podem atrapalhar o turno do usuário.
- **`hooks/hooks.json` migrado para a forma shell.** As cinco entradas
  perderam `args` e ganharam `"shell": "bash"` explícito; `command` passou a
  ser a string `"${CLAUDE_PLUGIN_ROOT}/hooks/engine.sh" ... "${CLAUDE_PLUGIN_ROOT}/hooks/engine_*.py"`,
  com aspas em cada caminho (`CLAUDE_PLUGIN_ROOT` tem espaço/acento nesta
  máquina). A forma shell entrega a string a um shell de verdade — Git Bash no
  Windows, `sh`/`bash` em macOS/Linux — em vez de resolver `command`
  literalmente no PATH sem shell (o que a forma exec fazia, e por isso não
  tinha como decidir o interpretador em runtime).
- **Bit de execução registrado no git** (`git update-index --chmod=+x`,
  modo `100755`) e `.gitattributes` novo forçando `eol=lf` em `*.sh` — sem
  isso, `core.autocrlf=true` (ativo neste repositório) injetaria `\r` no
  script no próximo checkout, quebrando o shebang e as comparações de string.
- **`ferramentas/tests/test_lancador.py` (novo, 5 testes).** Cobre, via
  subprocesso e PATH controlado: repasse de stdin e código de saída com Python
  disponível; trava (`exit 2`, stderr menciona Python) com PATH vazio e
  `--travar-sem-python`; saída silenciosa (`exit 0`, stdout vazio) com PATH
  vazio e sem a flag; caminho de script com espaço e acentuação; e o descarte
  do stub `WindowsApps` reproduzindo o caso real desta máquina. Todo o módulo
  é pulado se `bash` não estiver no PATH. Suíte: **266 → 271 testes verdes**.
- **`README.md`**: removido o aviso de suporte só-Windows e a seção "Outras
  plataformas"; nova seção "Requisitos" pede Git Bash no Windows (a forma
  shell cai para PowerShell sem ele, onde o lançador bash não roda) e explica
  com franqueza que a trava sem Python é intencional, não defeito.

---

## [4.0.0] - 2026-07-31

### ✨ Adicionado
- **Volumes Dinâmicos**: Auto-discovery sem hardcoding
- **Detector de Volumes**: Cache inteligente (TTL 300s)
- **Hook V4**: Integração com detecção dinâmica
- **18 Testes**: 8 unitários + 6 integração + 4 E2E

### 🔧 Melhorado
- Performance com cache
- Validação de estrutura
- Ordem alfabética de volumes

### 📚 Documentação
- PLUGIN-README.md
- CHANGELOG.md

### 🎯 Status
- **Testes**: 18/18 PASSARAM ✅
- **Produção**: V4 ativado

---

## [3.0.0] - 2026-07-31

### ✨ Adicionado
- **Sugestão Automática**: Análise de diff
- **AnalisadorDiff**: 5 padrões detectáveis
- **Hook V3**: Com integração
- **17 Testes**: 8 unitários + 5 integração + 4 E2E

### 🎯 Status
- **Motores**: 5/5 detectados
- **Produção**: V3 ativado

---

## [2.0.0] - 2026-07-31

### ✨ Adicionado
- **Hook V2**: Motores + volumes
- **Teto de 50 linhas**: Respeitado

### 🎯 Status
- **Produção**: V2 ativado

---

## [1.0.0] - 2026-07-31

### ✨ Adicionado
- **5 Motores**: Base completa
- **8 Fases ENGINE**: Framework completo
- **9 Agentes**: Mapeados

### 🎯 Status
- **Arquitetura**: Base de 42 volumes
- **Testes**: 9/9 PASSARAM ✅

---

**Made with ❤️ for Claude Code**
