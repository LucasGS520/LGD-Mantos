"""Serviço de estoque com regras de negócio e controle transacional."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operational.repositories import StockRepository
from modules.shared.models import StockMovement
from modules.shared.schemas import StockMoveIn


class StockService:
    """Aplica regras de movimentação e consulta de estoque."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = StockRepository(db)

    async def register_movement(self, data: StockMoveIn) -> StockMovement:
        """Registra movimentação, ajusta saldo e confirma a transação."""
        variant = await self.repository.get_variant_by_id(data.variant_id)
        if not variant:
            raise HTTPException(404, "Variante não encontrada")

        # A atualização de saldo fica centralizada aqui para manter endpoint enxuto.
        if data.movement_type == "entrada":
            variant.stock_quantity += data.quantity
        elif data.movement_type == "saida":
            if variant.stock_quantity < data.quantity:
                raise HTTPException(400, "Estoque insuficiente")
            variant.stock_quantity -= data.quantity
        elif data.movement_type == "ajuste":
            variant.stock_quantity = data.quantity
        elif data.movement_type == "devolucao":
            variant.stock_quantity += data.quantity

        movement = StockMovement(**data.model_dump())
        await self.repository.add_movement(movement)

        try:
            await self.db.flush()
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        return movement

    async def list_alerts(self) -> list[dict]:
        """Monta payload de alertas para consumo direto da API."""
        variants = await self.repository.list_alerts()
        return [
            {
                "variant_id": v.id,
                "product_name": v.product.name,
                "sku": v.product.sku,
                "size": v.size,
                "color": v.color,
                "stock": v.stock_quantity,
                "min": v.min_stock_alert,
            }
            for v in variants
        ]

    async def list_history(self, variant_id: str) -> list[StockMovement]:
        """Retorna histórico recente de movimentações por variante."""
        return await self.repository.list_history(variant_id=variant_id)
