from collections import defaultdict

from app.shared.models.entities import Category, Photo, Product, Variant
from app.shared.persistence.base import identifier, rows_by_ids, serialize
from sqlalchemy import select


async def products(db, product_id=None):
    query = select(Product).order_by(Product.created_at, Product.id)
    variant_query, photo_query = select(Variant), select(Photo)
    if product_id is not None:
        product_id = identifier(product_id)
        query = query.where(Product.id == product_id)
        variant_query = variant_query.where(Variant.product_id == product_id)
        photo_query = photo_query.where(Photo.product_id == product_id)
    variants, photos = defaultdict(list), defaultdict(list)
    for variant in (await db.scalars(variant_query.order_by(Variant.id))).all():
        variants[variant.product_id].append(serialize(variant))
    for photo in (
        await db.scalars(photo_query.order_by(Photo.product_id, Photo.position, Photo.id))
    ).all():
        photos[photo.product_id].append(serialize(photo))
    return [
        {
            **serialize(p),
            "variants": variants[p.id],
            "photos": sorted(
                photos[p.id],
                key=lambda f: (f["position"], f["id"]),
            ),
        }
        for p in (await db.scalars(query)).all()
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


async def variant_context(db, ids):
    variants = await rows_by_ids(db, Variant, ids)
    products = await rows_by_ids(db, Product, [variant.product_id for variant in variants.values()])
    categories = await rows_by_ids(
        db, Category, [product.category_id for product in products.values() if product.category_id]
    )
    return variants, products, categories
