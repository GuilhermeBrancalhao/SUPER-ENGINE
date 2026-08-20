---
name: otimizar-performance
description: Motor de otimização — mede antes de otimizar, identifica o gargalo real (algoritmo, query, I/O, rede), prova a correção com baseline reproduzível e entrega ganho quantificado. Use quando o usuário disser "tá lento", "trava", "timeout", "demora demais", "picos de CPU/memória", mencionar latência ou volume. Força Número-Primeira: sem medição não há otimização, só adivinhação com custo de manutenção. Não use quando o problema é de arquitetura (aí é `arquitetar-sistema`) ou design (aí é `revisar-codigo`).
---

# Motor de performance

Otimização sem medição é adivinhação com custo.

A regra de ouro é tão universal que merece estar em 120 pontos: **meça, identifique o 20% que custa 80% do tempo/recurso, queime esse, meça de novo.**

## Antes de qualquer linha de código

Três respostas obrigatórias:

1. **Como você sabe que está lento?** Relação concreta: endpoint responde em 5s quando esperado era 1s, função que processa 100k registros leva 10 minutos. Sem o número é subjetivo — e otimização subjetiva produz resultado subjetivo.

2. **Sob qual carga?** Quantos registros, quantas requisições simultâneas, qual o hardware. Otimizar para 10 quando o cliente tem 100k desperdiça engenharia no lugar errado.

3. **Qual o recurso limitante?** CPU, memória, disco, rede, latência de contrato com terceiro. Se for contrato com terceiro (API lenta de terceiro), otimização local é inútil — o problema está fora.

Dados que não tem? Peça. Responder no vácuo é jogar dinheiro fora.

## Medir

Estabeleça baseline reproduzível:

- **Código de teste que produz o dado que você vai otimizar.** Se o dado é criado manualmente em banco, não é reproduzível — próxima corrida terá dado diferente e a comparação quebra.
- **Ferramenta de medição.** Para algoritmo: contador, cronômetro, benchmark. Para query: `EXPLAIN PLAN` e `pg_stat_statements`. Para processo: `perf`, `profiler` da linguagem.
- **Resultado nomeado.** Antes: `5000ms p99, 1000 queries, 400MB memória`. Depois: o mesmo conjunto, mesmas métricas. Sem isso não há "melhorou" ou "piorou" — há só suposição.

**Não meça em produção em clientes reais.** Log é destrutivo, pode impactar a métrica que você está lendo, e você treina a aplicação errada.

## Identificar

O gargalo que custa 80% é raro estar onde você acha. Leia a evidência:

| Fonte de evidência | Como ler |
|---|---|
| Profiler | Qual função acumula mais tempo? Chama-se a si mesma (recursão), ou chama outra função que não retorna? |
| Query log | Qual query roda mais vezes (`COUNT` em `pg_stat_statements`)? Qual roda menos vezes mas leva mais tempo? |
| Memória | Qual estrutura cresce? Há vazamento ou alocação desnecessária? |
| Rede | Qual chamada para fora é feita com mais frequência ou demora mais? |

**Ler a evidência é fundamentalmente diferente de desconfiar.** "Acho que a query tá lenta" vs "a query SQL roda 1000 vezes quando deveria rodar 1" é a diferença entre adivinhar e saber.

Quando há múltiplos gargalos, comece pelo maior. Código que muda 5% da latência custa tanto para manter quanto código que muda 50% — então queima o 50% antes.

## Padrão 1: Algoritmo

`O(n²)` sobre `O(n log n)`.

**Causa real:** laço aninhado, busca linear em vetor onde deveria ser índice ou hash, recursão sem memoização. Algoritmo errado é o gargalo que mais se paga corrigir, e não custa infraestrutura.

**Prova:** benchmark com três volumes: pequeno (validação), médio (volume esperado), grande (10x volume esperado). Não é suficiente que 100 registros fique rápido.

**Cuidado:** `O(1)` em operação com custo oculto (hash computation) pode perder para `O(log n)` em árvore com ramos pequenos. Meça; não confie na notação.

## Padrão 2: Query

N+1 é o clássico: laço que executa uma query por item.

**Causa:** buscar o pai do registro dentro da iteração em vez de buscar todos os pais em uma operação. Ou lazy loading de associação que não foi precarregada.

