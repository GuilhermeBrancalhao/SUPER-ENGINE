from confianca import Confianca, Evidencia, classificar


def test_match_exato_com_nome_forte_e_alta():
    ev = Evidencia(match_exato_valor=True, similaridade_nome=0.9)
    assert classificar(ev) is Confianca.ALTA


def test_historico_forte_promove_a_alta_mesmo_sem_valor_exato():
    ev = Evidencia(
        match_exato_valor=False, similaridade_nome=0.3,
        ocorrencias_historicas=6, dominancia_historica=0.85,
    )
    assert classificar(ev) is Confianca.ALTA


def test_ocorrencia_isolada_nao_vira_regra():
    ev = Evidencia(
        match_exato_valor=False, similaridade_nome=0.3,
        ocorrencias_historicas=1, dominancia_historica=1.0,
    )
    assert classificar(ev) is not Confianca.ALTA


def test_ausencia_de_fonte_de_evidencia_so_pode_rebaixar_nunca_subir():
    """Simula rodar sem a base historica disponivel: ocorrencias ficam em 0 e a
    confianca cai para o nivel que a similaridade de nome sozinha sustenta --
    nunca mais alto do que isso."""
    com_historico = classificar(
        Evidencia(False, 0.3, ocorrencias_historicas=6, dominancia_historica=0.85)
    )
    sem_historico = classificar(
        Evidencia(False, 0.3, ocorrencias_historicas=0, dominancia_historica=0.0)
    )
    ordem = {Confianca.BAIXA: 0, Confianca.MEDIA: 1, Confianca.ALTA: 2}
    assert ordem[sem_historico] <= ordem[com_historico]


def test_baixa_similaridade_sem_match_exato_e_baixa():
    ev = Evidencia(match_exato_valor=False, similaridade_nome=0.1)
    assert classificar(ev) is Confianca.BAIXA


def test_dominancia_fraca_nao_promove_a_alta_mesmo_com_volume_alto():
    """Achado da 3a auditoria: volume alto sozinho nao pode bastar -- e
    preciso volume E dominancia. Ocorrencias altas com dominancia fraca
    (fornecedor aparece muito, mas dividido entre destinos diferentes) nao
    e' historico forte."""
    ev = Evidencia(
        match_exato_valor=False, similaridade_nome=0.3,
        ocorrencias_historicas=6, dominancia_historica=0.3,
    )
    assert classificar(ev) is not Confianca.ALTA
