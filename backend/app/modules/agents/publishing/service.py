"""PublishingService — gerencia a fila de publicação de campanhas aprovadas."""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.marketing_ops.models import Approval, Campaign, PublishingQueue
from app.modules.agents.policy_engine import PolicyEngine


class PublishingService:

    @staticmethod
    async def queue_campaign(
        db: AsyncSession,
        campaign_id: str,
        channel: str,
        scheduled_at: datetime | None = None,
    ) -> PublishingQueue:
        """Enfileira campanha para publicação.

        Requer aprovação humana registrada — PolicyEngine.validate_publish_requires_approval()
        é chamado antes de qualquer operação de fila.
        """
        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campanha não encontrada")

        # Busca aprovação registrada para a campanha
        result = await db.execute(
            select(Approval)
            .where(Approval.campaign_id == campaign_id)
            .order_by(Approval.created_at.desc())
        )
        approval = result.scalar_one_or_none()
        approval_status = approval.status if approval else "none"

        # Validação determinística: publicação exige aprovação
        policy = PolicyEngine.validate_publish_requires_approval(approval_status)
        if not policy.ok:
            raise HTTPException(status_code=403, detail=policy.reason)

        entry = PublishingQueue(
            campaign_id=campaign_id,
            channel=channel,
            scheduled_at=scheduled_at,
            status="approved",
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def list_queue(db: AsyncSession, status: str | None = None) -> list[PublishingQueue]:
        """Lista a fila de publicação com filtro opcional por status."""
        q = select(PublishingQueue).order_by(PublishingQueue.created_at.desc())
        if status:
            q = q.where(PublishingQueue.status == status)
        result = await db.execute(q)
        return result.scalars().all()
