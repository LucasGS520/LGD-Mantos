from app.modules.catalog.public import products as products
from app.modules.operations.public import operations as operations
from app.shared.models.entities import Category, Control
from app.shared.persistence.base import rows as rows


async def snapshot(db):
    """Materializa somente valores; a sessão deve estar em snapshot repetível."""
    catalog, history = await products(db), await operations(db)
    auxiliary_names = {a.id: a.name for a in await rows(db, Category)}
    control = await db.get(Control, 1)
    return (
        catalog,
        history,
        auxiliary_names,
        {
            "revision": control.revision if control else 0,
            "started_at": control.started_at.isoformat()
            if control and control.started_at
            else None,
        },
    )
