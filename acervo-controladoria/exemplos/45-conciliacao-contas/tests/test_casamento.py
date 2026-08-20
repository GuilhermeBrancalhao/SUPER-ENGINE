import casamento
from casamento import Movimento, TituloAberto, casar, similaridade


def test_casa_por_valor_exato_e_nome_similar():
    aberto = [TituloAberto("T1", "FORNECEDOR AGUA MINERAL LTDA", 500.0)]
    mov = Movimento("PAGTO FORNECEDOR AGUA MINERAL", -500.0)
    assert casar(mov, aberto) is aberto[0]


def test_nao_casa_quando_nao_ha_titulo_no_valor():
    aberto = [TituloAberto("T1", "FORNECEDOR X", 500.0)]
    mov = Movimento("PAGTO FORNECEDOR X", -900.0)
    assert casar(mov, aberto) is None


def test_boilerplate_nao_derruba_a_identificacao_de_fornecedores_diferentes():
    """T1 e o movimento compartilham 11 palavras de boilerplate bancario (todo o
    prefixo generico), diferindo so no nome real do fornecedor; T2 nao tem
    boilerplate nenhum, so o nome real. Sem descontar boilerplate a comparacao
    bruta favorece T1 (muito mais palavra em comum), e o titulo errado venceria
    -- e' exatamente esse cenario que test_boilerplate_e_load_bearing prova
    fazendo o desconto sumir e conferindo que o vencedor muda."""
    aberto = [
        TituloAberto(
            "T1",
            "PAGAMENTO RECEBIMENTO TRANSFERENCIA TARIFA COMPRA NACIONAL "
            "DEBITO CREDITO CARTAO BANCO LTDA PADARIA CENTRAL",
            80.0,
        ),
        TituloAberto("T2", "FARMACIA SAUDE", 80.0),
    ]
    mov = Movimento(
        "PAGAMENTO RECEBIMENTO TRANSFERENCIA TARIFA COMPRA NACIONAL "
        "DEBITO CREDITO CARTAO BANCO LTDA FARMACIA SAUDE",
        -80.0,
    )
    resultado = casar(mov, aberto)
    assert resultado is not None
    assert resultado.id == "T2"


def test_boilerplate_e_load_bearing(monkeypatch):
    """Regressao do achado da auditoria de 2026-08-20: o teste anterior citava
    boilerplate como prova mas passava mesmo com o desconto desligado, porque o
    movimento era identico a T2. Aqui, esvaziar BOILERPLATE muda o vencedor de
    T2 (correto) para T1 (errado) -- e' a prova de que o mecanismo importa."""
    aberto = [
        TituloAberto(
            "T1",
            "PAGAMENTO RECEBIMENTO TRANSFERENCIA TARIFA COMPRA NACIONAL "
            "DEBITO CREDITO CARTAO BANCO LTDA PADARIA CENTRAL",
            80.0,
        ),
        TituloAberto("T2", "FARMACIA SAUDE", 80.0),
    ]
    mov = Movimento(
        "PAGAMENTO RECEBIMENTO TRANSFERENCIA TARIFA COMPRA NACIONAL "
        "DEBITO CREDITO CARTAO BANCO LTDA FARMACIA SAUDE",
        -80.0,
    )
    assert casar(mov, aberto).id == "T2"

    monkeypatch.setattr(casamento, "BOILERPLATE", set())
    assert casar(mov, aberto).id == "T1"


def test_consumo_variavel_ainda_casa_dentro_da_tolerancia():
    aberto = [TituloAberto("T1", "PROVEDOR INTERNET FIBRA", 200.0)]
    mov = Movimento("PROVEDOR INTERNET FIBRA", -204.50)
    assert casar(mov, aberto) is aberto[0]


def test_similaridade_zero_quando_os_dois_lados_sao_so_boilerplate():
    assert similaridade("PAGAMENTO TRANSFERENCIA", "RECEBIMENTO CONTA") == 0.0


def test_limiar_similaridade_e_load_bearing():
    """Achado de reauditoria 2026-08-20: desligar limiar_similaridade nao
    derrubava nenhum teste -- o descarte por ambiguidade nao tinha prova.
    Fornecedores parecidos mas nao identicos ('AGUA MINERAL' vs 'AGUA
    POTAVEL') tem similaridade baixa e nao devem casar por padrao; forcando
    o limiar para 0.0 (o que um mutante que desliga o descarte faria), o
    mesmo par passa a casar -- prova que o parametro decide o resultado."""
    aberto = [TituloAberto("T1", "DISTRIBUIDORA AGUA POTAVEL LTDA", 80.0)]
    mov = Movimento("FORNECEDOR AGUA MINERAL EIRELI", -80.0)

    assert casar(mov, aberto) is None  # ambiguo demais com o limiar padrao (0.6)
    assert casar(mov, aberto, limiar_similaridade=0.0) is aberto[0]  # sem limiar, casaria


def test_filtro_de_token_curto_e_load_bearing():
    """Achado de reauditoria 2026-08-20: o filtro `len(t) >= 4` em `_tokens()`
    nao tinha teste que falhasse se removido. Aqui dois fornecedores bem
    diferentes (LOJA vs MERCADO) só compartilham tokens curtos que não
    identificam nada de fato ('SP', 'AB') -- filtrados, a similaridade cai a
    quase zero e não casa; sem o filtro de tamanho, esses tokens curtos
    bastam para ultrapassar o limiar e casar errado."""
    import re
    from difflib import SequenceMatcher

    aberto = [TituloAberto("T1", "MERCADO SP AB", 80.0)]
    mov = Movimento("LOJA SP AB", -80.0)

    assert casar(mov, aberto) is None  # com o filtro len>=4, tokens curtos nao contam

    def _tokens_sem_filtro_de_tamanho(texto):
        brutos = re.sub(r"[^A-Z0-9 ]", " ", texto.upper()).split()
        return {t for t in brutos if t not in casamento.BOILERPLATE}

    def _similaridade_sem_filtro(a, b):
        ta, tb = _tokens_sem_filtro_de_tamanho(a), _tokens_sem_filtro_de_tamanho(b)
        return SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()

    # reproduz o que um mutante sem o filtro `len(t) >= 4` produziria
    sim_mutante = _similaridade_sem_filtro(mov.descricao, aberto[0].contraparte)
    assert sim_mutante >= 0.6  # ultrapassaria o limiar por acidente, via "SP"/"AB"
