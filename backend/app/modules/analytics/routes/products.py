"""Rotas de análise de produtos."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.product_analysis_service import ProductAnalysisService

router = APIRouter()


@router.get("/top-products")
async def top_products(
    period: str | None = Query(None),
    days: int = Query(30),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    return await ProductAnalysisService.top_products(db, period, days)


@router.get("/products/analysis")
async def product_analysis(
    period: str | None = Query(None),
    days: int = Query(30),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Análise completa de produtos: margem, parados e ruptura."""
    return await ProductAnalysisService.product_analysis(db, period, days)
