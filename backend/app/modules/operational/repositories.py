from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.shared.models.catalog import Category, Product, ProductVariant, Supplier
from app.shared.models.operations import (
    Expense,
    PurchaseOrder,
    Sale,
    StockMovement,
)


async def get_category(db: AsyncSession, category_id: str) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def list_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.name))
    return list(result.scalars().all())


async def list_suppliers(db: AsyncSession) -> list[Supplier]:
    result = await db.execute(
        select(Supplier).where(Supplier.is_active == True).order_by(Supplier.name)
    )
    return list(result.scalars().all())


async def get_supplier(db: AsyncSession, supplier_id: str) -> Supplier | None:
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    return result.scalar_one_or_none()


async def get_product_by_sku(db: AsyncSession, sku: str) -> Product | None:
    result = await db.execute(select(Product).where(Product.sku == sku))
    return result.scalar_one_or_none()


async def get_product(db: AsyncSession, product_id: str, with_variants: bool = True) -> Product | None:
    query = select(Product).where(Product.id == product_id)
    if with_variants:
        query = query.options(selectinload(Product.variants))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_products(
    db: AsyncSession,
    search: str | None = None,
    category_id: str | None = None,
    supplier_id: str | None = None,
    active_only: bool = True,
) -> list[Product]:
    query = select(Product).options(selectinload(Product.variants))
    if active_only:
        query = query.where(Product.is_active == True)
    if search:
        query = query.where(or_(Product.name.ilike(f"%{search}%"), Product.sku.ilike(f"%{search}%")))
    if category_id:
        query = query.where(Product.category_id == category_id)
    if supplier_id:
        query = query.where(Product.supplier_id == supplier_id)
    result = await db.execute(query.order_by(Product.name))
    return list(result.scalars().all())


async def get_variant(db: AsyncSession, variant_id: str) -> ProductVariant | None:
    result = await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
    return result.scalar_one_or_none()


async def get_product_variant(
    db: AsyncSession, product_id: str, variant_id: str
) -> ProductVariant | None:
    result = await db.execute(
        select(ProductVariant).where(
            ProductVariant.id == variant_id,
            ProductVariant.product_id == product_id,
        )
    )
    return result.scalar_one_or_none()


async def list_stock_alerts(db: AsyncSession) -> list[ProductVariant]:
    result = await db.execute(
        select(ProductVariant)
        .options(selectinload(ProductVariant.product))
        .where(ProductVariant.stock_quantity <= ProductVariant.min_stock_alert)
    )
    return list(result.scalars().all())


async def list_stock_history(db: AsyncSession, variant_id: str) -> list[StockMovement]:
    result = await db.execute(
        select(StockMovement)
        .where(StockMovement.variant_id == variant_id)
        .order_by(StockMovement.created_at.desc())
        .limit(60)
    )
    return list(result.scalars().all())


async def list_sales(db: AsyncSession, limit: int) -> list[Sale]:
    result = await db.execute(
        select(Sale).options(selectinload(Sale.items)).order_by(Sale.sold_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def list_expenses(db: AsyncSession) -> list[Expense]:
    result = await db.execute(select(Expense).order_by(Expense.date.desc()).limit(200))
    return list(result.scalars().all())


async def get_expense(db: AsyncSession, expense_id: str) -> Expense | None:
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    return result.scalar_one_or_none()


async def list_purchases(db: AsyncSession) -> list[PurchaseOrder]:
    result = await db.execute(
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .order_by(PurchaseOrder.order_date.desc())
        .limit(100)
    )
    return list(result.scalars().all())


async def get_purchase(db: AsyncSession, purchase_id: str) -> PurchaseOrder | None:
    result = await db.execute(
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .where(PurchaseOrder.id == purchase_id)
    )
    return result.scalar_one_or_none()
