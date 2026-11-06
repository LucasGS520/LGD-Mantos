from difflib import SequenceMatcher

from app.modules.auxiliaries.public import auxiliary
from app.shared.application.audit import audit
from app.shared.application.errors import ApplicationError
from app.shared.application.normalization import normalize
from app.shared.application.versioning import check_version
from app.shared.models.common import uid
from app.shared.models.entities import Product
from app.shared.persistence import base as repo

from .repository import products
from .variants import create_variant


async def save_product(db, data, entity_id=None):
    control = await repo.lock(db)
    row = await repo.require(db, Product, entity_id) if entity_id else None
    if row:
        check_version(row, data)
        if data.variants:
            raise ApplicationError(422, "Edite cada variante no seu próprio cadastro")
    if data.category_id:
        await auxiliary(db, data.category_id, "category", row.category_id if row else None)
    similar = [
        p
        for p in await repo.rows(db, Product)
        if p.id != entity_id
        and SequenceMatcher(
            None,
            normalize(p.name + " " + p.print_name),
            normalize(data.name + " " + data.print_name),
        ).ratio()
        >= 0.85
    ]
    if similar and not data.accept_similar:
        raise ApplicationError(
            409,
            {
                "message": "Existem produtos semelhantes. Confirme se são peças distintas.",
                "similar_products": [
                    {"id": p.id, "name": p.name, "print_name": p.print_name} for p in similar
                ],
            },
        )
    before = repo.serialize(row)
    if row is None:
        row = Product(id=uid(), version=1)
        db.add(row)
    else:
        row.version += 1
    for field in ("name", "print_name", "brand", "model", "category_id", "notes", "active"):
        setattr(row, field, getattr(data, field))
    await db.flush()
    for variant in data.variants:
        await create_variant(db, row, variant)
    audit(
        db,
        "product",
        row.id,
        "edit" if before else "create",
        data.reason or "Cadastro inicial",
        before,
        repo.serialize(row),
    )
    control.revision += 1
    return next(p for p in await products(db) if p["id"] == row.id)
