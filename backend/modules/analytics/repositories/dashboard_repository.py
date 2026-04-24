"""Repositório analítico com consultas de dashboard e relatórios."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.shared.models import Expense, Product, ProductVariant, Sale, SaleItem


class DashboardRepository:
    """Encapsula consultas SQLAlchemy usadas pelos serviços analíticos."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def month_revenue(self, month_start: datetime) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.sum(SaleItem.unit_price * SaleItem.quantity), 0)).join(Sale).where(Sale.sold_at >= month_start)
        )
        return float(result.scalar())

    async def month_cogs(self, month_start: datetime) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.sum(SaleItem.unit_cost * SaleItem.quantity), 0)).join(Sale).where(Sale.sold_at >= month_start)
        )
        return float(result.scalar())

    async def month_expenses(self, month_start_str: str) -> float:
        result = await self.db.execute(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.date >= month_start_str))
        return float(result.scalar())

    async def today_count(self, today_start: datetime) -> int:
        result = await self.db.execute(select(func.count(Sale.id)).where(Sale.sold_at >= today_start))
        return int(result.scalar())

    async def today_revenue(self, today_start: datetime) -> float:
        result = await self.db.execute(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at >= today_start))
        return float(result.scalar())

    async def stock_alerts(self) -> int:
        result = await self.db.execute(
            select(func.count(ProductVariant.id)).where(ProductVariant.stock_quantity <= ProductVariant.min_stock_alert)
        )
        return int(result.scalar())

    async def stock_values(self) -> tuple[float, float, int]:
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(ProductVariant.stock_quantity * Product.cost_price), 0),
                func.coalesce(func.sum(ProductVariant.stock_quantity * Product.sale_price), 0),
                func.coalesce(func.sum(ProductVariant.stock_quantity), 0),
            )
            .join(Product)
            .where(Product.is_active == True)
        )
        values = result.one()
        return float(values[0]), float(values[1]), int(values[2])

    async def daily_revenue(self, start: datetime, end: datetime) -> float:
        result = await self.db.execute(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at.between(start, end)))
        return float(result.scalar())

    async def top_products(self, since: datetime) -> list[tuple]:
        result = await self.db.execute(
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
        return list(result)

    async def sales_by_size(self, since: datetime) -> list[tuple]:
        result = await self.db.execute(
            select(ProductVariant.size, func.sum(SaleItem.quantity).label("qty"))
            .join(SaleItem, SaleItem.variant_id == ProductVariant.id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .where(Sale.sold_at >= since)
            .group_by(ProductVariant.size)
            .order_by(func.sum(SaleItem.quantity).desc())
        )
        return list(result)

    async def sales_by_channel(self, since: datetime) -> list[tuple]:
        result = await self.db.execute(
            select(Sale.channel, func.count(Sale.id), func.sum(Sale.total)).where(Sale.sold_at >= since).group_by(Sale.channel)
        )
        return list(result)

    async def velocity_30d(self, since: datetime) -> dict[str, int]:
        result = await self.db.execute(
            select(SaleItem.variant_id, func.sum(SaleItem.quantity).label("sold30"))
            .join(Sale)
            .where(Sale.sold_at >= since)
            .group_by(SaleItem.variant_id)
        )
        return {row.variant_id: int(row.sold30) for row in result}

    async def active_variants(self) -> list[ProductVariant]:
        result = await self.db.execute(
            select(ProductVariant).options(selectinload(ProductVariant.product)).join(Product).where(Product.is_active == True)
        )
        return list(result.scalars().all())

    async def dre_revenue(self, start_dt: datetime, end_dt: datetime) -> float:
        result = await self.db.execute(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at.between(start_dt, end_dt)))
        return float(result.scalar())

    async def dre_cogs(self, start_dt: datetime, end_dt: datetime) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.sum(SaleItem.unit_cost * SaleItem.quantity), 0))
            .join(Sale)
            .where(Sale.sold_at.between(start_dt, end_dt))
        )
        return float(result.scalar())

    async def dre_expenses(self, start: str, end: str) -> float:
        result = await self.db.execute(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.date >= start, Expense.date < end))
        return float(result.scalar())
