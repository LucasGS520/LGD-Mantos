"""Repositório de estoque com operações SQLAlchemy focadas em variantes e movimentações."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.shared.models import ProductVariant, StockMovement


class StockRepository:
    """Centraliza consultas e persistência relacionadas ao estoque."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_variant_by_id(self, variant_id: str) -> ProductVariant | None:
        """Busca uma variante por identificador."""
        result = await self.db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
        return result.scalar_one_or_none()

    async def list_alerts(self) -> list[ProductVariant]:
        """Lista variantes em nível de alerta com dados do produto carregados."""
        result = await self.db.execute(
            select(ProductVariant)
            .options(selectinload(ProductVariant.product))
            .where(ProductVariant.stock_quantity <= ProductVariant.min_stock_alert)
        )
        return list(result.scalars().all())

    async def list_history(self, variant_id: str, limit: int = 60) -> list[StockMovement]:
        """Retorna histórico de movimentações de uma variante."""
        result = await self.db.execute(
            select(StockMovement)
            .where(StockMovement.variant_id == variant_id)
            .order_by(StockMovement.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add_movement(self, movement: StockMovement) -> None:
        """Adiciona movimentação no contexto transacional atual."""
        self.db.add(movement)