**Prova:** `EXPLAIN PLAN` antes e depois mostrando redução de scans sequenciais. Número de queries (leia os logs) antes e depois.

**Cuidado:** paginação com `LIMIT` e `OFFSET` pode esconder a explosão — offset grande requer ler todas as linhas até ele. Cursor-based pagination é alternativa quando relevante.

Índice: adicione só se `EXPLAIN` mostra seq scan onde deveria haver index scan. Índice falso custa escrita e espaço. Não adivinhe.

## Padrão 3: I/O e rede

Chamada para banco, para API externa, para storage remoto.

**Causa:** operação de bloqueio esperando resposta quando poderia ser paralela, polling quando deveria ser event, conexão sem conexão em pool.

**Prova:** antes/depois em latência de P99 (não média — outlier esconde o problema real).

**Cuidado:** paralelização adiciona contenção. 100 requisições paralelas ao mesmo banco podem degradar em vez de melhorar — o limite de conexão do banco fica saturado. Teste sob carga, não em laboratório.

Batch: se faz uma chamada por item, vire lote. Tempo total cai em ordens de magnitude.

## Padrão 4: Memória

Estrutura que cresce, cache sem limite, string concatenada em laço, builder que aloca em dobro a cada operação.

**Causa:** alocação efusiva ou não-liberação. Vazamento costuma ser em linguagem sem GC; em linguagem com GC é mais frequente ser alocação excessiva que pressiona o coletor.

**Prova:** profiler de memória (`jdwp`, `valgrind`, heap dump). Não conjeture; veja qual objeto ocupa quanto.

**Cuidado:** cache "para melhorar performance" pode piorar se o custo de invalidação > benefício de hit. Medir taxa de hit real.

## Padrão 5: CPU

Thread que consome 100% em operação que deveria ser rápida.

**Causa:** operação em tight loop sem yield, spinner em vez de sleep/event, compilação ou parsing a cada execução.

**Prova:** profile mostrando qual função acumula CPU. Muitas vezes é função que você não esperava.

## Reescrever ou configurar?

Nem tudo é código.

| Problema | Primeira tentativa |
|---|---|
| JVM pausando por GC | Tuning de GC flags em vez de reescrever |
| Database trava em lock | Isolamento de transação, ou reorganizar ordem de aquisição |
| Memória crescendo | Limite em cache, ou política de expiração |
| Query lenta | Índice, ou plano de execução diferente |

Reescrever é última opção — e muitas vezes nem é necessária. Configuração custa menos, quebra menos.

## Ganho quantificado

Resultado é uma tabela:

| Métrica | Antes | Depois | Ganho |
|---|---|---|---|
| Tempo P99 | 5000ms | 800ms | 6.2x |
| Queries por req | 1000 | 1 | 1000x |
| Memória pico | 400MB | 50MB | 8x |

Sem a métrica "depois" não há validação — você pode ter quebrado algo e estar mais rápido por acaso.

## Quando parar

Otimização tem retorno decrescente. Ganhar 10x é espetacular; ganhar 1% depois custa dia inteiro.

Parou quando:

- A latência atende ao requisito
- O próximo gargalo é externo (terceiro, rede, infraestrutura)
- Ganho marginal < custo de manutenção do código

Documento o ganho. "Antes era X, agora é Y" em algum lugar — relatório, ADR, PR — porque em seis meses alguém vai querer saber por que o código ficou mais complexo, e você precisa ter resposta.

## Formato

1. **Baseline** — qual é a latência/uso/volume agora, medido como descrito acima
2. **Diagnóstico** — qual estrutura custa quanto (gráfico de profiler ou plano de query)
3. **Alternativas** — qual a forma mais barata de corrigir (algoritmo vs configuração vs cache vs índice)
4. **Mudança** — código antes/depois, justificativa de por quê foi feita
5. **Validação** — mesma métrica, com os mesmos dados, resultado depois
6. **Custo aceito** — o que piorou com a mudança (manutenibilidade, memória em troca de velocidade, etc)

## Referências

Este motor ainda não tem `references/` próprio — o mapa de ferramenta de
medição por plataforma (perf, jdwp, py-spy, pprof) e o catálogo de padrões de
otimização com antes/depois ficam para quando alguém os escrever. Até lá, a
escolha de ferramenta de profiling fica a critério de quem conduz a fase,
guiada pela stack real do projeto.
