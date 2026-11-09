from datetime import datetime

from app.shared.models.entities import Operation, RequestReceipt
from app.shared.persistence.base import serialize
from sqlalchemy import select


async def operations(db):
    # A leitura integral não precisa instanciar/guardar 50 mil entidades ORM.
    values = (
        await db.execute(
            select(Operation.__table__).order_by(Operation.effective_at, Operation.sequence)
        )
    ).mappings()
    return [
        {
            key: value.isoformat() if isinstance(value, datetime) else value
            for key, value in row.items()
        }
        for row in values
    ]


async def receipt(db, key):
    return await db.get(RequestReceipt, key)


async def affected_operations(db, ids):
    """Carrega dependentes em lotes; correção antiga não faz um SELECT por impacto."""
    result = {}
    for start in range(0, len(ids), 500):
        for row in (
            await db.scalars(select(Operation).where(Operation.id.in_(ids[start : start + 500])))
        ).all():
            result[row.id] = row
    return result


async def page(db, kind, limit, before_sequence):
    query = select(Operation).order_by(Operation.sequence.desc()).limit(limit)
    if kind is not None:
        query = query.where(Operation.kind == kind)
    if before_sequence is not None:
        query = query.where(Operation.sequence < before_sequence)
    return [serialize(row) for row in (await db.scalars(query)).all()]
