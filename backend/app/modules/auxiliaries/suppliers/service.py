"""Casos de uso específicos de suppliers."""

from ..common.service import save
from .schemas import SuppliersIn


async def save_suppliers(db, data: SuppliersIn, entity_id=None):
    return await save(db, data, entity_id)
