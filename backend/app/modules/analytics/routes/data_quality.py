"""Rota de qualidade dos dados — score e problemas detectados."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.data_quality_service import DataQualityService

router = APIRouter()


@router.get("/data-quality")
async def data_quality(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna score de qualidade dos dados e lista de inconsistências por tipo."""
    return await DataQualityService.data_quality(db)
