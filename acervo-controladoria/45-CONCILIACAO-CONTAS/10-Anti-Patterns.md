---
volume: "45"
volume_nome: CONCILIACAO-CONTAS
tipo: ENGINE
secao: 10-Anti-Patterns
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Anti-Patterns

**Usar um índice de sistema externo como fonte de idempotência.** Um ERP pode apagar ou mutar o
campo que seria usado como chave depois que a própria escrita aconteceu — um caso real e
documentado é um sistema que limpa o número de um boleto do índice de consulta assim que ele é
liquidado via API. Consultar esse índice para perguntar "isso já foi processado?" produz falso
negativo: o item some do índice, o motor conclui que nunca foi tratado e tenta escrever de novo.
A trilha local (`trilha.py`) existe exatamente para não depender desse índice.

**Comparar por valor absoluto isolado na guarda de duplicidade.** Duas transferências legítimas
de mesmo valor redondo, em dias diferentes ou para contrapartes diferentes, não são a mesma
transação — mas um duplicado real tem, por definição, o mesmo valor absoluto que o original.
Decidir só por valor garante que a guarda bloqueie transação legítima (falso positivo) com a
mesma frequência com que pega duplicata de verdade. A chave tem de ser composta: ver
`test_valores_redondos_repetidos_em_dias_diferentes_nao_sao_duplicata`.

**Criar lançamento avulso sem varrer título aberto antes.** É a causa mais comum de despesa
duplicada num motor de conciliação: existe previsão no sistema contábil, o motor não olhou, e
cria um segundo lançamento para o mesmo fato. `casar()` é chamado antes de qualquer decisão de
criação justamente para eliminar essa classe de erro.

**Ancorar o saldo de trás para frente a partir do saldo de hoje.** Um lançamento com data de
registro correta mas recebido com atraso faz o saldo atual carregar um resíduo que não pertence
a nenhum dia — e esse resíduo desloca a âncora de todos os dias igualmente, fazendo a
reconciliação parecer quebrada quando na verdade só falta esperar o dado chegar. `07-Regras.md`
detalha a correção.

**Misturar chamada de rede dentro da lógica de decisão.** Um módulo que consulta API dentro da
mesma função que decide se casa ou não só pode ser testado com mock de rede — e mock de rede
tende a divergir do comportamento real do sistema externo com o tempo. Nenhuma função de
decisão deste volume toca rede, disco ou relógio — `guarda.registrar()` e `trilha.registrar()`
mutam estado em memória por desenho (ver `03-Escopo.md`/`09-Boas-Praticas.md`), mas isso não é
I/O externo; a integração de fato fica inteiramente em `54-INTEGRACAO-ERP`.

**Elevar a confiança na ausência de evidência.** Um motor que assume "sem dado histórico,
confio do mesmo jeito" inverte a garantia de degradação segura — e é exatamente o oposto do que
`test_ausencia_de_fonte_de_evidencia_so_pode_rebaixar_nunca_subir` existe para impedir.
