"""Casos de uso específicos de payment_methods."""

from ..common.service import save
from .schemas import PaymentMethodsIn


async def save_payment_methods(db, data: PaymentMethodsIn, entity_id=None):
    return await save(db, data, entity_id)
