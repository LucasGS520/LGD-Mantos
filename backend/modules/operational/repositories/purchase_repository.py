"""Repositório de pedidos de compra e seus itens."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.shared.models import PurchaseOrder, PurchaseOrderItem


class PurchaseRepository:
    """Disponibiliza operações de leitura e escrita para compras."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_purchases(self, limit: int = 100) -> list[PurchaseOrder]:
        """Lista pedidos de compra recentes com itens."""
        result = await self.db.execute(
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items))
            .order_by(PurchaseOrder.order_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_purchase(self, purchase: PurchaseOrder) -> None:
        """Adiciona pedido de compra na sessão atual."""
        self.db.add(purchase)

    async def add_purchase_item(self, item: PurchaseOrderItem) -> None:
        """Adiciona item de pedido na sessão atual."""
        self.db.add(item)

    async def get_purchase_with_items(self, po_id: str) -> PurchaseOrder | None:
        """Busca pedido por ID trazendo coleção de itens."""
        result = await self.db.execute(
            select(PurchaseOrder).options(selectinload(PurchaseOrder.items)).where(PurchaseOrder.id == po_id)
        )
        return result.scalar_one_or_none()
