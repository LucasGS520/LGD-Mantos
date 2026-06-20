"""Serviço de entrada de mercadoria — cria produtos, variantes e estoque atomicamente."""

import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operational import repositories as repo
from app.shared.models.catalog import Product, ProductVariant
from app.shared.models.operations import MerchandiseEntry, MerchandiseEntryItem, StockMovement
from app.shared.schemas.entry import EntryIn, EntryItemOut, EntryOut


def _generate_sku() -> str:
    return f"LGD-{uuid.uuid4().hex[:8].upper()}"


class EntryService:
    @staticmethod
    async def create_entry(db: AsyncSession, data: EntryIn) -> EntryOut:
        """Registra uma entrada de mercadoria criando produtos inline quando necessário."""

        entry = MerchandiseEntry(
            supplier_id=data.supplier_id,
            entry_date=data.entry_date,
            notes=data.notes,
        )
        db.add(entry)
        await db.flush()

        total_cost = 0.0
        products_created = 0
        variants_added = 0
        item_outs: list[EntryItemOut] = []

        for item in data.items:
            if item.new_product is not None:
                np = item.new_product

                if np.category_id and not await repo.get_category(db, np.category_id):
                    raise HTTPException(400, f"Categoria não encontrada: {np.category_id}")

                sku = _generate_sku()
                product = Product(
                    sku=sku,
                    name=np.name,
                    description=np.description,
                    category_id=np.category_id,
                    supplier_id=data.supplier_id,
                    cost_price=np.cost_price if np.cost_price > 0 else min(v.unit_cost for v in np.variants),
                    sale_price=np.sale_price,
                    brand=np.brand,
                    tags=np.tags or [],
                )
                db.add(product)
                await db.flush()
                products_created += 1

                for v in np.variants:
                    variant = ProductVariant(
                        product_id=product.id,
                        size=v.size,
                        color=v.color,
                        stock_quantity=v.quantity,
                    )
                    db.add(variant)
                    await db.flush()

                    db.add(StockMovement(
                        variant_id=variant.id,
                        movement_type="entrada",
                        quantity=v.quantity,
                        unit_cost=v.unit_cost,
                        notes=f"Entrada #{entry.id[:8]}",
                    ))
                    db.add(MerchandiseEntryItem(
                        entry_id=entry.id,
                        variant_id=variant.id,
                        quantity=v.quantity,
                        unit_cost=v.unit_cost,
                    ))

                    total_cost += v.quantity * v.unit_cost
                    variants_added += 1
                    item_outs.append(EntryItemOut(
                        variant_id=variant.id,
                        product_name=np.name,
                        size=v.size,
                        quantity=v.quantity,
                        unit_cost=v.unit_cost,
                    ))

            elif item.existing_variant is not None:
                ev = item.existing_variant
                variant = await repo.get_variant_with_product(db, ev.variant_id)
                if not variant:
                    raise HTTPException(404, f"Variante não encontrada: {ev.variant_id}")

                variant.stock_quantity += ev.quantity
                db.add(StockMovement(
                    variant_id=variant.id,
                    movement_type="entrada",
                    quantity=ev.quantity,
                    unit_cost=ev.unit_cost,
                    notes=f"Entrada #{entry.id[:8]}",
                ))
                db.add(MerchandiseEntryItem(
                    entry_id=entry.id,
                    variant_id=variant.id,
                    quantity=ev.quantity,
                    unit_cost=ev.unit_cost,
                ))

                total_cost += ev.quantity * ev.unit_cost
                variants_added += 1
                product_name = variant.product.name if variant.product else "—"
                item_outs.append(EntryItemOut(
                    variant_id=variant.id,
                    product_name=product_name,
                    size=variant.size,
                    quantity=ev.quantity,
                    unit_cost=ev.unit_cost,
                ))
            else:
                raise HTTPException(400, "Cada item deve ter new_product ou existing_variant")

        await db.flush()

        return EntryOut(
            id=entry.id,
            supplier_id=entry.supplier_id,
            entry_date=entry.entry_date,
            notes=entry.notes,
            total_cost=round(total_cost, 2),
            products_created=products_created,
            variants_added=variants_added,
            created_at=entry.created_at,
            items=item_outs,
        )
