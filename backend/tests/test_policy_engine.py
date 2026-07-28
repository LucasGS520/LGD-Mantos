"""Testes do PolicyEngine — todas as regras determinísticas da camada de agentes.

Estas são as regras de segurança que protegem a operação da loja contra ações
indevidas dos agentes de IA. Nenhum teste aqui usa banco ou LLM.
"""

from app.modules.agents.policy_engine import PolicyEngine


# ---------------------------------------------------------------------------
# Conteúdo — preço inventado
# ---------------------------------------------------------------------------

class TestPrecoInventado:
    def test_bloqueia_cifrao(self):
        r = PolicyEngine.validate_content_has_no_invented_price("Só R$ 99 hoje!")
        assert not r.ok

    def test_bloqueia_desconto_de(self):
        r = PolicyEngine.validate_content_has_no_invented_price("Desconto de 20% no manto")
        assert not r.ok

    def test_bloqueia_percentual_off(self):
        r = PolicyEngine.validate_content_has_no_invented_price("Aproveite 30% OFF")
        assert not r.ok

    def test_bloqueia_promocao_de(self):
        r = PolicyEngine.validate_content_has_no_invented_price("Promoção de lançamento")
        assert not r.ok

    def test_bloqueia_valor_em_reais(self):
        r = PolicyEngine.validate_content_has_no_invented_price("Leve por 199 reais")
        assert not r.ok

    def test_permite_fotos_reais(self):
        """Regressão: 'fotos reais do produto' não é preço — não pode bloquear."""
        r = PolicyEngine.validate_content_has_no_invented_price(
            "Confira as fotos reais do produto no carrossel"
        )
        assert r.ok

    def test_permite_copy_limpo(self):
        r = PolicyEngine.validate_content_has_no_invented_price(
            "Manto retrô do penta chegou. Chama na DM!"
        )
        assert r.ok


# ---------------------------------------------------------------------------
# Conteúdo — promessa de estoque
# ---------------------------------------------------------------------------

class TestPromessaEstoque:
    def test_bloqueia_todos_os_tamanhos(self):
        r = PolicyEngine.validate_content_has_no_stock_promise(
            "Disponível em todos os tamanhos!"
        )
        assert not r.ok

    def test_bloqueia_estoque_completo(self):
        r = PolicyEngine.validate_content_has_no_stock_promise("Estoque completo na loja")
        assert not r.ok

    def test_permite_copy_sem_promessa(self):
        r = PolicyEngine.validate_content_has_no_stock_promise(
            "Garanta o seu antes que acabe"
        )
        assert r.ok


# ---------------------------------------------------------------------------
# Campanha
# ---------------------------------------------------------------------------

class TestCampanha:
    def test_bloqueia_produto_sem_estoque(self):
        assert not PolicyEngine.validate_campaign_product_has_stock(0).ok

    def test_permite_produto_com_estoque(self):
        assert PolicyEngine.validate_campaign_product_has_stock(3).ok

    def test_bloqueia_desconto_nao_autorizado(self):
        r = PolicyEngine.validate_campaign_has_no_auto_discount({"discount_pct": 10})
        assert not r.ok

    def test_permite_desconto_autorizado(self):
        r = PolicyEngine.validate_campaign_has_no_auto_discount(
            {"discount_pct": 10, "discount_authorized": True}
        )
        assert r.ok

    def test_permite_campanha_sem_desconto(self):
        assert PolicyEngine.validate_campaign_has_no_auto_discount({}).ok


# ---------------------------------------------------------------------------
# Aprovação humana
# ---------------------------------------------------------------------------

class TestAprovacaoHumana:
    def test_bloqueia_sem_identificacao(self):
        assert not PolicyEngine.validate_approval_is_human(None).ok
        assert not PolicyEngine.validate_approval_is_human("").ok

    def test_bloqueia_identidades_de_agente(self):
        for who in ("agent", "supervisor", "auto", "system", "AGENT"):
            assert not PolicyEngine.validate_approval_is_human(who).ok

    def test_permite_humano(self):
        assert PolicyEngine.validate_approval_is_human("owner").ok


# ---------------------------------------------------------------------------
# Publicação
# ---------------------------------------------------------------------------

class TestPublicacao:
    def test_bloqueia_sem_aprovacao(self):
        for status in ("pending", "rejected", "revision_requested", "none"):
            assert not PolicyEngine.validate_publish_requires_approval(status).ok

    def test_permite_aprovado(self):
        assert PolicyEngine.validate_publish_requires_approval("approved").ok

    def test_bloqueia_canal_nao_autorizado(self):
        r = PolicyEngine.validate_publish_channel_is_authorized("TikTok", ["Instagram"])
        assert not r.ok

    def test_permite_canal_autorizado(self):
        r = PolicyEngine.validate_publish_channel_is_authorized(
            "Instagram", ["Instagram", "WhatsApp"]
        )
        assert r.ok


# ---------------------------------------------------------------------------
# Barreiras absolutas — sempre bloqueiam, com motivo preenchido
# ---------------------------------------------------------------------------

class TestBarreirasAbsolutas:
    def test_barreiras_sempre_bloqueiam(self):
        barreiras = [
            PolicyEngine.block_stock_mutation,
            PolicyEngine.block_price_mutation,
            PolicyEngine.block_sale_registration,
            PolicyEngine.block_product_deletion,
            PolicyEngine.block_local_image_generation,
            PolicyEngine.block_auto_publish,
        ]
        for barreira in barreiras:
            resultado = barreira()
            assert not resultado.ok
            assert resultado.reason
