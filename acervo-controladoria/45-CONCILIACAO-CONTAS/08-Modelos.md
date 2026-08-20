---
volume: "45"
volume_nome: CONCILIACAO-CONTAS
tipo: ENGINE
secao: 08-Modelos
status: RASCUNHO
atualizado_em: 2026-08-03
---

# Modelos

Todas as estruturas são `dataclass(frozen=True)` — imutáveis por construção, porque nenhuma
delas deveria mudar depois de criada: uma decisão de casamento ou de confiança é um fato
histórico, não um objeto que evolui.

## `ancora.py`

`Movimento(data: date, valor: float)` — positivo é entrada, negativo é saída. `Ancora(data: date,
saldo_banco: float, saldo_sistema: float, residuo: float)` — devolvida por `achar_ancora()`
quando o resíduo fica abaixo de `CENTAVO` (0.005).

## `casamento.py`

`TituloAberto(id: str, contraparte: str, valor: float)` e `Movimento(descricao: str, valor:
float)` — este `Movimento` é local ao módulo, deliberadamente sem os mesmos campos do
`Movimento` de `ancora.py`: um representa um evento de saldo, o outro representa um evento a
casar por nome e valor, e forçar um tipo único faria um dos dois carregar campo que não usa.

## `confianca.py`

`Evidencia(match_exato_valor: bool, similaridade_nome: float, ocorrencias_historicas: int = 0,
dominancia_historica: float = 0.0)` — os dois últimos campos têm default zero de propósito: um
chamador que não tem acesso a histórico simplesmente não os preenche, e a ausência já produz a
degradação segura descrita em `07-Regras.md`. `Confianca` é um `Enum` de três valores (`ALTA`,
`MEDIA`, `BAIXA`), nunca um booleano — um booleano esconderia a diferença entre "seguro escrever"
e "seguro descartar", que são respostas diferentes.

## `guarda.py`

`ChaveMovimento(data: date, valor: float, contraparte: str)`, com o método `normalizada()` que
arredonda o valor a duas casas e uniformiza a contraparte em maiúsculas sem espaço nas pontas —
a normalização existe para que "Fornecedor A" e "fornecedor a " sejam a mesma chave.

## `trilha.py`

`RegistroTrilha(chave: str, usuario: str, quando: datetime, acao: str, detalhe: str = "")` —
imutável e append-only por construção do próprio `Trilha`, que expõe `historico()` como tupla,
não lista, para que quem consulta não possa mutar o registro por engano.
