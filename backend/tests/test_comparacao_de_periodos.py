"""Resolução do par (período atual, período anterior) e cálculo de variação.

Funções puras, sem banco. As bordas que importam são as viradas de mês e de ano,
e o caso em que o mês anterior é mais curto que o corrente.
"""

from datetime import datetime, timezone

import pytest

from app.modules.analytics.schemas.comparacao import Comparado
from app.modules.analytics.utils import resolve_comparison_period


def _em(ano: int, mes: int, dia: int, hora: int = 12) -> datetime:
    return datetime(ano, mes, dia, hora, tzinfo=timezone.utc)


class TestMesCorrente:
    def test_compara_contra_os_mesmos_dias_decorridos(self):
        agora = _em(2026, 9, 12)
        (ini_atual, fim_atual), (ini_ant, fim_ant) = resolve_comparison_period(
            "current_month", agora=agora
        )
        assert ini_atual == _em(2026, 9, 1, 0)
        assert fim_atual == agora
        assert ini_ant == _em(2026, 8, 1, 0)
        # 11 dias e 12 horas decorridos em setembro → mesma janela em agosto.
        assert fim_ant == _em(2026, 8, 12)

    def test_mes_anterior_mais_curto_limita_a_janela(self):
        # 31 de março: março tem 31 dias, fevereiro de 2026 tem 28. A janela
        # anterior não pode invadir março — para no fim de fevereiro.
        agora = _em(2026, 3, 31)
        _, (ini_ant, fim_ant) = resolve_comparison_period("current_month", agora=agora)
        assert ini_ant == _em(2026, 2, 1, 0)
        assert fim_ant == _em(2026, 3, 1, 0)

    def test_virada_de_ano(self):
        agora = _em(2026, 1, 10)
        _, (ini_ant, fim_ant) = resolve_comparison_period("current_month", agora=agora)
        assert ini_ant == _em(2025, 12, 1, 0)
        assert fim_ant == _em(2025, 12, 10)


class TestMesAnterior:
    def test_compara_dois_meses_fechados(self):
        agora = _em(2026, 9, 12)
        (ini_atual, fim_atual), (ini_ant, fim_ant) = resolve_comparison_period(
            "last_month", agora=agora
        )
        assert ini_atual == _em(2026, 8, 1, 0)
        assert fim_atual == _em(2026, 9, 1, 0)
        assert ini_ant == _em(2026, 7, 1, 0)
        assert fim_ant == _em(2026, 8, 1, 0)


class TestJanelasMoveis:
    @pytest.mark.parametrize("period,dias", [("last_3_months", 90), ("last_6_months", 180)])
    def test_janela_anterior_tem_o_mesmo_tamanho(self, period, dias):
        agora = _em(2026, 9, 12)
        (ini_atual, fim_atual), (ini_ant, fim_ant) = resolve_comparison_period(
            period, agora=agora
        )
        assert (fim_atual - ini_atual).days == dias
        assert (fim_ant - ini_ant).days == dias
        assert fim_ant == ini_atual

    def test_fallback_em_dias_usa_a_janela_imediatamente_anterior(self):
        agora = _em(2026, 9, 12)
        (ini_atual, fim_atual), (ini_ant, fim_ant) = resolve_comparison_period(
            None, days=7, agora=agora
        )
        assert (fim_atual - ini_atual).days == 7
        assert (fim_ant - ini_ant).days == 7
        assert fim_ant == ini_atual


class TestAnoCorrente:
    def test_compara_contra_o_mesmo_periodo_do_ano_passado(self):
        agora = _em(2026, 3, 15)
        (ini_atual, _), (ini_ant, fim_ant) = resolve_comparison_period(
            "current_year", agora=agora
        )
        assert ini_atual == _em(2026, 1, 1, 0)
        assert ini_ant == _em(2025, 1, 1, 0)
        assert fim_ant == _em(2025, 3, 15)


class TestComparado:
    def test_calcula_variacao_percentual(self):
        c = Comparado.de(atual=18200.0, anterior=16350.0)
        assert c.atual == 18200.0
        assert c.anterior == 16350.0
        assert c.variacao_pct == 11.3

    def test_queda_gera_variacao_negativa(self):
        c = Comparado.de(atual=4230.0, anterior=4539.0)
        assert c.variacao_pct == -6.8

    def test_anterior_zero_nao_gera_variacao(self):
        # Dividir por zero produziria infinito; "+∞%" não informa nada ao operador.
        c = Comparado.de(atual=500.0, anterior=0.0)
        assert c.variacao_pct is None

    def test_anterior_ausente_nao_gera_variacao(self):
        c = Comparado.de(atual=500.0, anterior=None)
        assert c.variacao_pct is None

    def test_ambos_zero_nao_gera_variacao(self):
        c = Comparado.de(atual=0.0, anterior=0.0)
        assert c.variacao_pct is None
