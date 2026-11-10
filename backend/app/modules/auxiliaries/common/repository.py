from app.shared.application.errors import ApplicationError
from app.shared.models.entities import AUXILIARY_MODELS
from app.shared.persistence.base import identifier, require, rows, serialize
from sqlalchemy import select


async def duplicate(db, kind, name):
    return await db.scalar(
        select(AUXILIARY_MODELS[kind]).where(AUXILIARY_MODELS[kind].normalized_name == name)
    )


async def list_all(db):
    return [serialize(row) for model in AUXILIARY_MODELS.values() for row in await rows(db, model)]


async def require_kind(db, entity_id, kind):
    entity_id = identifier(entity_id)
    try:
        return await require(db, AUXILIARY_MODELS[kind], entity_id)
    except ApplicationError as exc:
        if exc.status_code != 404:
            raise
        for other_kind, model in AUXILIARY_MODELS.items():
            if other_kind != kind and await db.get(model, entity_id):
                raise ApplicationError(422, "Cadastro auxiliar incompatível") from None
        raise
