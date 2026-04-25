"""Rotas HTTP para pedidos de compra e recebimento de mercadoria."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.operational import repositories as repo
from app.modules.operational.services.purchase_service import PurchaseService
from app.shared.schemas.operations import POIn, POOut

router = APIRouter(tags=["operational"])


@router.get("/purchases", response_model=list[POOut])
async def list_purchases(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista pedidos de compra recentes."""

    return await repo.list_purchases(db)


@router.post("/purchases", response_model=POOut)
async def create_purchase(data: POIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria pedido de compra para um fornecedor."""

    return await PurchaseService.create_purchase(db, data)


@router.put("/purchases/{po_id}/receive")
async def receive_purchase(po_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Confirma recebimento de compra e aplica entrada no estoque."""

    return await PurchaseService.receive_purchase(db, po_id)
