from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operational import repositories as repo
from app.shared.models.operations import PurchaseOrder, PurchaseOrderItem, StockMovement
from app.shared.schemas.operations import POIn


class PurchaseService:
    @staticmethod
    async def create_purchase(db: AsyncSession, data: POIn) -> PurchaseOrder:
        supplier = await repo.get_supplier(db, data.supplier_id)
        if not supplier:
            raise HTTPException(404, "Fornecedor nao encontrado")

        purchase = PurchaseOrder(
            supplier_id=data.supplier_id,
            order_date=data.order_date,
            notes=data.notes,
        )
        db.add(purchase)
        await db.flush()
        for item in data.items:
            db.add(PurchaseOrderItem(order_id=purchase.id, **item.model_dump()))
        await db.flush()
        await db.refresh(purchase, ["items"])
        return purchase

    @staticmethod
    async def receive_purchase(db: AsyncSession, purchase_id: str) -> dict:
        purchase = await repo.get_purchase(db, purchase_id)
        if not purchase:
            raise HTTPException(404, "Compra nao encontrada")
        if purchase.status == "recebido":
            raise HTTPException(400, "Ja recebido")

        purchase.status = "recebido"
        for item in purchase.items:
            variant = await repo.get_variant(db, item.variant_id)
            if variant:
                variant.stock_quantity += item.quantity
                db.add(
                    StockMovement(
                        variant_id=variant.id,
                        movement_type="entrada",
                        quantity=item.quantity,
                        unit_cost=item.unit_cost,
                        notes=f"Compra #{purchase.id[:8]}",
                    )
                )
        return {"ok": True}
