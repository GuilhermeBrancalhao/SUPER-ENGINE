# Catálogo de cartões

| Cartão | Papéis que carregam | Fase do ENGINE |
|---|---|---|
| `python` | arquiteto, implementador, revisor | 1 |
| `pytest` | arquiteto, implementador, testador, revisor | 1 |
| `ui-ux` | arquiteto, designer, implementador, revisor | 1 |
| `fastapi` | arquiteto, implementador, testador, revisor | 2 |
| `excel-vba` | arquiteto, implementador, revisor | 2 |
| `office-scripts` | arquiteto, implementador, revisor | 2 |
| `power-query` | arquiteto, implementador, revisor | 2 |
| `react` | arquiteto, designer, implementador, testador, revisor | 2 |
| `typescript` | arquiteto, implementador, testador, revisor | 2 |
| `postgresql` | arquiteto, implementador, revisor | 2 |
| `sqlite` | arquiteto, implementador, revisor | 2 |
| `csharp` | arquiteto, implementador, testador, revisor | 2 |
| `vbnet` | arquiteto, implementador, testador, revisor | 2 |
| `fsharp` | arquiteto, implementador, testador, revisor | 2 |
| `mermaid` | arquiteto, documentador | 2 |
| `openpyxl-xlwings` | arquiteto, implementador, revisor | 3 |
| `ui-ux-producao` | arquiteto, designer, implementador, revisor | 3 |

Elenco completo: 17 cartões. `openpyxl-xlwings` tem `detectar: []` de propósito — não existe
âncora forte de arquivo para "este projeto usa openpyxl/xlwings" (ver a nota no próprio
cartão), então ele nunca dispara sozinho; o `cartografo` carrega à mão quando confirma
manipulação de Excel real na ANÁLISE. `ui-ux-producao` reusa o `detectar:` de `ui-ux` — os
dois co-carregam sempre juntos, de propósito (piso de acessibilidade + qualidade de produção).

Os `papeis` de `pytest` e `ui-ux` foram revisados na Fase 2
(adicionado `testador` em `pytest` e `designer` em `ui-ux`, coerente com o que já valia para
os cartões novos de teste e de interface).

Na Fase 1 os cartões eram lidos diretamente pelos papéis. A partir da Fase 2, a detecção
automática de stack (`ferramentas/detectar.py`) varre o projeto hospedeiro e grava em
`estado.cartoes` a lista de tecnologias presentes; cada papel carrega só os cartões que o
listam em `papeis`.

## Regra do campo `detectar:` — âncora forte, não extensão genérica

Carregar o cartão errado propaga o erro para todo código do ciclo: o implementador passa a
seguir convenções de uma tecnologia que o projeto não usa, e o revisor cobra por elas. Por
isso **`detectar:` só aceita âncora forte** — nome de arquivo que praticamente só existe
naquela tecnologia. Extensão genérica não serve, mesmo quando é comum na tecnologia.

A revisão adversarial da Fase 2 mediu o estrago: um projeto com `main.py` + `dados.db` +
`schema.sql` disparava `fastapi`, `postgresql` **e** `sqlite` ao mesmo tempo. `main.py` é o
nome mais comum do Python inteiro; `*.sql` vale para qualquer banco relacional; `*.db` vale
para qualquer arquivo que alguém resolveu chamar de "db". Os três padrões foram removidos,
junto com `*.cls` em `excel-vba` (colide com LaTeX e Apex) e `*.ts` solto em `typescript`
(colide com stream MPEG e tradução Qt — `tsconfig.json`/`*.tsx` cobrem o caso real).

**Quando não existe âncora forte por nome de arquivo, prefira não detectar.** É melhor o
usuário citar a tecnologia à mão do que o motor afirmar uma stack errada. `fastapi` e
`postgresql` ficaram com detecção estreita por causa disso: FastAPI não tem arquivo de
projeto próprio (sobrou a pasta `routers/` do layout oficial) e PostgreSQL só se anuncia
por nome nos arquivos de configuração do servidor. Detectar essas duas pelo CONTEÚDO do
arquivo de dependências (`requirements.txt`, `pyproject.toml`, `package.json` nomeando o
pacote) é item de Fase 3 — o `detectar:` de hoje só casa nome de arquivo.

Uma exceção conhecida e não corrigida: `pytest` detecta por `pyproject.toml`, que é
genérico de Python e não de pytest. Ficou como está porque é padrão da Fase 1 coberto por
teste existente; a âncora forte no lugar dele seria `conftest.py`.
