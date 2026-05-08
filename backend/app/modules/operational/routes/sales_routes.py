"""Rotas HTTP para consulta e registro de vendas."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.operational import repositories as repo
from app.modules.operational.services.sales_service import SalesService
from app.shared.schemas.operations import SaleIn, SaleOut

router = APIRouter(tags=["operational"])


@router.get("/sales", response_model=list[SaleOut])
async def list_sales(limit: int = Query(100), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista vendas recentes respeitando o limite informado."""

    return await repo.list_sales(db, limit)


@router.post("/sales", response_model=SaleOut)
async def create_sale(data: SaleIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Registra uma venda e delega a baixa de estoque ao serviço."""

    return await SalesService.create_sale(db, data)


@router.delete("/sales/{sid}")
async def delete_sale(sid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Remove uma venda e estorna o estoque dos itens correspondentes."""

    return await SalesService.delete_sale(db, sid)
