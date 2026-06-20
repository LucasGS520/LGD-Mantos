"""Rotas de análise centradas em categoria."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.schemas.categories import (
    CategoryCoverage,
    CategoryPerformance,
    CategorySizeDistribution,
    ProductAttributeAnalysis,
)
from app.modules.analytics.services.category_analysis_service import CategoryAnalysisService

router = APIRouter(tags=["analytics"])


@router.get("/categories/performance", response_model=list[CategoryPerformance])
async def category_performance(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Performance por categoria: receita, margem e velocidade diária."""
    return await CategoryAnalysisService.performance(db, days)


@router.get("/categories/size-distribution", response_model=list[CategorySizeDistribution])
async def category_size_distribution(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Distribuição de vendas por tamanho dentro de cada categoria."""
    return await CategoryAnalysisService.size_distribution(db, days)


@router.get("/categories/stock-coverage", response_model=list[CategoryCoverage])
async def category_stock_coverage(
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Cobertura de estoque por categoria em dias de venda."""
    return await CategoryAnalysisService.stock_coverage(db)


@router.get("/categories/buying-patterns")
async def category_buying_patterns(
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Padrões de compra por categoria baseados nos últimos 90 dias."""
    return await CategoryAnalysisService.buying_patterns(db)


@router.get("/products/attributes", response_model=ProductAttributeAnalysis)
async def product_attribute_analysis(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Análise por marca e tipo de produto (drill-down secundário)."""
    return await CategoryAnalysisService.attribute_analysis(db, days)
