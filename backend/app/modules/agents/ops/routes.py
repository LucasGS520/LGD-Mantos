"""Rotas de observabilidade da camada de agentes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.agents.ops.schemas import OpsMetrics
from app.modules.agents.ops.service import OpsService

router = APIRouter(prefix="/ops", tags=["agent-ops"])


@router.get("/metrics", response_model=OpsMetrics)
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Métricas consolidadas da camada de agentes: runs, aprovações, campanhas e knowledge."""
    return await OpsService.get_metrics(db)
