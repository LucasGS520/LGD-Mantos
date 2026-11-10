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
    from app.shared.models.entities import (
        Base,
        Movement,
        OperationItem,
        Photo,
        RequestReceipt,
        SalePayment,
        Variant,
    )
    from sqlalchemy import select, text

    async with AsyncSessionLocal() as db:
        await db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        assert await db.scalar(text("SELECT current_user")) == "lgd_app"
        assert await db.scalar(text("SELECT version_num FROM alembic_version")) == "0007"
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
        assert all(
            receipt.operation_id == receipt.response["operation"]["id"] for receipt in receipts
        )
        for table in ("lgd_movements", "lgd_revisions", "lgd_requests"):
            assert not await db.scalar(
                text(
                    "SELECT has_table_privilege('lgd_app',:table,'UPDATE') OR has_table_privilege('lgd_app',:table,'DELETE')"
                ),
                {"table": table},
            )
        tables = set(
            (
                await db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
            ).scalars()
        )
        assert tables == set(Base.metadata.tables) | {"alembic_version"}
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
                    "schema_revision": "0007",
                    "application_role": "lgd_app",
                    "items_verified": len((await db.scalars(select(OperationItem))).all()),
                    "payments_verified": len((await db.scalars(select(SalePayment))).all()),
                }
            )
        )
        await db.rollback()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
