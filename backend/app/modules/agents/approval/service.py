"""ApprovalService — lógica de negócio do human-in-the-loop.

Regras absolutas:
- Aprovação só pode ser feita por um humano (validada pelo PolicyEngine).
- Rejeição e pedido de revisão exigem comentário.
- O serviço nunca chama LLM.
- O serviço nunca publica conteúdo.
"""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.agents.marketing_ops.models import AgentRun, Approval, Campaign, CreativeBrief, Post
from app.modules.agents.policy_engine import PolicyEngine


class ApprovalService:

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    @staticmethod
    async def list_pending(db: AsyncSession) -> list[Approval]:
        """Retorna todas as aprovações com status pending, com campaign carregada."""
        result = await db.execute(
            select(Approval)
            .options(selectinload(Approval.campaign))
            .where(Approval.status == "pending")
            .order_by(Approval.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_all(db: AsyncSession, status: str | None = None) -> list[Approval]:
        """Retorna aprovações filtradas por status (ou todas se status=None)."""
        query = (
            select(Approval)
            .options(selectinload(Approval.campaign))
            .order_by(Approval.created_at.desc())
        )
        if status:
            query = query.where(Approval.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_detail(db: AsyncSession, approval_id: str) -> Approval:
        """Retorna aprovação com campaign, posts e creative_briefs carregados."""
        result = await db.execute(
            select(Approval)
            .options(
                selectinload(Approval.campaign).options(
                    selectinload(Campaign.posts),
                    selectinload(Campaign.creative_briefs),
                )
            )
            .where(Approval.id == approval_id)
        )
        approval = result.scalar_one_or_none()
        if not approval:
            raise HTTPException(status_code=404, detail="Aprovação não encontrada.")
        return approval

    # ------------------------------------------------------------------
    # Decisões — approve / reject / revision
    # ------------------------------------------------------------------

    @staticmethod
    async def approve(db: AsyncSession, approval_id: str, comment: str | None = None) -> Approval:
        """Aprova a campanha. Atualiza status de Approval, Campaign, Posts e Briefs."""
        policy = PolicyEngine.validate_approval_is_human("owner")
        if not policy.ok:
            raise HTTPException(status_code=403, detail=policy.reason)

        approval = await ApprovalService.get_detail(db, approval_id)

        if approval.status != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"Aprovação já foi decidida (status atual: '{approval.status}').",
            )

        approval.status = "approved"
        approval.comment = comment
        approval.decided_at = datetime.now(timezone.utc)

        if approval.campaign:
            approval.campaign.status = "approved"
            for post in approval.campaign.posts:
                post.status = "approved"
            for brief in approval.campaign.creative_briefs:
                brief.status = "approved"

        await db.commit()
        await db.refresh(approval)
        return approval

    @staticmethod
    async def reject(db: AsyncSession, approval_id: str, comment: str) -> Approval:
        """Rejeita a campanha. Comentário obrigatório."""
        if not comment or not comment.strip():
            raise HTTPException(
                status_code=422,
                detail="Comentário é obrigatório ao rejeitar uma aprovação.",
            )

        policy = PolicyEngine.validate_approval_is_human("owner")
        if not policy.ok:
            raise HTTPException(status_code=403, detail=policy.reason)

        approval = await ApprovalService.get_detail(db, approval_id)

        if approval.status != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"Aprovação já foi decidida (status atual: '{approval.status}').",
            )

        approval.status = "rejected"
        approval.comment = comment
        approval.decided_at = datetime.now(timezone.utc)

        if approval.campaign:
            approval.campaign.status = "rejected"
            for post in approval.campaign.posts:
                post.status = "rejected"
            for brief in approval.campaign.creative_briefs:
                brief.status = "rejected"

        await db.commit()
        await db.refresh(approval)
        return approval

    @staticmethod
    async def request_revision(db: AsyncSession, approval_id: str, comment: str) -> Approval:
        """Solicita revisão. Comentário com o que deve ser ajustado é obrigatório."""
        if not comment or not comment.strip():
            raise HTTPException(
                status_code=422,
                detail="Comentário é obrigatório ao solicitar revisão — descreva o que deve ser ajustado.",
            )

        policy = PolicyEngine.validate_approval_is_human("owner")
        if not policy.ok:
            raise HTTPException(status_code=403, detail=policy.reason)

        approval = await ApprovalService.get_detail(db, approval_id)

        if approval.status != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"Aprovação já foi decidida (status atual: '{approval.status}').",
            )

        approval.status = "revision_requested"
        approval.comment = comment
        approval.decided_at = datetime.now(timezone.utc)

        # Conteúdo volta para draft — aguarda re-geração ou edição manual
        if approval.campaign:
            approval.campaign.status = "draft"
            for post in approval.campaign.posts:
                post.status = "draft"
            for brief in approval.campaign.creative_briefs:
                brief.status = "draft"

        await db.commit()
        await db.refresh(approval)
        return approval

    # ------------------------------------------------------------------
    # Status de runs (polling)
    # ------------------------------------------------------------------

    @staticmethod
    async def get_run_status(db: AsyncSession, run_id: str) -> AgentRun:
        """Retorna o estado atual de um agent_run para polling de status."""
        run = await db.get(AgentRun, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Agent run não encontrado.")
        return run
