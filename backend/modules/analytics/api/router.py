"""Endpoints analíticos com rotas finas e delegação para serviços."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from modules.analytics.schemas import (
    DashboardOut,
    DreOut,
    PurchaseSuggestionOut,
    SalesByChannelOut,
    SalesBySizeOut,
    TopProductOut,
)
from modules.analytics.services import DashboardService
from modules.shared.services import get_db, verify_token

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardOut)
async def dashboard(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna indicadores consolidados para o dashboard principal."""
    return await DashboardService(db).dashboard()


@router.get("/top-products", response_model=list[TopProductOut])
async def top_products(days: int = Query(30, ge=1, le=365), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna ranking de produtos por volume e margem."""
    return await DashboardService(db).top_products(days=days)


@router.get("/by-size", response_model=list[SalesBySizeOut])
async def sales_by_size(days: int = Query(30, ge=1, le=365), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Agrupa vendas por tamanho no período informado."""
    return await DashboardService(db).sales_by_size(days=days)


@router.get("/by-channel", response_model=list[SalesByChannelOut])
async def sales_by_channel(days: int = Query(30, ge=1, le=365), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Agrupa vendas por canal no período informado."""
    return await DashboardService(db).sales_by_channel(days=days)


@router.get("/purchase-suggestions", response_model=list[PurchaseSuggestionOut])
async def purchase_suggestions(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista sugestões de reposição calculadas pelo serviço analítico."""
    return await DashboardService(db).purchase_suggestions()


@router.get("/finance/dre", response_model=DreOut)
async def dre(
    month: int = Query(None, ge=1, le=12),
    year: int = Query(None, ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Calcula DRE simplificado para o mês/ano desejado."""
    return await DashboardService(db).dre(month=month, year=year)
