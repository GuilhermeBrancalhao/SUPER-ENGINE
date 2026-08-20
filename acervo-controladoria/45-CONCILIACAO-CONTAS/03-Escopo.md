---
volume: "45"
volume_nome: CONCILIACAO-CONTAS
tipo: ENGINE
secao: 03-Escopo
status: RASCUNHO
atualizado_em: 2026-08-03
---

# Escopo

## Dentro deste volume

O motor de decisão que recebe um movimento bancário já extraído (data, valor, descrição) e um
conjunto de títulos em aberto já consultados, e decide: qual título casa, com que confiança, se
pode escrever sozinho, se seria duplicata, e como registrar a decisão. Os cinco módulos —
âncora de saldo, casamento por título, classificação de confiança, guarda de duplicidade e
trilha de auditoria — e a composição entre eles.

## Fora deste volume, e para onde vai

**Extrair o extrato do banco e consultar o ERP por títulos abertos** é `54-INTEGRACAO-ERP`: este
volume assume que os dados já chegaram como `Movimento` e `TituloAberto`, e não sabe nada sobre
formato de arquivo bancário, autenticação de API ou paginação de resultado.

**Decidir a categoria contábil e o centro de custo de um lançamento** é `43-CONTABILIDADE-BASICA`:
quando este volume decide escrever, o "o quê escrever" (débito, crédito, plano de contas) vem de
lá, não daqui.

**Generalizar o conceito de trilha de auditoria para qualquer módulo do acervo-controladoria** é
`53-AUDITORIA-TRILHA`: `trilha.py`, citado aqui, é uma implementação de referência do padrão que
aquele volume descreve em abstrato — este volume não define o padrão, o usa.

**Apresentar o resultado da conciliação em relatório ou dashboard** é `51-RELATORIOS-GERENCIAIS`
e `44-INDICADORES-KPI`: este volume produz decisões (escreveu, não escreveu, ficou pendente), não
telas.

## Fronteira deliberada

O motor não faz retry de rede, não lê arquivo, não chama API — nenhuma das funções e métodos
de `exemplos/45-conciliacao-contas/` toca rede, disco ou relógio de parede. As funções de
*decisão* (`achar_ancora`, `casar`, `similaridade`, `classificar`) são puras: recebem estrutura
de dados e devolvem estrutura de dados, sem mutar nada. `guarda.registrar()` e
`trilha.registrar()` são a exceção deliberada — mutam estado *em memória* (ver
`09-Boas-Praticas.md`), nunca I/O externo; é essa distinção, não "tudo é puro", que a fronteira
deste volume protege. Isso é proposital: mistura entre lógica de
decisão e chamada de rede é a razão mais comum pela qual motores de conciliação viram
impossíveis de testar sem ambiente externo, tema aprofundado em `10-Anti-Patterns.md`.
