"""Casos de uso específicos de sale_channels."""

from ..common.service import save
from .schemas import SaleChannelsIn


async def save_sale_channels(db, data: SaleChannelsIn, entity_id=None):
    return await save(db, data, entity_id)
