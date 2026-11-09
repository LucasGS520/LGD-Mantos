"""Mede a aplicação com dados sintéticos exclusivamente no banco de testes.

O opt-in literal é obrigatório: a preparação substitui os dados da suíte isolada.
Não executar junto de pytest ou Playwright que utilizem o mesmo banco.
"""

import argparse
import asyncio
import json
import os
import platform
import statistics
import time
import tracemalloc
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL, uuid5


def identity(value):
    return str(uuid5(NAMESPACE_URL, "lgd-benchmark/" + str(value)))


def dataset(count, variant_count):
    """Inclui entrada desconhecida, compra, venda e recebimentos parciais."""
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    variants = [identity(f"variant-{n}") for n in range(variant_count)]
    snapshots = {
        vid: {
            "product_id": identity("product"),
            "product_name": "Peça sintética",
            "print_name": "Benchmark",
            "size": str(n),
            "color": "Preto",
            "code": f"BENCH-{n}",
            "reference_price": "30.00",
            "category": None,
            "category_id": None,
            "brand": "Teste",
            "model": "Teste",
        }
        for n, vid in enumerate(variants)
    }
    result = []
    for n in range(count):
        vid = variants[(n // 2) % variant_count]
        kind = "inventory" if n == 0 else "purchase" if n % 2 else "sale"
        items = (
            [
                {"variant_id": v, "quantity": 10, "unit_cost": None if i % 3 == 0 else "10.00"}
                for i, v in enumerate(variants)
            ]
            if n == 0
            else [{"variant_id": vid, "quantity": 2, "unit_cost": "12.00"}]
            if kind == "purchase"
            else [{"variant_id": vid, "quantity": 1, "unit_price": "25.00"}]
        )
        stamp = (start + timedelta(seconds=n)).isoformat()
        payload = {
            "kind": kind,
            "items": items,
            "payments": [],
            "snapshots": {i["variant_id"]: snapshots[i["variant_id"]] for i in items},
            "labels": {},
        }
        if kind == "purchase":
            payload.update(
                supplier_id=identity("supplier"),
                channel_id=identity("purchase_channel"),
                purchase_date=stamp[:10],
            )
            payload["labels"] = {"supplier_id": "Fornecedor", "channel_id": "Compra"}
        if kind == "sale":
            payload["channel_id"] = identity("sale_channel")
            payload["labels"] = {"channel_id": "Venda"}
            payload["payments"] = [
                {
                    "id": identity(f"payment-{n}"),
                    "amount": "10.00",
                    "method_id": identity("payment_method"),
                    "method_name": "Pagamento",
                    "created_at": stamp,
                }
            ]
        result.append(
            {
                "id": identity(f"op-{n}"),
                "sequence": n + 1,
                "kind": kind,
                "effective_at": stamp,
                "created_at": stamp,
                "version": 1,
                "cancelled": False,
                "payload": payload,
            }
        )
    return variants, result


async def run(args):
    url = os.environ.get("TEST_DATABASE_URL", "")
    if (
        urlsplit(url).path != "/lgd_mantos_alignment_test"
        or args.replace_test_data != "lgd_mantos_alignment_test"
    ):
        raise RuntimeError("Defina TEST_DATABASE_URL e confirme apenas lgd_mantos_alignment_test")
    os.environ.update(
        DATABASE_URL=url, APP_PASSWORD="senha-testes", APP_SECRET="segredo-exclusivo-de-testes"
    )
    import main
    from app.core.database import AsyncSessionLocal, engine
    from app.modules.operations.domain.ledger import replay
    from app.shared.models.entities import Auxiliary, Control, Operation, Product, Variant
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy import insert, text

    output = {
        "label": args.label,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "samples": args.samples,
        "warmup": 1,
        "presentation": args.presentation,
        "targets_ms": {
            "simple_query": 1000,
            "preview_confirm": 2000,
            "management_correction": 5000,
        },
        "scenarios": [],
    }
    for count in args.sizes:
        variant_count = min(500, max(10, count // 100))
        variants, history = dataset(count, variant_count)
        tracemalloc.start()
        replay_started = time.perf_counter()
        states, results = replay(history, variants)
        replay_ms = (time.perf_counter() - replay_started) * 1000
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "TRUNCATE lgd_requests, lgd_revisions, lgd_movements, lgd_operations, lgd_photos, lgd_variants, lgd_products, lgd_auxiliaries, lgd_control"
                )
            )
            await conn.execute(
                insert(Auxiliary),
                [
                    {"id": identity(k), "kind": k, "name": k, "normalized_name": k}
                    for k in ("supplier", "purchase_channel", "sale_channel", "payment_method")
                ],
            )
            await conn.execute(
                insert(Product),
                [{"id": identity("product"), "name": "Peça sintética", "print_name": "Benchmark"}],
            )
            await conn.execute(
                insert(Variant),
                [
                    {
                        "id": vid,
                        "product_id": identity("product"),
                        "code": f"BENCH-{n}",
                        "size": str(n),
                        "color": "Preto",
                        "normalized_size": str(n),
                        "normalized_color": "preto",
                        "reference_price": "30.00",
                        "stock": states[vid]["stock"],
                        "average_cost": states[vid]["average_cost"],
                    }
                    for n, vid in enumerate(variants)
                ],
            )
            await conn.execute(
                insert(Control),
                [
                    {
                        "id": 1,
                        "revision": count,
                        "started_at": datetime.fromisoformat(history[0]["effective_at"]),
                    }
                ],
            )
            for offset in range(0, count, 500):
                await conn.execute(
                    insert(Operation),
                    [
                        {
                            **op,
                            "effective_at": datetime.fromisoformat(op["effective_at"]),
                            "created_at": datetime.fromisoformat(op["created_at"]),
                            "result": results[op["id"]],
                        }
                        for op in history[offset : offset + 500]
                    ],
                )
        async with AsyncClient(
            transport=ASGITransport(app=main.app), base_url="http://benchmark"
        ) as client:
            token = (
                await client.post("/api/v1/auth/login", json={"password": "senha-testes"})
            ).json()["token"]
            client.headers["Authorization"] = "Bearer " + token
            scenario = {
                "operations": count,
                "variants": variant_count,
                "replay_traced_ms": round(replay_ms, 2),
                "replay_peak_mib": round(peak / 1024 / 1024, 2),
                "requests": {},
            }

            async def measure(name, method, path, **kwargs):
                samples, sizes = [], []
                for iteration in range(args.samples + 1):
                    started = time.perf_counter()
                    response = await client.request(method, "/api/v1" + path, **kwargs)
                    elapsed = (time.perf_counter() - started) * 1000
                    response.raise_for_status()
                    if iteration:
                        samples.append(elapsed)
                        sizes.append(len(response.content))
                scenario["requests"][name] = {
                    "median_ms": round(statistics.median(samples), 2),
                    "p95_ms": round(
                        sorted(samples)[max(0, __import__("math").ceil(len(samples) * 0.95) - 1)], 2
                    ),
                    "bytes": max(sizes),
                    "errors": 0,
                }
                return response

            await measure("catalog", "GET", "/products")
            await measure(
                "operations",
                "GET",
                "/operations?kind=sale&limit=50" if args.presentation else "/operations",
            )
            await measure(
                "management",
                "GET",
                "/analytics?view=overview" if args.presentation else "/analytics",
            )
            if args.presentation:
                await measure("management_sales", "GET", "/analytics?view=sales&limit=50")
            data = {
                "kind": "sale",
                "channel_id": identity("sale_channel"),
                "items": [{"variant_id": variants[0], "quantity": 1, "unit_price": "25.00"}],
            }
            preview = await measure("preview", "POST", "/operations/preview", json=data)
            # Repetições incluem recibo quente em medida própria, não como confirmação nova.
            started = time.perf_counter()
            confirmed = await client.post(
                "/api/v1/operations",
                json={"data": data, "preview_token": preview.json()["preview_token"]},
                headers={"Idempotency-Key": f"bench-{count}"},
            )
            confirmed.raise_for_status()
            scenario["requests"]["confirm_single"] = {
                "ms": round((time.perf_counter() - started) * 1000, 2),
                "bytes": len(confirmed.content),
            }
            for name, index in (("old", 0), ("middle", count // 2), ("recent", count - 2)):
                op = (await client.get("/api/v1/operations/" + history[index]["id"])).json()
                payload = {
                    k: v for k, v in op["payload"].items() if k not in {"snapshots", "labels"}
                }
                payload["payments"] = [
                    {k: p[k] for k in ("id", "amount", "method_id")} for p in payload["payments"]
                ]
                payload.update(version=op["version"], reason="Correção sintética")
                await measure(
                    "correction_preview_" + name,
                    "POST",
                    f"/operations/{op['id']}/preview",
                    json=payload,
                )
            await measure(
                "movements_origin",
                "GET",
                "/movements?operation_id=" + confirmed.json()["operation"]["id"],
            )
            if args.impact:
                inventory = (await client.get("/api/v1/operations/" + history[0]["id"])).json()
                edit = {
                    "kind": "inventory",
                    "version": inventory["version"],
                    "reason": "Custo conferido no ensaio",
                    "items": [
                        {**item, "unit_cost": "11.00"} for item in inventory["payload"]["items"]
                    ],
                }
                impact = await measure(
                    "correction_cost_preview",
                    "POST",
                    f"/operations/{inventory['id']}/preview",
                    json=edit,
                )
                scenario["correction_affected"] = len(impact.json()["affected"])
                started = time.perf_counter()
                saved = await client.put(
                    f"/api/v1/operations/{inventory['id']}",
                    json={"data": edit, "preview_token": impact.json()["preview_token"]},
                    headers={"Idempotency-Key": f"cost-bench-{count}"},
                )
                saved.raise_for_status()
                scenario["requests"]["correction_cost_confirm_single"] = {
                    "ms": round((time.perf_counter() - started) * 1000, 2),
                    "bytes": len(saved.content),
                }

                async def simultaneous_preview():
                    started = time.perf_counter()
                    response = await client.post("/api/v1/operations/preview", json=data)
                    return {
                        "status": response.status_code,
                        "ms": round((time.perf_counter() - started) * 1000, 2),
                    }

                scenario["four_concurrent_previews"] = await asyncio.gather(
                    *(simultaneous_preview() for _ in range(4))
                )
            output["scenarios"].append(scenario)
            print(json.dumps(scenario, ensure_ascii=False), flush=True)
        async with AsyncSessionLocal() as session:
            output["postgres"] = await session.scalar(text("SHOW server_version"))
        Path(args.output).write_text(
            json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace-test-data", required=True)
    parser.add_argument("--sizes", nargs="+", type=int, default=[1000, 10000, 50000])
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--label", default="baseline")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--presentation",
        action="store_true",
        help="Mede os contratos paginados usados pela interface",
    )
    parser.add_argument(
        "--impact",
        action="store_true",
        help="Inclui correção real de custo e quatro prévias concorrentes",
    )
    arguments = parser.parse_args()
    if min(arguments.sizes) < 10 or arguments.samples < 1:
        parser.error("Use ao menos dez operações e uma amostra")
    asyncio.run(run(arguments))
