"""Despacho explícito entre capacidades."""

from .categories.service import save_categories
from .payment_methods.service import save_payment_methods
from .purchase_channels.service import save_purchase_channels
from .sale_channels.service import save_sale_channels
from .suppliers.service import save_suppliers

HANDLERS = {
    "supplier": save_suppliers,
    "category": save_categories,
    "purchase_channel": save_purchase_channels,
    "sale_channel": save_sale_channels,
    "payment_method": save_payment_methods,
}


async def save(db, data, entity_id=None):
    return await HANDLERS[data.kind](db, data, entity_id)
