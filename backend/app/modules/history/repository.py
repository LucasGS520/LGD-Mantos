from app.shared.models.entities import Movement, Revision
from app.shared.persistence.base import rows, serialize
from sqlalchemy import select


async def history(db, entity_id):
    return [
        serialize(r)
        for r in (
            await db.scalars(
                select(Revision)
                .where(Revision.entity_id == entity_id)
                .order_by(Revision.created_at)
            )
        ).all()
    ]


async def movements(db):
    return [serialize(row) for row in await rows(db, Movement)]
