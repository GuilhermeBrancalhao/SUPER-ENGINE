---
name: arquitetar-sistema
description: Motor de decisão arquitetural — define fronteiras entre módulos, escolhe entre alternativas com trade-off explícito, registra a decisão em ADR e comunica a estrutura em diagrama C4. Use quando o usuário perguntar "como estruturar isso", "onde devo colocar", "vale a pena separar em serviço", "monolito ou microserviço", "qual padrão usar aqui", quando precisar escolher entre stacks ou bancos, ou quando o problema for de acoplamento e não de código. Não use para corrigir código existente — aí o motor é `revisar-codigo`.
---

# Motor de arquitetura

Arquitetura é o conjunto de decisões caras de reverter. O trabalho aqui é identificar quais são essas decisões, decidir com fundamento e **deixar registro de por quê** — porque em dois anos ninguém lembra da alternativa descartada e alguém vai propô-la de novo.

## Primeiro: isto é problema de arquitetura?

Boa parte do que chega como pergunta de arquitetura é outra coisa. Diagnostique antes de desenhar.

| Sintoma | Provável causa real | Motor |
|---|---|---|
| "Tá difícil de testar" | Efeito colateral capturado do ambiente | Arquitetura — fronteira errada |
| "Toda mudança quebra outra coisa" | Acoplamento ou invariante duplicada | Arquitetura |
| "Tá lento" | Consulta, algoritmo ou I/O | `otimizar-performance` — **meça antes** |
| "O código tá feio" | Legibilidade local | `revisar-codigo` |
| "Precisa escalar" | Geralmente ainda não precisa | Peça o número antes de responder |

**Se o problema não é de fronteira, diga isso e roteie.** Rearquitetar código que só precisava de uma extração de função é o erro mais caro deste motor.

## Escala da resposta

Nem toda decisão merece ADR e diagrama.

- **Decisão local** — onde colocar uma função, se extrair uma classe. Responda em duas linhas, sem cerimônia.
- **Decisão estrutural** — fronteira nova, contrato entre módulos, escolha de banco ou stack, mudança que outros times sentem. Aí sim: alternativas, trade-off, ADR.
- **Decisão que já foi tomada** — se existe ADR ou padrão no projeto, siga. Divergir exige argumento novo, não preferência. Procure em `docs/adr/`, `CLAUDE.md`, convenções do repositório antes de propor.

## Ler antes de decidir

Nunca proponha estrutura sem ver a estrutura atual.

1. Árvore de diretórios até 2 ou 3 níveis — revela a organização real, que raramente é a documentada
2. Como os módulos se importam — o grafo de dependência é a arquitetura de fato
3. Onde estão as transações, onde estão os efeitos externos
4. Testes: o que é testado sem infraestrutura já indica onde a fronteira funciona
5. ADR e convenção existentes

Delegue varredura ampla ao agente `Explore`.

## Fronteira

A pergunta que define uma fronteira não é "isso é uma camada?" — é **"o que muda junto?"**. Coisas que mudam pelo mesmo motivo ficam juntas. Coisas que mudam por motivos diferentes se separam.

Critérios que valem:

- **Motivo de mudança.** Regra fiscal e layout de tela mudam por motivos distintos e em ritmos distintos. Separe.
- **Direção da dependência.** Aponta para dentro: detalhe depende de política, nunca o contrário. Se o domínio importa o framework, a fronteira está invertida.
- **Contrato, não estrutura.** Módulo expõe o que faz, não como guarda. Tipo de persistência atravessando a borda anula a fronteira.
- **Teste como prova.** Se testar a regra exige subir banco, a regra e o I/O não estão separados — independente do que diga o diagrama.

Critérios que **não** valem: simetria ("as outras têm três camadas"), previsão ("um dia vamos precisar"), e organização por tipo técnico (`controllers/`, `services/`, `models/`) quando o domínio pedia organização por capacidade.

**Camada que só delega é cerimônia.** Porta que repassa um `findById` custa manutenção e não isola nada. Diga isso quando encontrar — vale mais que manter a simetria.

## Monolito e serviço

Padrão: **monolito modular com fronteira interna clara.**

Separar em serviço adiciona rede, versionamento de contrato, observabilidade distribuída e transação que virou eventual. Isso é conta operacional permanente, e alguém precisa pagá-la.

Separe quando houver motivo nomeável:

- Times independentes que se bloqueiam no mesmo deploy
- Perfil de escala genuinamente diferente — um componente que precisa de 20x a capacidade dos outros
- Isolamento de falha exigido por requisito, não por estética
- Restrição de compliance sobre onde o dado roda

"Ficar mais organizado" não é motivo — fronteira interna dá o mesmo isolamento lógico sem a conta.

**Se o monolito atual está emaranhado, separá-lo em serviços transforma acoplamento local em acoplamento distribuído** — o mesmo problema, agora com latência de rede e falha parcial. Organize por dentro primeiro.

## Comparar alternativas

Toda decisão estrutural precisa de pelo menos uma alternativa considerada. Sem alternativa, não foi decisão — foi hábito.

Compare em dimensões concretas, nunca em adjetivo:

- Custo de manutenção — quem sustenta isso em dois anos
- Acoplamento introduzido
- Performance **sob qual carga** — número, não "escalável"
- Testabilidade
- Custo operacional e de infraestrutura
- Reversibilidade: quanto custa desfazer

**Recomende uma.** Comparação sem veredito devolve ao usuário o trabalho que ele delegou. Quando duas opções não têm diferença prática, diga que não têm e escolha — deliberar sobre empate é desperdício.

Quando a decisão depende de dado que você não tem — volume, latência atual, tamanho do time, prazo — **peça o dado**. Uma pergunta específica vale mais que três parágrafos condicionais.

## Registrar

Decisão estrutural sai em ADR curto: contexto, decisão, alternativas descartadas com o motivo, consequências aceitas.

A seção que mais importa é **alternativas descartadas** — é o que impede a discussão de recomeçar do zero daqui a um ano.

Registre também o que a decisão **custou**. ADR que só lista benefício é propaganda, e ninguém confia na segunda leitura.

## Comunicar

Diagrama quando a estrutura é o que precisa ser entendido. Delegue ao motor `diagramar`.

Nível C4 conforme a pergunta: contexto para quem é externo, container para quem opera, componente para quem vai codar. **Não desenhe os quatro níveis por completude** — desenhe o que responde a pergunta em jogo.

Todo diagrama acompanhado de descrição textual: quem não renderiza Mermaid precisa entender igual.

## Formato

1. **Diagnóstico** — qual é o problema de fato, uma linha. Se não é arquitetura, diga e roteie
2. **Decisão** — o que fazer
3. **Por quê** — trade-off contra a alternativa mais forte, não contra um espantalho
4. **Custo aceito** — o que piora com esta escolha
5. **Como chegar lá** — passos, se a mudança for grande. Caminho incremental que mantém o sistema funcionando a cada passo vence big bang

Sem preâmbulo. Sem "excelente pergunta".

## Referências

Este motor ainda não tem `references/` próprio — o detalhamento de quando um
ADR se justifica e o catálogo de sinais de acoplamento errado (com o teste que
revela cada um) ficam para quando alguém os escrever. Até lá, a seção "ADR" ali
em cima é o guia real.
