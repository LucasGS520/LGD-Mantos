from app.shared.application.errors import ApplicationError
from app.shared.models.entities import Auxiliary
from app.shared.persistence import base as repo


async def auxiliary(db, entity_id, kind, previous_id=None):
    row = await repo.require(db, Auxiliary, entity_id)
    if row.kind != kind or (not row.active and row.id != previous_id):
        raise ApplicationError(422, "Cadastro auxiliar incompatível ou desativado")
    return row
