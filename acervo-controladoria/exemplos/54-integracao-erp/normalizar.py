#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalizar CSV de banco para modelo PROCESSADO padrão (XLSX)

Uso:
    python normalizar.py <arquivo.csv> <nome_banco> [--output <saida.xlsx>]

Exemplo:
    python normalizar.py "DIGIO - 110075 01.07.csv" "DIGIO" --output "DIGIO - 01-07 - PROCESSADO.xlsx"
"""

import pandas as pd
import sys
import re
from pathlib import Path
from datetime import datetime
import argparse

# Console do Windows nao roda em UTF-8 por padrao (cp1252/cp850) -- os emojis
# nos prints deste modulo levantavam UnicodeEncodeError mesmo para quem so
# importa a classe (ex.: `from normalizar import Normalizador; n.ler_csv()`),
# nao so para quem roda via CLI. Achado de auditoria 2026-08-20: a correcao
# anterior vivia so dentro de main() e nao protegia esse caminho. errors=
# 'replace' garante que a normalizacao em si nunca falha por causa de print.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class Normalizador:
    """Converte CSV de banco para modelo PROCESSADO padrão."""

    # Colunas do modelo PROCESSADO
    COLUNAS_PADRAO = [
        'NUM_BANCO', 'NOM_BANCO', 'NUM_PROPOSTA', 'NUM_CONTRATO', 'NOM_CLIENTE',
        'COD_CPF_CLIENTE', 'DSC_PRODUTO', 'DSC_SITUACAO_BANCO', 'DSC_OBSERVACAO',
        'DAT_CREDITO', 'VAL_BRUTO', 'VAL_LIQUIDO', 'VAL_SALDO_REFINANCIAMENTO',
        'VAL_BASE_COMISSAO', 'VAL_COMISSAO', 'PCL_COMISSAO', 'DSC_TIPO_COMISSAO',
        'COD_LOJA', 'COD_UNIDADE_EMPRESA', 'COD_BANCO', 'COD_TIPO_PROPOSTA_EMPRESTIMO',
        'DSC_TIPO_PROPOSTA_EMPRESTIMO', 'NIC_CTR_USUARIO', 'COD_PRODUTO',
        'COD_PRODUTOR_VENDA', 'COD_PRODUTOR_VENDA_BANCO', 'COD_TIPO_COMISSAO',
        'COD_SITUACAO_EMPRESTIMO', 'QTD_PARCELA', 'NUM_PARCELA_DIFERIDA_EMPRESA',
        'DAT_EMPRESTIMO', 'DAT_CONFIRMACAO', 'DAT_ESTORNO', 'DAT_CTR_INCLUSAO',
        'TIPO_COMISSAO_BANCO', 'PCL_TAXA_EMPRESTIMO'
    ]

    def __init__(self, arquivo_csv, nome_banco):
        """Inicializa com caminho do CSV e nome do banco."""
        self.arquivo_csv = Path(arquivo_csv)
        self.nome_banco = nome_banco
        self.df_original = None
        self.df_processado = None
        self.deteccoes = {}
        self._series_numericas = {}  # coluna original -> série já convertida para número

    def _detectar_separador(self, encoding):
        """Espia a primeira linha do arquivo e decide o separador por
        contagem de ocorrência, não só presença - ';' pode aparecer dentro
        de um valor de texto mesmo quando ',' é o separador real."""
        with open(self.arquivo_csv, 'r', encoding=encoding, errors='ignore') as f:
            primeira_linha = f.readline()

        contagens = {c: primeira_linha.count(c) for c in (';', ',', '\t')}
        separador = max(contagens, key=contagens.get)
        if contagens[separador] == 0:
            raise ValueError("Não consegui detectar separador. Use --sep")
        return separador

    def ler_csv(self, encoding='utf-8-sig', separador=None):
        """Lê CSV detectando separador automaticamente.

        `utf-8-sig` como padrão (não `utf-8`) faz o próprio decodificador
        descartar o BOM quando presente, e se comporta como UTF-8 comum
        quando ausente - não custa nada no caso sem BOM, evita reler o
        arquivo no caso com.
        """
        print(f"📖 Lendo {self.arquivo_csv.name}...", end=" ")

        def _tentar(enc, sep):
            kwargs = {'encoding': enc}
            if sep:
                kwargs['sep'] = sep
            return pd.read_csv(self.arquivo_csv, **kwargs)

        try:
            self.df_original = _tentar(encoding, separador)
        except UnicodeDecodeError:
            print(f"\n  UTF-8 falhou, tentando Latin-1...", end=" ")
            encoding = 'latin-1'
            self.df_original = _tentar(encoding, separador)
        except (ValueError, TypeError):
            if separador:
                raise
            print(f"\n  Detectando separador...", end=" ")
            separador = self._detectar_separador(encoding)
            print(f"'{separador}'", end=" ")
            self.df_original = _tentar(encoding, separador)

        # Uma leitura com separador errado nem sempre levanta excecao: sem
        # ',' no arquivo, pd.read_csv aceita a linha inteira como 1 coluna
        # e devolve normalmente - foi exatamente esse silencio que deixou
        # passar um CSV real (separador ';') sendo lido como 2 colunas em
        # vez de ~29, sem nunca acionar a deteccao acima.
        if len(self.df_original.columns) <= 1 and not separador:
            print(f"\n  1 coluna e implausivel, detectando separador...", end=" ")
            separador = self._detectar_separador(encoding)
            print(f"'{separador}'", end=" ")
            self.df_original = _tentar(encoding, separador)

        print(f"✓ ({len(self.df_original)} linhas, {len(self.df_original.columns)} colunas)")
        return self.df_original

    @staticmethod
    def _para_numerico(serie):
        """Converte uma série para número, aceitando formato brasileiro
        (ponto de milhar, vírgula decimal: '1.234,56'). Colunas já
        numéricas passam direto.

        Sem isso, toda coluna monetária de banco brasileiro ('886,39')
        chega como texto e cai fora de qualquer detecção baseada em
        is_numeric_dtype - foi o que escondeu 'Valor Comiss' e deixou
        colunas vazias (dtype numérico, mas 100% NaN) como únicas
        candidatas "numéricas" no CSV real.
        """
        if pd.api.types.is_numeric_dtype(serie):
            return serie

        # astype(str) funciona para qualquer dtype (inclusive o dtype
        # 'str' nativo do pandas recente, que não é 'object' clássico
        # e por isso escapava de um filtro `dtype == object`). Valor
        # genuinamente não numérico (data, texto) vira NaN no to_numeric
        # abaixo e é descartado normalmente pelo chamador.
        texto = serie.astype(str).str.strip()

        direto = pd.to_numeric(texto, errors='coerce')
        if direto.notna().sum() >= texto.notna().sum() * 0.9:
            return direto

        formato_br = pd.to_numeric(
            texto.str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
            errors='coerce'
        )
        return formato_br

    def _coluna_numerica_candidata(self, col):
        """Série convertida para número se a coluna tiver valor de fato;
        None se vier vazia (100% NaN) ou não for conversível.

        Uma coluna 100% NaN não pode virar candidata - é exatamente o
        caso real do CSV DIGIO, onde '% da Comissão' e outra coluna
        numérica vazia passavam no `is_numeric_dtype` antigo e a soma
        de uma coluna vazia contra ela mesma "validava" com 0,00.
        """
        convertida = self._para_numerico(self.df_original[col])
        return convertida if convertida.notna().any() else None

    def _escolher_valor_comissao(self, candidatos):
        """Entre colunas candidatas a COMISSÃO, escolhe a de valor pago
        (não percentual). `candidatos` é {nome_coluna: série_numérica}.
        Retorna (escolhida, descartada_como_percentual).

        Critério de desempate, do mais para o menos confiável:
        1. Nome com '%'/'pcl'/'percent'/'taxa' é percentual, descarta.
        2. Nome com 'valor'/'vl'/'montante' é o valor pago, prioriza.
        3. Magnitude: percentual de comissão fica em 0-100; valor pago,
           via de regra, não. Sobra a de maior amplitude.
        """
        nomes = list(candidatos.keys())
        if len(nomes) == 1:
            return nomes[0], None

        def eh_nome_percentual(col):
            col_lower = col.lower()
            return any(x in col_lower for x in ['%', 'pcl', 'percent', 'taxa'])

        sem_percentual = [c for c in nomes if not eh_nome_percentual(c)]
        percentuais = [c for c in nomes if eh_nome_percentual(c)]

        if len(sem_percentual) == 1:
            return sem_percentual[0], (percentuais[0] if percentuais else None)

        restantes = sem_percentual or nomes

        com_valor = [c for c in restantes if any(
            x in c.lower() for x in ['valor', 'vl', 'montante']
        )]
        if len(com_valor) == 1:
            outros = [c for c in restantes if c != com_valor[0]]
            return com_valor[0], (outros[0] if outros else None)
        if com_valor:
            restantes = com_valor

        if len(restantes) == 1:
            outros = [c for c in nomes if c != restantes[0]]
            return restantes[0], (outros[0] if outros else None)

        def parece_percentual_por_valor(col):
            serie = candidatos[col].dropna()
            return not serie.empty and serie.max() <= 100 and serie.min() >= 0

        nao_percentuais = [c for c in restantes if not parece_percentual_por_valor(c)]
        if nao_percentuais:
            escolhida = nao_percentuais[0]
        else:
            # Todas ficam em 0-100 - fica com a de maior amplitude,
            # mais provável de ser valor monetário (mesmo que pequeno)
            escolhida = max(restantes, key=lambda c: candidatos[c].max())

        outros = [c for c in nomes if c != escolhida]
        return escolhida, (outros[0] if outros else None)

    def detectar_colunas(self):
        """Detecta automaticamente as colunas críticas."""
        print("\n🔍 Detectando colunas críticas...")

        if self.df_original is None:
            raise ValueError("Primeiro chame ler_csv()")

        cols = self.df_original.columns
        self.deteccoes = {
            'comissao': None,
            'pcl_comissao': None,
            'data': None,
            'proposta': None,
            'valor_bruto': None,
            'base_comissao': None,
            'status': None,
            'tipo_comissao': None
        }

        # Detectar COMISSÃO
        # "% da Comissão" e "Valor Comiss" casam no mesmo padrão de nome
        # (os dois têm "comiss"). Pegar o primeiro que aparecer no CSV
        # sem desempatar já causou o bug real: escolheu o percentual,
        # e a validação de soma bateu comparando a coluna com ela mesma.
        candidatos_comissao = {}
        for col in cols:
            if any(x in col.lower() for x in ['comiss', 'commission', 'incentiv', 'fee', 'vl_comiss']):
                serie = self._coluna_numerica_candidata(col)
                if serie is not None:
                    candidatos_comissao[col] = serie

        if candidatos_comissao:
            escolhida, descartada = self._escolher_valor_comissao(candidatos_comissao)
            self.deteccoes['comissao'] = escolhida
            self.deteccoes['pcl_comissao'] = descartada
            self._series_numericas[escolhida] = candidatos_comissao[escolhida]
            if descartada:
                self._series_numericas[descartada] = candidatos_comissao[descartada]
            print(f"  ✓ Comissão: {escolhida}")
            if descartada:
                print(f"    (descartado como percentual: {descartada})")
        else:
            # Fallback: se nenhuma coluna casou com "comiss", tentar "valor" genérico
            # mas excluir colunas óbvias de contexto diferente (valor_bruto, valor_operacao)
            for col in cols:
                col_lower = col.lower()
                if (col_lower in ['valor', 'value', 'amount', 'vl', 'vl_commission', 'vl_comissao'] or
                    (col_lower.endswith('valor') and not any(x in col_lower for x in ['bruto', 'operacao', 'banco']))):
                    serie = self._coluna_numerica_candidata(col)
                    if serie is not None:
                        self.deteccoes['comissao'] = col
                        self._series_numericas[col] = serie
                        print(f"  ✓ Comissão: {col} (fallback genérico)")
                        break

        # Detectar DATA
        for col in cols:
            col_lower = col.lower()
            if any(x in col_lower for x in ['data', 'date', 'dt.', 'data_']):
                # Tentar converter para data
                # dayfirst=True: banco brasileiro exporta dd/mm/aaaa, e sem isso
                # pandas assume mm/dd/aaaa por padrao -- dia e mes trocados em
                # silencio para dia<=12, e ValueError para dia>12 (achado de
                # auditoria 2026-08-20: qualquer arquivo cobrindo um mes real
                # tem dia >12 em alguma linha e a deteccao falhava).
                try:
                    pd.to_datetime(self.df_original[col], dayfirst=True)
                    self.deteccoes['data'] = col
                    print(f"  ✓ Data: {col}")
                    break
                except (ValueError, TypeError):
                    pass

        # Detectar PROPOSTA (ID único)
        for col in cols:
            col_lower = col.lower()
            if any(x in col_lower for x in ['prop', 'operaç', 'oper', 'id', 'numero', 'contract', 'op_id', 'transaction_id']):
                # Validar se tem valores únicos
                if self.df_original[col].nunique() >= len(self.df_original) * 0.9:  # 90% únicos
                    self.deteccoes['proposta'] = col
                    print(f"  ✓ Proposta: {col}")
                    break

        # Detectar VALOR BRUTO
        # Exclui explicitamente a(s) coluna(s) ja usada(s) por COMISSAO: a mesma
        # coluna casando em duas deteccoes deixaria VAL_BRUTO == VAL_COMISSAO em
        # silencio (achado de auditoria 2026-08-20) -- ambas colunas frequentemente
        # tem "valor"/"vl" no nome.
        # Exclui TODAS as colunas candidatas a comissao (nao so as duas que
        # deteccoes rastreia) -- com 3+ colunas "comiss" no CSV, a terceira
        # vazava para VAL_BRUTO em silencio (achado de auditoria 2026-08-20).
        ja_usadas = set(candidatos_comissao.keys()) | {
            self.deteccoes.get('comissao'), self.deteccoes.get('pcl_comissao')
        }
        for col in cols:
            if col in ja_usadas:
                continue
            col_lower = col.lower()
            if any(x in col_lower for x in ['valor', 'value', 'vl', 'bruto', 'liquido', 'amount']):
                serie = self._coluna_numerica_candidata(col)
                if serie is not None:
                    self.deteccoes['valor_bruto'] = col
                    self._series_numericas[col] = serie
                    print(f"  ✓ Valor Bruto: {col}")
                    break

        # Detectar BASE COMISSÃO
        for col in cols:
            col_lower = col.lower()
            if any(x in col_lower for x in ['base', 'calculo']):
                serie = self._coluna_numerica_candidata(col)
                if serie is not None:
                    self.deteccoes['base_comissao'] = col
                    self._series_numericas[col] = serie
                    print(f"  ✓ Base Comissão: {col}")
                    break

        # Detectar STATUS
        for col in cols:
            col_lower = col.lower()
            if any(x in col_lower for x in ['status', 'situação', 'sit', 'estado', 'state']):
                self.deteccoes['status'] = col
                print(f"  ✓ Status: {col}")
                break

        # Detectar TIPO COMISSÃO
        for col in cols:
            col_lower = col.lower()
            if any(x in col_lower for x in ['tipo', 'type', 'categoria']):
                self.deteccoes['tipo_comissao'] = col
                print(f"  ✓ Tipo Comissão: {col}")
                break

        # Validar que foi detectado o mínimo
        if not self.deteccoes['comissao']:
            raise ValueError("❌ Não consegui detectar coluna de COMISSÃO")
        if not self.deteccoes['data']:
            raise ValueError("❌ Não consegui detectar coluna de DATA")
        if not self.deteccoes['proposta']:
            raise ValueError("❌ Não consegui detectar coluna de PROPOSTA")

        print(f"\n  ⚠️  Não detectadas: {[k for k,v in self.deteccoes.items() if not v]}")
        return self.deteccoes

    def mapear_para_padrao(self):
        """Mapeia colunas detectadas para o modelo PROCESSADO."""
        print("\n🔄 Mapeando para modelo padrão...")

        if not self.deteccoes['comissao']:
            raise ValueError("Primeiro chame detectar_colunas()")

        # Inicializar DataFrame padrão com o MESMO indice de df_original -- um
        # DataFrame sem indice (0 linhas) faz atribuicao escalar (NUM_BANCO=999,
        # NOM_BANCO=nome_banco) virar NaN em silencio, porque nao ha linha para
        # broadcast (achado de auditoria 2026-08-20: NUM_BANCO/NOM_BANCO saiam
        # sempre vazios).
        self.df_processado = pd.DataFrame(
            index=self.df_original.index, columns=self.COLUNAS_PADRAO
        )

        # Mapear valores
        # Banco
        self.df_processado['NUM_BANCO'] = 999  # Placeholder
        self.df_processado['NOM_BANCO'] = self.nome_banco

        # IDs
        self.df_processado['NUM_PROPOSTA'] = self.df_original[self.deteccoes['proposta']]
        self.df_processado['NUM_CONTRATO'] = self.df_original[self.deteccoes['proposta']]  # Usar proposta como contrato

        # Datas (dayfirst=True -- ver deteccao acima; a MESMA opcao tem de valer
        # aqui, senao o parse que decidiu que a coluna e valida na deteccao usa
        # uma regra diferente do parse que grava o valor final)
        self.df_processado['DAT_CREDITO'] = pd.to_datetime(
            self.df_original[self.deteccoes['data']], dayfirst=True
        ).dt.strftime('%d/%m/%Y')

        # Valores (usa a série já convertida para número - a coluna crua
        # do CSV brasileiro vem como texto '886,39', não como float)
        self.df_processado['VAL_COMISSAO'] = self._series_numericas[self.deteccoes['comissao']]

        if self.deteccoes['pcl_comissao']:
            self.df_processado['PCL_COMISSAO'] = self._series_numericas[self.deteccoes['pcl_comissao']]

        if self.deteccoes['valor_bruto']:
            self.df_processado['VAL_BRUTO'] = self._series_numericas[self.deteccoes['valor_bruto']]

        if self.deteccoes['base_comissao']:
            self.df_processado['VAL_BASE_COMISSAO'] = self._series_numericas[self.deteccoes['base_comissao']]

        # Status
        if self.deteccoes['status']:
            self.df_processado['DSC_SITUACAO_BANCO'] = self.df_original[self.deteccoes['status']]

        if self.deteccoes['tipo_comissao']:
            self.df_processado['TIPO_COMISSAO_BANCO'] = self.df_original[self.deteccoes['tipo_comissao']]

        print(f"  ✓ Mapeadas {len(self.df_processado)} linhas")
        return self.df_processado

    def validar(self):
        """Valida a transformação."""
        print("\n✅ Validando...")

        if self.df_processado is None:
            raise ValueError("Primeiro chame mapear_para_padrao()")

        erros = []

        # Validação 0: coluna de comissão não pode estar vazia.
        # .sum() de uma série 100% NaN dá 0,00 (skipna por padrão) e
        # bateria "igual" contra si mesma sem que exista comissão real -
        # foi o falso-positivo real visto ao rodar contra um CSV DIGIO.
        comissao_vazia = self.df_processado['VAL_COMISSAO'].isna().all()
        if comissao_vazia:
            erros.append("  ❌ Coluna de comissão detectada está vazia (100% NaN)")

        # Validação 1: Total de comissão (pulada se a Validação 0 já reprovou --
        # comparar soma de coluna vazia não acrescenta nada, e nos testes que
        # simulam esse cenário sintético a coluna nem existe em df_original)
        # Recalcula a partir do CSV bruto (df_original), NAO do cache
        # self._series_numericas -- comparar a serie cacheada contra ela mesma
        # (o bug original) sempre bate por definicao, mesmo se mapear_para_padrao
        # tivesse copiado a coluna errada (achado de auditoria 2026-08-20). Esta
        # comparacao pega mutacao/desalinhamento de indice entre a deteccao e o
        # mapeamento; nao pega "coluna errada escolhida em detectar_colunas()" --
        # isso e responsabilidade de _escolher_valor_comissao(), nao desta validacao.
        if not comissao_vazia:
            total_original = self._para_numerico(
                self.df_original[self.deteccoes['comissao']]
            ).sum()
            total_processado = self.df_processado['VAL_COMISSAO'].sum()

            if abs(total_original - total_processado) > 0.01:
                erros.append(f"  ❌ Soma de comissão não bate: {total_original} → {total_processado}")
            else:
                print(f"  ✓ Soma de comissão OK: {total_original:,.2f}")

        # Validação 2: Contagem de linhas
        if len(self.df_original) != len(self.df_processado):
            erros.append(f"  ❌ Número de linhas: {len(self.df_original)} → {len(self.df_processado)}")
        else:
            print(f"  ✓ Número de linhas OK: {len(self.df_processado)}")

        # Validação 3: Duplicatas
        dups = self.df_processado['NUM_PROPOSTA'].duplicated().sum()
        if dups > 0:
            erros.append(f"  ⚠️  {dups} propostas duplicadas")
        else:
            print(f"  ✓ Sem propostas duplicadas")

        # Validação 4: Valores negativos
        negs = (self.df_processado['VAL_COMISSAO'] < 0).sum()
        if negs > 0:
            erros.append(f"  ⚠️  {negs} comissões negativas")
        else:
            print(f"  ✓ Sem comissões negativas")

        if erros:
            print("\n⚠️  Avisos de validação:")
            for err in erros:
                print(err)

        return len(erros) == 0

    def salvar_xlsx(self, output_path=None):
        """Salva o DataFrame processado como XLSX."""
        if self.df_processado is None:
            raise ValueError("Primeiro chame mapear_para_padrao()")

        if output_path is None:
            output_path = self.arquivo_csv.with_suffix('.xlsx').name
            output_path = self.arquivo_csv.parent.parent / 'PROCESSADOS' / f"{self.nome_banco} - PROCESSADO.xlsx"

        print(f"\n💾 Salvando em {output_path}...", end=" ")
        self.df_processado.to_excel(output_path, index=False, engine='openpyxl')
        print("✓")

        return output_path

    def executar(self, output_path=None, separador=None, encoding='utf-8-sig'):
        """Executa o fluxo completo de normalização.

        Salva o XLSX mesmo quando validar() reprova -- o resultado parcial
        continua util para inspecao manual -- mas o AVISO tem de ser visivel
        e o chamador da CLI (main()) sai com codigo != 0, porque "salvou" e
        "salvou validado" sao coisas diferentes (achado de auditoria
        2026-08-20: antes, os dois pareciam a mesma coisa no exit code).

        sep/encoding sao repassados a ler_csv() -- achado de 3a auditoria:
        antes ficavam parseados pelo argparse e nunca chegavam ao leitor,
        deixando --sep/--encoding da CLI inertes.
        """
        try:
            self.ler_csv(separador=separador, encoding=encoding)
            self.detectar_colunas()
            self.mapear_para_padrao()
            validado = self.validar()
            saida = self.salvar_xlsx(output_path)

            if validado:
                print(f"\n✨ Normalização concluída com sucesso!")
            else:
                print(f"\n⚠️  Normalização concluída COM AVISOS DE VALIDAÇÃO -- revise antes de usar.")
            print(f"   Saída: {saida}")

            return saida, validado
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    # A proteção de encoding do stdout vive no topo do módulo (linha 26) --
    # cobre quem importa a classe direto, não só quem chama a CLI.
    parser = argparse.ArgumentParser(
        description='Normalizar CSV de banco para modelo PROCESSADO padrão'
    )
    parser.add_argument('arquivo', help='Caminho do CSV a normalizar')
    parser.add_argument('banco', help='Nome do banco (ex: DIGIO, SANTANDER)')
    parser.add_argument('--output', '-o', help='Caminho de saída XLSX (padrão: auto)')
    parser.add_argument('--sep', help='Separador do CSV (padrão: auto-detecta)')
    parser.add_argument('--encoding', default='utf-8-sig', help='Encoding (padrão: utf-8-sig)')

    args = parser.parse_args()

    normalizador = Normalizador(args.arquivo, args.banco)
    _, validado = normalizador.executar(args.output, separador=args.sep, encoding=args.encoding)
    if not validado:
        sys.exit(2)  # salvou, mas com avisos de validacao -- distinto de erro (1) e sucesso (0)


if __name__ == '__main__':
    main()
