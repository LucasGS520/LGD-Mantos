"""Endpoints do domínio operacional."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.shared.models import (
    Expense,
    ProductVariant,
    PurchaseOrder,
    PurchaseOrderItem,
    Sale,
    SaleItem,
    StockMovement,
)
from modules.shared.schemas import ExpenseIn, ExpenseOut, POIn, POOut, SaleIn, SaleOut, StockMoveIn, StockMoveOut
from modules.shared.services import get_db, verify_token

router = APIRouter(prefix="/operational", tags=["operational"])


@router.post("/stock/movements", response_model=StockMoveOut)
async def stock_movement(data: StockMoveIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Registra movimentações de estoque e atualiza o saldo da variante."""
    r = await db.execute(select(ProductVariant).where(ProductVariant.id == data.variant_id))
    variant = r.scalar_one_or_none()
    if not variant:
        raise HTTPException(404, "Variante não encontrada")

    if data.movement_type == "entrada":
        variant.stock_quantity += data.quantity
    elif data.movement_type == "saida":
        if variant.stock_quantity < data.quantity:
            raise HTTPException(400, "Estoque insuficiente")
        variant.stock_quantity -= data.quantity
    elif data.movement_type == "ajuste":
        variant.stock_quantity = data.quantity
    elif data.movement_type == "devolucao":
        variant.stock_quantity += data.quantity

    movement = StockMovement(**data.model_dump())
    db.add(movement)
    await db.flush()
    return movement


@router.get("/stock/alerts")
async def stock_alerts(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista variantes com estoque em nível de alerta."""
    r = await db.execute(
        select(ProductVariant)
        .options(selectinload(ProductVariant.product))
        .where(ProductVariant.stock_quantity <= ProductVariant.min_stock_alert)
    )
    return [
        {
            "variant_id": v.id,
            "product_name": v.product.name,
            "sku": v.product.sku,
            "size": v.size,
            "color": v.color,
            "stock": v.stock_quantity,
            "min": v.min_stock_alert,
        }
        for v in r.scalars().all()
    ]


@router.get("/stock/history/{variant_id}")
async def stock_history(variant_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna o histórico recente de movimentações de uma variante."""
    r = await db.execute(
        select(StockMovement)
        .where(StockMovement.variant_id == variant_id)
        .order_by(StockMovement.created_at.desc())
        .limit(60)
    )
    return r.scalars().all()


@router.get("/sales", response_model=list[SaleOut])
async def list_sales(
    limit: int = Query(100), db: AsyncSession = Depends(get_db), _=Depends(verify_token)
):
    """Lista as vendas mais recentes com itens agregados."""
    r = await db.execute(select(Sale).options(selectinload(Sale.items)).order_by(Sale.sold_at.desc()).limit(limit))
    return r.scalars().all()


@router.post("/sales", response_model=SaleOut)
async def create_sale(data: SaleIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria uma venda, baixa estoque e registra saída de estoque automática."""
    if not data.items:
        raise HTTPException(400, "Sem itens")

    total = 0.0
    pairs = []
    for item in data.items:
        r = await db.execute(select(ProductVariant).where(ProductVariant.id == item.variant_id))
        variant = r.scalar_one_or_none()
        if not variant:
            raise HTTPException(404, f"Variante {item.variant_id}")
        if variant.stock_quantity < item.quantity:
            raise HTTPException(400, f"Estoque insuficiente: {variant.size}/{variant.color}")

        total += item.unit_price * item.quantity
        pairs.append((variant, item))

    sale = Sale(channel=data.channel, notes=data.notes, total=round(total, 2))
    db.add(sale)
    await db.flush()

    for variant, item in pairs:
        db.add(
            SaleItem(
                sale_id=sale.id,
                variant_id=variant.id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                unit_cost=item.unit_cost,
            )
        )
        variant.stock_quantity -= item.quantity
        db.add(
            StockMovement(
                variant_id=variant.id,
                movement_type="saida",
                quantity=item.quantity,
                notes=f"Venda #{sale.id[:8]}",
            )
        )

    await db.flush()
    await db.refresh(sale, ["items"])
    return sale


@router.get("/expenses", response_model=list[ExpenseOut])
async def list_expenses(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna as despesas ordenadas da mais recente para a mais antiga."""
    r = await db.execute(select(Expense).order_by(Expense.date.desc()).limit(200))
    return r.scalars().all()


@router.post("/expenses", response_model=ExpenseOut)
async def create_expense(data: ExpenseIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria um registro de despesa."""
    expense = Expense(**data.model_dump())
    db.add(expense)
    await db.flush()
    return expense


@router.delete("/expenses/{eid}")
async def delete_expense(eid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Exclui uma despesa por identificador."""
    r = await db.execute(select(Expense).where(Expense.id == eid))
    expense = r.scalar_one_or_none()
    if not expense:
        raise HTTPException(404)

    await db.delete(expense)
    return {"ok": True}


@router.get("/purchases", response_model=list[POOut])
async def list_purchases(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista pedidos de compra e seus itens."""
    r = await db.execute(
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .order_by(PurchaseOrder.order_date.desc())
        .limit(100)
    )
    return r.scalars().all()


@router.post("/purchases", response_model=POOut)
async def create_purchase(data: POIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria pedido de compra com itens iniciais."""
    purchase = PurchaseOrder(supplier_id=data.supplier_id, order_date=data.order_date, notes=data.notes)
    db.add(purchase)
    await db.flush()

    for item in data.items:
        db.add(PurchaseOrderItem(order_id=purchase.id, **item.model_dump()))

    await db.flush()
    return purchase


@router.put("/purchases/{po_id}/receive")
async def receive_purchase(po_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Marca pedido como recebido e incrementa o estoque das variantes."""
    r = await db.execute(
        select(PurchaseOrder).options(selectinload(PurchaseOrder.items)).where(PurchaseOrder.id == po_id)
    )
    purchase = r.scalar_one_or_none()
    if not purchase:
        raise HTTPException(404)
    if purchase.status == "recebido":
        raise HTTPException(400, "Já recebido")

    purchase.status = "recebido"
    for item in purchase.items:
        r2 = await db.execute(select(ProductVariant).where(ProductVariant.id == item.variant_id))
        variant = r2.scalar_one_or_none()
        if variant:
            variant.stock_quantity += item.quantity
            db.add(
                StockMovement(
                    variant_id=variant.id,
                    movement_type="entrada",
                    quantity=item.quantity,
                    unit_cost=item.unit_cost,
                    notes=f"Compra #{purchase.id[:8]}",
                )
            )

    return {"ok": True}
