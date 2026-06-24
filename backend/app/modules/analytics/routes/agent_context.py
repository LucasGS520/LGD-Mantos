"""Rota de contexto para agentes de IA — payload analítico agregado e curado."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.agent_context_service import AgentContextService

router = APIRouter()


@router.get("/agent-context")
async def agent_context(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna pacote estruturado com saúde da loja, alertas e oportunidades."""
    return await AgentContextService.agent_context(db)
