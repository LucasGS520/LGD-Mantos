from app.shared.models.entities import Control

from .repository import detail as detail


async def state(db):
    control = await db.get(Control, 1)
    return {
        "revision": control.revision if control else 0,
        "started_at": control.started_at if control else None,
    }
