"""Rotas HTTP para dashboards, rankings e indicadores analíticos."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.services import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna os principais indicadores para a tela inicial de análise."""

    return await AnalyticsService.dashboard(db)


@router.get("/top-products")
async def top_products(days: int = Query(30), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna produtos mais vendidos no período informado em dias."""

    return await AnalyticsService.top_products(db, days)


@router.get("/by-size")
async def sales_by_size(days: int = Query(30), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna vendas agrupadas por tamanho."""

    return await AnalyticsService.sales_by_size(db, days)


@router.get("/by-channel")
async def sales_by_channel(days: int = Query(30), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna vendas agrupadas por canal."""

    return await AnalyticsService.sales_by_channel(db, days)


@router.get("/purchase-suggestions")
async def purchase_suggestions(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna sugestões de reposição de estoque."""

    return await AnalyticsService.purchase_suggestions(db)


@router.get("/finance/dre")
async def dre(
    month: int | None = Query(None),
    year: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Retorna DRE simplificado para o mês e ano solicitados."""

    return await AnalyticsService.dre(db, month, year)
