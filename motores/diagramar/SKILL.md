---
name: diagramar
description: Motor de visualização — converte descrição de sistema, fluxo, estrutura ou processo em diagrama Mermaid renderizável, derivando estilo e nível de detalhe da pergunta. Use quando o usuário disser "desenha", "mostra o fluxo", "diagrama de", "como isso se conecta", ou quando outro motor (arquitetar-sistema, materializar-ideia) precisar comunicar estrutura. Cobre C4 (contexto/container/componente), sequência, atividade, ER, BPMN, state machine, deployment, mind map. Nível e nfase derivam do contexto — não produz os 4 níveis C4 por completude.
---

# Motor de diagramas

Diagrama é ferramenta de comunicação, não de documentação por cumprimento. Desenha o mínimo que responde à pergunta, na notação certa, de forma que renderiza.

## Primeiro: é preciso um diagrama?

Nem tudo que é visual precisa de diagrama. Texto estruturado frequentemente é mais rápido e cabe melhor em documento.

| Pergunta | Responde melhor com |
|---|---|
| "Como estruturar isto" | Diagrama C4 **container** |
| "Qual o fluxo quando o usuário..." | Diagrama de sequência |
| "Como os processos falam entre si" | Diagrama de componente ou deployment |
| "Qual é o ciclo de vida desta entidade" | State machine |
| "Como os dados se relacionam" | ER diagram |
| "Que passos executam para chegar ao resultado" | Atividade (BPMN ou flowchart) |
| "Qual é o escopo de fora para dentro" | Diagrama C4 **contexto** |
| "Como a equipe se organiza" | Mind map ou organograma |

Quando o usuário diz "diagrama", confirme qual desses em vez de desenhar todos.

## Linguagem

**Mermaid**, sempre. Renderiza no GitHub, MkDocs, artifacts. SVG ou PNG à mão é pixel-locked, se mudou o sistema a imagem fica obsoleta e ninguém vai reatualizar — é um custo lixo que sedimenta.

Versão mínima que suporta a sintaxe desejada. Se Mermaid não tem, documento a pergunta em prosa estruturada e oferça ser revisitado quando Mermaid render.

Cada notação tem regra de sintaxe — existem armadilhas silenciosas. Valide renderização antes de entregar.

## Nível C4

Contexto, container, componente, código. **Não desenhe os quatro por completude** — desenhe o que responde à pergunta em jogo.

### Contexto

"O que é este sistema para o mundo exterior". Caixas: usuário, sistema central, sistema externo (API de terceiro, banco, integração). Setas: como falam.

Uso: pitch para não-técnico, escopo de projeto, "qual é meu trabalho".

Armadilha: detalhe demais. Contexto é escorço — sistema inteiro é uma caixa.

### Container

"Qual é o deployable". Código, banco, fila, app mobile. Não é classe — é coisa que roda em separado.

Uso: arquitetura de quem vai operar, onde a transação é quebrada.

Armadilha: confundir deployment com lógica. Se tudo é monolito, tudo é um container.

### Componente

"Dentro do container, como os pedaços falam". Camada de apresentação, negócio, persistência. Módulo que tem contrato.

Uso: quem vai codar, entender onde mexer.

Armadilha: inventar componente que não existe. Se duas coisas sempre mudam juntas, é uma coisa.

### Código

Classes, funções. Raro valer um diagrama aqui — pseudocódigo em prosa costuma ser mais legível.

## Sequência

Quem faz o quê em que ordem, com quem. Ator, caixa (sistema), seta com mensagem.

**Use para:** "Como o fluxo de pagamento funciona", "O que acontece quando clico em [botão]".

**Não use para:** estrutura estática (aí é C4) ou pipeline sem dependência de tempo (aí é atividade).

Regra: não aninha acima de 3 níveis, senão fica ilegível.

## Estado

Círculos nomeados, seta com gatilho. Quando a entidade tem ciclo de vida nomeável (Draft → Approved → Published, Order → Paid → Shipped).

**Use para:** "Quais são os estados possíveis desta entidade", "Quando posso fazer tal coisa".

## ER

Tabelas e relacionamento. Cardinality notada (1:1, 1:N, M:N).

**Use para:** "Como os dados se estruturam", "Qual é a chave estrangeira", "Qual é a restrição de unicidade".

**Não use para:** estrutura de classe (use diagrama de classe) ou dado que não é relacional.

## BPMN

Processos de negócio, não código. Ator, tarefa, decisão, paralelo, subprocesso.

**Use para:** "Como o fluxo de negócio funciona, com quem", "Qual é o ciclo de aprovação", "Onde está o gargalo".

Mais rico que flowchart, mas também mais pesado. Se for técnico e não negócio, flowchart (atividade) é mais leve.

## Deployment

Como o código sai do computador de quem escreve até rodar em produção. Container, node, ligação entre eles, volume persistido.

**Use para:** operação, infraestrutura, "onde roda isto", "qual o caminho de falha".

## Mind map

Raiz no centro, conceito ramificado. Estrutura de árvore que cabe em uma página.

**Use para:** "Vou explicar este tema do zero", exploração inicial, estruturação de aprendizado.

## Regras sempre

1. **Legenda.** O diagrama responde qual é a cor, qual é a textura. Não assume que quem lê vai se lembrar de um documento anterior.

2. **Rótulo que comunica.** Não "Processo A", "Processar pagamento". Não "Container 1", "API de checkout".

3. **Seta é verbo.** "envia pedido", "consulta", "persiste", não seta sem label.

4. **Sem cruzamento de setas quando viável.** Reordene a disposição.

5. **Validação.** Renderize antes de entregar — Mermaid silenciosamente não renderiza sintaxe inválida.

6. **Escala:** quantas caixas cabe em um diagrama legível? Regra de dedo: 5-7. Acima disso, separe em dois níveis.

## Tema e cores

Mermaid renderiza em tema do usuário (light/dark). **Não override cores por decoração** — deixe o tema decidir.

Se a cor carrega informação (severidade, tipo, status), aí sim nomeie. E valide que as cores funcionam nos dois temas.

## Formato

1. **A pergunta que o diagrama responde**, em uma linha
2. **O diagrama Mermaid**, em bloco código
3. **Legenda**, nomeando o que é cada elemento e cor
4. **Notas de contexto**, uma ou duas linhas se a estrutura não é óbvia

Sem preâmbulo. Sem "deixa eu desenhar".

## Referências

Este motor ainda não tem `references/` próprio — as duas leituras que valeriam a
pena (sintaxe de cada notação Mermaid com armadilhas de renderização; qual nível
C4 responde qual pergunta) ficam para quando alguém as escrever. Até lá, use o
que já está acima e a sintaxe Mermaid padrão.
