"""Endpoints do domínio operacional com delegação para serviços."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operational.services import ExpenseService, PurchaseService, SalesService, StockService
from modules.shared.schemas import ExpenseIn, ExpenseOut, POIn, POOut, SaleIn, SaleOut, StockMoveIn, StockMoveOut
from modules.shared.services import get_db, verify_token

router = APIRouter(prefix="/operational", tags=["operational"])


@router.post("/stock/movements", response_model=StockMoveOut)
async def stock_movement(data: StockMoveIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Valida payload e delega registro de movimentação ao serviço de estoque."""
    return await StockService(db).register_movement(data)


@router.get("/stock/alerts")
async def stock_alerts(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna alertas de estoque tratados pela camada de serviço."""
    return await StockService(db).list_alerts()


@router.get("/stock/history/{variant_id}")
async def stock_history(variant_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista histórico de movimentações de uma variante."""
    return await StockService(db).list_history(variant_id)


@router.get("/sales", response_model=list[SaleOut])
async def list_sales(limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista vendas recentes conforme limite informado."""
    return await SalesService(db).list_sales(limit=limit)


@router.post("/sales", response_model=SaleOut)
async def create_sale(data: SaleIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria venda e aplica regras de estoque via serviço."""
    return await SalesService(db).create_sale(data)


@router.get("/expenses", response_model=list[ExpenseOut])
async def list_expenses(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista despesas operacionais recentes."""
    return await ExpenseService(db).list_expenses()


@router.post("/expenses", response_model=ExpenseOut)
async def create_expense(data: ExpenseIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria despesa no fluxo transacional do serviço."""
    return await ExpenseService(db).create_expense(data)


@router.delete("/expenses/{eid}")
async def delete_expense(eid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Exclui despesa por identificador."""
    await ExpenseService(db).delete_expense(eid)
    return {"ok": True}


@router.get("/purchases", response_model=list[POOut])
async def list_purchases(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista pedidos de compra com itens."""
    return await PurchaseService(db).list_purchases()


@router.post("/purchases", response_model=POOut)
async def create_purchase(data: POIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria pedido de compra a partir do serviço de compras."""
    return await PurchaseService(db).create_purchase(data)


@router.put("/purchases/{po_id}/receive")
async def receive_purchase(po_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Recebe pedido de compra e atualiza estoques."""
    await PurchaseService(db).receive_purchase(po_id)
    return {"ok": True}
