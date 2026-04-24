"""Endpoints analíticos para dashboards e relatórios operacionais."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.shared.models import Expense, Product, ProductVariant, Sale, SaleItem
from modules.shared.services import get_db, verify_token

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Consolida os principais indicadores financeiros e de estoque do mês."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    rev = await db.execute(
        select(func.coalesce(func.sum(SaleItem.unit_price * SaleItem.quantity), 0))
        .join(Sale)
        .where(Sale.sold_at >= month_start)
    )
    month_revenue = float(rev.scalar())

    cogs = await db.execute(
        select(func.coalesce(func.sum(SaleItem.unit_cost * SaleItem.quantity), 0))
        .join(Sale)
        .where(Sale.sold_at >= month_start)
    )
    month_cogs = float(cogs.scalar())

    exp = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.date >= month_start.strftime("%Y-%m-%d"))
    )
    month_expenses = float(exp.scalar())

    sc = await db.execute(select(func.count(Sale.id)).where(Sale.sold_at >= today_start))
    today_count = int(sc.scalar())

    tr = await db.execute(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at >= today_start))
    today_revenue = float(tr.scalar())

    sa = await db.execute(
        select(func.count(ProductVariant.id)).where(ProductVariant.stock_quantity <= ProductVariant.min_stock_alert)
    )
    alerts = int(sa.scalar())

    sv = await db.execute(
        select(
            func.coalesce(func.sum(ProductVariant.stock_quantity * Product.cost_price), 0),
            func.coalesce(func.sum(ProductVariant.stock_quantity * Product.sale_price), 0),
            func.coalesce(func.sum(ProductVariant.stock_quantity), 0),
        )
        .join(Product)
        .where(Product.is_active == True)
    )
    stock = sv.one()

    daily = []
    # Gera série diária simples para frontend plotar tendência sem pós-processamento.
    for i in range(29, -1, -1):
        d = now - timedelta(days=i)
        ds = d.replace(hour=0, minute=0, second=0, microsecond=0)
        de = d.replace(hour=23, minute=59, second=59, microsecond=999999)
        dr = await db.execute(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at.between(ds, de)))
        daily.append({"date": d.strftime("%d/%m"), "value": float(dr.scalar())})

    gross_profit = month_revenue - month_cogs
    net_profit = gross_profit - month_expenses

    return {
        "today_revenue": today_revenue,
        "today_count": today_count,
        "month_revenue": month_revenue,
        "month_cogs": month_cogs,
        "month_expenses": month_expenses,
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "margin_pct": round(net_profit / month_revenue * 100, 1) if month_revenue else 0,
        "stock_alerts": alerts,
        "stock_cost_value": float(stock[0]),
        "stock_sale_value": float(stock[1]),
        "stock_units": int(stock[2]),
        "daily_revenue": daily,
    }


@router.get("/top-products")
async def top_products(days: int = Query(30), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna produtos mais vendidos por volume no período informado."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    r = await db.execute(
        select(
            Product.name,
            Product.sku,
            func.sum(SaleItem.quantity).label("qty"),
            func.sum(SaleItem.unit_price * SaleItem.quantity).label("revenue"),
            func.sum((SaleItem.unit_price - SaleItem.unit_cost) * SaleItem.quantity).label("profit"),
        )
        .join(ProductVariant, SaleItem.variant_id == ProductVariant.id)
        .join(Product, ProductVariant.product_id == Product.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .group_by(Product.id, Product.name, Product.sku)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(15)
    )
    return [
        {"name": x[0], "sku": x[1], "qty": int(x[2] or 0), "revenue": float(x[3] or 0), "profit": float(x[4] or 0)}
        for x in r
    ]


@router.get("/by-size")
async def sales_by_size(days: int = Query(30), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Agrupa vendas por tamanho para orientar reposição e mix de grade."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    r = await db.execute(
        select(ProductVariant.size, func.sum(SaleItem.quantity).label("qty"))
        .join(SaleItem, SaleItem.variant_id == ProductVariant.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .group_by(ProductVariant.size)
        .order_by(func.sum(SaleItem.quantity).desc())
    )
    return [{"size": x[0], "qty": int(x[1] or 0)} for x in r]


@router.get("/by-channel")
async def sales_by_channel(days: int = Query(30), db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Agrupa vendas por canal para avaliação de performance comercial."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    r = await db.execute(
        select(Sale.channel, func.count(Sale.id), func.sum(Sale.total)).where(Sale.sold_at >= since).group_by(Sale.channel)
    )
    return [{"channel": x[0], "count": int(x[1]), "total": float(x[2] or 0)} for x in r]


@router.get("/purchase-suggestions")
async def purchase_suggestions(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Sugere reposição combinando velocidade de venda e nível de estoque atual."""
    since = datetime.now(timezone.utc) - timedelta(days=30)
    vel = await db.execute(
        select(SaleItem.variant_id, func.sum(SaleItem.quantity).label("sold30"))
        .join(Sale)
        .where(Sale.sold_at >= since)
        .group_by(SaleItem.variant_id)
    )
    velocity = {row.variant_id: int(row.sold30) for row in vel}

    vr = await db.execute(
        select(ProductVariant).options(selectinload(ProductVariant.product)).join(Product).where(Product.is_active == True)
    )
    variants = vr.scalars().all()

    suggestions = []
    for v in variants:
        sold = velocity.get(v.id, 0)
        days_left = (v.stock_quantity / (sold / 30)) if sold > 0 else 999
        score = sold * 2 - v.stock_quantity
        if score > 0 or v.stock_quantity <= v.min_stock_alert:
            suggestions.append(
                {
                    "variant_id": v.id,
                    "product_name": v.product.name,
                    "sku": v.product.sku,
                    "size": v.size,
                    "color": v.color,
                    "stock": v.stock_quantity,
                    "sold_30d": sold,
                    "days_remaining": round(days_left, 1) if days_left < 999 else None,
                    "urgency": "alta" if (v.stock_quantity <= v.min_stock_alert or days_left < 7) else "media",
                    "suggested_qty": max(10, sold * 2 - v.stock_quantity),
                }
            )

    return sorted(suggestions, key=lambda x: (x["urgency"] == "alta", x["sold_30d"]), reverse=True)[:20]


