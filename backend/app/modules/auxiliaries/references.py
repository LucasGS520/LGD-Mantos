from app.shared.application.errors import ApplicationError
from app.shared.models.entities import AUXILIARY_MODELS
from app.shared.persistence.base import rows_by_ids

from .common.repository import require_kind


async def auxiliary(db, entity_id, kind, previous_id=None):
    row = await require_kind(db, entity_id, kind)
    if row.kind != kind or (not row.active and row.id != previous_id):
        raise ApplicationError(422, "Cadastro auxiliar incompatível ou desativado")
    return row


async def auxiliary_many(db, ids, kind):
    """Carrega em lote; o caso de uso decide atividade conforme o vínculo histórico."""
    records = await rows_by_ids(db, AUXILIARY_MODELS[kind], ids)
    for entity_id in dict.fromkeys(ids):
        if entity_id not in records:
            await require_kind(db, entity_id, kind)
    return records
