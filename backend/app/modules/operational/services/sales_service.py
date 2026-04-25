"""Serviços de negócio para registro de vendas."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operational import repositories as repo
from app.shared.models.operations import Sale, SaleItem, StockMovement
from app.shared.schemas.operations import SaleIn


class SalesService:
    """Valida vendas, baixa estoque e cria histórico de movimentação."""

    @staticmethod
    async def create_sale(db: AsyncSession, data: SaleIn) -> Sale:
        """Cria uma venda com itens e registra saídas de estoque correspondentes."""

        if not data.items:
            raise HTTPException(400, "Sem itens")

        # Primeiro valida todos os itens; a baixa de estoque só acontece depois.
        total = 0.0
        pairs = []
        for item in data.items:
            variant = await repo.get_variant(db, item.variant_id)
            if not variant:
                raise HTTPException(404, f"Variante {item.variant_id}")
            if variant.stock_quantity < item.quantity:
                raise HTTPException(400, f"Estoque insuficiente: {variant.size}/{variant.color}")
            total += item.unit_price * item.quantity
            pairs.append((variant, item))

        sale = Sale(channel=data.channel, notes=data.notes, total=round(total, 2))
        db.add(sale)
        await db.flush()

        for variant, item in pairs:
            db.add(
                SaleItem(
                    sale_id=sale.id,
                    variant_id=variant.id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    unit_cost=item.unit_cost,
                )
            )
            # A venda sempre gera uma saída de estoque rastreável no histórico.
            variant.stock_quantity -= item.quantity
            db.add(
                StockMovement(
                    variant_id=variant.id,
                    movement_type="saida",
                    quantity=item.quantity,
                    notes=f"Venda #{sale.id[:8]}",
                )
            )

        await db.flush()
        await db.refresh(sale, ["items"])
        return sale
