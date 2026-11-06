from app.shared.models.entities import Auxiliary
from app.shared.persistence.base import rows, serialize
from sqlalchemy import select


async def duplicate(db, kind, name):
    return await db.scalar(
        select(Auxiliary).where(Auxiliary.kind == kind, Auxiliary.normalized_name == name)
    )


async def list_all(db):
    return [serialize(row) for row in await rows(db, Auxiliary)]
