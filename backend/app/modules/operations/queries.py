from app.shared.models.entities import Control, Operation
from app.shared.persistence.base import require, serialize


async def detail(db, entity_id):
    return serialize(await require(db, Operation, entity_id))


async def state(db):
    control = await db.get(Control, 1)
    return {
        "revision": control.revision if control else 0,
        "started_at": control.started_at if control else None,
    }
