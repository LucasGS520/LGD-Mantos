"""Serviço de vendas com regras de validação, estoque e persistência."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operational.repositories import SalesRepository, StockRepository
from modules.shared.models import Sale, SaleItem, StockMovement
from modules.shared.schemas import SaleIn


class SalesService:
    """Orquestra criação de vendas e baixa automática de estoque."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = SalesRepository(db)
        self.stock_repository = StockRepository(db)

    async def list_sales(self, limit: int) -> list[Sale]:
        """Lista vendas recentes com itens."""
        return await self.repository.list_sales(limit=limit)

    async def create_sale(self, data: SaleIn) -> Sale:
        """Cria venda e registra saídas de estoque em transação única."""
        if not data.items:
            raise HTTPException(400, "Sem itens")

        total = 0.0
        pairs: list[tuple] = []

        for item in data.items:
            variant = await self.repository.get_variant_by_id(item.variant_id)
            if not variant:
                raise HTTPException(404, f"Variante {item.variant_id}")
            if variant.stock_quantity < item.quantity:
                raise HTTPException(400, f"Estoque insuficiente: {variant.size}/{variant.color}")

            total += item.unit_price * item.quantity
            pairs.append((variant, item))

        sale = Sale(channel=data.channel, notes=data.notes, total=round(total, 2))
        await self.repository.add_sale(sale)

        try:
            await self.db.flush()

            for variant, item in pairs:
                await self.repository.add_sale_item(
                    SaleItem(
                        sale_id=sale.id,
                        variant_id=variant.id,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        unit_cost=item.unit_cost,
                    )
                )
                variant.stock_quantity -= item.quantity
                await self.stock_repository.add_movement(
                    StockMovement(
                        variant_id=variant.id,
                        movement_type="saida",
                        quantity=item.quantity,
                        notes=f"Venda #{sale.id[:8]}",
                    )
                )

            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(sale, ["items"])
        except Exception:
            await self.db.rollback()
            raise

        return sale
