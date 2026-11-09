"""Confere replay, projeções, recibos e arquivos apenas na base isolada restaurada."""

import asyncio
import json
import os
from urllib.parse import urlsplit


async def main():
    if urlsplit(os.environ.get("DATABASE_URL", "")).path != "/lgd_mantos_alignment_test":
        raise RuntimeError("Verificação permitida somente no banco de testes")
    from app.core.database import AsyncSessionLocal, engine
    from app.modules.operations.public import operations, replay
    from app.modules.photos.infrastructure.local_storage import storage
    from app.shared.models.entities import Movement, Photo, RequestReceipt, Variant
    from sqlalchemy import select, text

    async with AsyncSessionLocal() as db:
        await db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        history = await operations(db)
        variants = list((await db.scalars(select(Variant))).all())
        states, results = replay(history, [v.id for v in variants])
        for operation in history:
            assert operation["result"] == results[operation["id"]], "Resultado diverge do replay"
        for variant in variants:
            assert variant.stock == states[variant.id]["stock"]
            assert (
                str(variant.average_cost) if variant.average_cost is not None else None
            ) == states[variant.id]["average_cost"]
            movements = (
                await db.scalars(select(Movement).where(Movement.variant_id == variant.id))
            ).all()
            assert sum(m.delta for m in movements) == variant.stock
        ids = {op["id"] for op in history}
        receipts = (await db.scalars(select(RequestReceipt))).all()
        assert all(receipt.response["operation"]["id"] in ids for receipt in receipts)
        photos = (await db.scalars(select(Photo))).all()
        for photo in photos:
            storage.validate(storage.path(photo.filename).read_bytes())
        print(
            json.dumps(
                {
                    "operations_equivalent_to_replay": len(history),
                    "variants_verified": len(variants),
                    "receipts_verified": len(receipts),
                    "photo_contents_verified": len(photos),
                }
            )
        )
        await db.rollback()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
