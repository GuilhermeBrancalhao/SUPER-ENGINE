---
tecnologia: openpyxl-xlwings
detectar: ["*.xlsm", "*.xlsb"]
papeis: [arquiteto, implementador, revisor]
versao: 2026-08-20
---

## Nota sobre detecção
Âncora deliberadamente restrita a planilha **com macro** (`.xlsm`/`.xlsb`), não `.xlsx`
puro — `.xlsx` é genérico demais (qualquer planilha, a maioria sem nenhuma necessidade de
`openpyxl`/`xlwings`); `.xlsm`/`.xlsb` já sinaliza um artefato de automação real, coerente com
a regra do catálogo ("âncora forte, não extensão genérica"). Ainda assim, o padrão real do
usuário costuma manipular `.xlsx` puro preservando fórmula/pivot via `xlwings`, caso em que
não existe arquivo-âncora e a detecção automática não dispara. Quando o `cartografo` confirmar
esse padrão na ANÁLISE (leitura/gravação de Excel real como parte do fluxo do projeto),
carregue este cartão à mão mesmo sem `.xlsm`/`.xlsb` presente.

## Convenções
- Leitura é sempre `openpyxl.load_workbook(caminho, read_only=True, data_only=True)` — nunca
  abrir para leitura o mesmo arquivo que será gravado por COM no mesmo processo.
- Gravação que precisa preservar fórmula, gráfico ou tabela dinâmica vai por `xlwings`/COM
  (Excel real rodando), nunca `openpyxl.save()` sobre o arquivo inteiro — `openpyxl` não lê
  nem escreve pivot table, e regrava fórmula como valor calculado, não como fórmula viva.
- Todo fluxo de gravação tem modo `--dry`: roda a lógica inteira, produz o mesmo relatório de
  conferência, e para antes do `save()`/da escrita COM final. Não é opcional — é requisito de
  design desde a primeira versão.
- Backup automático (cópia com timestamp do arquivo original) antes de qualquer gravação real
  fora do `--dry`.
- Sessão `xlwings` sempre dentro de `try/finally` fechando `app.quit()` — uma exceção no meio
  da gravação sem isso deixa `EXCEL.EXE` órfão rodando em segundo plano, acumulando a cada
  execução falha.

## Armadilhas
- `outline_level` é **0-based** em `openpyxl` e **1-based** em COM/`xlwings` — comparar os dois
  valores crus entre as duas bibliotecas quebra silenciosamente (nenhuma exceção, resultado
  errado). Sempre normalizar para uma convenção antes de comparar.
- Ler um arquivo `.xlsx` com `openpyxl` enquanto uma sessão `xlwings`/COM tem o mesmo arquivo
  aberto para escrita produz dado obsoleto ou erro de arquivo em uso — nunca sobrepor as duas
  sessões no mesmo arquivo.
- `app.quit()` sem `try/finally` ao redor de todo o bloco que usa a sessão: qualquer exceção
  entre o `app = xlwings.App(...)` e o `quit()` deixa processo zumbi.
- Comparar float lido de célula com `==` falha (herda a armadilha geral de `cartoes/python.md`)
  — ainda mais comum aqui porque toda comparação de saldo/valor financeiro é float.
- `openpyxl` com `data_only=True` só devolve o **último valor calculado salvo pelo Excel** —
  se o arquivo nunca foi recalculado/salvo pelo Excel de verdade, a leitura devolve `None` em
  vez do valor da fórmula.

## Comandos
- Suíte: `python -m pytest -q` (a camada de regra pura é testável; a camada Excel/COM em si
  normalmente não é — validação manual abrindo o arquivo gerado é parte do fluxo, não falha
  de cobertura).

## Checklist de review
- [ ] Modo `--dry` cobre exatamente o mesmo caminho de código que a gravação real, só sem o
      `save()`/write COM final.
- [ ] Leitura usa `read_only=True`; nenhuma leitura e escrita concorrente no mesmo arquivo.
- [ ] `outline_level` nunca é comparado cru entre `openpyxl` e COM/`xlwings` sem normalizar.
- [ ] Sessão `xlwings`/COM sempre fecha em `finally`, mesmo em caminho de exceção.
- [ ] Existe backup com timestamp antes de qualquer gravação real.
- [ ] Relatório de conferência em Markdown é gerado tanto no `--dry` quanto na gravação real.
