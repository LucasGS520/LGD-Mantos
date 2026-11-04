"""Consultas e serialização das entidades do núcleo."""

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select, text

from app.domain.models import Control, Operation, Photo, Product, Revision, Variant


def serialize(row):
    """Representa valores monetários como decimais textuais, sem perda binária."""
    if row is None:
        return None
    result = {}
    for col in row.__table__.columns:
        value = getattr(row, col.name)
        result[col.name] = value.isoformat() if isinstance(value, datetime) else str(value) if isinstance(value, Decimal) else value
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
        raise HTTPException(404, "Registro não encontrado")
    return row


async def products(db):
    variants, photos = await rows(db, Variant), await rows(db, Photo)
    return [{**serialize(p), "variants": [serialize(v) for v in variants if v.product_id == p.id],
             "photos": sorted([serialize(f) for f in photos if f.product_id == p.id], key=lambda f: (f["position"], f["id"]))}
            for p in await rows(db, Product)]


async def operations(db):
    return sorted([serialize(op) for op in await rows(db, Operation)], key=lambda op: (op["effective_at"], op["sequence"]))


async def history(db, entity_id):
    return [serialize(r) for r in (await db.scalars(select(Revision).where(Revision.entity_id == entity_id).order_by(Revision.created_at))).all()]
