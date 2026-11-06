from app.shared.application.audit import audit
from app.shared.application.errors import ApplicationError
from app.shared.application.normalization import normalize
from app.shared.application.versioning import check_version
from app.shared.models.common import uid
from app.shared.models.entities import Auxiliary
from app.shared.persistence import base as repo

from .repository import duplicate as find_duplicate


async def save(db, data, entity_id=None):
    control = await repo.lock(db)
    row = await repo.require(db, Auxiliary, entity_id) if entity_id else None
    if row:
        check_version(row, data)
        if data.kind != row.kind:
            raise ApplicationError(422, "O tipo do cadastro não pode ser alterado")
    duplicate = await find_duplicate(db, data.kind, normalize(data.name))
    if duplicate and duplicate.id != entity_id:
        raise ApplicationError(409, "Nome já cadastrado após normalização")
    before = repo.serialize(row)
    if row is None:
        row = Auxiliary(id=uid(), kind=data.kind, version=1)
        db.add(row)
    else:
        row.version += 1
    row.name, row.normalized_name, row.notes, row.active = (
        data.name,
        normalize(data.name),
        data.notes,
        data.active,
    )
    await db.flush()
    audit(
        db,
        "auxiliary",
        row.id,
        "edit" if before else "create",
        data.reason or "Cadastro inicial",
        before,
        repo.serialize(row),
    )
    control.revision += 1
    return repo.serialize(row)
