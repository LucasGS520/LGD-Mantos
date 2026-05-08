"""Consultas de leitura e busca usadas pelo módulo operacional.

Os repositórios concentram o acesso ao banco e evitam espalhar consultas
SQLAlchemy pelas rotas e serviços. Regras de negócio e mutações ficam nos
serviços da camada operacional.
"""

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
    """Busca uma categoria pelo identificador interno."""

    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def list_categories(db: AsyncSession) -> list[Category]:
    """Lista categorias em ordem alfabética para uso em cadastros."""

    result = await db.execute(select(Category).order_by(Category.name))
    return list(result.scalars().all())


async def list_suppliers(db: AsyncSession) -> list[Supplier]:
    """Lista apenas fornecedores ativos, ordenados pelo nome."""

    result = await db.execute(
        select(Supplier).where(Supplier.is_active == True).order_by(Supplier.name)
    )
    return list(result.scalars().all())


async def get_supplier(db: AsyncSession, supplier_id: str) -> Supplier | None:
    """Busca um fornecedor pelo identificador interno."""

    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    return result.scalar_one_or_none()


async def get_product_by_sku(db: AsyncSession, sku: str) -> Product | None:
    """Busca produto por SKU para impedir duplicidade no cadastro."""

    result = await db.execute(select(Product).where(Product.sku == sku))
    return result.scalar_one_or_none()


async def get_product(db: AsyncSession, product_id: str, with_variants: bool = True) -> Product | None:
    """Busca um produto e, opcionalmente, carrega suas variantes."""

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
    """Lista produtos filtrando por busca textual, categoria, fornecedor e status."""

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
    """Busca uma variante vendável pelo identificador interno."""

    result = await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
    return result.scalar_one_or_none()


async def get_product_variant(
    db: AsyncSession, product_id: str, variant_id: str
) -> ProductVariant | None:
    """Busca uma variante garantindo que ela pertence ao produto informado."""

    result = await db.execute(
        select(ProductVariant).where(
            ProductVariant.id == variant_id,
            ProductVariant.product_id == product_id,
        )
    )
    return result.scalar_one_or_none()


async def list_stock_alerts(db: AsyncSession) -> list[ProductVariant]:
    """Lista variantes cujo estoque está igual ou abaixo do mínimo definido."""

    result = await db.execute(
        select(ProductVariant)
        .options(selectinload(ProductVariant.product))
        .where(ProductVariant.stock_quantity <= ProductVariant.min_stock_alert)
    )
    return list(result.scalars().all())


async def list_stock_history(db: AsyncSession, variant_id: str) -> list[StockMovement]:
    """Retorna o histórico recente de movimentações de uma variante."""

    result = await db.execute(
        select(StockMovement)
        .where(StockMovement.variant_id == variant_id)
        .order_by(StockMovement.created_at.desc())
        .limit(60)
    )
    return list(result.scalars().all())


async def list_sales(db: AsyncSession, limit: int) -> list[Sale]:
    """Lista vendas recentes com seus itens para consulta operacional."""

    result = await db.execute(
        select(Sale).options(selectinload(Sale.items)).order_by(Sale.sold_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def get_sale(db: AsyncSession, sale_id: str) -> Sale | None:
    """Busca uma venda com seus itens para estorno."""

    result = await db.execute(
        select(Sale).options(selectinload(Sale.items)).where(Sale.id == sale_id)
    )
    return result.scalar_one_or_none()


async def list_expenses(db: AsyncSession) -> list[Expense]:
    """Lista despesas recentes para acompanhamento financeiro operacional."""

    result = await db.execute(select(Expense).order_by(Expense.date.desc()).limit(200))
    return list(result.scalars().all())


async def get_expense(db: AsyncSession, expense_id: str) -> Expense | None:
    """Busca uma despesa pelo identificador interno."""

    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    return result.scalar_one_or_none()


async def list_purchases(db: AsyncSession) -> list[PurchaseOrder]:
    """Lista pedidos de compra recentes com seus itens."""

    result = await db.execute(
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .order_by(PurchaseOrder.order_date.desc())
        .limit(100)
    )
    return list(result.scalars().all())


async def get_purchase(db: AsyncSession, purchase_id: str) -> PurchaseOrder | None:
    """Busca um pedido de compra com itens para recebimento ou consulta."""

    result = await db.execute(
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .where(PurchaseOrder.id == purchase_id)
    )
    return result.scalar_one_or_none()
