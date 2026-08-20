---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 14-Metricas
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Métricas

**Taxa de detecção automática sem intervenção manual, por banco.** Proporção de execuções de
`detectar_colunas()` que não levantam `ValueError` para um banco já em produção. Uma queda nessa
taxa para um banco específico é o sinal mais direto de que ele mudou o layout do CSV — e é
justamente o comportamento que `07-Regras.md` defende: falhar explicitamente em vez de mapear
errado em silêncio.

**Cobertura de bancos testados contra CSV real, sobre o total de bancos em produção.** Hoje: 1
de 40+ (DIGIO, dois arquivos — um funcional, um que revelou o bug de BOM descrito em
`12-Exemplos.md`, corrigido em 2026-08-04). Esta é a métrica mais honesta sobre o estado real
deste volume: a lógica de detecção foi validada contra um banco real, não quarenta.

**Divergência entre `VAL_COMISSAO` e `PCL_COMISSAO * VAL_BASE_COMISSAO`, quando os três campos
existem.** Não é uma validação que o script roda hoje — é uma métrica que poderia ser calculada
a partir do XLSX gerado, como checagem cruzada independente de que a coluna escolhida como
comissão é de fato a correta, mesmo quando a validação de soma interna (`validar()`) já passou.

**Tempo entre o banco mudar o layout do CSV e alguém notar.** Hoje, a única forma de notar é a
exceção `ValueError` aparecer numa execução manual — não existe monitoramento automático que
rode `normalizar.py` periodicamente e alerte sobre falha. Enquanto esse monitoramento não existe,
esta métrica não tem valor mensurável, só o registro de que a lacuna existe.
