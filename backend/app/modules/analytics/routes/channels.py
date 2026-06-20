"""Rotas de análise por canal de venda e por tamanho."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.channel_analysis_service import ChannelAnalysisService

router = APIRouter()


@router.get("/by-size")
async def sales_by_size(
    days: int = Query(30),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    return await ChannelAnalysisService.sales_by_size(db, days)


@router.get("/by-channel")
async def sales_by_channel(
    days: int = Query(30),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    return await ChannelAnalysisService.sales_by_channel(db, days)
