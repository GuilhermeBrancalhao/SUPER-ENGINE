"""Cobre o bug real encontrado ao rodar normalizar.py contra um CSV de
producao (DIGIO, janeiro/2026): duas colunas do banco casam com o padrao
"comiss" no nome -- "% da Comissao" e "Valor Comiss" -- e a versao antiga
pegava a primeira que aparecesse no CSV, escolhendo o percentual.

A causa raiz era mais funda: toda coluna monetaria de banco brasileiro
chega como texto com virgula decimal ('886,39'), entao o filtro antigo
por `is_numeric_dtype` excluia essas colunas dos candidatos e so sobravam
colunas numericas vazias (100% NaN) -- cuja soma, por padrao do pandas
(skipna), da 0,00 e nao NaN. Isso fazia a validacao de soma "passar"
comparando vazio com vazio.
"""
from pathlib import Path

import pandas as pd

from normalizar import Normalizador


def _normalizador_com(df: pd.DataFrame) -> Normalizador:
    n = Normalizador("arquivo-fake.csv", "BANCO-TESTE")
    n.df_original = df
    return n


def test_para_numerico_converte_formato_brasileiro():
    serie = pd.Series(["886,39", "109,48", "1.528,36"])
    convertida = Normalizador._para_numerico(serie)
    assert convertida.tolist() == [886.39, 109.48, 1528.36]


def test_para_numerico_preserva_coluna_ja_numerica():
    serie = pd.Series([886.39, 109.48])
    convertida = Normalizador._para_numerico(serie)
    assert convertida.tolist() == [886.39, 109.48]


def test_para_numerico_no_dtype_str_nativo_do_pandas_recente():
    """dtype 'str' (nao o 'object' classico) escapava de um filtro
    `dtype == object` e a coluna virava all-NaN por engano -- bug real
    reproduzido rodando contra CSV do DIGIO nesta maquina."""
    serie = pd.Series(["886,39", "109,48"], dtype="str")
    convertida = Normalizador._para_numerico(serie)
    assert convertida.notna().all()
    assert convertida.tolist() == [886.39, 109.48]


def test_coluna_100_por_cento_vazia_nao_vira_candidata():
    df = pd.DataFrame({"Valor Comiss": ["886,39", "109,48"]})
    n = _normalizador_com(df)
    assert n._coluna_numerica_candidata("Valor Comiss") is not None

    df_vazio = pd.DataFrame({"Comissionado Origem Reat.": [float("nan"), float("nan")]})
    n_vazio = _normalizador_com(df_vazio)
    assert n_vazio._coluna_numerica_candidata("Comissionado Origem Reat.") is None


def test_escolhe_valor_comissao_e_nao_o_percentual():
    """Reproduz o caso real do DIGIO: '% da Comissao' e 'Valor Comiss'
    casam no mesmo padrao de nome. A escolha certa e a que tem 'valor'
    no nome, nao a primeira que aparece na ordem das colunas."""
    df = pd.DataFrame({
        "Oper.": [500003141261, 500003141425],
        "Data Base": ["02/01/2026", "02/01/2026"],
        "% da Comissao": [3.0, 3.0],
        "Valor Comiss": ["886,39", "109,48"],
    })
    n = _normalizador_com(df)
    n.detectar_colunas()

    assert n.deteccoes["comissao"] == "Valor Comiss"
    assert n.deteccoes["pcl_comissao"] == "% da Comissao"


def test_mapeamento_grava_valor_correto_nao_o_percentual():
    df = pd.DataFrame({
        "Oper.": [500003141261, 500003141425],
        "Data Base": ["02/01/2026", "02/01/2026"],
        "% da Comissao": [3.0, 3.0],
        "Valor Comiss": ["886,39", "109,48"],
    })
    n = _normalizador_com(df)
    n.detectar_colunas()
    n.mapear_para_padrao()

    assert n.df_processado["VAL_COMISSAO"].tolist() == [886.39, 109.48]
    assert n.df_processado["PCL_COMISSAO"].tolist() == [3.0, 3.0]


def test_mapeamento_preenche_num_banco_e_nom_banco(tmp_path):
    """Achado de auditoria 2026-08-20: df_processado nascia sem indice (0
    linhas), e as atribuicoes escalares NUM_BANCO=999/NOM_BANCO=nome_banco
    nao tinham onde fazer broadcast -- as duas colunas saiam sempre NaN,
    mesmo passando um nome de banco real."""
    df = pd.DataFrame({
        "Oper.": [500003141261, 500003141425],
        "Data Base": ["02/01/2026", "02/01/2026"],
        "Valor Comiss": ["886,39", "109,48"],
    })
    n = _normalizador_com(df)
    n.nome_banco = "DIGIO"
    n.detectar_colunas()
    n.mapear_para_padrao()

    assert n.df_processado["NOM_BANCO"].tolist() == ["DIGIO", "DIGIO"]
    assert n.df_processado["NUM_BANCO"].tolist() == [999, 999]


