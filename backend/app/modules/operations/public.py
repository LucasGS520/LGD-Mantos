"""Consulta pública de acontecimentos; não acopla o ledger à infraestrutura."""

from .domain.ledger import ZERO as ZERO
from .domain.ledger import amount as amount
from .domain.ledger import money as money
from .domain.ledger import replay as replay


async def operations(db):
    """Carrega o histórico completo; não é uma consulta paginada de interface."""
    from .repository import operations as load

    return await load(db)
