"""Rotas do ApprovalAgent — human-in-the-loop da camada de agentes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.agents.approval.schemas import (
    ApprovalDetail,
    ApprovalListItem,
    DecisionRequest,
)
from app.modules.agents.approval.service import ApprovalService

router = APIRouter()


# ---------------------------------------------------------------------------
# Listagem de aprovações
# ---------------------------------------------------------------------------

@router.get("/approvals", response_model=list[ApprovalListItem])
async def list_approvals(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Lista aprovações filtradas por status. Sem filtro retorna todas."""
    approvals = await ApprovalService.list_all(db, status=status)
    return [
        ApprovalListItem(
            id=a.id,
            status=a.status,
            campaign_id=a.campaign_id,
            campaign_name=a.campaign.name if a.campaign else None,
            campaign_channel=a.campaign.channel if a.campaign else None,
            created_at=a.created_at,
        )
        for a in approvals
    ]


@router.get("/approvals/pending", response_model=list[ApprovalListItem])
async def list_pending_approvals(
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Atalho para listar somente aprovações pendentes."""
    approvals = await ApprovalService.list_pending(db)
    return [
        ApprovalListItem(
            id=a.id,
            status=a.status,
            campaign_id=a.campaign_id,
            campaign_name=a.campaign.name if a.campaign else None,
            campaign_channel=a.campaign.channel if a.campaign else None,
            created_at=a.created_at,
        )
        for a in approvals
    ]


@router.get("/approvals/{approval_id}", response_model=ApprovalDetail)
async def get_approval(
    approval_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Detalhe completo de uma aprovação — inclui campanha, posts e briefings."""
    return await ApprovalService.get_detail(db, approval_id)


# ---------------------------------------------------------------------------
# Decisões humanas
# ---------------------------------------------------------------------------

@router.post("/approvals/{approval_id}/approve", response_model=ApprovalDetail)
async def approve(
    approval_id: str,
    body: DecisionRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Aprova campanha, post e briefing. Comentário opcional."""
    return await ApprovalService.approve(db, approval_id, comment=body.comment)


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalDetail)
async def reject(
    approval_id: str,
    body: DecisionRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Rejeita campanha. Comentário explicando o motivo é obrigatório."""
    return await ApprovalService.reject(db, approval_id, comment=body.comment or "")


@router.post("/approvals/{approval_id}/revision", response_model=ApprovalDetail)
async def request_revision(
    approval_id: str,
    body: DecisionRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Solicita revisão da campanha. Comentário com o que ajustar é obrigatório."""
    return await ApprovalService.request_revision(db, approval_id, comment=body.comment or "")


