"""Testes da resolução tolerante de SKU do Supervisor.

O StrategyAgent (LLM) pode distorcer SKUs — a resolução em camadas precisa
reconhecer variações inambíguas e rejeitar tudo que for ambíguo ou inexistente.
"""

from app.modules.agents.supervisor.service import (
    _normalize_sku_tokens,
    _resolve_campaign_product,
)
from tests.conftest import create_product


class TestNormalizacaoTokens:
    def test_reordenacao_gera_mesmos_tokens(self):
        assert _normalize_sku_tokens("BR02-MANTO") == _normalize_sku_tokens("MANTO-BR02")

    def test_separadores_diferentes_gera_mesmos_tokens(self):
        assert _normalize_sku_tokens("MANTO_BR02") == _normalize_sku_tokens("manto br02")

    def test_skus_diferentes_geram_tokens_diferentes(self):
        assert _normalize_sku_tokens("MANTO-BR02") != _normalize_sku_tokens("MANTO-RM25")


class TestResolucaoProduto:
    async def test_camada_1_sku_exato(self, db):
        p = await create_product(db, sku="MANTO-BR02")
        resolvido = await _resolve_campaign_product(db, "MANTO-BR02")
        assert resolvido is not None and resolvido.id == p.id

    async def test_camada_2_caixa_diferente(self, db):
        p = await create_product(db, sku="MANTO-BR02")
        resolvido = await _resolve_campaign_product(db, "manto-br02")
        assert resolvido is not None and resolvido.id == p.id

    async def test_camada_3_tokens_reordenados(self, db):
        """Regressão do run #2 real: LLM devolveu 'BR02-MANTO'."""
        p = await create_product(db, sku="MANTO-BR02")
        resolvido = await _resolve_campaign_product(db, "BR02-MANTO")
        assert resolvido is not None and resolvido.id == p.id

    async def test_camada_4_nome_do_produto(self, db):
        p = await create_product(db, sku="MANTO-BR02", name="Manto Retrô Brasil 2002")
        resolvido = await _resolve_campaign_product(
            db, "SKU-INVENTADO", product_name="Manto Retrô Brasil 2002"
        )
        assert resolvido is not None and resolvido.id == p.id

    async def test_sku_inexistente_retorna_none(self, db):
        await create_product(db, sku="MANTO-BR02")
        assert await _resolve_campaign_product(db, "XYZ-999") is None

    async def test_produto_inativo_nao_resolve(self, db):
        await create_product(db, sku="MANTO-BR02", active=False)
        assert await _resolve_campaign_product(db, "MANTO-BR02") is None

    async def test_ambiguidade_de_tokens_nao_resolve(self, db):
        """Dois produtos com os mesmos tokens em ordem diferente → ambíguo, falha."""
        await create_product(db, sku="MANTO-BR02")
        await create_product(db, sku="BR02-MANTO", name="Outro Manto")
        # 'br02 manto' tem os mesmos tokens dos dois SKUs acima; a camada 2
        # (caixa) e a camada 3 (tokens) encontram 2 candidatos → None.
        assert await _resolve_campaign_product(db, "br02_manto_") is None
