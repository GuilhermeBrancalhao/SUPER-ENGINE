---
volume: "54"
volume_nome: INTEGRACAO-ERP
tipo: ARQUITETURA
secao: 15-Checklist
status: RASCUNHO
atualizado_em: 2026-08-20
---

# Checklist

Antes de considerar este volume pronto para uso em produção — não confundir com a Definição de
PRONTO do acervo, tratada em `00-INTRODUCAO/Convencoes.md`:

- [x] `normalizar.py` existe, é testado (16 testes) e roda contra pelo menos um CSV real de
      produção com resultado conferido à mão, e a CLI documentada (`python normalizar.py ...`)
      roda de ponta a ponta num console Windows sem erro de encoding — a proteção de encoding
      agora vive no topo do módulo (cobre quem importa a classe direto, não só a CLI).
- [x] `DAT_CREDITO` usa `dayfirst=True` na detecção e na gravação (as duas em conjunto — usar
      só numa delas reintroduziria o bug). Sem isso, dia e mês trocavam para dia ≤ 12 e a
      detecção de coluna abortava para dia > 12, em praticamente todo arquivo mensal real
      (achado da 2ª rodada de auditoria, 2026-08-20).
- [x] `executar()`/`main()` propagam o resultado de `validar()`: salva o XLSX mesmo quando
      reprova (resultado parcial ainda é útil), mas o exit code (2, distinto de 0/1) e o print
      deixam de esconder que a validação falhou.
- [x] Terceira coluna candidata a COMISSAO não vaza para VALOR BRUTO — a exclusão agora cobre
      todas as colunas candidatas, não só as duas rastreadas em `deteccoes`.
- [x] O bug real do percentual escolhido em vez do valor pago está corrigido e coberto por teste
      que falha se for reintroduzido.
- [x] Os dois diagramas exigidos pelo tipo `ARQUITETURA` (`C4Context` em `04-Arquitetura.md`,
      `sequenceDiagram` em `05-Diagramas.md`) existem e têm parágrafo descritivo logo depois.
- [x] Todo exemplo citado no volume existe como arquivo e tem teste correspondente.
- [x] Bug do BOM UTF-8 e coluna única silenciosa em `ler_csv` (arquivo de julho do DIGIO,
      `12-Exemplos.md`) — corrigido em 2026-08-04, coberto por teste (ver `13-Testes.md` para a
      contagem exata; três outras seções deste volume ainda diziam "pendente" até 2026-08-20).
- [x] Validação de soma de comissão recalcula a partir do CSV original, não compara mais um
      cache contra ele mesmo (achado de auditoria 2026-08-20, corrigido).
- [x] `NUM_BANCO`/`NOM_BANCO` são preenchidos de fato no `df_processado` (saíam sempre vazios
      antes de 2026-08-20 por bug de DataFrame sem índice).
- [x] Detecção de VALOR BRUTO não reusa a coluna já escolhida como COMISSAO (corrigido em
      2026-08-20 — antes, com só uma coluna "valor" no CSV, as duas saíam idênticas).
- [ ] Testado contra mais de um banco — hoje só DIGIO (real, 29 colunas). Item anterior
      afirmava teste sintético contra SANTANDER/ITAÚ/CAIXA/BRADESCO/NUBANK/BTG; auditoria de
      2026-08-20 não encontrou nenhum vestígio desses testes na suíte, e o item foi desmarcado
      até que existam de fato — ver `17-Conclusao.md`, que já dizia isso corretamente.
- [ ] Conector de API de ERP (SAP, Oracle, Omie, IFS) — só intenção declarada em
      `02-Objetivos.md`, zero linha de código.
- [ ] `depende_de` aponta para `45-CONCILIACAO-CONTAS` e `43-CONTABILIDADE-BASICA` assim que o
      segundo for reescrito com o mesmo rigor — hoje fica vazio de propósito, ver `_VOLUME.yml`.
- [ ] Auditoria por outro modelo, com média maior ou igual a 8,0 e nenhuma seção abaixo de 6,
      registrada em `auditorias/`.
- [ ] Resultado registrado em `CHANGELOG.md` (raiz de `SUPER-ENGINE/`, não existe changelog
      próprio dentro de `acervo-controladoria/`) com a data do dia.

Os cinco últimos itens são o que falta para o `status` no front-matter passar de `RASCUNHO`
para `PRONTO` — os gates mecânicos (estrutural e executável) já rodam verdes, mas isso não
substitui auditoria de qualidade nem cobertura real contra mais de um banco.