def test_valor_bruto_nao_reusa_a_coluna_ja_escolhida_como_comissao():
    """Achado de auditoria 2026-08-20: se so existe uma coluna com 'valor' no
    nome, ela era detectada como COMISSAO e, na deteccao de VALOR BRUTO (que
    tambem procura 'valor' no nome), a MESMA coluna era escolhida de novo --
    VAL_BRUTO saia identico a VAL_COMISSAO em silencio."""
    df = pd.DataFrame({
        "Oper.": [500003141261, 500003141425],
        "Data Base": ["02/01/2026", "02/01/2026"],
        "Valor Comiss": ["886,39", "109,48"],
    })
    n = _normalizador_com(df)
    n.detectar_colunas()

    assert n.deteccoes["comissao"] == "Valor Comiss"
    assert n.deteccoes["valor_bruto"] is None  # nao ha outra coluna de valor


def test_validar_recalcula_soma_do_original_e_nao_so_compara_o_cache_com_ele_mesmo():
    """Achado de auditoria 2026-08-20: a validacao antiga comparava
    self._series_numericas[...] com ela mesma (sempre bate por definicao).
    Mutando o cache depois do mapeamento (simulando um bug de desalinhamento
    de indice em outro ponto do codigo), a validacao tem de continuar
    olhando para o CSV original, nao para o cache, e reprovar."""
    df = pd.DataFrame({
        "Oper.": [500003141261, 500003141425],
        "Data Base": ["02/01/2026", "02/01/2026"],
        "Valor Comiss": ["886,39", "109,48"],
    })
    n = _normalizador_com(df)
    n.detectar_colunas()
    n.mapear_para_padrao()

    # simula desalinhamento: o cache diz uma coisa, o CSV original diz outra --
    # mutar SO o cache nao muda mais o resultado, porque validar() nao le o cache
    n._series_numericas["Valor Comiss"] = pd.Series([9999.99, 9999.99])
    assert n.validar() is True  # continua batendo porque df_processado == df_original

    # mas se o PROCESSADO de fato divergir do original, a validacao pega
    n.df_processado["VAL_COMISSAO"] = pd.Series([1.0, 1.0])
    assert n.validar() is False


def test_dat_credito_nao_troca_dia_por_mes(tmp_path):
    """Achado de auditoria 2026-08-20: sem dayfirst=True, pandas assume
    mm/dd/aaaa (padrao americano) e 03/01/2026 (3 de janeiro, formato
    brasileiro) virava 1 de marco em silencio -- e qualquer dia >12
    (formato so existe em dd/mm) levantava ValueError e abortava a deteccao
    de coluna de data inteira."""
    df = pd.DataFrame({
        "Oper.": [1, 2],
        "Data Base": ["03/01/2026", "15/01/2026"],  # dia 15 so existe em dd/mm
        "Valor Comiss": ["886,39", "109,48"],
    })
    n = _normalizador_com(df)
    n.detectar_colunas()
    assert n.deteccoes["data"] == "Data Base"  # nao aborta com dia > 12

    n.mapear_para_padrao()
    datas = n.df_processado["DAT_CREDITO"].tolist()
    assert datas == ["03/01/2026", "15/01/2026"]  # dia preservado, nao virou mes


def test_terceira_coluna_de_comissao_nao_vaza_para_valor_bruto():
    """Achado de auditoria 2026-08-20: com 3+ colunas casando 'comiss' no
    nome, so as 2 primeiras (comissao + pcl_comissao) eram excluidas da
    deteccao de VALOR BRUTO -- a terceira virava VAL_BRUTO por acidente."""
    df = pd.DataFrame({
        "Oper.": [1, 2],
        "Data Base": ["02/01/2026", "02/01/2026"],
        "% da Comissao": [3.0, 3.0],
        "Vl Comiss Extra": [500.0, 600.0],
        "Valor Comiss": ["886,39", "109,48"],
    })
    n = _normalizador_com(df)
    n.detectar_colunas()

    assert n.deteccoes["valor_bruto"] is None  # nenhuma coluna de comissao vaza
    # residuo conhecido (3a auditoria): decide por ordem de coluna, nao por
    # conteudo -- documenta o comportamento em vez de deixa-lo sem asserção
    assert n.deteccoes["comissao"] == "Vl Comiss Extra"


def test_executar_reporta_exit_code_diferente_quando_validacao_reprova(tmp_path, monkeypatch):
    """Achado de auditoria 2026-08-20: a CLI chamava validar() e descartava
    o retorno, salvando o XLSX e saindo com codigo 0 mesmo com avisos reais
    de validacao -- 'salvou' e 'salvou validado' pareciam a mesma coisa."""
    csv = tmp_path / "real.csv"
    csv.write_text("Oper.;Data Base;Valor Comiss\n1;02/01/2026;886,39\n", encoding="utf-8")

    n = Normalizador(str(csv), "TESTE")
    monkeypatch.setattr(n, "validar", lambda: False)  # simula reprovacao real

    saida, validado = n.executar(str(tmp_path / "saida.xlsx"))
    assert saida is not None  # salvou mesmo assim -- resultado parcial ainda e util
    assert validado is False  # mas o chamador (main()) agora sabe que reprovou


