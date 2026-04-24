from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.operational import repositories as repo
from backend.app.modules.operational.services.sales_service import SalesService
from app.shared.schemas.operations import SaleIn, SaleOut

router = APIRouter(tags=["operational"])


@router.get("/sales", response_model=list[SaleOut])
async def list_sales(limit: int = Query(100), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await repo.list_sales(db, limit)


@router.post("/sales", response_model=SaleOut)
async def create_sale(data: SaleIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await SalesService.create_sale(db, data)
