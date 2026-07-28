"""Testes dos workflows do Supervisor com agentes LLM substituídos por stubs.

Validam a orquestração completa (persistência, políticas, aprovação) sem
depender do Ollama — os 4 agentes são trocados por funções determinísticas.
"""

import pytest
from sqlalchemy import select

import app.modules.agents.supervisor.service as sup
from app.modules.agents.agents.schemas import (
    CampaignStrategy,
    ContentAgentOutput,
    CopyVariation,
    CreativeAgentOutput,
    DataAgentOutput,
    MarketingOpportunity,
    StrategyAgentOutput,
)
from app.modules.agents.marketing_ops.models import Approval, Campaign, Post
from app.modules.agents.supervisor.service import SupervisorService
from tests.conftest import create_campaign_bundle, create_product


# ---------------------------------------------------------------------------
# Stubs determinísticos dos outputs de cada agente
# ---------------------------------------------------------------------------

def _stub_data_output() -> DataAgentOutput:
    op = MarketingOpportunity(
        product_name="Manto de Teste",
        sku="MANTO-TESTE",
        opportunity_type="mais_vendido",
        stock=5,
        sold_30d=3,
        margin_pct=60.0,
        reason="Melhor desempenho recente",
    )
    return DataAgentOutput(opportunities=[op], primary=op, summary="Panorama de teste.")


def _stub_strategy_output(sku="MANTO-TESTE") -> StrategyAgentOutput:
    return StrategyAgentOutput(campaign=CampaignStrategy(
        name="Campanha Stub",
        objective="Vender o manto de teste",
        product_name="Manto de Teste",
        product_sku=sku,
        channel="Instagram",
        format="feed",
        angle="Nostalgia",
        cta="Chama na DM",
        risk_level="low",
        reasoning="Estratégia de teste.",
    ))


def _stub_content_output(caption="Legenda gerada pelo stub") -> ContentAgentOutput:
    return ContentAgentOutput(
        caption=caption,
        headline="Headline stub",
        cta_text="Chama na DM",
        format="feed",
        variations=[
            CopyVariation(style="urgência", caption="Var 1", headline="H1"),
            CopyVariation(style="aspiracional", caption="Var 2", headline="H2"),
        ],
        tone_applied="Tom de teste",
    )


def _stub_creative_output() -> CreativeAgentOutput:
    return CreativeAgentOutput(
        visual_briefing="Briefing visual completo do stub.",
        image_prompt="Prompt de imagem do stub.",
        photo_recommendations="Use a foto de frente.",
        carousel_idea=None,
        reel_script_outline=None,
    )


@pytest.fixture
def stub_agents(monkeypatch):
    """Substitui os 4 agentes por stubs; captura o feedback passado ao ContentAgent."""
    capturas = {}

    async def data_stub(objective, marketing_data, agent_ctx):
        return _stub_data_output()

    async def strategy_stub(objective, data_output, strategy_ctx, valid_skus=None):
        capturas["valid_skus"] = valid_skus
        return _stub_strategy_output()

    async def content_stub(strategy_output, brand_ctx, revision_feedback=None):
        capturas["feedback"] = revision_feedback
        return _stub_content_output()

    async def creative_stub(strategy_output, content_output, photos, ctx, revision_feedback=None):
        return _stub_creative_output()

    monkeypatch.setattr(sup, "_run_data_agent", data_stub)
    monkeypatch.setattr(sup, "_run_strategy_agent", strategy_stub)
    monkeypatch.setattr(sup, "_run_content_agent", content_stub)
    monkeypatch.setattr(sup, "_run_creative_agent", creative_stub)
    return capturas


# ---------------------------------------------------------------------------
# Workflow completo (geração inicial)
# ---------------------------------------------------------------------------

