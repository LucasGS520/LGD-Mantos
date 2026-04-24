from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operational import repositories as repo
from app.shared.models.operations import StockMovement
from app.shared.schemas.operations import StockMoveIn


class StockService:
    @staticmethod
    async def stock_movement(db: AsyncSession, data: StockMoveIn) -> StockMovement:
        variant = await repo.get_variant(db, data.variant_id)
        if not variant:
            raise HTTPException(404, "Variante nao encontrada")

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
        else:
            raise HTTPException(400, "Tipo de movimentacao invalido")

        movement = StockMovement(**data.model_dump())
        db.add(movement)
        await db.flush()
        return movement

    @staticmethod
    async def stock_alerts(db: AsyncSession) -> list[dict]:
        variants = await repo.list_stock_alerts(db)
        return [
            {
                "variant_id": variant.id,
                "product_name": variant.product.name,
                "sku": variant.product.sku,
                "size": variant.size,
                "color": variant.color,
                "stock": variant.stock_quantity,
                "min": variant.min_stock_alert,
            }
            for variant in variants
        ]
