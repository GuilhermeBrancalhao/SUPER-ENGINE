---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 07-Regras
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Regras

- **CSV de banco brasileiro chega com vírgula decimal como texto** (`'886,39'`), nunca como
  número — filtrar coluna candidata por `is_numeric_dtype` sem converter primeiro descarta a
  coluna certa e deixa sobrar só coluna vazia. `_para_numerico()` existe para resolver isso antes
  de qualquer outra decisão; coberto por `test_para_numerico_converte_formato_brasileiro`.
- **Coluna 100% vazia (`NaN` em toda linha) nunca pode virar candidata**: soma de coluna vazia dá
  `0,00` no pandas (skipna por padrão), não `NaN` — isso faz validação de soma "passar"
  comparando vazio com vazio. `_coluna_numerica_candidata()` filtra isso na origem; coberto por
  `test_coluna_100_por_cento_vazia_nao_vira_candidata`.
- **Nome de coluna sozinho não desambigua**: "% da Comissão" e "Valor Comiss" casam no mesmo
  padrão (`comiss`). Desempate por nome (percentual descarta, "valor" prioriza) e, na falta
  disso, por magnitude (percentual de comissão fica em 0-100, valor pago não) — a árvore
  completa está em `06-Fluxogramas.md`; coberto por `test_escolhe_valor_comissao_e_nao_o_percentual`.
- **Toda transformação precisa de validação que compare contra a origem** — soma bater,
  contagem de linha bater, proposta sem duplicata, coluna de comissão não pode ficar vazia —
  porque silêncio (coluna errada escolhida, valor `None`) é mais perigoso que erro explícito;
  coberto por `test_validar_trava_se_coluna_de_comissao_ficar_vazia`.
- **Data de banco brasileiro é dd/mm/aaaa, nunca mm/dd/aaaa.** `pd.to_datetime()` sem
  `dayfirst=True` assume o formato americano por padrão: dia e mês trocados em silêncio para
  dia ≤ 12, `ValueError` (e detecção de coluna abortada) para dia > 12 — ou seja, praticamente
  todo CSV cobrindo um mês real de movimento. A MESMA opção `dayfirst=True` tem de valer tanto
  na detecção de coluna quanto na gravação final em `DAT_CREDITO`; achado de auditoria
  2026-08-20, coberto por `test_dat_credito_nao_troca_dia_por_mes`.
- **dtype `str` nativo do pandas recente não é o `object` clássico.** Um filtro que checa
  `dtype == object` para decidir se vale a pena tentar converter texto deixa passar batido uma
  coluna com esse dtype mais novo, e ela vira `NaN` sem aviso — `_para_numerico()` evita esse
  filtro e tenta converter via `astype(str)` independente do dtype de origem, deixando o próprio
  `pd.to_numeric` decidir o que é convertível.