class TestWorkflowCompleto:
    async def test_pipeline_persiste_artefatos_e_aprovacao(self, db, stub_agents):
        await create_product(db, sku="MANTO-TESTE", stock=5)
        run = await SupervisorService.create_run(db, "Objetivo de teste")

        await SupervisorService.execute_workflow(run.id, "Objetivo de teste")

        await db.refresh(run)
        assert run.status == "completed"
        assert run.result["campaign_id"]

        campaign = (await db.execute(select(Campaign))).scalar_one()
        assert campaign.status == "pending_approval"
        assert campaign.product_id is not None  # FK gravada — regressão da consolidação

        approval = (await db.execute(select(Approval))).scalar_one()
        assert approval.status == "pending"

        # A lista fechada de SKUs do catálogo foi passada ao StrategyAgent.
        assert stub_agents["valid_skus"] == ["MANTO-TESTE"]

    async def test_bloqueia_produto_sem_estoque(self, db, stub_agents):
        await create_product(db, sku="MANTO-TESTE", stock=0)
        run = await SupervisorService.create_run(db, "Objetivo")

        await SupervisorService.execute_workflow(run.id, "Objetivo")

        await db.refresh(run)
        assert run.status == "failed"
        assert "sem estoque" in run.error.lower()

    async def test_bloqueia_copy_com_preco_inventado(self, db, stub_agents, monkeypatch):
        await create_product(db, sku="MANTO-TESTE", stock=5)

        async def content_com_preco(strategy_output, brand_ctx, revision_feedback=None):
            return _stub_content_output(caption="Só R$ 99, aproveite!")

        monkeypatch.setattr(sup, "_run_content_agent", content_com_preco)
        run = await SupervisorService.create_run(db, "Objetivo")

        await SupervisorService.execute_workflow(run.id, "Objetivo")

        await db.refresh(run)
        assert run.status == "failed"
        assert "policyengine" in run.error.lower()

    async def test_format_longo_nao_derruba_persistencia(self, db, stub_agents, monkeypatch):
        """Regressão do gate 3 real: LLM devolveu descrição de 159 chars no campo
        format (VARCHAR(100)) e o INSERT falhava com StringDataRightTruncationError."""
        await create_product(db, sku="MANTO-TESTE", stock=5)

        async def strategy_verborragica(objective, data_output, strategy_ctx, valid_skus=None):
            saida = _stub_strategy_output()
            saida.campaign.format = "Video em estilo documentário " * 10  # ~290 chars
            return saida

        monkeypatch.setattr(sup, "_run_strategy_agent", strategy_verborragica)
        run = await SupervisorService.create_run(db, "Objetivo")

        await SupervisorService.execute_workflow(run.id, "Objetivo")

        await db.refresh(run)
        assert run.status == "completed"
        campaign = (await db.execute(select(Campaign))).scalar_one()
        assert len(campaign.format) <= 100

    async def test_sku_inexistente_falha_com_erro_claro(self, db, stub_agents, monkeypatch):
        await create_product(db, sku="MANTO-TESTE", stock=5)

        async def strategy_alucinada(objective, data_output, strategy_ctx, valid_skus=None):
            # SKU e nome inexistentes: nenhuma camada da resolução tolerante
            # pode encontrar o produto — o run deve falhar com erro claro.
            saida = _stub_strategy_output(sku="SKU-QUE-NAO-EXISTE")
            saida.campaign.product_name = "Produto Fantasma"
            return saida

        monkeypatch.setattr(sup, "_run_strategy_agent", strategy_alucinada)
        run = await SupervisorService.create_run(db, "Objetivo")

        await SupervisorService.execute_workflow(run.id, "Objetivo")

        await db.refresh(run)
        assert run.status == "failed"
        assert "SKU" in run.error


# ---------------------------------------------------------------------------
# Workflow de re-geração pós-revisão (FASE B)
# ---------------------------------------------------------------------------

class TestWorkflowRevisao:
    async def test_regeneracao_atualiza_post_e_cria_nova_aprovacao(self, db, stub_agents):
        produto = await create_product(db, sku="MANTO-TESTE", stock=5)
        _, campaign, post, brief, approval = await create_campaign_bundle(
            db, product=produto, status="draft"
        )
        # Simula o pedido de revisão já decidido sobre a aprovação original.
        approval.status = "revision_requested"
        approval.comment = "Deixe a legenda mais curta"
        await db.commit()

        run = await SupervisorService.create_run(db, "Revisão da campanha")
        await SupervisorService.execute_revision_workflow(
            run.id, campaign.id, "Deixe a legenda mais curta"
        )

        await db.refresh(run)
        assert run.status == "completed"
        assert run.result.get("revision") is True

        # O feedback humano chegou ao ContentAgent.
        assert stub_agents["feedback"] == "Deixe a legenda mais curta"

        # Post foi ATUALIZADO (mesmo id), não duplicado.
        # populate_existing força recarga do banco — o workflow rodou em outra
        # sessão e a sessão do teste guarda atributos cacheados no identity map.
        posts = (
            await db.execute(select(Post).execution_options(populate_existing=True))
        ).scalars().all()
        assert len(posts) == 1
        assert posts[0].id == post.id
        assert posts[0].caption == "Legenda gerada pelo stub"
        assert posts[0].status == "pending_approval"

        # Nova aprovação pendente criada; a original permanece decidida.
        approvals = (
            await db.execute(select(Approval).execution_options(populate_existing=True))
        ).scalars().all()
        status = sorted(a.status for a in approvals)
        assert status == ["pending", "revision_requested"]

    async def test_regeneracao_bloqueia_se_estoque_zerou(self, db, stub_agents):
        produto = await create_product(db, sku="MANTO-TESTE", stock=0)
        _, campaign, _, _, _ = await create_campaign_bundle(db, product=produto, status="draft")

        run = await SupervisorService.create_run(db, "Revisão")
        await SupervisorService.execute_revision_workflow(run.id, campaign.id, "feedback")

        await db.refresh(run)
        assert run.status == "failed"
        assert "sem estoque" in run.error.lower()
