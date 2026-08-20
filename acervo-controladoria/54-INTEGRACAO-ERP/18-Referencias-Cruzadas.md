---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 18-Referencias-Cruzadas
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Referências Cruzadas

## Vizinhança de assunto

O campo `depende_de` está vazio no `_VOLUME.yml` — ver o comentário lá para o motivo. A
vizinhança real, em prosa:

| Volume vizinho | Relação |
|---|---|
| `45-CONCILIACAO-CONTAS` | Consome o modelo `PROCESSADO` que este volume produz, como `Movimento`/`TituloAberto` já normalizados; este volume não sabe nada sobre casamento ou confiança |
| `43-CONTABILIDADE-BASICA` | Decidiria a categoria contábil e o centro de custo do lançamento já normalizado — removido deste acervo por ser esqueleto sem conteúdo real |
| `53-AUDITORIA-TRILHA` | Generalizaria o padrão de trilha de auditoria — também removido pelo mesmo motivo |

## Links que resolvem hoje

- [`../00-INTRODUCAO/Convencoes.md`](../00-INTRODUCAO/Convencoes.md) — o contrato deste acervo e a Definição de PRONTO
- [`../ESTADO.md`](../ESTADO.md) — a auditoria de 2026-08-04 que classificou este volume como "parcial" e motivou esta reescrita
- [`../exemplos/54-integracao-erp/normalizar.py`](../exemplos/54-integracao-erp/normalizar.py) — o normalizador
- [`../exemplos/54-integracao-erp/MODELO_UNIVERSAL.md`](../exemplos/54-integracao-erp/MODELO_UNIVERSAL.md) — o modelo `PROCESSADO` documentado
- [`../exemplos/54-integracao-erp/tests/test_normalizar.py`](../exemplos/54-integracao-erp/tests/test_normalizar.py) — os 16 testes

## Navegação interna

Para implementar contra o normalizador: `11-Implementacao.md` seguido de `12-Exemplos.md`. Para
entender as garantias e os bugs já corrigidos: `07-Regras.md` e `10-Anti-Patterns.md`. Para
estender a um banco novo: `03-Escopo.md` e `16-Roadmap.md`, nessa ordem.
