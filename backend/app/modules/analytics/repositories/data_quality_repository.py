"""Consultas de qualidade dos dados: campos ausentes, inconsistências e completude."""

from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.catalog import Product, ProductVariant
from app.shared.models.operations import Expense, Sale


async def products_no_cost_price(db: AsyncSession) -> list:
    result = await db.execute(
        select(Product.name, Product.sku)
        .where(Product.is_active == True)
        .where(Product.cost_price == 0)
        .order_by(Product.name)
    )
    return [{"name": r[0], "sku": r[1]} for r in result.all()]


async def products_no_sale_price(db: AsyncSession) -> list:
    result = await db.execute(
        select(Product.name, Product.sku)
        .where(Product.is_active == True)
        .where(Product.sale_price == 0)
        .order_by(Product.name)
    )
    return [{"name": r[0], "sku": r[1]} for r in result.all()]


async def products_no_supplier(db: AsyncSession) -> list:
    result = await db.execute(
        select(Product.name, Product.sku)
        .where(Product.is_active == True)
        .where(Product.supplier_id.is_(None))
        .order_by(Product.name)
    )
    return [{"name": r[0], "sku": r[1]} for r in result.all()]


async def products_no_category(db: AsyncSession) -> list:
    result = await db.execute(
        select(Product.name, Product.sku)
        .where(Product.is_active == True)
        .where(Product.category_id.is_(None))
        .order_by(Product.name)
    )
    return [{"name": r[0], "sku": r[1]} for r in result.all()]


async def products_no_photo(db: AsyncSession) -> list:
    """Produtos ativos sem foto (photos NULL ou lista vazia)."""
    result = await db.execute(
        select(Product.name, Product.sku)
        .where(Product.is_active == True)
        .where(
            or_(
                Product.photos.is_(None),
                func.json_array_length(Product.photos) == 0,
            )
        )
        .order_by(Product.name)
    )
    return [{"name": r[0], "sku": r[1]} for r in result.all()]


async def variants_no_info(db: AsyncSession) -> list:
    """Variantes com tamanho vazio (preenchimento incompleto)."""
    result = await db.execute(
        select(Product.name, Product.sku, ProductVariant.size, ProductVariant.color)
        .join(Product, ProductVariant.product_id == Product.id)
        .where(Product.is_active == True)
        .where(or_(ProductVariant.size == "", ProductVariant.color == ""))
        .order_by(Product.name)
    )
    return [
        {"name": r[0], "sku": r[1], "size": r[2], "color": r[3]}
        for r in result.all()
    ]


async def sales_no_channel(db: AsyncSession, since: datetime) -> list:
    """Vendas sem canal ou com canal vazio nos últimos N dias."""
    result = await db.execute(
        select(Sale.id, Sale.sold_at, Sale.total)
        .where(Sale.sold_at >= since)
        .where(Sale.sale_channel_id.is_(None))
        .order_by(Sale.sold_at.desc())
        .limit(50)
    )
    return [
        {"id": r[0], "sold_at": r[1].isoformat(), "total": float(r[2])}
        for r in result.all()
    ]


async def expenses_no_category(db: AsyncSession) -> list:
    """Despesas com categoria vazia ou ausente."""
    result = await db.execute(
        select(Expense.id, Expense.date, Expense.amount, Expense.description)
        .where(or_(Expense.category.is_(None), Expense.category == ""))
        .order_by(Expense.date.desc())
        .limit(50)
    )
    return [
        {"id": r[0], "date": r[1], "amount": float(r[2]), "description": r[3]}
        for r in result.all()
    ]


async def count_active_products(db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count(Product.id)).where(Product.is_active == True)
    )
    return int(result.scalar())


async def count_active_variants(db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count(ProductVariant.id))
        .join(Product)
        .where(Product.is_active == True)
    )
    return int(result.scalar())
