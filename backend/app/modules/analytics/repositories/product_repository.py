"""Consultas sobre produtos, variantes, estoque e vendas por tamanho."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.shared.models.catalog import Category, Product, ProductVariant
from app.shared.models.operations import Sale, SaleItem


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


async def top_products(db: AsyncSession, since: datetime):
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
    result = await db.execute(
        select(ProductVariant.size, func.sum(SaleItem.quantity).label("qty"))
        .join(SaleItem, SaleItem.variant_id == ProductVariant.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .group_by(ProductVariant.size)
        .order_by(func.sum(SaleItem.quantity).desc())
    )
    return result.all()


async def active_variants(db: AsyncSession) -> list[ProductVariant]:
    result = await db.execute(
        select(ProductVariant)
        .options(selectinload(ProductVariant.product))
        .join(Product)
        .where(Product.is_active == True)
    )
    return list(result.scalars().all())


async def top_products_by_margin(db: AsyncSession, since: datetime):
    """Produtos ordenados por margem percentual no período."""
    margin_expr = (
        func.sum((SaleItem.unit_price - SaleItem.unit_cost) * SaleItem.quantity)
        / func.nullif(func.sum(SaleItem.unit_price * SaleItem.quantity), 0)
        * 100
    )
    result = await db.execute(
        select(
            Product.name,
            Product.sku,
            func.sum(SaleItem.quantity).label("qty"),
            func.sum(SaleItem.unit_price * SaleItem.quantity).label("revenue"),
            func.sum((SaleItem.unit_price - SaleItem.unit_cost) * SaleItem.quantity).label("profit"),
            margin_expr.label("margin_pct"),
        )
        .join(ProductVariant, SaleItem.variant_id == ProductVariant.id)
        .join(Product, ProductVariant.product_id == Product.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .group_by(Product.id, Product.name, Product.sku)
        .having(func.sum(SaleItem.quantity) > 0)
        .order_by(margin_expr.desc())
        .limit(15)
    )
    return result.all()


async def stopped_products(db: AsyncSession, since: datetime):
    """Produtos ativos com estoque mas sem venda desde a data informada."""
    sold_product_ids = (
        select(ProductVariant.product_id)
        .join(SaleItem, SaleItem.variant_id == ProductVariant.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .where(Sale.sold_at >= since)
        .scalar_subquery()
    )
    result = await db.execute(
        select(
            Product.name,
            Product.sku,
            func.sum(ProductVariant.stock_quantity).label("total_stock"),
        )
        .join(ProductVariant, ProductVariant.product_id == Product.id)
        .where(Product.is_active == True)
        .where(ProductVariant.stock_quantity > 0)
        .where(Product.id.not_in(sold_product_ids))
        .group_by(Product.id, Product.name, Product.sku)
        .having(func.sum(ProductVariant.stock_quantity) > 0)
        .order_by(func.sum(ProductVariant.stock_quantity).desc())
        .limit(20)
    )
    return result.all()


async def top_categories(db: AsyncSession, since: datetime):
    """Categorias mais vendidas por quantidade e receita no período."""
    result = await db.execute(
        select(
            Category.name,
            func.sum(SaleItem.quantity).label("qty"),
            func.sum(SaleItem.unit_price * SaleItem.quantity).label("revenue"),
        )
        .join(ProductVariant, SaleItem.variant_id == ProductVariant.id)
        .join(Product, ProductVariant.product_id == Product.id)
        .join(Category, Product.category_id == Category.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .where(Product.category_id.is_not(None))
        .group_by(Category.id, Category.name)
        .order_by(func.sum(SaleItem.quantity).desc())
    )
    return result.all()


async def category_performance(db: AsyncSession, since: datetime):
    """Performance por categoria: unidades, receita, custo, margem e velocidade diária."""
    margin_expr = (
        func.sum((SaleItem.unit_price - SaleItem.unit_cost) * SaleItem.quantity)
        / func.nullif(func.sum(SaleItem.unit_price * SaleItem.quantity), 0)
        * 100
    )
    result = await db.execute(
        select(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.sum(SaleItem.quantity).label("units"),
            func.sum(SaleItem.unit_price * SaleItem.quantity).label("revenue"),
            func.sum(SaleItem.unit_cost * SaleItem.quantity).label("cogs"),
            func.sum((SaleItem.unit_price - SaleItem.unit_cost) * SaleItem.quantity).label("profit"),
            margin_expr.label("margin_pct"),
        )
        .join(ProductVariant, SaleItem.variant_id == ProductVariant.id)
        .join(Product, ProductVariant.product_id == Product.id)
        .join(Category, Product.category_id == Category.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .where(Product.category_id.is_not(None))
        .group_by(Category.id, Category.name)
        .order_by(func.sum(SaleItem.unit_price * SaleItem.quantity).desc())
    )
    return result.all()


async def category_size_distribution(db: AsyncSession, since: datetime):
    """Distribuição de vendas por categoria e tamanho."""
    result = await db.execute(
        select(
            Category.name.label("category_name"),
            ProductVariant.size,
            func.sum(SaleItem.quantity).label("qty"),
        )
        .join(ProductVariant, SaleItem.variant_id == ProductVariant.id)
        .join(Product, ProductVariant.product_id == Product.id)
        .join(Category, Product.category_id == Category.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .where(Product.category_id.is_not(None))
        .group_by(Category.name, ProductVariant.size)
        .order_by(Category.name, func.sum(SaleItem.quantity).desc())
    )
    return result.all()


async def category_stock(db: AsyncSession):
    """Estoque atual por categoria: unidades totais e valor de custo."""
    result = await db.execute(
        select(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(func.sum(ProductVariant.stock_quantity), 0).label("stock_units"),
            func.coalesce(
                func.sum(ProductVariant.stock_quantity * Product.cost_price), 0
            ).label("stock_value"),
        )
        .join(Product, Product.category_id == Category.id)
        .join(ProductVariant, ProductVariant.product_id == Product.id)
        .where(Product.is_active == True)
        .group_by(Category.id, Category.name)
        .order_by(func.sum(ProductVariant.stock_quantity).desc())
    )
    return result.all()


async def product_attribute_analysis(db: AsyncSession, since: datetime):
    """Análise por marca e tipo de produto."""
    by_brand = await db.execute(
        select(
            Product.brand,
            func.sum(SaleItem.quantity).label("units"),
            func.sum(SaleItem.unit_price * SaleItem.quantity).label("revenue"),
            func.sum((SaleItem.unit_price - SaleItem.unit_cost) * SaleItem.quantity).label("profit"),
        )
        .join(ProductVariant, SaleItem.variant_id == ProductVariant.id)
        .join(Product, ProductVariant.product_id == Product.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .where(Product.brand.is_not(None))
        .group_by(Product.brand)
        .order_by(func.sum(SaleItem.unit_price * SaleItem.quantity).desc())
    )

    by_type = await db.execute(
        select(
            Product.product_type,
            func.sum(SaleItem.quantity).label("units"),
            func.sum(SaleItem.unit_price * SaleItem.quantity).label("revenue"),
            func.sum((SaleItem.unit_price - SaleItem.unit_cost) * SaleItem.quantity).label("profit"),
        )
        .join(ProductVariant, SaleItem.variant_id == ProductVariant.id)
        .join(Product, ProductVariant.product_id == Product.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .where(Product.product_type.is_not(None))
        .group_by(Product.product_type)
        .order_by(func.sum(SaleItem.unit_price * SaleItem.quantity).desc())
    )

    return by_brand.all(), by_type.all()
