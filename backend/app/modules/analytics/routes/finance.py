"""Rotas de análise financeira e DRE."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.finance_service import FinanceService

router = APIRouter()


@router.get("/finance/dre")
async def dre(
    month: int | None = Query(None),
    year: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    return await FinanceService.dre(db, month, year)
