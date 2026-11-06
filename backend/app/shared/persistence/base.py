from datetime import datetime
from decimal import Decimal

from app.shared.application.errors import ApplicationError
from app.shared.models.entities import Control
from sqlalchemy import select, text


def serialize(row):
    """Representa valores monetários como decimais textuais, sem perda binária."""
    if row is None:
        return None
    result = {}
    for col in row.__table__.columns:
        value = getattr(row, col.name)
        result[col.name] = (
            value.isoformat()
            if isinstance(value, datetime)
            else str(value)
            if isinstance(value, Decimal)
            else value
        )
    return result


async def lock(db):
    """Serializa gravações inclusive na primeira inicialização do controle."""
    await db.execute(text("SELECT pg_advisory_xact_lock(741206031)"))
    control = await db.get(Control, 1, with_for_update=True)
    if control is None:
        control = Control(id=1, revision=0)
        db.add(control)
        await db.flush()
    return control


async def rows(db, model):
    return list((await db.scalars(select(model))).all())


async def require(db, model, entity_id):
    row = await db.get(model, entity_id)
    if row is None:
        raise ApplicationError(404, "Registro não encontrado")
    return row
