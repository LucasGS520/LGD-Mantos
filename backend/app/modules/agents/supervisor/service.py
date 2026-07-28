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
    CampaignStrategy,
    ContentAgentOutput,
    CreativeAgentOutput,
    DataAgentOutput,
    StrategyAgentOutput,
)
from app.modules.agents.agents.strategy_agent import build_strategy_agent, build_strategy_agent_input
from app.modules.agents.knowledge.service import KnowledgeService
from app.modules.agents.marketing_ops.models import AgentRun, Approval, Campaign, CreativeBrief, Post
from app.modules.agents.policy_engine import PolicyEngine
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
                # A lista de SKUs válidos do catálogo vai no prompt como conjunto
                # fechado — reduz a chance de o LLM alucinar/reordenar um SKU.
                logger.info("[%s] StrategyAgent iniciado", run_id)
                valid_skus = await _load_active_skus(db)
                strategy_output = await _run_strategy_agent(
                    objective, data_output, strategy_ctx, valid_skus
                )
                logger.info("[%s] StrategyAgent concluído: campanha '%s'", run_id, strategy_output.campaign.name)

                # --- Valida produto da campanha (PolicyEngine) ---
                # O SKU vem do LLM: precisa existir no catálogo e ter estoque,
                # senão o run falha aqui — antes de gerar qualquer conteúdo.
                product = await _resolve_campaign_product(
                    db,
                    strategy_output.campaign.product_sku,
                    strategy_output.campaign.product_name,
                )
                if product is None:
                    raise ValueError(
                        f"StrategyAgent referenciou SKU inexistente ou inativo: "
                        f"'{strategy_output.campaign.product_sku}'."
                    )
                total_stock = sum(v.stock_quantity for v in product.variants)
                stock_policy = PolicyEngine.validate_campaign_product_has_stock(total_stock)
                if not stock_policy.ok:
                    raise ValueError(f"PolicyEngine bloqueou a campanha: {stock_policy.reason}")

                # --- Persiste Campaign draft ---
                campaign = await _save_campaign(db, run_id, strategy_output, product.id)

                # --- ContentAgent ---
                logger.info("[%s] ContentAgent iniciado", run_id)
                content_output = await _run_content_agent(strategy_output, brand_ctx)
                logger.info("[%s] ContentAgent concluído", run_id)

                # --- Valida copy gerado (PolicyEngine) ---
                _validate_content_policies(content_output)

                # --- Persiste Post draft ---
                post = await _save_post(db, campaign.id, content_output, strategy_output)

                # --- CreativeAgent ---
                logger.info("[%s] CreativeAgent iniciado", run_id)
                product_photos = _extract_product_photos(product)
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
    # Re-geração pós-revisão (FASE B do ciclo de aprovação)
    # ------------------------------------------------------------------

    @staticmethod
    async def execute_revision_workflow(run_id: str, campaign_id: str, feedback: str) -> None:
        """Re-gera copy e direção criativa de uma campanha existente com feedback humano.

        Diferenças em relação ao workflow completo:
        - NÃO re-executa DataAgent nem StrategyAgent — a estratégia aprovada na
          campanha original é preservada e reconstruída a partir do banco.
        - O comentário da revisão entra nos prompts como instrução prioritária.
        - Post e CreativeBrief existentes são ATUALIZADOS (não duplicados) e uma
          NOVA Approval pendente é criada para a decisão humana.
        """
        from sqlalchemy.orm import selectinload

        async with AsyncSessionLocal() as db:
            try:
                await SupervisorService._mark_running(db, run_id)

                # --- Carrega campanha com artefatos e produto associado ---
                result = await db.execute(
                    select(Campaign)
                    .options(selectinload(Campaign.posts), selectinload(Campaign.creative_briefs))
                    .where(Campaign.id == campaign_id)
                )
                campaign = result.scalar_one_or_none()
                if campaign is None:
                    raise ValueError(f"Campanha '{campaign_id}' não encontrada para re-geração.")
                if not campaign.product_id:
                    raise ValueError("Campanha sem produto associado — re-geração indisponível.")

                product_result = await db.execute(
                    select(Product)
                    .options(selectinload(Product.variants))
                    .where(Product.id == campaign.product_id)
                    .where(Product.is_active == True)
                )
                product = product_result.scalar_one_or_none()
                if product is None:
                    raise ValueError("Produto da campanha não existe mais ou está inativo.")

                # O estoque pode ter mudado desde a geração original — revalida.
                total_stock = sum(v.stock_quantity for v in product.variants)
                stock_policy = PolicyEngine.validate_campaign_product_has_stock(total_stock)
                if not stock_policy.ok:
                    raise ValueError(f"PolicyEngine bloqueou a re-geração: {stock_policy.reason}")

                # --- Reconstrói a estratégia a partir da campanha persistida ---
                strategy_output = StrategyAgentOutput(
                    campaign=CampaignStrategy(
                        name=campaign.name,
                        objective=campaign.objective,
                        product_name=product.name,
                        product_sku=product.sku,
                        channel=campaign.channel,
                        format=campaign.format,
                        angle=campaign.angle,
                        cta=campaign.cta,
                        risk_level=campaign.risk_level,
                        reasoning="Re-geração pós-revisão: estratégia original preservada.",
                    )
                )

                brand_ctx = await KnowledgeService.get_brand_context(db)
                creative_ctx = await KnowledgeService.get_creative_context(db)

                # --- ContentAgent com feedback ---
                logger.info("[%s] ContentAgent (revisão) iniciado", run_id)
                content_output = await _run_content_agent(strategy_output, brand_ctx, feedback)
                _validate_content_policies(content_output)

                # --- Atualiza o Post existente (ou cria, se a campanha não tiver) ---
                if campaign.posts:
                    post = campaign.posts[-1]
                    post.caption = content_output.caption
                    post.headline = content_output.headline
                    post.cta_text = content_output.cta_text
                    post.copy_variations = [
                        {"style": v.style, "caption": v.caption, "headline": v.headline}
                        for v in content_output.variations
                    ]
                    await db.flush()
                else:
                    post = await _save_post(db, campaign.id, content_output, strategy_output)

                # --- CreativeAgent com feedback ---
                logger.info("[%s] CreativeAgent (revisão) iniciado", run_id)
                photos = _extract_product_photos(product)
                creative_output = await _run_creative_agent(
                    strategy_output, content_output, photos, creative_ctx, feedback
                )

                if campaign.creative_briefs:
                    brief = campaign.creative_briefs[-1]
                    brief.visual_briefing = creative_output.visual_briefing
                    brief.image_prompt = creative_output.image_prompt
                    brief.carousel_idea = creative_output.carousel_idea
                    brief.reel_script = creative_output.reel_script_outline
                    brief.photo_analysis = {"recommendations": creative_output.photo_recommendations}
                    await db.flush()
                else:
                    brief = await _save_creative_brief(db, campaign.id, creative_output)

                # --- Nova rodada de aprovação humana ---
                approval = await _create_approval(db, campaign.id)

                await SupervisorService._mark_completed(db, run_id, {
                    "campaign_id": campaign.id,
                    "campaign_name": campaign.name,
                    "post_id": post.id,
                    "creative_brief_id": brief.id,
                    "approval_id": approval.id,
                    "revision": True,
                })
                logger.info("[%s] Re-geração concluída com sucesso", run_id)

            except Exception as exc:
                logger.exception("[%s] Re-geração falhou: %s", run_id, exc)
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
    valid_skus: list[str] | None = None,
) -> StrategyAgentOutput:
    agent = build_strategy_agent()
    prompt = build_strategy_agent_input(objective, data_output, strategy_ctx, valid_skus)
    response = await agent.arun(prompt)
    if isinstance(response.content, StrategyAgentOutput):
        return response.content
    raise ValueError(f"StrategyAgent retornou output inesperado: {type(response.content)}")


