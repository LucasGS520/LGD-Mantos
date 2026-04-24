"""Serviço de compras com criação e recebimento de pedidos."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operational.repositories import PurchaseRepository, StockRepository
from modules.shared.models import PurchaseOrder, PurchaseOrderItem, StockMovement
from modules.shared.schemas import POIn


class PurchaseService:
    """Orquestra regras de compra e atualização de estoque ao receber pedido."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = PurchaseRepository(db)
        self.stock_repository = StockRepository(db)

    async def list_purchases(self) -> list[PurchaseOrder]:
        """Lista pedidos de compra recentes com itens."""
        return await self.repository.list_purchases()

    async def create_purchase(self, data: POIn) -> PurchaseOrder:
        """Cria pedido de compra e itens iniciais na mesma transação."""
        purchase = PurchaseOrder(supplier_id=data.supplier_id, order_date=data.order_date, notes=data.notes)
        await self.repository.create_purchase(purchase)

        try:
            await self.db.flush()
            for item in data.items:
                await self.repository.add_purchase_item(PurchaseOrderItem(order_id=purchase.id, **item.model_dump()))
            await self.db.flush()
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        return purchase

    async def receive_purchase(self, po_id: str) -> None:
        """Marca pedido como recebido e lança entradas no estoque."""
        purchase = await self.repository.get_purchase_with_items(po_id)
        if not purchase:
            raise HTTPException(404)
        if purchase.status == "recebido":
            raise HTTPException(400, "Já recebido")

        purchase.status = "recebido"

        try:
            for item in purchase.items:
                variant = await self.stock_repository.get_variant_by_id(item.variant_id)
                if variant:
                    variant.stock_quantity += item.quantity
                    await self.stock_repository.add_movement(
                        StockMovement(
                            variant_id=variant.id,
                            movement_type="entrada",
                            quantity=item.quantity,
                            unit_cost=item.unit_cost,
                            notes=f"Compra #{purchase.id[:8]}",
                        )
                    )

            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
