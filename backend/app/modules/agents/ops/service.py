"""OpsService — queries de agregação para observabilidade da camada de agentes."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.knowledge.models import KnowledgeDocument
from app.modules.agents.marketing_ops.models import AgentRun, Approval, Campaign
from app.modules.agents.ops.schemas import OpsMetrics


class OpsService:

    @staticmethod
    async def get_metrics(db: AsyncSession) -> OpsMetrics:
        """Retorna métricas consolidadas: runs, aprovações, campanhas e knowledge."""

        # Contagem de runs por status
        run_result = await db.execute(
            select(AgentRun.status, func.count(AgentRun.id).label("n"))
            .group_by(AgentRun.status)
        )
        run_map = {row[0]: row[1] for row in run_result.all()}
        total = sum(run_map.values())
        completed = run_map.get("completed", 0)
        success_rate = round(completed / total * 100, 1) if total > 0 else 0.0

        # Aprovações pendentes
        pending_result = await db.execute(
            select(func.count(Approval.id)).where(Approval.status == "pending")
        )
        pending_approvals = pending_result.scalar() or 0

        # Campanhas por status
        campaign_result = await db.execute(
            select(Campaign.status, func.count(Campaign.id).label("n"))
            .group_by(Campaign.status)
        )
        campaign_map = {row[0]: row[1] for row in campaign_result.all()}

        # Knowledge documents ativos
        knowledge_result = await db.execute(
            select(func.count(KnowledgeDocument.id))
            .where(KnowledgeDocument.is_active.is_(True))
        )
        knowledge_active = knowledge_result.scalar() or 0

        return OpsMetrics(
            total_runs=total,
            runs_pending=run_map.get("pending", 0),
            runs_running=run_map.get("running", 0),
            runs_completed=completed,
            runs_failed=run_map.get("failed", 0),
            success_rate=success_rate,
            pending_approvals=pending_approvals,
            approved_campaigns=campaign_map.get("approved", 0),
            rejected_campaigns=campaign_map.get("rejected", 0),
            knowledge_docs_active=knowledge_active,
        )
