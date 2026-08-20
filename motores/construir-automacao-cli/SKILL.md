---
name: construir-automacao-cli
description: Motor para construir automação/CLI em Python que substitui um processo manual (planilha, conferência, relatório). Use quando o pedido for "automatiza isso", "cria um script para", "substitui esse processo manual por código", ou quando o ciclo já identificou que o entregável é uma ferramenta rodada por uma pessoa (não um serviço multiusuário). Cobre separação regra/orquestração, modo --dry como requisito de design, backup antes de escrita irreversível, relatório de conferência, e o critério de escolha entre interface Flask e Tkinter. Não use para serviço web multiusuário com múltiplos acessos simultâneos reais (aí o cartão certo é de framework web + banco, não este motor) nem para script descartável de uso único que não será rodado de novo.
---

# Motor de automação/CLI em Python

Um script que substitui um processo manual carrega um risco que um serviço não tem: quem
usa confia que o resultado está certo porque "o computador fez", e não vai conferir célula
por célula como fazia manualmente. O motor existe para que essa confiança seja merecida, não
suposta.

## Estrutura: regra pura separada de orquestração

Duas camadas, sempre:

- **Regra pura** (`regras.py` ou equivalente): recebe dado já carregado, decide o quê fazer,
  devolve o resultado — sem abrir arquivo, sem gravar nada, sem chamar rede. Testável com
  `pytest` direto, sem mock de I/O.
- **Orquestração** (`main.py`/`app.py`/o script de entrada): lê a entrada, chama a regra,
  grava a saída. É a camada que normalmente NÃO tem teste automatizado (I/O real, COM,
  planilha) — e é aceitável que não tenha, contanto que a lógica de decisão esteja toda na
  camada de baixo.

Misturar as duas é o defeito mais caro de encontrar depois: um bug de regra escondido dentro
de um loop de I/O só aparece rodando o script inteiro contra dado real.

## `--dry` é requisito de design, não feature opcional

Todo fluxo que grava alguma coisa (arquivo, planilha, e-mail, banco) tem um modo `--dry` que
roda a lógica inteira — leitura, decisão, geração do relatório de conferência — e para
exatamente antes da escrita/envio final. Não é um "if" adicionado depois: o código já nasce
com o ponto de corte entre "decidir" e "efetivar" como uma fronteira explícita, porque
adicionar isso depois de tudo pronto normalmente exige reescrever a orquestração inteira.

## Backup antes de escrita irreversível

Qualquer gravação que sobrescreve um arquivo existente (não um arquivo novo) faz cópia com
timestamp antes. Isso vale mesmo quando existe versionamento externo (OneDrive, Git) —
aquele protege contra perda de longo prazo, este protege a recuperação imediata sem precisar
navegar histórico de versão sob pressão.

## Relatório de conferência

Saída obrigatória de toda execução real (e do `--dry`, no mesmo formato): um documento
legível sem abrir o artefato original, dizendo o que foi lido, o que foi decidido, e o que
foi gravado (ou seria gravado, no `--dry`). Formato Markdown por padrão — abre em qualquer
lugar, sem programa específico, e é diffável se alguém quiser comparar duas execuções.

## Critério de escolha de interface

| Situação | Interface |
|---|---|
| Precisa de histórico de execuções, dashboard, ou múltiplos acessos (mesmo que só uma pessoa, mas de máquinas diferentes) | Flask local, server-side, sem build step de frontend |
| Uso local único, uma pessoa, uma máquina, sem necessidade de servidor rodando | Tkinter — mais simples de distribuir, sem porta, sem processo em segundo plano |
| Execução agendada/sem supervisão | Nenhuma das duas — CLI puro com log em arquivo |

Não escolher framework SPA/build-step JS para este tipo de ferramenta: o custo de manutenção
de um pipeline de build para uma tela de uso interno não se paga.

## Checklist antes de considerar pronto

- [ ] Regra de decisão está isolada em função/módulo testável sem I/O.
- [ ] `pytest` cobre a camada de regra pura.
- [ ] Existe `--dry` que roda tudo exceto a escrita final.
- [ ] Backup com timestamp acontece antes de qualquer sobrescrita.
- [ ] Relatório de conferência é gerado tanto em `--dry` quanto em execução real, mesmo
      formato.
- [ ] Interface escolhida (Flask/Tkinter/nenhuma) tem justificativa registrada, não foi
      copiada do último projeto por hábito.
- [ ] Se o projeto manipula Excel real, consultar também `cartoes/openpyxl-xlwings.md`.
