"""Casos de uso específicos de purchase_channels."""

from ..common.service import save
from .schemas import PurchaseChannelsIn


async def save_purchase_channels(db, data: PurchaseChannelsIn, entity_id=None):
    return await save(db, data, entity_id)
