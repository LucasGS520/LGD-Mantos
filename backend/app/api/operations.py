from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.auth import verify_token
from app.models import ProductVariant, StockMovement, Sale, SaleItem, Product, Expense, PurchaseOrder, PurchaseOrderItem
from app.schemas import StockMoveIn, StockMoveOut, SaleIn, SaleOut, ExpenseIn, ExpenseOut, POIn, POOut

router = APIRouter(tags=["operations"])

# ── Stock ──────────────────────────────────────────────────────────────────────
@router.post("/stock/movements", response_model=StockMoveOut)
async def stock_movement(data: StockMoveIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(ProductVariant).where(ProductVariant.id==data.variant_id))
    v = r.scalar_one_or_none()
    if not v: raise HTTPException(404, "Variante não encontrada")
    if data.movement_type == "entrada":    v.stock_quantity += data.quantity
    elif data.movement_type == "saida":
        if v.stock_quantity < data.quantity: raise HTTPException(400, "Estoque insuficiente")
        v.stock_quantity -= data.quantity
    elif data.movement_type == "ajuste":   v.stock_quantity = data.quantity
    elif data.movement_type == "devolucao": v.stock_quantity += data.quantity
    m = StockMovement(**data.model_dump()); db.add(m); await db.flush(); return m

@router.get("/stock/alerts")
async def stock_alerts(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(
        select(ProductVariant).options(selectinload(ProductVariant.product))
        .where(ProductVariant.stock_quantity <= ProductVariant.min_stock_alert)
    )
    return [{"variant_id":v.id,"product_name":v.product.name,"sku":v.product.sku,
             "size":v.size,"color":v.color,"stock":v.stock_quantity,"min":v.min_stock_alert}
            for v in r.scalars().all()]

@router.get("/stock/history/{variant_id}")
async def stock_history(variant_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(
        select(StockMovement).where(StockMovement.variant_id==variant_id)
        .order_by(StockMovement.created_at.desc()).limit(60)
    )
    return r.scalars().all()

# ── Sales ──────────────────────────────────────────────────────────────────────
@router.get("/sales", response_model=list[SaleOut])
async def list_sales(limit: int = Query(100), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Sale).options(selectinload(Sale.items)).order_by(Sale.sold_at.desc()).limit(limit))
    return r.scalars().all()

@router.post("/sales", response_model=SaleOut)
async def create_sale(data: SaleIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    if not data.items: raise HTTPException(400, "Sem itens")
    total = 0.0
    pairs = []
    for item in data.items:
        r = await db.execute(select(ProductVariant).where(ProductVariant.id==item.variant_id))
        v = r.scalar_one_or_none()
        if not v: raise HTTPException(404, f"Variante {item.variant_id}")
        if v.stock_quantity < item.quantity: raise HTTPException(400, f"Estoque insuficiente: {v.size}/{v.color}")
        total += item.unit_price * item.quantity
        pairs.append((v, item))
    sale = Sale(channel=data.channel, notes=data.notes, total=round(total,2))
    db.add(sale); await db.flush()
    for v, item in pairs:
        db.add(SaleItem(sale_id=sale.id, variant_id=v.id, quantity=item.quantity,
                        unit_price=item.unit_price, unit_cost=item.unit_cost))
        v.stock_quantity -= item.quantity
        db.add(StockMovement(variant_id=v.id, movement_type="saida",
                             quantity=item.quantity, notes=f"Venda #{sale.id[:8]}"))
    await db.flush(); await db.refresh(sale, ["items"]); return sale

# ── Expenses ───────────────────────────────────────────────────────────────────
@router.get("/expenses", response_model=list[ExpenseOut])
async def list_expenses(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Expense).order_by(Expense.date.desc()).limit(200))
    return r.scalars().all()

@router.post("/expenses", response_model=ExpenseOut)
async def create_expense(data: ExpenseIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    e = Expense(**data.model_dump()); db.add(e); await db.flush(); return e

@router.delete("/expenses/{eid}")
async def delete_expense(eid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Expense).where(Expense.id==eid))
    e = r.scalar_one_or_none()
    if not e: raise HTTPException(404)
    await db.delete(e); return {"ok": True}

# ── Purchase Orders ────────────────────────────────────────────────────────────
@router.get("/purchases", response_model=list[POOut])
async def list_purchases(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(PurchaseOrder).options(selectinload(PurchaseOrder.items))
                         .order_by(PurchaseOrder.order_date.desc()).limit(100))
    return r.scalars().all()

@router.post("/purchases", response_model=POOut)
async def create_purchase(data: POIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    po = PurchaseOrder(supplier_id=data.supplier_id, order_date=data.order_date, notes=data.notes)
    db.add(po); await db.flush()
    for item in data.items:
        db.add(PurchaseOrderItem(order_id=po.id, **item.model_dump()))
    await db.flush(); return po

@router.put("/purchases/{po_id}/receive")
async def receive_purchase(po_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(PurchaseOrder).options(selectinload(PurchaseOrder.items))
                         .where(PurchaseOrder.id==po_id))
    po = r.scalar_one_or_none()
    if not po: raise HTTPException(404)
    if po.status == "recebido": raise HTTPException(400, "Já recebido")
    po.status = "recebido"
    for item in po.items:
        r2 = await db.execute(select(ProductVariant).where(ProductVariant.id==item.variant_id))
        v = r2.scalar_one_or_none()
        if v:
            v.stock_quantity += item.quantity
            db.add(StockMovement(variant_id=v.id, movement_type="entrada",
                                 quantity=item.quantity, unit_cost=item.unit_cost,
                                 notes=f"Compra #{po.id[:8]}"))
    return {"ok": True}
