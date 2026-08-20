---
name: conciliar-dados
description: Motor de reconciliação — decide como cruzar duas fontes de dados (arquivos, planilhas, exports, tabelas) e produzir um relatório de divergência auditável. Use quando o pedido for "bate isso com aquilo", "confere orçado com realizado", "acha o que não fechou entre X e Y", "concilia extrato com lançamento", ou qualquer variante de "duas fontes deveriam concordar e preciso saber onde não concordam". Cobre chave de casamento, tolerância de valor/data, tratamento de item sem par e formato do relatório. Não use para anotar duas colunas dentro de UMA planilha já aberta (isso é a skill `conciliar-planilhas`) nem para o critério de domínio de conciliação contábil (isso é `acervo-controladoria/45-CONCILIACAO-CONTAS`, quando PRONTO — este motor referencia aquele volume, não duplica o conteúdo dele).
---

# Motor de conciliação de dados

Reconciliar é responder uma pergunta específica: **cada registro da fonte A tem um par
correspondente na fonte B, e os dois concordam?** Três resultados possíveis por registro —
casado e concordante, casado e divergente, sem par — e o motor existe porque decidir os
critérios de casamento no meio da implementação produz resultado inconsistente entre
execuções.

## Antes de qualquer código

Três decisões, na ordem, cada uma bloqueando a seguinte:

1. **Qual é a chave de casamento?** Um campo único (número de documento) é o caso fácil.
   Combinação de campos (data + valor + descrição parcial) é o caso comum em dados
   financeiros que não compartilham um identificador único entre sistemas — e aí a chave
   precisa de uma ordem de prioridade declarada (tenta casar por A, o que sobrar tenta por B),
   não uma tentativa só.
2. **Qual é a tolerância?** Valor: `math.isclose` com tolerância absoluta OU relativa
   declarada — nunca `==` em float (herdado de `cartoes/python.md`). Data: mesma data exata,
   ou janela de N dias (comum quando uma fonte lança na compensação e outra na liquidação).
   Tolerância sem justificativa registrada é tolerância inventada.
3. **O que fazer com item sem par?** Três casos distintos, não um só "pendência" genérico:
   está em A mas não em B (o quê causaria isso — atraso, erro, fraude?), está em B mas não em
   A (mesma pergunta do outro lado), e casou mas os valores divergem (é a divergência
   propriamente dita). Cada caso tem tratamento e prioridade de investigação diferentes.

## Formato do relatório de divergência

Sempre as quatro seções, mesmo quando alguma vier vazia — vazio é informação (nada
divergente é um resultado, não a ausência de resultado):

1. **Resumo numérico** — total em A, total em B, quantos casaram concordantes, quantos
   casaram divergentes, quantos ficaram sem par de cada lado.
2. **Casado e divergente** — a lista, com os dois valores lado a lado e a diferença.
3. **Sem par em A** / **Sem par em B** — as duas listas separadas, nunca uma lista só
   "não bateu" misturando os dois lados.
4. **Parâmetros usados** — a chave de casamento e a tolerância aplicada, registradas no
   próprio relatório. Sem isso, ninguém audita o relatório sem reler o código.

O relatório é legível sem abrir a fonte original — Markdown, texto simples, ou planilha
anotada, nunca só um número de "X divergências encontradas" sem a lista.

## Relação com as outras duas peças de conciliação

- **Skill `conciliar-planilhas`** (externa): caso tático de comparar duas ÁREAS dentro de uma
  MESMA planilha já aberta, produzindo a própria planilha anotada como saída. Use quando o
  output desejado É a planilha, não um relatório à parte.
- **Volume `acervo-controladoria/45-CONCILIACAO-CONTAS`** (quando `PRONTO`): fonte de critério
  de domínio para conciliação bancária especificamente — âncora de saldo, casamento de
  movimento, confiança, guarda contra duplicidade, trilha de auditoria. Consulte-o para
  conciliação contábil/bancária real; este motor é o processo genérico, aquele é o
  aprofundamento de domínio.

## Checklist antes de considerar pronto

- [ ] Chave de casamento e tolerância estão declaradas no código E no relatório, não só na
      cabeça de quem implementou.
- [ ] Os três casos de resultado (concordante, divergente, sem par) têm tratamento distinto.
- [ ] Nenhuma comparação de valor usa `==` em float.
- [ ] O relatório é legível sem reabrir as fontes originais.
- [ ] Rodar em modo `--dry` (ver `motores/construir-automacao-cli`) não altera nenhuma fonte —
      conciliação é operação de leitura, gravação (se houver) é etapa separada e posterior.