async def _run_content_agent(
    strategy_output: StrategyAgentOutput,
    brand_ctx: str,
    revision_feedback: str | None = None,
) -> ContentAgentOutput:
    agent = build_content_agent()
    prompt = build_content_agent_input(strategy_output, brand_ctx, revision_feedback)
    response = await agent.arun(prompt)
    if isinstance(response.content, ContentAgentOutput):
        return response.content
    raise ValueError(f"ContentAgent retornou output inesperado: {type(response.content)}")


async def _run_creative_agent(
    strategy_output: StrategyAgentOutput,
    content_output: ContentAgentOutput,
    product_photos: list[dict],
    creative_ctx: str,
    revision_feedback: str | None = None,
) -> CreativeAgentOutput:
    agent = build_creative_agent()
    prompt = build_creative_agent_input(
        strategy_output, content_output, product_photos, creative_ctx, revision_feedback
    )
    response = await agent.arun(prompt)
    if isinstance(response.content, CreativeAgentOutput):
        return response.content
    raise ValueError(f"CreativeAgent retornou output inesperado: {type(response.content)}")


async def _load_active_skus(db: AsyncSession) -> list[str]:
    """Retorna os SKUs de todos os produtos ativos do catálogo."""
    result = await db.execute(select(Product.sku).where(Product.is_active == True))
    return [row[0] for row in result.all()]


