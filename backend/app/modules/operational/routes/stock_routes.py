from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.operational import repositories as repo
from backend.app.modules.operational.services.stock_service import StockService
from app.shared.schemas.operations import StockMoveIn, StockMoveOut

router = APIRouter(tags=["operational"])


@router.post("/stock/movements", response_model=StockMoveOut)
async def stock_movement(data: StockMoveIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await StockService.stock_movement(db, data)


@router.get("/stock/alerts")
async def stock_alerts(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await StockService.stock_alerts(db)


@router.get("/stock/history/{variant_id}")
async def stock_history(variant_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await repo.list_stock_history(db, variant_id)
