from app.shared.models.entities import Photo, Product, Variant
from app.shared.persistence.base import rows, serialize
from sqlalchemy import select


async def products(db):
    variants, photos = await rows(db, Variant), await rows(db, Photo)
    return [
        {
            **serialize(p),
            "variants": [serialize(v) for v in variants if v.product_id == p.id],
            "photos": sorted(
                [serialize(f) for f in photos if f.product_id == p.id],
                key=lambda f: (f["position"], f["id"]),
            ),
        }
        for p in await rows(db, Product)
    ]


async def locked_variants(db):
    return list((await db.scalars(select(Variant).order_by(Variant.id).with_for_update())).all())


async def duplicate_variant(db, product_id, size, color):
    return await db.scalar(
        select(Variant).where(
            Variant.product_id == product_id,
            Variant.normalized_size == size,
            Variant.normalized_color == color,
        )
    )
