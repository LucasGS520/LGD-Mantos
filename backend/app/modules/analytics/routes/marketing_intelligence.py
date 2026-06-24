"""Rota de inteligência de marketing — classificação de produtos para ações."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.marketing_intelligence_service import MarketingIntelligenceService

router = APIRouter()


@router.get("/marketing-intelligence")
async def marketing_intelligence(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Classifica produtos em listas de ação: postar, promover, destacar, evitar."""
    return await MarketingIntelligenceService.marketing_intelligence(db)
