---
volume: "45"
volume_nome: CONCILIACAO-CONTAS
tipo: ENGINE
secao: 14-Metricas
status: RASCUNHO
atualizado_em: 2026-08-03
---

# Métricas

**Taxa de dias com âncora fechada.** Proporção de dias do período em que `achar_ancora` devolve
um resultado não nulo, sobre o total de dias com saldo de banco disponível. Fonte: execução
diária do motor, contando o resultado de `Ancora | None`. Um número persistentemente abaixo de
100% indica origem de dado incompleta (saldo de banco ou lista de movimentos faltando algo), não
necessariamente um erro do motor — a métrica serve para apontar onde investigar, não para
condenar o código sozinha.

**Taxa de escrita automática (confiança ALTA) sobre total de movimentos casados.** Proporção de
movimentos que `classificar()` marcou `ALTA` sobre o total que `casar()` conseguiu associar a
algum título. Fonte: contagem de `Confianca` por execução. Essa métrica é a que mais importa
para medir a economia real de trabalho manual do motor — mas nunca deve ser otimizada às custas
de baixar o limiar de similaridade ou o limiar histórico, porque isso trocaria trabalho manual
por risco de escrita errada, o trade-off oposto ao que o volume defende.

**Taxa de falso positivo de escrita automática.** Dos itens escritos com confiança ALTA, quantos
foram posteriormente revertidos por decisão humana. Fonte: cruzamento entre a trilha
(`trilha.historico()`) e o registro de reversões do sistema contábil (fora deste volume). A
trilha não precisa carregar o nível de confiança em cada registro para essa métrica ser
computável: por invariante de projeto (`07-Regras.md`, "só confiança ALTA escreve sozinha"), a
ÚNICA forma de uma chave chegar a `trilha.registrar()` é ter sido classificada ALTA primeiro —
então **todo** registro em `trilha.historico()` já é, por construção, uma escrita de confiança
ALTA, e o numerador é só contar quantas dessas chaves aparecem no registro de reversão externo.
Esta é a métrica de segurança: o alvo declarado é zero, e qualquer valor acima de zero é motivo
de revisão imediata dos limiares em `confianca.py`, não de tolerância.

**Tempo entre o dia do movimento e o dia do fechamento da âncora.** Mede o atraso típico entre um
fato acontecer no banco e o motor conseguir confirmar que o saldo bate — relevante porque
lançamentos retroativos (ver `07-Regras.md`) fazem esse tempo variar por natureza da origem, não
por defeito do motor.

**Contagem de itens em `PendenciaHumana` por motivo** (sem título, confiança insuficiente,
suspeita de duplicata) — decompor a pendência por motivo, em vez de reportar um número agregado
único, é o que permite decidir se o próximo investimento deveria ir para melhorar casamento,
melhorar histórico, ou aceitar que aquele volume de pendência é estruturalmente humano.
