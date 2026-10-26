"""Rotas do ApprovalAgent — human-in-the-loop da camada de agentes."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.agents.config import require_agent_model
from app.modules.agents.approval.schemas import (
    ApprovalDetail,
    ApprovalListItem,
    DecisionRequest,
)
from app.modules.agents.approval.service import ApprovalService
from app.modules.agents.marketing_ops.models import Approval
from app.modules.agents.supervisor.schemas import RunStatus
from app.modules.agents.supervisor.service import SupervisorService

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


# ---------------------------------------------------------------------------
# Re-geração pós-revisão
# ---------------------------------------------------------------------------

@router.post("/approvals/{approval_id}/regenerate", response_model=RunStatus, status_code=202)
async def regenerate_after_revision(
    approval_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Re-gera copy e direção criativa usando o comentário da revisão como feedback.

    Só é permitido para aprovações em 'revision_requested'. A estratégia da
    campanha é preservada; apenas ContentAgent e CreativeAgent re-executam.
    Retorna 202 com o run de re-geração — acompanhe via GET /runs/{run_id}.
    """
    require_agent_model()
    approval = await ApprovalService.get_detail(db, approval_id)

    if approval.status != "revision_requested":
        raise HTTPException(
            status_code=409,
            detail=f"Re-geração só é permitida após pedido de revisão "
                   f"(status atual: '{approval.status}').",
        )
    if not approval.campaign_id:
        raise HTTPException(status_code=422, detail="Aprovação sem campanha associada.")

    # Evita re-gerações duplicadas: se já existe nova aprovação pendente para a
    # campanha, uma re-geração anterior já foi concluída.
    pending = await db.execute(
        select(Approval)
        .where(Approval.campaign_id == approval.campaign_id)
        .where(Approval.status == "pending")
    )
    if pending.first():
        raise HTTPException(
            status_code=409,
            detail="Já existe uma aprovação pendente para esta campanha — "
                   "re-geração anterior já concluída.",
        )

    feedback = approval.comment or ""
    campaign_name = approval.campaign.name if approval.campaign else approval.campaign_id
    run = await SupervisorService.create_run(
        db, f"Revisão da campanha '{campaign_name}': {feedback}"
    )
    background_tasks.add_task(
        SupervisorService.execute_revision_workflow, run.id, approval.campaign_id, feedback
    )
    return RunStatus(
        run_id=run.id,
        status=run.status,
        objective=run.objective,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


