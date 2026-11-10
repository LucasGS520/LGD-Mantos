from app.shared.application.audit import audit
from app.shared.application.errors import ApplicationError
from app.shared.application.normalization import normalize
from app.shared.application.versioning import check_version
from app.shared.models.common import uid
from app.shared.models.entities import Product, Variant
from app.shared.persistence import base as repo

from .repository import duplicate_variant


async def create_variant(db, product, data, entity_id=None):
    if entity_id is not None:
        entity_id = repo.identifier(entity_id)
    row = await repo.require(db, Variant, entity_id) if entity_id else None
    if row:
        if row.product_id != product.id:
            raise ApplicationError(422, "Variante não pertence ao produto")
        check_version(row, data)
    key = (normalize(data.size), normalize(data.color))
    duplicate = await duplicate_variant(db, product.id, key[0], key[1])
    if duplicate and duplicate.id != entity_id:
        raise ApplicationError(409, "Combinação de tamanho e cor já cadastrada")
    before = repo.serialize(row)
    if row is None:
        row = Variant(
            id=uid(),
            product_id=product.id,
            code="LGD-" + uid().replace("-", "").upper(),
            stock=0,
            version=1,
        )
        db.add(row)
    else:
        row.version += 1
    for field in ("size", "color", "reference_cost", "reference_price", "active"):
        setattr(row, field, getattr(data, field))
    row.normalized_size, row.normalized_color = key
    await db.flush()
    audit(
        db,
        "variant",
        row.id,
        "edit" if before else "create",
        data.reason or "Cadastro inicial",
        before,
        repo.serialize(row),
    )
    return repo.serialize(row)


async def save_variant(db, product_id, data, entity_id=None):
    control = await repo.lock(db)
    result = await create_variant(db, await repo.require(db, Product, product_id), data, entity_id)
    control.revision += 1
    return result
