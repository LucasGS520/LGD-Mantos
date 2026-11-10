import time
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from app.shared.application.errors import ApplicationError
from app.shared.application.telemetry import emit
from app.shared.models.entities import Control
from sqlalchemy import select, text


def value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value) if isinstance(value, (Decimal, UUID)) else value


def document_version(version):
    if version != 1:
        raise ApplicationError(503, "Registro em formato incompatível; processamento interrompido")


def serialize(row):
    """Representa valores monetários como decimais textuais, sem perda binária."""
    if row is None:
        return None
    result = {}
    for col in row.__table__.columns:
        field_value = getattr(row, col.name)
        result[col.name] = value(field_value)
    if hasattr(row, "kind") and row.__table__.name != "lgd_operations":
        result["kind"] = row.kind
    if "document_version" in result:
        document_version(result.pop("document_version"))
    return result


async def lock(db):
    """Serializa gravações inclusive na primeira inicialização do controle."""
    started = time.perf_counter()
    await db.execute(text("SELECT pg_advisory_xact_lock(741206031)"))
    acquired = time.perf_counter()
    emit("lock_acquired", wait_ms=round((acquired - started) * 1000, 2))
    db.info.setdefault("lock_started", acquired)
    control = await db.get(Control, 1, with_for_update=True)
    if control is None:
        control = Control(id=1, revision=0)
        db.add(control)
        await db.flush()
    return control


async def rows(db, model):
    return list((await db.scalars(select(model))).all())


async def rows_by_ids(db, model, ids):
    """Consulta explícita em lotes, sem carregamentos implícitos por entidade."""
    values = list(dict.fromkeys(ids))
    result = {}
    for start in range(0, len(values), 500):
        for row in (
            await db.scalars(select(model).where(model.id.in_(values[start : start + 500])))
        ).all():
            result[row.id] = row
    return result


def identifier(entity_id):
    try:
        entity_id = str(UUID(str(entity_id)))
    except (ValueError, TypeError, AttributeError):
        raise ApplicationError(404, "Registro não encontrado") from None
    return entity_id


async def require(db, model, entity_id):
    entity_id = identifier(entity_id)
    row = await db.get(model, entity_id)
    if row is None:
        raise ApplicationError(404, "Registro não encontrado")
    return row
