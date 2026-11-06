from app.shared.models.entities import Operation, RequestReceipt
from app.shared.persistence.base import rows, serialize


async def operations(db):
    return sorted(
        [serialize(op) for op in await rows(db, Operation)],
        key=lambda op: (op["effective_at"], op["sequence"]),
    )


async def receipt(db, key):
    return await db.get(RequestReceipt, key)
