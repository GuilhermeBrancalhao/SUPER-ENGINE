"""Testes da integração Motores + Engine sobre o hook VIVO `hooks/engine_contexto.py`.

Reapontados da cópia antiga `engine_contexto_v2` (removida) para o módulo que o
`hooks.json` executa de verdade. O teste da lista hardcoded `VOLUMES_PRONTOS`
foi removido: o módulo vivo deliberadamente não tem mais essa lista — volumes
são detectados dinamicamente (ver test_engine_contexto.py e
test_volume_detector.py).
"""
import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "hooks"))

# O hook vivo — mesmo caminho de import de test_hooks.py, para que o módulo
# exista uma única vez na sessão do pytest.
import engine_contexto as engine_vivo  # noqa: E402


class TestCarregamentoMotores:
    """Verifica que motores são detectados e carregados."""

    def test_motores_por_fase_completo(self):
        """Fases relevantes têm motores."""
        assert engine_vivo.MOTORES_POR_FASE["PLANO"] == [
            "arquitetar-sistema",
            "materializar-ideia",
            "conciliar-dados",
            "construir-automacao-cli",
            "integrar-api-externa",
        ]
        assert engine_vivo.MOTORES_POR_FASE["REVISAO"] == [
            "revisar-codigo",
            "otimizar-performance",
            "gauntlet-loop",
        ]
        assert engine_vivo.MOTORES_POR_FASE["BUILD"] == [
            "materializar-ideia",
            "revisar-codigo",
            "conciliar-dados",
            "construir-automacao-cli",
            "integrar-api-externa",
        ]

    def test_ler_descricao_motor_existe(self, tmp_path):
        """Lê description de um SKILL.md válido."""
        motor_dir = tmp_path / "motores" / "revisar-codigo"
        motor_dir.mkdir(parents=True)

        skill_content = '''---
name: revisar-codigo
description: Motor que revisa código com critério escrito
---

# Motor de revisão
'''
        (motor_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

        desc = engine_vivo._ler_descricao_motor(tmp_path, "revisar-codigo")
        assert desc is not None
        assert "revisa código" in desc

    def test_ler_descricao_motor_nao_existe(self, tmp_path):
        """Retorna None se motor não existe."""
        desc = engine_vivo._ler_descricao_motor(tmp_path, "inexistente")
        assert desc is None

    def test_cortar_respeita_limite(self):
        """Função de corte respeita limite de caracteres."""
        texto_longo = "a" * 200
        cortado = engine_vivo._cortar(texto_longo, 50)
        assert len(cortado) <= 50
        assert cortado.endswith("…")

    def test_teto_efetivo_respeita_minimo(self):
        """Teto nunca fica abaixo do mínimo."""
        cfg = {"teto_cartao_linhas": 5}
        teto = engine_vivo._teto_efetivo(cfg)
        assert teto >= engine_vivo.MINIMO_CARTAO

    def test_teto_efetivo_normaliza_nao_numerico(self):
        """Valor não-numérico cai no default."""
        cfg = {"teto_cartao_linhas": "not_a_number"}
        teto = engine_vivo._teto_efetivo(cfg)
        assert teto == 40


class TestMontaçãoCartão:
    """Verifica montagem do cartão com motores."""

    def test_cartao_com_motores_fase_revisao(self, tmp_path):
        """Cartão da fase REVISAO inclui motores corretos."""
        motor_dir = tmp_path / "motores" / "revisar-codigo"
        motor_dir.mkdir(parents=True)
        (motor_dir / "SKILL.md").write_text(
            '---\nname: revisar-codigo\ndescription: Revisa com severidade\n---\n',
            encoding="utf-8",
        )

        dados = {
            "ativo": True,
            "fase": "REVISAO",
            "ciclo": {"objetivo": "Otimizar performance", "modo": "normal"},
            "cartoes": ["python", "pytest"],
        }
        cfg = {"teto_cartao_linhas": 60}

        cartao = engine_vivo.montar_cartao_estendido(dados, cfg, tmp_path, str(tmp_path))

        assert "REVISAO" in cartao
        assert "Motores desta fase:" in cartao
        assert "revisar-codigo" in cartao
        assert "otimizar-performance" in cartao

    def test_cartao_fase_sem_motores(self, tmp_path):
        """Fases sem motores não listam seção."""
        dados = {
            "ativo": True,
            "fase": "DESCOBERTA",
            "ciclo": {"objetivo": "Entender o pedido", "modo": "normal"},
        }
        cfg = {"teto_cartao_linhas": 60}

        cartao = engine_vivo.montar_cartao_estendido(dados, cfg, tmp_path, str(tmp_path))

        # DESCOBERTA não tem motores, então a seção não aparece
        assert "Motores desta fase:" not in cartao

    def test_cartao_respeita_teto(self, tmp_path):
        """Cartão nunca ultrapassa o teto de linhas."""
        motor_dir = tmp_path / "motores" / "revisar-codigo"
        motor_dir.mkdir(parents=True)
        (motor_dir / "SKILL.md").write_text(
            '---\nname: revisar-codigo\ndescription: Uma descrição bem longa que deveria ser cortada se for muito grande\n---\n',
            encoding="utf-8",
        )

        dados = {
            "ativo": True,
            "fase": "REVISAO",
            "ciclo": {
                "objetivo": "Fazer algo bem complicado que exige muita explicação",
                "modo": "normal",
            },
            "cartoes": ["python", "pytest", "fastapi", "react"],
            "decisoes": [{"o_que": "coisa", "porque": "motivo"}],
        }
        cfg = {"teto_cartao_linhas": 30}

        cartao = engine_vivo.montar_cartao_estendido(dados, cfg, tmp_path, str(tmp_path))
        linhas = cartao.count("\n") + 1

        assert linhas <= 30, f"Cartão tem {linhas} linhas, máximo é 30"


class TestInjeçãoNohook:
    """Verifica comportamento completo do hook (entrada real via stdin)."""

    def test_principal_com_engine_inativo(self, tmp_path, capsys):
        """Hook retorna 0 e não imprime nada se o engine está inativo."""
        entrada = json.dumps({"cwd": str(tmp_path)})

        with patch("sys.stdin", io.StringIO(entrada)), patch.object(
            engine_vivo.estado, "carregar", return_value={"ativo": False}
        ):
            assert engine_vivo.principal() == 0

        assert capsys.readouterr().out == ""

    def test_principal_entrada_invalida(self, capsys):
        """Hook retorna 0 silenciosamente se a entrada JSON é inválida."""
        with patch("sys.stdin", io.StringIO("isso não é JSON")):
            assert engine_vivo.principal() == 0

        assert capsys.readouterr().out == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
