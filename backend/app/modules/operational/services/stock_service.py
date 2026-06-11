"""Serviços de negócio para controle de estoque."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operational import repositories as repo
from app.shared.models.operations import StockMovement
from app.shared.schemas.operations import StockMoveIn


class StockService:
    """Aplica movimentações de entrada e saída de estoque."""

    @staticmethod
    async def stock_movement(db: AsyncSession, data: StockMoveIn) -> StockMovement:
        """Registra movimentação manual e ajusta o saldo da variante."""

        variant = await repo.get_variant(db, data.variant_id)
        if not variant:
            raise HTTPException(404, "Variante nao encontrada")

        if data.movement_type == "entrada":
            variant.stock_quantity += data.quantity
        elif data.movement_type == "saida":
            if variant.stock_quantity < data.quantity:
                raise HTTPException(400, "Estoque insuficiente")
            variant.stock_quantity -= data.quantity
        else:
            raise HTTPException(400, "Tipo de movimentacao invalido")

        movement = StockMovement(**data.model_dump())
        db.add(movement)
        await db.flush()
        return movement
