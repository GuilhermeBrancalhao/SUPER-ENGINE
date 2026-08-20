"""Casamento de movimento bancario contra titulo em aberto: nunca cria
lancamento avulso sem antes varrer os titulos abertos, e o casamento por nome
descarta o boilerplate bancario antes de medir similaridade.

Duas descricoes de cartao do tipo "COMPRA NACIONAL DEBIT <fornecedor>" tem alta
similaridade textual mesmo quando o fornecedor e diferente, porque o prefixo
compartilhado domina a comparacao. Comparar so os tokens que sobram depois de
remover o vocabulario generico (compra, nacional, debito, pagamento, conta...)
evita que esse boilerplate esconda o nome real da contraparte.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

BOILERPLATE = {
    "PAGAMENTO", "RECEBIMENTO", "TRANSFERENCIA", "TRANSF", "CONTA", "CONTAS",
    "TITULARIDADE", "MESMA", "FAVORECIDO", "COBRANCA", "TITULO", "COMPE",
    "EFETIVADO", "REALIZADA", "TARIFA", "COMPRA", "NACIONAL", "DEBITO",
    "DEBIT", "CREDITO", "CARTAO", "BANCO", "LTDA", "EIRELI", "MATRIZ", "FILIAL",
}


@dataclass(frozen=True)
class TituloAberto:
    id: str
    contraparte: str
    valor: float


@dataclass(frozen=True)
class Movimento:
    descricao: str
    valor: float


def _tokens(texto: str) -> set[str]:
    brutos = re.sub(r"[^A-Z0-9 ]", " ", texto.upper()).split()
    return {t for t in brutos if len(t) >= 4 and t not in BOILERPLATE}


def similaridade(a: str, b: str) -> float:
    """Similaridade sobre os tokens que sobram depois de descontar boilerplate."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()


def casar(
    movimento: Movimento,
    titulos_abertos: list[TituloAberto],
    tolerancia_valor: float = 0.05,
    limiar_similaridade: float = 0.6,
) -> TituloAberto | None:
    """Titulo aberto sempre vence lancamento novo, mesmo quando o valor do
    movimento diverge um pouco do valor previsto -- consumo variavel e o
    normal, nao motivo para descartar o titulo. Dentro dos candidatos por
    valor, o de maior similaridade de nome vence; abaixo do limiar, ambiguo
    demais para decidir sozinho."""
    candidatos = [
        t for t in titulos_abertos
        if abs(abs(t.valor) - abs(movimento.valor)) <= abs(t.valor) * tolerancia_valor
    ]
    if not candidatos:
        return None
    candidatos.sort(key=lambda t: similaridade(movimento.descricao, t.contraparte), reverse=True)
    melhor = candidatos[0]
    if similaridade(movimento.descricao, melhor.contraparte) < limiar_similaridade:
        return None
    return melhor
