"""Consultas sobre vendas, receita e velocidade de variantes."""

from datetime import datetime

from sqlalchemy import cast, Date, func, select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.operations import Sale, SaleItem


async def month_revenue(db: AsyncSession, start: datetime, end: datetime | None = None) -> float:
    query = select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at >= start)
    if end:
        query = query.where(Sale.sold_at < end)
    result = await db.execute(query)
    return float(result.scalar())


async def month_cogs(db: AsyncSession, start: datetime, end: datetime | None = None) -> float:
    query = (
        select(func.coalesce(func.sum(SaleItem.unit_cost * SaleItem.quantity), 0))
        .join(Sale)
        .where(Sale.sold_at >= start)
    )
    if end:
        query = query.where(Sale.sold_at < end)
    result = await db.execute(query)
    return float(result.scalar())


async def sales_count_since(db: AsyncSession, since: datetime) -> int:
    result = await db.execute(select(func.count(Sale.id)).where(Sale.sold_at >= since))
    return int(result.scalar())


async def revenue_since(db: AsyncSession, since: datetime) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at >= since)
    )
    return float(result.scalar())


async def daily_revenue(db: AsyncSession, start: datetime, end: datetime) -> float:
    """Soma o faturamento de um intervalo fechado de datas (mantido para compatibilidade)."""
    result = await db.execute(
        select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at.between(start, end))
    )
    return float(result.scalar())


async def daily_revenue_series(db: AsyncSession, start: datetime, end: datetime) -> dict[str, float]:
    """Retorna receita por dia como {YYYY-MM-DD: float} em uma única query SQL."""
    result = await db.execute(
        select(
            cast(Sale.sold_at, Date).label("day"),
            func.coalesce(func.sum(Sale.total), 0).label("total"),
        )
        .where(Sale.sold_at.between(start, end))
        .group_by(cast(Sale.sold_at, Date))
        .order_by(cast(Sale.sold_at, Date))
    )
    return {str(row.day): float(row.total) for row in result}


async def sales_by_channel(db: AsyncSession, since: datetime, end: datetime | None = None):
    from app.shared.models.catalog import SaleChannel
    query = (
        select(
            func.coalesce(SaleChannel.name, "Sem canal").label("channel_name"),
            func.count(Sale.id).label("count"),
            func.coalesce(func.sum(Sale.total), 0).label("total"),
        )
        .outerjoin(SaleChannel, Sale.sale_channel_id == SaleChannel.id)
        .where(Sale.sold_at >= since)
        .group_by(SaleChannel.name, Sale.sale_channel_id)
    )
    if end:
        query = query.where(Sale.sold_at < end)
    result = await db.execute(query)
    return result.all()


async def units_sold_since(db: AsyncSession, since: datetime) -> int:
    """Soma todas as unidades vendidas desde o instante informado."""
    result = await db.execute(
        select(func.coalesce(func.sum(SaleItem.quantity), 0))
        .join(Sale)
        .where(Sale.sold_at >= since)
    )
    return int(result.scalar())


async def variant_velocity_30d(db: AsyncSession, since: datetime) -> dict[str, int]:
    result = await db.execute(
        select(SaleItem.variant_id, func.sum(SaleItem.quantity).label("sold30"))
        .join(Sale)
        .where(Sale.sold_at >= since)
        .group_by(SaleItem.variant_id)
    )
    return {row.variant_id: int(row.sold30) for row in result}
