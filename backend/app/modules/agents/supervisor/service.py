"""SupervisorService — orquestra o pipeline multi-agente de marketing.

Fluxo completo de um run:
  1. Cria AgentRun com status pending.
  2. Carrega dados de Análise e contexto de marca da Knowledge Layer.
  3. Executa DataAgent → StrategyAgent → ContentAgent → CreativeAgent.
  4. Persiste Campaign, Post, CreativeBrief e Approval no Marketing Ops.
  5. Atualiza AgentRun com status final e referências aos artefatos gerados.

Regras:
- O SupervisorService não chama LLM diretamente. Isso é responsabilidade dos agentes.
- O SupervisorService não altera dados de Operacional ou Análise.
- Falhas parciais marcam o run como failed e registram o erro.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.modules.agents.agents.content_agent import build_content_agent, build_content_agent_input
from app.modules.agents.agents.creative_agent import build_creative_agent, build_creative_agent_input
from app.modules.agents.agents.data_agent import build_data_agent, build_data_agent_input
from app.modules.agents.agents.schemas import (
    ContentAgentOutput,
    CreativeAgentOutput,
    DataAgentOutput,
    StrategyAgentOutput,
)
from app.modules.agents.agents.strategy_agent import build_strategy_agent, build_strategy_agent_input
from app.modules.agents.knowledge.service import KnowledgeService
from app.modules.agents.marketing_ops.models import AgentRun, Approval, Campaign, CreativeBrief, Post
from app.modules.analytics.services.agent_context_service import AgentContextService
from app.modules.analytics.services.marketing_intelligence_service import MarketingIntelligenceService
from app.shared.models.catalog import Product

logger = logging.getLogger(__name__)


class SupervisorService:
    """Coordena o ciclo completo de geração de campanha via agentes especializados."""

    # ------------------------------------------------------------------
    # Gestão de runs
    # ------------------------------------------------------------------

    @staticmethod
    async def create_run(db: AsyncSession, objective: str) -> AgentRun:
        """Persiste um novo AgentRun em estado pending e retorna o objeto."""
        run = AgentRun(objective=objective, status="pending")
        db.add(run)
        await db.commit()
        await db.refresh(run)
        return run

    @staticmethod
    async def get_run(db: AsyncSession, run_id: str) -> AgentRun | None:
        """Retorna um AgentRun pelo ID."""
        return await db.get(AgentRun, run_id)

    # ------------------------------------------------------------------
    # Execução do workflow (chamado em background)
    # ------------------------------------------------------------------

    @staticmethod
    async def execute_workflow(run_id: str, objective: str) -> None:
        """Executa o pipeline completo em uma sessão de banco independente.

        Projetado para rodar em background (FastAPI BackgroundTasks ou asyncio.create_task).
        Cria sua própria sessão para não depender da sessão da requisição original.
        """
        async with AsyncSessionLocal() as db:
            try:
                await SupervisorService._mark_running(db, run_id)

                # --- Carregamento de dados ---
                logger.info("[%s] Carregando dados de Análise e Knowledge Layer", run_id)
                marketing_data, agent_ctx, brand_ctx, strategy_ctx, creative_ctx = (
                    await _load_context(db)
                )

                # --- DataAgent ---
                logger.info("[%s] DataAgent iniciado", run_id)
                data_output = await _run_data_agent(objective, marketing_data, agent_ctx)
                logger.info("[%s] DataAgent concluído: %d oportunidades", run_id, len(data_output.opportunities))

                # --- StrategyAgent ---
                logger.info("[%s] StrategyAgent iniciado", run_id)
                strategy_output = await _run_strategy_agent(objective, data_output, strategy_ctx)
                logger.info("[%s] StrategyAgent concluído: campanha '%s'", run_id, strategy_output.campaign.name)

                # --- Persiste Campaign draft ---
                campaign = await _save_campaign(db, run_id, strategy_output)

                # --- ContentAgent ---
                logger.info("[%s] ContentAgent iniciado", run_id)
                content_output = await _run_content_agent(strategy_output, brand_ctx)
                logger.info("[%s] ContentAgent concluído", run_id)

                # --- Persiste Post draft ---
                post = await _save_post(db, campaign.id, content_output, strategy_output)

                # --- CreativeAgent ---
                logger.info("[%s] CreativeAgent iniciado", run_id)
                product_photos = await _load_product_photos(db, strategy_output.campaign.product_sku)
                creative_output = await _run_creative_agent(
                    strategy_output, content_output, product_photos, creative_ctx
                )
                logger.info("[%s] CreativeAgent concluído", run_id)

                # --- Persiste CreativeBrief ---
                brief = await _save_creative_brief(db, campaign.id, creative_output)

                # --- Cria pedido de aprovação inicial ---
                approval = await _create_approval(db, campaign.id)

                # --- Marca run como completed ---
                await SupervisorService._mark_completed(db, run_id, {
                    "campaign_id": campaign.id,
                    "campaign_name": campaign.name,
                    "post_id": post.id,
                    "creative_brief_id": brief.id,
                    "approval_id": approval.id,
                })
                logger.info("[%s] Run concluído com sucesso", run_id)

            except Exception as exc:
                logger.exception("[%s] Run falhou: %s", run_id, exc)
                await db.rollback()
                await SupervisorService._mark_failed(run_id, str(exc))

    # ------------------------------------------------------------------
    # Helpers de status
    # ------------------------------------------------------------------

    @staticmethod
    async def _mark_running(db: AsyncSession, run_id: str) -> None:
        run = await db.get(AgentRun, run_id)
        if run:
            run.status = "running"
            await db.commit()

    @staticmethod
    async def _mark_completed(db: AsyncSession, run_id: str, result: dict) -> None:
        run = await db.get(AgentRun, run_id)
        if run:
            run.status = "completed"
            run.result = result
            await db.commit()

    @staticmethod
    async def _mark_failed(run_id: str, error: str) -> None:
        async with AsyncSessionLocal() as db:
            run = await db.get(AgentRun, run_id)
            if run:
                run.status = "failed"
                run.error = error
                await db.commit()


# ------------------------------------------------------------------
# Funções auxiliares privadas — cada uma com responsabilidade única
# ------------------------------------------------------------------

async def _load_context(db: AsyncSession) -> tuple:
    """Carrega todo o contexto necessário para o pipeline de uma só vez."""
    marketing_data = await MarketingIntelligenceService.marketing_intelligence(db)
    agent_ctx = await AgentContextService.agent_context(db)
    brand_ctx = await KnowledgeService.get_brand_context(db)
    strategy_ctx = await KnowledgeService.get_strategy_context(db)
    creative_ctx = await KnowledgeService.get_creative_context(db)
    return marketing_data, agent_ctx, brand_ctx, strategy_ctx, creative_ctx


async def _run_data_agent(objective: str, marketing_data: dict, agent_ctx: dict) -> DataAgentOutput:
    agent = build_data_agent()
    prompt = build_data_agent_input(objective, marketing_data, agent_ctx)
    response = await agent.arun(prompt)
    if isinstance(response.content, DataAgentOutput):
        return response.content
    raise ValueError(f"DataAgent retornou output inesperado: {type(response.content)}")


async def _run_strategy_agent(
    objective: str,
    data_output: DataAgentOutput,
    strategy_ctx: str,
) -> StrategyAgentOutput:
    agent = build_strategy_agent()
    prompt = build_strategy_agent_input(objective, data_output, strategy_ctx)
    response = await agent.arun(prompt)
    if isinstance(response.content, StrategyAgentOutput):
        return response.content
    raise ValueError(f"StrategyAgent retornou output inesperado: {type(response.content)}")


async def _run_content_agent(
    strategy_output: StrategyAgentOutput,
    brand_ctx: str,
) -> ContentAgentOutput:
    agent = build_content_agent()
    prompt = build_content_agent_input(strategy_output, brand_ctx)
    response = await agent.arun(prompt)
    if isinstance(response.content, ContentAgentOutput):
        return response.content
    raise ValueError(f"ContentAgent retornou output inesperado: {type(response.content)}")


async def _run_creative_agent(
    strategy_output: StrategyAgentOutput,
    content_output: ContentAgentOutput,
    product_photos: list[dict],
    creative_ctx: str,
) -> CreativeAgentOutput:
    agent = build_creative_agent()
    prompt = build_creative_agent_input(strategy_output, content_output, product_photos, creative_ctx)
    response = await agent.arun(prompt)
    if isinstance(response.content, CreativeAgentOutput):
        return response.content
    raise ValueError(f"CreativeAgent retornou output inesperado: {type(response.content)}")


async def _load_product_photos(db: AsyncSession, product_sku: str) -> list[dict]:
    """Busca as fotos do produto pelo SKU. Retorna lista vazia se não encontrado."""
    result = await db.execute(
        select(Product).where(Product.sku == product_sku).where(Product.is_active == True)
    )
    product = result.scalar_one_or_none()
    if not product or not product.photos:
        return []
    photos = product.photos if isinstance(product.photos, list) else []
    return [p for p in photos if isinstance(p, dict)]


async def _save_campaign(db: AsyncSession, run_id: str, strategy_output: StrategyAgentOutput) -> Campaign:
    c = strategy_output.campaign
    campaign = Campaign(
        agent_run_id=run_id,
        name=c.name,
        objective=c.objective,
        channel=c.channel,
        format=c.format,
        angle=c.angle,
        cta=c.cta,
        risk_level=c.risk_level,
        status="draft",
    )
    db.add(campaign)
    await db.flush()
    return campaign


async def _save_post(
    db: AsyncSession,
    campaign_id: str,
    content_output: ContentAgentOutput,
    strategy_output: StrategyAgentOutput,
) -> Post:
    variations = [
        {"style": v.style, "caption": v.caption, "headline": v.headline}
        for v in content_output.variations
    ]
    post = Post(
        campaign_id=campaign_id,
        caption=content_output.caption,
        headline=content_output.headline,
        cta_text=content_output.cta_text,
        format=strategy_output.campaign.format,
        copy_variations=variations,
        status="draft",
    )
    db.add(post)
    await db.flush()
    return post


async def _save_creative_brief(
    db: AsyncSession,
    campaign_id: str,
    creative_output: CreativeAgentOutput,
) -> CreativeBrief:
    brief = CreativeBrief(
        campaign_id=campaign_id,
        visual_briefing=creative_output.visual_briefing,
        image_prompt=creative_output.image_prompt,
        carousel_idea=creative_output.carousel_idea,
        reel_script=creative_output.reel_script_outline,
        photo_analysis={"recommendations": creative_output.photo_recommendations},
        status="draft",
    )
    db.add(brief)
    await db.flush()
    return brief


async def _create_approval(db: AsyncSession, campaign_id: str) -> Approval:
    """Cria pedido de aprovação e atualiza status de todos os artefatos para pending_approval."""
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.posts), selectinload(Campaign.creative_briefs))
        .where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one()
    campaign.status = "pending_approval"
    for post in campaign.posts:
        post.status = "pending_approval"
    for brief in campaign.creative_briefs:
        brief.status = "pending_approval"

    approval = Approval(campaign_id=campaign_id, status="pending")
    db.add(approval)
    await db.commit()
    return approval
