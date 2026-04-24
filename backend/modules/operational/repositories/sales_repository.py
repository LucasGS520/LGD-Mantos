"""Repositório de vendas para leitura e escrita de pedidos e itens."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.shared.models import ProductVariant, Sale, SaleItem


class SalesRepository:
    """Encapsula consultas de venda e variantes usadas na baixa de estoque."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_sales(self, limit: int) -> list[Sale]:
        """Lista vendas recentes com itens associados."""
        result = await self.db.execute(select(Sale).options(selectinload(Sale.items)).order_by(Sale.sold_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_variant_by_id(self, variant_id: str) -> ProductVariant | None:
        """Busca variante por identificador para validação de estoque."""
        result = await self.db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
        return result.scalar_one_or_none()

    async def add_sale(self, sale: Sale) -> None:
        """Registra venda no contexto da sessão atual."""
        self.db.add(sale)

    async def add_sale_item(self, item: SaleItem) -> None:
        """Registra item de venda no contexto da sessão atual."""
        self.db.add(item)
