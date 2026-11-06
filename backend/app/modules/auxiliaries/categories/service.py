"""Casos de uso específicos de categories."""

from ..common.service import save
from .schemas import CategoriesIn


async def save_categories(db, data: CategoriesIn, entity_id=None):
    return await save(db, data, entity_id)