def test_cli_sai_com_codigo_2_quando_validacao_reprova(tmp_path):
    """Achado da 3a auditoria: o teste acima cobre so o retorno de
    executar(), nunca o sys.exit(2) de main() -- roda a CLI de verdade,
    via subprocess, com uma comissao negativa (reprova validar())."""
    import subprocess
    import sys as _sys

    csv = tmp_path / "negativa.csv"
    csv.write_text(
        "Oper.;Data Base;Valor Comiss\n1;02/01/2026;-886,39\n", encoding="utf-8"
    )
    modulo = Path(__file__).resolve().parent.parent / "normalizar.py"

    resultado = subprocess.run(
        [_sys.executable, str(modulo), str(csv), "TESTE",
         "--output", str(tmp_path / "saida.xlsx")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert resultado.returncode == 2


def test_cli_repassa_sep_e_encoding_para_ler_csv(tmp_path):
    """Achado da 3a auditoria: --sep/--encoding eram parseados pelo argparse
    e nunca chegavam a ler_csv() -- a CLI os aceitava e os ignorava em
    silencio. Roda a CLI de verdade com um CSV latin-1 separado por '|'."""
    import subprocess
    import sys as _sys

    linha = "Oper.|Data Base|Valor Comiss\n1|02/01/2026|886,39\n"
    csv = tmp_path / "latin1_pipe.csv"
    csv.write_bytes(linha.encode("latin-1"))
    modulo = Path(__file__).resolve().parent.parent / "normalizar.py"

    resultado = subprocess.run(
        [_sys.executable, str(modulo), str(csv), "TESTE",
         "--sep", "|", "--encoding", "latin-1",
         "--output", str(tmp_path / "saida.xlsx")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert resultado.returncode in (0, 2)  # rodou o fluxo -- nao travou na leitura
    assert "Erro" not in (resultado.stdout or "")


def test_ler_csv_com_bom_e_separador_ponto_e_virgula_nao_fica_em_1_coluna(tmp_path):
    """Bug real do arquivo de julho do DIGIO: BOM UTF-8 no inicio do
    arquivo, separador ';'. `pd.read_csv(encoding='utf-8')` sem `sep`
    explicito nao levanta excecao nesse caso - aceita a linha inteira
    como uma unica coluna, com nome faltando ';'. A deteccao antiga so
    era acionada por excecao, e aqui nao havia nenhuma: o arquivo virava
    2 colunas em vez de ~29, em silencio."""
    conteudo = "Tp. Lnc;Prop.;Valor Comiss\nA;500003141261;886,39\n"
    arquivo = tmp_path / "digio_com_bom.csv"
    arquivo.write_bytes(b"\xef\xbb\xbf" + conteudo.encode("utf-8"))

    n = Normalizador(str(arquivo), "DIGIO")
    df = n.ler_csv()

    assert list(df.columns) == ["Tp. Lnc", "Prop.", "Valor Comiss"]
    assert df["Valor Comiss"].tolist() == ["886,39"]


def test_ler_csv_sem_bom_com_separador_ponto_e_virgula_ainda_funciona(tmp_path):
    """Mesmo caso sem BOM - a deteccao por contagem de separador nao pode
    regredir o caminho que ja funcionava antes da correcao."""
    conteudo = "Tp. Lnc;Prop.;Valor Comiss\nA;500003141261;886,39\n"
    arquivo = tmp_path / "digio_sem_bom.csv"
    arquivo.write_text(conteudo, encoding="utf-8")

    n = Normalizador(str(arquivo), "DIGIO")
    df = n.ler_csv()

    assert list(df.columns) == ["Tp. Lnc", "Prop.", "Valor Comiss"]


def test_ler_csv_com_virgula_continua_funcionando(tmp_path):
    """Separador ',' e o caso mais comum - a deteccao por contagem nao
    pode quebrar o caminho feliz de um CSV convencional."""
    conteudo = "Prop.,Valor Comiss\n500003141261,886.39\n"
    arquivo = tmp_path / "convencional.csv"
    arquivo.write_text(conteudo, encoding="utf-8")

    n = Normalizador(str(arquivo), "BANCO-TESTE")
    df = n.ler_csv()

    assert list(df.columns) == ["Prop.", "Valor Comiss"]


def test_validar_trava_se_coluna_de_comissao_ficar_vazia():
    """Insurance direta contra o falso-positivo real: soma de coluna
    100% NaN da 0,00 no pandas (skipna por padrao), nao NaN -- sem este
    guard, 0,00 contra 0,00 'validaria' uma comissao que nao existe."""
    df = pd.DataFrame({"Oper.": [1, 2], "Data Base": ["02/01/2026", "02/01/2026"]})
    n = _normalizador_com(df)
    n.deteccoes = {"comissao": "Fantasma", "pcl_comissao": None, "proposta": "Oper."}
    n._series_numericas["Fantasma"] = pd.Series([float("nan"), float("nan")])
    n.df_processado = pd.DataFrame({
        "NUM_PROPOSTA": [1, 2],
        "VAL_COMISSAO": [float("nan"), float("nan")],
    })

    assert n.validar() is False
