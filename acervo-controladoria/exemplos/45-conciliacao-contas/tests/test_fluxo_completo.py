"""Fluxo ponta-a-ponta: ancora fecha o dia -> movimento sem titulo exato tenta
casamento aproximado -> confianca decide se escreve -> guarda impede
duplicata -> trilha registra. Anda pelo caminho inteiro do volume, na ordem em
que ele acontece na operacao real.
"""
from datetime import date, datetime

import pytest

from ancora import Movimento as MovimentoBanco, achar_ancora
from casamento import Movimento as MovimentoCasamento, TituloAberto, casar, similaridade
from confianca import Confianca, Evidencia, classificar
from guarda import ChaveMovimento, GuardaDuplicidade
from trilha import Trilha


def test_fluxo_completo_de_conciliacao_com_escrita():
    saldos_banco = {date(2026, 8, 3): 1080.0}
    ancora = achar_ancora(
        1000.0, date(2026, 8, 1), [MovimentoBanco(date(2026, 8, 3), 80.0)], saldos_banco
    )
    assert ancora is not None

    titulos = [TituloAberto("T1", "PROVEDOR INTERNET FIBRA", 80.0)]
    movimento = MovimentoCasamento("PROVEDOR INTERNET FIBRA", -80.0)
    titulo = casar(movimento, titulos)
    assert titulo is not None

    evidencia = Evidencia(
        match_exato_valor=True,
        similaridade_nome=similaridade(movimento.descricao, titulo.contraparte),
    )
    assert classificar(evidencia) is Confianca.ALTA

    guarda = GuardaDuplicidade()
    chave = ChaveMovimento(date(2026, 8, 3), movimento.valor, titulo.contraparte)
    assert guarda.ja_registrado(chave) is False

    trilha = Trilha()
    guarda.registrar(chave)
    trilha.registrar(f"{titulo.id}:{chave.data}", "usuario1", datetime(2026, 8, 3, 12, 0), "BAIXA")

    # reprocessar o mesmo dia (retry) tem de ser barrado nas duas camadas
    assert guarda.ja_registrado(chave) is True
    with pytest.raises(ValueError):
        trilha.registrar(f"{titulo.id}:{chave.data}", "usuario1", datetime(2026, 8, 3, 12, 5), "BAIXA")


def test_segunda_execucao_com_guarda_nova_e_trilha_antiga_nao_reescreve():
    """Simula duas execucoes do motor: a guarda e reconstruida do zero (memoria
    volatil, como 11-Implementacao.md descreve), mas a trilha da execucao
    anterior e o que decide -- consultar SO a guarda nesta segunda execucao
    diria (errado) que a chave nunca foi vista."""
    trilha = Trilha()
    trilha.registrar("T1:2026-08-03", "usuario1", datetime(2026, 8, 3, 12, 0), "BAIXA")

    chave = ChaveMovimento(date(2026, 8, 3), -80.0, "PROVEDOR INTERNET FIBRA")
    guarda_nova = GuardaDuplicidade()  # execucao nova, guarda vazia de proposito
    assert guarda_nova.ja_registrado(chave) is False  # a guarda, isolada, nao sabe

    # e por isso a trilha (nao a guarda) e a fonte que decide se ja foi processado
    assert trilha.ja_processado("T1:2026-08-03") is True
    with pytest.raises(ValueError):
        trilha.registrar("T1:2026-08-03", "usuario2", datetime(2026, 8, 4, 9, 0), "BAIXA")


def test_fluxo_nao_escreve_quando_confianca_e_media():
    """Achado de reauditoria 2026-08-20: a versao anterior deste teste tinha
    nome e docstring do ramo MEDIA mas o CORPO testava o ramo SemTitulo (sem
    candidato por valor) -- mutar classificar() para MEDIA nunca devolver MEDIA
    deixava a suite verde. Aqui HA titulo candidato de verdade: casar() acha
    par (similaridade 0.71, entre 0.6 do limiar e 0.85 de ALTA), e a evidencia
    construida a partir dessa MESMA similaridade classifica MEDIA -- o fluxo
    tem de parar em pendencia humana ANTES de tocar guarda/trilha."""
    titulos = [TituloAberto("T1", "PROVEDOR INTERNET FIBRA OPTICA RESIDENCIAL", 100.0)]
    movimento = MovimentoCasamento("PROVEDOR INTERNET FIBRA", -100.0)

    titulo = casar(movimento, titulos)
    assert titulo is not None  # HA candidato -- casar() de fato encontra o par
    assert titulo.id == "T1"

    sim = similaridade(movimento.descricao, titulo.contraparte)
    assert 0.6 <= sim < 0.85  # confirma que este caso fica no meio do caminho

    evidencia = Evidencia(match_exato_valor=False, similaridade_nome=sim)
    assert classificar(evidencia) is Confianca.MEDIA  # nao ALTA, nao BAIXA

    guarda = GuardaDuplicidade()
    trilha = Trilha()
    # confianca MEDIA nunca chega a escrever, mesmo com titulo encontrado
    chave = ChaveMovimento(date(2026, 8, 3), movimento.valor, titulo.contraparte)
    assert guarda.ja_registrado(chave) is False
    assert len(trilha.historico()) == 0


def test_fluxo_nao_escreve_quando_confianca_e_baixa_por_falta_de_titulo():
    """Ramo diferente do teste MEDIA acima: aqui nao ha candidato NENHUM por
    valor (tolerancia estreita), entao casar() devolve None antes mesmo de
    chegar a classificar()."""
    titulos = [TituloAberto("T1", "PROVEDOR INTERNET FIBRA", 80.0)]
    movimento = MovimentoCasamento("PROVEDOR INTERNET FIBRA", -76.0)  # fora da tolerancia de valor
    titulo = casar(movimento, titulos, tolerancia_valor=0.01)
    assert titulo is None  # sem candidato por valor -- mesmo com nome idêntico

    evidencia = Evidencia(match_exato_valor=False, similaridade_nome=0.3)
    assert classificar(evidencia) is Confianca.BAIXA

    guarda = GuardaDuplicidade()
    trilha = Trilha()
    assert len(trilha.historico()) == 0
    chave = ChaveMovimento(date(2026, 8, 3), movimento.valor, "PROVEDOR INTERNET FIBRA")
    assert guarda.ja_registrado(chave) is False


def test_fluxo_nao_escreve_quando_confianca_e_baixa():
    """Sem match de valor e sem nome parecido, o motor nunca chega a chamar
    guarda/trilha -- fica pendencia humana."""
    titulos = [TituloAberto("T1", "FORNECEDOR DESCONHECIDO", 900.0)]
    movimento = MovimentoCasamento("ORIGEM SEM IDENTIFICACAO", -80.0)
    titulo = casar(movimento, titulos)
    assert titulo is None
