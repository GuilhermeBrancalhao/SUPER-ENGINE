---
name: gauntlet-loop
description: Motor de crítica cega contra barra externa — não substitui revisar-codigo/otimizar-performance, complementa quando o artefato já passa em teste e lint mas precisa ficar excelente, não só correto. Divide o entregável em peças julgáveis, dá a cada uma um crítico com contexto limpo, compara às cegas contra referência, e itera sem número fixo de rodadas. Use em REVISAO/DOC quando houver um padrão de qualidade externo e comparável (UI, documento, texto) e o ciclo puder pagar o custo de mais de uma rodada. Não use como substituto do motor de risco/segurança nem do critério de aceite funcional do ciclo — aqueles continuam obrigatórios e independentes deste.
---

# Motor de crítica cega (gauntlet-loop)

Este motor **não vive neste repositório**, e nunca vai viver: é a skill `gauntlet-loop`,
instalada e mantida como skill separada do ambiente Claude Code de quem conduz o ciclo — não
um artefato interno do ENGINE que um dia foi ou será fundido para cá. Este arquivo é só um
ponteiro: existe para que o nome apareça na lista de motores consultáveis das fases REVISAO e
DOC (`hooks/engine_contexto.py:MOTORES_POR_FASE`), sem duplicar aqui uma lógica que muda em
outro lugar e divergiria.

**Antes de consultar, confirme que a skill está disponível na sessão** — ela aparece na
listagem de skills invocáveis do ambiente (o mesmo lugar onde `revisar-codigo` ou qualquer
skill de projeto apareceria). Se não aparecer, ela não está instalada nesta máquina/sessão, e
este motor não pode ser usado neste ciclo — trate como motor indisponível, não force a
invocação nem simule o comportamento dele.

## Quando consultar

- REVISAO já produziu um artefato que passa nos testes e no critério de aceite funcional,
  mas a qualidade dele (design, clareza, robustez de UX) precisa ser medida contra uma
  barra externa, não só "compila e passa".
- DOC está produzindo um documento, diagrama ou material de entrega cujo padrão de
  qualidade é comparável a uma referência real (não um relatório interno de trilha).

## Quando NÃO consultar

- Correção de bug, segurança, ou performance — isso é `revisar-codigo` e
  `otimizar-performance`, e o resultado deles é objetivo (passa/não passa), não uma
  comparação de qualidade.
- Ciclo em modo `--dry` ou de baixo orçamento: o gauntlet-loop assume mais de uma rodada de
  crítica, e isso tem custo de tokens que o modo seco existe justamente para evitar.

## Como isso entra no ciclo

A entrada deste motor no cartão da fase é **regra fixa**, gravada em código
(`MOTORES_POR_FASE`), não uma decisão do modelo em tempo de execução. Quem decide *usar* o
motor continua sendo quem conduz a fase, lendo o cartão — exatamente como já acontece hoje
com `revisar-codigo`. Isto não altera o classificador de risco nem o despacho automático de
papel: `revisor` e `sentinela` continuam sendo os únicos agentes desta fase.
