"""Compara índices em carga SQL sintética somente na base isolada confirmada.

Esta carga mede padrões de acesso, não um histórico operacional para replay.
Substitui os dados de teste; não executar junto de outras suítes.
"""

import argparse
import asyncio
import json
import os
import statistics
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL, uuid5

from app.shared.models.entities import (
    Base,
    Movement,
    Operation,
    Photo,
    Product,
    PurchaseChannel,
    Revision,
    SaleChannel,
    Supplier,
    Variant,
)
from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import create_async_engine


def identity(key):
    return str(uuid5(NAMESPACE_URL, "lgd-index/" + str(key)))


async def run(args):
    url = os.environ.get("TEST_MIGRATION_DATABASE_URL", "")
    if (
        args.replace_test_data != "lgd_mantos_alignment_test"
        or urlsplit(url).path != "/lgd_mantos_alignment_test"
    ):
        raise RuntimeError("Confirme exclusivamente a base isolada de teste")
    engine = create_async_engine(url, hide_parameters=True)
    stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    async with engine.begin() as conn:
        await conn.execute(
            text("TRUNCATE " + ",".join('"' + name + '"' for name in sorted(Base.metadata.tables)))
        )
        for model in (Supplier, PurchaseChannel, SaleChannel):
            await conn.execute(
                insert(model),
                [
                    {
                        "id": identity(model.__tablename__),
                        "name": "Sintético",
                        "normalized_name": "sintetico",
                    }
                ],
            )
        await conn.execute(
            insert(Product),
            [
                {"id": identity("p" + str(n)), "name": "Peça", "print_name": str(n)}
                for n in range(500)
            ],
        )
        await conn.execute(
            insert(Variant),
            [
                {
                    "id": identity("v"),
                    "product_id": identity("p0"),
                    "code": "INDEX",
                    "size": "M",
                    "color": "Preto",
                    "normalized_size": "m",
                    "normalized_color": "preto",
                }
            ],
        )
        for start in range(0, 50000, 500):
            await conn.execute(
                insert(Operation),
                [
                    {
                        "id": identity(n),
                        "kind": "sale" if n % 2 else "purchase",
                        "sequence": n + 1,
                        "effective_at": stamp + timedelta(seconds=n),
                        "purchase_date": date(2026, 1, 1) if n % 2 == 0 else None,
                        "supplier_id": identity("lgd_suppliers") if n % 2 == 0 else None,
                        "purchase_channel_id": identity("lgd_purchase_channels")
                        if n % 2 == 0
                        else None,
                        "sale_channel_id": identity("lgd_sale_channels") if n % 2 else None,
                    }
                    for n in range(start, start + 500)
                ],
            )
        for start in range(0, 100000, 1000):
            await conn.execute(
                insert(Movement),
                [
                    {
                        "id": identity("m" + str(n)),
                        "operation_id": identity(0 if n % 100 == 0 else n % 50000),
                        "variant_id": identity("v"),
                        "version": 1,
                        "delta": 1 if n % 2 else -1,
                        "reason": "Carga de índice",
                        "created_at": stamp + timedelta(seconds=n),
                    }
                    for n in range(start, start + 1000)
                ],
            )
            await conn.execute(
                insert(Revision),
                [
                    {
                        "id": identity("r" + str(n)),
                        "entity_id": identity(0 if n % 100 == 0 else n % 50000),
                        "entity_type": "operation",
                        "action": "edit",
                        "reason": "Carga de índice",
                        "before": {"synthetic": True},
                        "after": {"synthetic": True},
                        "created_at": stamp + timedelta(seconds=n),
                    }
                    for n in range(start, start + 1000)
                ],
            )
        for start in range(0, 10000, 1000):
            await conn.execute(
                insert(Photo),
                [
                    {
                        "id": identity("f" + str(n)),
                        "product_id": identity("p" + str(n % 500)),
                        "filename": str(n) + ".png",
                        "position": n // 500,
                    }
                    for n in range(start, start + 1000)
                ],
            )
        await conn.execute(text("ANALYZE"))
    cases = [
        (
            "ix_lgd_operations_kind_sequence",
            "lgd_operations",
            "kind, sequence DESC",
            "SELECT * FROM lgd_operations WHERE kind='sale' AND sequence<25000 ORDER BY sequence DESC LIMIT 50",
            {},
        ),
        (
            "ix_lgd_movements_origin",
            "lgd_movements",
            "operation_id, created_at, id",
            "SELECT * FROM lgd_movements WHERE operation_id=:id ORDER BY created_at,id",
            {"id": identity(0)},
        ),
        (
            "ix_lgd_revisions_origin",
            "lgd_revisions",
            "entity_id, created_at, id",
            "SELECT * FROM lgd_revisions WHERE entity_id=:id ORDER BY created_at,id",
            {"id": identity(0)},
        ),
        (
            "ix_lgd_photos_product_order",
            "lgd_photos",
            "product_id, position, id",
            "SELECT * FROM lgd_photos WHERE product_id=:id ORDER BY position,id",
            {"id": identity("p0")},
        ),
    ]
    output = {
        "synthetic": True,
        "samples": 5,
        "operations": 50000,
        "movements": 100000,
        "revisions": 100000,
        "photos": 10000,
        "cases": [],
    }
    async with engine.begin() as conn:

        async def measure(sql, params):
            samples = []
            for iteration in range(6):
                result = await conn.scalar(
                    text("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql), params
                )
                plan = json.loads(result) if isinstance(result, str) else result
                if iteration:
                    samples.append(plan[0])
            return {
                "median_ms": statistics.median(p["Execution Time"] for p in samples),
                "plan": samples[-1],
            }

        def sorts(plan):
            return int(plan.get("Node Type") == "Sort") + sum(
                sorts(child) for child in plan.get("Plans", [])
            )

        for name, table, fields, sql, params in cases:
            await conn.execute(text("DROP INDEX IF EXISTS " + name))
            before = await measure(sql, params)
            started = time.perf_counter()
            await conn.execute(text(f"CREATE INDEX {name} ON {table} ({fields})"))
            build_ms = (time.perf_counter() - started) * 1000
            after = await measure(sql, params)
            pre, post = before["plan"]["Plan"], after["plan"]["Plan"]
            buffers_before = pre.get("Shared Hit Blocks", 0) + pre.get("Shared Read Blocks", 0)
            buffers_after = post.get("Shared Hit Blocks", 0) + post.get("Shared Read Blocks", 0)
            chosen = (
                sorts(post) < sorts(pre)
                or buffers_after < buffers_before * 0.8
                or (before["median_ms"] >= 0.2 and after["median_ms"] < before["median_ms"] * 0.8)
            )
            output["cases"].append(
                {
                    "index": name,
                    "table": table,
                    "fields": fields,
                    "sql": sql,
                    "before": before,
                    "after": after,
                    "build_ms": round(build_ms, 2),
                    "bytes": await conn.scalar(text(f"SELECT pg_relation_size('{name}')")),
                    "chosen": chosen,
                }
            )
            await conn.execute(text("DROP INDEX " + name))
    await engine.dispose()
    Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(
        json.dumps(
            [{key: case[key] for key in ("index", "chosen", "bytes")} for case in output["cases"]]
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace-test-data", required=True)
    parser.add_argument("--output", required=True)
    asyncio.run(run(parser.parse_args()))
