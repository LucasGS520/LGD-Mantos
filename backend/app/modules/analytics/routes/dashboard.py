"""Rota do dashboard executivo."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await DashboardService.dashboard(db)
