from app.shared.models.entities import Movement, Revision
from app.shared.persistence.base import identifier, serialize
from sqlalchemy import select


async def history(db, entity_id):
    entity_id = identifier(entity_id)
    return [
        serialize(r)
        for r in (
            await db.scalars(
                select(Revision)
                .where(Revision.entity_id == entity_id)
                .order_by(Revision.created_at, Revision.id)
            )
        ).all()
    ]


async def movements(db, operation_id=None):
    query = select(Movement).order_by(Movement.created_at, Movement.id)
    if operation_id is not None:
        operation_id = identifier(operation_id)
        query = query.where(Movement.operation_id == operation_id)
    return [serialize(row) for row in (await db.scalars(query)).all()]
