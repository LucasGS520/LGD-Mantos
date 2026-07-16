"""Rotas do Supervisor — entry point para criação e monitoramento de agent runs."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.agents.marketing_ops.models import AgentRun
from app.modules.agents.supervisor.schemas import RunRequest, RunStatus
from app.modules.agents.supervisor.service import SupervisorService

router = APIRouter(prefix="/runs", tags=["agent-runs"])


@router.post("", response_model=RunStatus, status_code=202)
async def create_run(
    body: RunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Cria um agent run e dispara o pipeline de geração de campanha em background.

    Retorna imediatamente com status 'pending'. Use GET /runs/{run_id} para polling.
    """
    run = await SupervisorService.create_run(db, body.objective)
    background_tasks.add_task(SupervisorService.execute_workflow, run.id, body.objective)
    return RunStatus(
        run_id=run.id,
        status=run.status,
        objective=run.objective,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


@router.get("", response_model=list[RunStatus])
async def list_runs(
    status: str | None = Query(default=None, description="pending | running | completed | failed"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Lista agent runs com paginação e filtro opcional por status."""
    q = select(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit).offset(offset)
    if status:
        q = q.where(AgentRun.status == status)
    result = await db.execute(q)
    runs = result.scalars().all()
    return [
        RunStatus(
            run_id=r.id,
            status=r.status,
            objective=r.objective,
            created_at=r.created_at,
            updated_at=r.updated_at,
            error=r.error,
            result=r.result,
        )
        for r in runs
    ]


@router.get("/{run_id}", response_model=RunStatus)
async def get_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Retorna o status atual de um agent run — use para polling após criar um run."""
    run = await SupervisorService.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run não encontrado")
    return RunStatus(
        run_id=run.id,
        status=run.status,
        objective=run.objective,
        created_at=run.created_at,
        updated_at=run.updated_at,
        error=run.error,
        result=run.result,
    )