def _normalize_sku_tokens(sku: str) -> frozenset:
    """Normaliza um SKU em conjunto de tokens alfanuméricos maiúsculos.

    Permite reconhecer SKUs que o LLM reordenou ou cujos separadores foram
    alterados (ex.: 'BR02-MANTO' e 'MANTO-BR02' têm os mesmos tokens).
    """
    import re

    return frozenset(t for t in re.split(r"[^A-Za-z0-9]+", sku.upper()) if t)


async def _resolve_campaign_product(
    db: AsyncSession,
    product_sku: str,
    product_name: str | None = None,
) -> Product | None:
    """Resolve o SKU indicado pelo StrategyAgent para um produto ativo do catálogo.

    O LLM pode alucinar ou distorcer SKUs, então a resolução é feita em camadas
    determinísticas — todas exigem correspondência inambígua com o catálogo:
      1. SKU exato.
      2. SKU ignorando maiúsculas/minúsculas.
      3. Mesmos tokens alfanuméricos (captura reordenação tipo 'BR02-MANTO').
      4. Nome do produto exato (ignorando caixa), como último recurso.
    Retorna None se nenhuma camada encontrar exatamente um produto.
    """
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.is_active == True)
    )
    products = result.scalars().all()

    # Camada 1 — correspondência exata.
    for p in products:
        if p.sku == product_sku:
            return p

    # Camada 2 — sem diferenciar caixa.
    matches = [p for p in products if p.sku.upper() == product_sku.upper()]
    if len(matches) == 1:
        logger.warning("SKU '%s' resolvido por caixa para '%s'", product_sku, matches[0].sku)
        return matches[0]

    # Camada 3 — mesmos tokens (reordenação/separadores trocados pelo LLM).
    target = _normalize_sku_tokens(product_sku)
    if target:
        matches = [p for p in products if _normalize_sku_tokens(p.sku) == target]
        if len(matches) == 1:
            logger.warning("SKU '%s' resolvido por tokens para '%s'", product_sku, matches[0].sku)
            return matches[0]

    # Camada 4 — nome exato do produto (último recurso, também inambíguo).
    if product_name:
        wanted = product_name.strip().lower()
        matches = [p for p in products if p.name.strip().lower() == wanted]
        if len(matches) == 1:
            logger.warning("SKU '%s' resolvido pelo nome '%s'", product_sku, matches[0].sku)
            return matches[0]

    return None


def _extract_product_photos(product: Product) -> list[dict]:
    """Extrai a lista de fotos do produto já resolvido. Retorna lista vazia se não houver."""
    if not product.photos:
        return []
    photos = product.photos if isinstance(product.photos, list) else []
    return [p for p in photos if isinstance(p, dict)]


def _validate_content_policies(content_output: ContentAgentOutput) -> None:
    """Aplica as validações determinísticas de conteúdo do PolicyEngine.

    Verifica legenda, título e todas as variações de copy. Qualquer bloqueio
    interrompe o run com o motivo — preço ou promessa de estoque nunca podem
    vir do LLM.
    """
    texts = [content_output.caption, content_output.headline, content_output.cta_text]
    for variation in content_output.variations:
        texts.extend([variation.caption, variation.headline])

    for text in texts:
        if not text:
            continue
        for check in (
            PolicyEngine.validate_content_has_no_invented_price,
            PolicyEngine.validate_content_has_no_stock_promise,
        ):
            policy = check(text)
            if not policy.ok:
                raise ValueError(f"PolicyEngine bloqueou o copy gerado: {policy.reason}")


def _fit(text: str | None, limit: int) -> str | None:
    """Corta o texto no limite da coluna, preservando o início.

    Proteção contra outputs de LLM maiores que o schema — ex.: o StrategyAgent
    pode devolver uma descrição inteira no campo `format` (VARCHAR(100)), o que
    derrubaria o INSERT com StringDataRightTruncationError.
    """
    if text is None:
        return None
    return text if len(text) <= limit else text[:limit].rstrip()


async def _save_campaign(
    db: AsyncSession,
    run_id: str,
    strategy_output: StrategyAgentOutput,
    product_id: str,
) -> Campaign:
    c = strategy_output.campaign
    campaign = Campaign(
        agent_run_id=run_id,
        name=_fit(c.name, 255),
        objective=c.objective,
        product_id=product_id,
        channel=_fit(c.channel, 100),
        format=_fit(c.format, 100),
        angle=c.angle,
        cta=c.cta,
        risk_level=_fit(c.risk_level, 50),
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
        format=_fit(strategy_output.campaign.format, 100),
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
