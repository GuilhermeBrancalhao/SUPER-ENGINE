---
volume: "45"
volume_nome: CONCILIACAO-CONTAS
tipo: ENGINE
secao: 07-Regras
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Regras

## Invariantes

**A âncora caminha para frente, nunca para trás a partir do saldo de hoje.** Um lançamento com
data de registro correta que só chega dias depois (juros lançados com atraso, por exemplo) faz o
saldo atual carregar um resíduo que não pertence a nenhum dia específico. Caminhar de trás para
frente distribui esse resíduo por todos os dias igualmente e a âncora desaparece mesmo quando a
conciliação está correta. Caminhar para frente a partir de um saldo passado conhecido isola o
resíduo no dia em que ele de fato aparece — ver `test_lancamento_com_data_retroativa_fecha_o_dia_correto_quando_chega`.

**Título em aberto sempre vence lançamento novo.** Antes de qualquer criação de lançamento
avulso, o motor tem de varrer os títulos abertos por um candidato compatível. Divergência de
valor dentro de uma tolerância não é motivo para descartar o título — consumo variável (conta de
serviço que oscila mês a mês) é o caso normal, não a exceção.

**A chave de duplicidade é sempre composta.** Data, valor com sinal e contraparte normalizada —
nunca valor isolado. Dois movimentos legítimos podem compartilhar o mesmo valor absoluto; um
duplicado real também compartilha o mesmo valor absoluto que o original. Decidir por valor
sozinho garante falso positivo em qualquer conta com movimentação redonda recorrente.

**A trilha local é a única fonte de verdade sobre "já processado" — para o que o motor decidiu
escrever sozinho.** Um índice em sistema externo pode apagar ou mudar o campo usado como chave
depois da própria escrita que ele registrou — consultar esse índice para decidir idempotência
produz falso negativo sistemático (o item some do índice, o motor tenta escrever de novo). A
trilha é local, append-only, e consultada antes de qualquer índice remoto.

**Escopo desta garantia, precisado em auditoria de 2026-08-20:** a trilha só recebe registro de
escrita ALTA automática (`06-Fluxogramas.md`). Uma pendência resolvida por decisão HUMANA
(destino `PendenciaHumana`) não passa por `trilha.registrar()` — quem compõe o motor em
produção precisa de um segundo rastro para decisões humanas, se quiser que a próxima execução
também saiba delas. Este volume não resolve esse rastro; só garante que o que ELE ESCREVE
sozinho nunca duplica.

**Só confiança ALTA escreve sozinha.** Toda decisão MEDIA ou BAIXA vira pendência para revisão
humana — nunca aproximação, nunca "fecha por enquanto e corrige depois". A ausência de uma fonte
de evidência (histórico indisponível, por exemplo) só pode reduzir a confiança calculada, nunca
elevá-la acima do que a evidência disponível sustenta sozinha.

## O que nunca pode acontecer

Escrever a mesma chave duas vezes na trilha — `trilha.registrar()` levanta exceção em vez de
ignorar silenciosamente, porque uma segunda tentativa da mesma chave é sinal de outro bug
(reprocessamento indevido), e silenciar esconderia esse sinal.