@router.get("/finance/dre")
async def dre(
    month: int = Query(None),
    year: int = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Calcula DRE simplificado por mês com receita, custos, despesas e margem."""
    now = datetime.now(timezone.utc)
    m, y = month or now.month, year or now.year
    start = f"{y}-{m:02d}-01"
    end = f"{y}-{m + 1:02d}-01" if m < 12 else f"{y + 1}-01-01"
    start_dt = datetime(y, m, 1, tzinfo=timezone.utc)
    end_dt = datetime(y, m + 1, 1, tzinfo=timezone.utc) if m < 12 else datetime(y + 1, 1, 1, tzinfo=timezone.utc)

    rev = await db.execute(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at.between(start_dt, end_dt)))
    cogs = await db.execute(
        select(func.coalesce(func.sum(SaleItem.unit_cost * SaleItem.quantity), 0))
        .join(Sale)
        .where(Sale.sold_at.between(start_dt, end_dt))
    )
    exp = await db.execute(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.date >= start, Expense.date < end))

    revenue = float(rev.scalar())
    cogs_val = float(cogs.scalar())
    expenses = float(exp.scalar())
    gross = revenue - cogs_val
    net = gross - expenses

    return {
        "period": f"{m:02d}/{y}",
        "revenue": revenue,
        "cogs": cogs_val,
        "gross_profit": gross,
        "expenses": expenses,
        "net_profit": net,
        "margin_pct": round(net / revenue * 100, 1) if revenue else 0,
    }
