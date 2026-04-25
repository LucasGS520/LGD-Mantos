"""Consultas agregadas usadas pelo módulo de analytics.

Este arquivo concentra leituras numéricas sobre vendas, despesas, estoque e
velocidade de variantes. Os serviços transformam esses resultados em respostas
mais amigáveis para o app mobile.
"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.shared.models.catalog import Product, ProductVariant
from app.shared.models.operations import Expense, Sale, SaleItem


async def month_revenue(db: AsyncSession, start: datetime, end: datetime | None = None) -> float:
    """Soma o faturamento de vendas a partir de uma data inicial."""

    query = select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at >= start)
    if end:
        query = query.where(Sale.sold_at < end)
    result = await db.execute(query)
    return float(result.scalar())


async def month_cogs(db: AsyncSession, start: datetime, end: datetime | None = None) -> float:
    """Soma o custo dos produtos vendidos no período informado."""

    query = (
        select(func.coalesce(func.sum(SaleItem.unit_cost * SaleItem.quantity), 0))
        .join(Sale)
        .where(Sale.sold_at >= start)
    )
    if end:
        query = query.where(Sale.sold_at < end)
    result = await db.execute(query)
    return float(result.scalar())


async def expenses_total(db: AsyncSession, start: str, end: str | None = None) -> float:
    """Soma despesas por intervalo textual de datas no formato usado pelo modelo."""

    query = select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.date >= start)
    if end:
        query = query.where(Expense.date < end)
    result = await db.execute(query)
    return float(result.scalar())


async def sales_count_since(db: AsyncSession, since: datetime) -> int:
    """Conta vendas registradas desde o instante informado."""

    result = await db.execute(select(func.count(Sale.id)).where(Sale.sold_at >= since))
    return int(result.scalar())


async def revenue_since(db: AsyncSession, since: datetime) -> float:
    """Soma faturamento de vendas desde o instante informado."""

    result = await db.execute(
        select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at >= since)
    )
    return float(result.scalar())


async def stock_alert_count(db: AsyncSession) -> int:
    """Conta variantes com estoque igual ou menor que o mínimo configurado."""

    result = await db.execute(
        select(func.count(ProductVariant.id)).where(
            ProductVariant.stock_quantity <= ProductVariant.min_stock_alert
        )
    )
    return int(result.scalar())


async def stock_value(db: AsyncSession):
    """Calcula valor de custo, valor de venda e unidades totais em estoque ativo."""

    result = await db.execute(
        select(
            func.coalesce(func.sum(ProductVariant.stock_quantity * Product.cost_price), 0),
            func.coalesce(func.sum(ProductVariant.stock_quantity * Product.sale_price), 0),
            func.coalesce(func.sum(ProductVariant.stock_quantity), 0),
        )
        .join(Product)
        .where(Product.is_active == True)
    )
    return result.one()


async def daily_revenue(db: AsyncSession, start: datetime, end: datetime) -> float:
    """Soma o faturamento de um dia ou intervalo fechado de datas."""

    result = await db.execute(
        select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.sold_at.between(start, end))
    )
    return float(result.scalar())


async def top_products(db: AsyncSession, since: datetime):
    """Agrupa produtos mais vendidos por quantidade, receita e lucro bruto."""

    result = await db.execute(
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
    return result.all()


async def sales_by_size(db: AsyncSession, since: datetime):
    """Agrupa a quantidade vendida por tamanho de variante."""

    result = await db.execute(
        select(ProductVariant.size, func.sum(SaleItem.quantity).label("qty"))
        .join(SaleItem, SaleItem.variant_id == ProductVariant.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .group_by(ProductVariant.size)
        .order_by(func.sum(SaleItem.quantity).desc())
    )
    return result.all()


async def sales_by_channel(db: AsyncSession, since: datetime):
    """Agrupa vendas por canal, com quantidade de pedidos e faturamento."""

    result = await db.execute(
        select(Sale.channel, func.count(Sale.id), func.sum(Sale.total))
        .where(Sale.sold_at >= since)
        .group_by(Sale.channel)
    )
    return result.all()


async def variant_velocity_30d(db: AsyncSession, since: datetime) -> dict[str, int]:
    """Calcula quantas unidades cada variante vendeu desde a data informada."""

    result = await db.execute(
        select(SaleItem.variant_id, func.sum(SaleItem.quantity).label("sold30"))
        .join(Sale)
        .where(Sale.sold_at >= since)
        .group_by(SaleItem.variant_id)
    )
    return {row.variant_id: int(row.sold30) for row in result}


async def active_variants(db: AsyncSession) -> list[ProductVariant]:
    """Lista variantes de produtos ativos para cálculo de reposição."""

    result = await db.execute(
        select(ProductVariant)
        .options(selectinload(ProductVariant.product))
        .join(Product)
        .where(Product.is_active == True)
    )
    return list(result.scalars().all())
