"""Critérios operacionais do documento definitivo, em PostgreSQL real."""

import asyncio
import io
from uuid import uuid4

import pytest
from app.core.database import engine
from conftest import aux, confirm, correction, sale, setup
from PIL import Image
from sqlalchemy import text


async def test_complete_journey_and_payment_corrections(client):
    refs, product, vid, inventory = await setup(client)
    op = await confirm(
        client, sale(refs, vid, 2, [{"amount": "20.00", "method_id": refs["payment_method"]["id"]}])
    )
    assert op["result"]["balance"] == "30.00"
    assert op["result"]["gross_result"] == "30.00"
    assert op["result"]["commercial_difference"] == "10.00"
    edit = correction(op)
    edit["payments"].append({"amount": "30.00", "method_id": refs["payment_method"]["id"]})
    op = await confirm(client, edit, op["id"])
    assert op["result"]["financial_status"] == "concluída"
    edit = correction(op)
    edit["payments"].pop()
    op = await confirm(client, edit, op["id"])
    assert op["result"]["financial_status"] == "pendente"
    report = (await client.get("/api/v1/analytics")).json()
    assert report["summary"]["stock_units"] == 8
    assert report["summary"]["received"] == "20.00"
    assert report["summary"]["pending"] == "30.00"
    cancel = {**correction(op), "cancelled": True}
    op = await confirm(client, cancel, op["id"])
    assert op["cancelled"]
    report = (await client.get("/api/v1/analytics")).json()
    assert report["summary"]["stock_units"] == 10
    assert report["summary"]["received"] == "0.00"
    history = (await client.get(f"/api/v1/history/{op['id']}")).json()
    assert len(history) == 4
    assert history[-1]["before"]["payload"]["payments"]


async def test_unknown_cost_never_becomes_zero(client):
    refs, product, vid, inventory = await setup(client, cost=None)
    op = await confirm(client, sale(refs, vid))
    assert op["result"]["historical_cost"] is None
    assert op["result"]["gross_result"] is None
    assert op["result"]["unknown_cost_units"] == 1
    edit = correction(inventory)
    edit["items"][0]["unit_cost"] = "12.00"
    path = f"/api/v1/operations/{inventory['id']}"
    preview = (await client.post(path + "/preview", json=edit)).json()
    assert preview["affected"][0]["after"]["historical_cost"] == "12.00"
    await confirm(client, edit, inventory["id"])
    historical = (await client.get(f"/api/v1/operations/{op['id']}")).json()
    assert historical["result"]["historical_cost"] == "12.00"
    assert (await client.get(f"/api/v1/history/{op['id']}")).json()[-1]["action"] == "recalculate"


async def test_purchase_average_and_safe_cancellation(client):
    refs, product, vid, inventory = await setup(client, stock=2)
    purchase = await confirm(
        client,
        {
            "kind": "purchase",
            "supplier_id": refs["supplier"]["id"],
            "channel_id": refs["purchase_channel"]["id"],
            "items": [{"variant_id": vid, "quantity": 2, "unit_cost": "20.00"}],
        },
    )
    rows = (await client.get("/api/v1/products")).json()
    assert rows[0]["variants"][0]["average_cost"] == "15.00"
    detail = (await client.get(f"/api/v1/operations/{purchase['id']}")).json()
    assert len(detail["result"]["items"]) == 1
    op = await confirm(client, sale(refs, vid, 3))
    assert op["result"]["historical_cost"] == "45.00"
    cancel = {**correction(purchase), "cancelled": True}
    response = await client.post(f"/api/v1/operations/{purchase['id']}/preview", json=cancel)
    assert response.status_code == 422
    assert (await client.get(f"/api/v1/operations/{purchase['id']}")).json()["cancelled"] is False


async def test_idempotency_and_stale_preview(client):
    refs, _, vid, _ = await setup(client)
    data = sale(refs, vid)
    preview = (await client.post("/api/v1/operations/preview", json=data)).json()
    headers = {"Idempotency-Key": str(uuid4())}
    body = {"data": data, "preview_token": preview["preview_token"]}
    first = await client.post("/api/v1/operations", json=body, headers=headers)
    repeated = await client.post("/api/v1/operations", json=body, headers=headers)
    assert first.status_code == repeated.status_code == 200
    assert first.json()["operation"]["id"] == repeated.json()["operation"]["id"]
    stale = await client.post(
        "/api/v1/operations", json=body, headers={"Idempotency-Key": str(uuid4())}
    )
    assert stale.status_code == 409
    assert (await client.get("/api/v1/analytics")).json()["summary"]["stock_units"] == 9


async def test_concurrent_confirmations_cannot_oversell(client):
    refs, _, vid, _ = await setup(client, stock=1)
    data = sale(refs, vid)
    preview = (await client.post("/api/v1/operations/preview", json=data)).json()

    async def send():
        return await client.post(
            "/api/v1/operations",
            json={"data": data, "preview_token": preview["preview_token"]},
            headers={"Idempotency-Key": str(uuid4())},
        )

    responses = await asyncio.gather(send(), send())
    assert sorted(r.status_code for r in responses) == [200, 409]
    assert (await client.get("/api/v1/analytics")).json()["summary"]["stock_units"] == 0


async def test_normalization_and_auxiliary_rename_snapshots(client):
    await aux(client, "category", "  CAMÍSAS  ")
    duplicate = await client.post(
        "/api/v1/auxiliaries", json={"kind": "category", "name": "camisas"}
    )
    assert duplicate.status_code == 409
    refs, product, vid, _ = await setup(client)
    duplicate = await client.post(
        f"/api/v1/products/{product['id']}/variants", json={"size": " m ", "color": "PRÉTO"}
    )
    assert duplicate.status_code == 409
    op = await confirm(client, sale(refs, vid))
    channel = refs["sale_channel"]
    edited = await client.put(
        f"/api/v1/auxiliaries/{channel['id']}",
        json={
            "kind": channel["kind"],
            "name": "Direto",
            "version": channel["version"],
            "reason": "Nome conferido",
            "active": False,
        },
    )
    assert edited.status_code == 200
    historical = (await client.get(f"/api/v1/operations/{op['id']}")).json()
    assert historical["payload"]["labels"]["channel_id"] == "sale_channel"
    assert (
        await client.post("/api/v1/operations/preview", json=sale(refs, vid))
    ).status_code == 422


@pytest.mark.parametrize(
    "change",
    [
        {"quantity": 0},
        {"quantity": -1},
        {"quantity": 1.5},
        {"unit_price": "0.00"},
        {"unit_price": "-1.00"},
        {"unit_price": "1.001"},
        {"unit_cost": "1.00"},
    ],
)
async def test_invalid_sales_are_atomic(client, change):
    refs, _, vid, _ = await setup(client)
    data = sale(refs, vid)
    data["items"][0].update(change)
    assert (await client.post("/api/v1/operations/preview", json=data)).status_code == 422
    assert (await client.get("/api/v1/analytics")).json()["summary"]["stock_units"] == 10


async def test_repeated_variant_and_payment_excess(client):
    refs, _, vid, _ = await setup(client)
    data = sale(refs, vid)
    data["items"] *= 2
    assert (await client.post("/api/v1/operations/preview", json=data)).status_code == 422
    data = sale(
        refs, vid, payments=[{"amount": "26.00", "method_id": refs["payment_method"]["id"]}]
    )
    assert (await client.post("/api/v1/operations/preview", json=data)).status_code == 422


async def test_inventory_gate_and_initial_uniqueness(client):
    ref = await aux(client, "sale_channel")
    product = (
        await client.post(
            "/api/v1/products",
            json={"name": "A", "print_name": "A", "variants": [{"size": "M", "color": "Azul"}]},
        )
    ).json()
    vid = product["variants"][0]["id"]
    data = {
        "kind": "sale",
        "channel_id": ref["id"],
        "items": [{"variant_id": vid, "quantity": 1, "unit_price": "5.00"}],
    }
    assert (await client.post("/api/v1/operations/preview", json=data)).status_code == 422
    inv = {"kind": "inventory", "items": [{"variant_id": vid, "quantity": 1}]}
    await confirm(client, inv)
    assert (await client.post("/api/v1/operations/preview", json=inv)).status_code == 422


async def test_stock_cannot_be_written_in_catalog(client):
    _, product, vid, _ = await setup(client)
    response = await client.put(
        f"/api/v1/products/{product['id']}/variants/{vid}",
        json={"size": "M", "color": "Preto", "stock": 100, "version": 1, "reason": "teste"},
    )
    assert response.status_code == 422


async def test_adjustment_requires_reason_and_cost(client):
    _, _, vid, _ = await setup(client, cost=None)
    data = {"kind": "adjustment", "direction": "in", "items": [{"variant_id": vid, "quantity": 1}]}
    assert (await client.post("/api/v1/operations/preview", json=data)).status_code == 422
    data["reason"] = "Contagem conferida"
    assert (await client.post("/api/v1/operations/preview", json=data)).status_code == 422
    data["items"][0]["unit_cost"] = "12.00"
    await confirm(client, data)
    assert (await client.get("/api/v1/analytics")).json()["summary"]["unknown_stock_units"] == 10


async def test_photos_validate_ownership_and_access(client):
    _, product, vid, _ = await setup(client)
    bad = await client.post(
        f"/api/v1/products/{product['id']}/photos",
        files={"file": ("bad.jpg", b"not a photo", "image/jpeg")},
    )
    assert bad.status_code == 422
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(buffer, "PNG")
    photo = await client.post(
        f"/api/v1/products/{product['id']}/photos",
        files={"file": ("a.png", buffer.getvalue(), "image/png")},
    )
    assert photo.status_code == 200, photo.text
    photo = photo.json()
    assert photo["primary"]
    assert (await client.get(f"/api/v1/photos/{photo['id']}/content")).status_code == 200
    assert (
        await client.put(
            f"/api/v1/photos/{photo['id']}",
            json={"position": 2, "primary": True, "variant_id": vid, "color": "Preto"},
        )
    ).status_code == 200
    assert (await client.delete(f"/api/v1/photos/{photo['id']}")).status_code == 200
    assert (await client.get(f"/api/v1/photos/{photo['id']}/content")).status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        "/expenses",
        "/export/reports",
        "/analytics/finance/dre",
        "/analytics/product-classification",
        "/settings/preferences",
        "/agents/runs",
        "/uploads/a.jpg",
    ],
)
async def test_removed_capabilities_are_unreachable(client, path):
    assert (await client.get("/api/v1" + path)).status_code == 404


async def test_date_filter_and_current_pending(client):
    refs, _, vid, _ = await setup(client)
    await confirm(client, sale(refs, vid))
    report = (await client.get("/api/v1/analytics?start=2000-01-01&end=2000-01-02")).json()
    assert report["summary"]["sold"] == "0.00"
    assert report["summary"]["pending"] == "25.00"
    assert report["summary"]["stock_units"] == 9
    assert (
        await client.get("/api/v1/analytics?start=2026-02-01&end=2026-01-01")
    ).status_code == 422


async def test_migration_has_all_active_tables(client):
    async with engine.connect() as conn:
        assert (
            await conn.execute(text("SELECT version_num FROM alembic_version"))
        ).scalar() == "0006"
        assert (
            await conn.execute(
                text(
                    "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'lgd_%'"
                )
            )
        ).scalar() == 9


async def test_empty_inventory_and_unknown_reference(client):
    await confirm(client, {"kind": "inventory", "items": []})
    refs = {kind: await aux(client, kind) for kind in ("sale_channel", "payment_method")}
    product = (
        await client.post(
            "/api/v1/products",
            json={
                "name": "Peça",
                "print_name": "Sem referência",
                "variants": [{"size": "P", "color": "Azul"}],
            },
        )
    ).json()
    vid = product["variants"][0]["id"]
    await confirm(
        client,
        {
            "kind": "adjustment",
            "direction": "in",
            "reason": "Contagem",
            "items": [{"variant_id": vid, "quantity": 1, "unit_cost": "8.00"}],
        },
    )
    op = await confirm(client, sale(refs, vid))
    assert op["result"]["commercial_difference"] is None
    assert op["result"]["historical_cost"] == "8.00"
    await confirm(
        client,
        {
            "kind": "adjustment",
            "direction": "in",
            "reason": "Contagem seguinte",
            "items": [{"variant_id": vid, "quantity": 1}],
        },
    )
    assert (await client.get("/api/v1/products")).json()[0]["variants"][0]["average_cost"] == "8.00"


async def test_purchase_does_not_hide_unknown_inventory_cost(client):
    refs, _, vid, _ = await setup(client, stock=2, cost=None)
    await confirm(
        client,
        {
            "kind": "purchase",
            "supplier_id": refs["supplier"]["id"],
            "channel_id": refs["purchase_channel"]["id"],
            "items": [{"variant_id": vid, "quantity": 2, "unit_cost": "20.00"}],
        },
    )
    variant = (await client.get("/api/v1/products")).json()[0]["variants"][0]
    assert variant["average_cost"] is None
    report = (await client.get("/api/v1/analytics")).json()
    assert report["summary"]["stock_value"] == "40.00"
    assert report["summary"]["unknown_stock_units"] == 2
    op = await confirm(client, sale(refs, vid, 2))
    assert op["result"]["unknown_cost_units"] == 2
    assert (await client.get("/api/v1/products")).json()[0]["variants"][0][
        "average_cost"
    ] == "20.00"


async def test_purchase_cost_correction_recalculates_later_sale(client):
    refs, _, vid, _ = await setup(client, stock=2)
    purchase = await confirm(
        client,
        {
            "kind": "purchase",
            "supplier_id": refs["supplier"]["id"],
            "channel_id": refs["purchase_channel"]["id"],
            "items": [{"variant_id": vid, "quantity": 2, "unit_cost": "20.00"}],
        },
    )
    op = await confirm(client, sale(refs, vid))
    edit = correction(purchase)
    edit["items"][0]["unit_cost"] = "30.00"
    await confirm(client, edit, purchase["id"])
    later = (await client.get(f"/api/v1/operations/{op['id']}")).json()
    assert later["result"]["historical_cost"] == "20.00"
    assert later["version"] == 2
    assert (await client.get("/api/v1/products")).json()[0]["variants"][0][
        "average_cost"
    ] == "20.00"


async def test_edit_stock_delta_and_all_or_nothing(client):
    refs, _, vid, _ = await setup(client, stock=5)
    op = await confirm(client, sale(refs, vid, 2))
    edit = correction(op)
    edit["items"][0]["quantity"] = 3
    op = await confirm(client, edit, op["id"])
    moves = [
        m for m in (await client.get("/api/v1/movements")).json() if m["operation_id"] == op["id"]
    ]
    assert sum(m["delta"] for m in moves) == -3
    edit = correction(op)
    edit["items"][0]["quantity"] = 6
    assert (
        await client.post(f"/api/v1/operations/{op['id']}/preview", json=edit)
    ).status_code == 422
    assert (await client.get("/api/v1/analytics")).json()["summary"]["stock_units"] == 2


async def test_payment_edit_preserves_time_and_rejects_excess(client):
    refs, _, vid, _ = await setup(client)
    op = await confirm(
        client,
        sale(refs, vid, payments=[{"amount": "25.00", "method_id": refs["payment_method"]["id"]}]),
    )
    old_time = op["payload"]["payments"][0]["created_at"]
    edit = correction(op)
    edit["payments"][0]["amount"] = "20.00"
    op = await confirm(client, edit, op["id"])
    assert op["payload"]["payments"][0]["created_at"] == old_time
    assert op["result"]["balance"] == "5.00"
    edit = correction(op)
    edit["items"][0]["unit_price"] = "10.00"
    assert (
        await client.post(f"/api/v1/operations/{op['id']}/preview", json=edit)
    ).status_code == 422


async def test_photo_file_compensated_on_database_failure(client, monkeypatch):
    from app.modules.photos import service
    from app.modules.photos.infrastructure.local_storage import storage

    _, product, _, _ = await setup(client)
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4)).save(buffer, "PNG")

    def fail(*args, **kwargs):
        raise RuntimeError("Falha simulada na persistência")

    monkeypatch.setattr(service, "audit", fail)
    with pytest.raises(RuntimeError, match="Falha simulada"):
        await client.post(
            f"/api/v1/products/{product['id']}/photos",
            files={"file": ("a.png", buffer.getvalue(), "image/png")},
        )
    assert not list(storage.root.glob("*"))
    assert (await client.get("/api/v1/products")).json()[0]["photos"] == []


async def test_photo_association_cannot_cross_products(client):
    _, product, _, _ = await setup(client)
    other = (
        await client.post(
            "/api/v1/products",
            json={
                "name": "Outra peça",
                "print_name": "Outra arte",
                "variants": [{"size": "G", "color": "Branco"}],
            },
        )
    ).json()
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4)).save(buffer, "PNG")
    photo = (
        await client.post(
            f"/api/v1/products/{product['id']}/photos",
            files={"file": ("a.png", buffer.getvalue(), "image/png")},
        )
    ).json()
    response = await client.put(
        f"/api/v1/photos/{photo['id']}",
        json={"position": 0, "variant_id": other["variants"][0]["id"]},
    )
    assert response.status_code == 422
    token = client.headers.pop("Authorization")
    assert (await client.get(f"/api/v1/photos/{photo['id']}/content")).status_code in (401, 403)
    client.headers["Authorization"] = token


async def test_stale_versions_and_idempotency_key_reuse(client):
    refs, _, vid, _ = await setup(client)
    data = sale(refs, vid)
    key = str(uuid4())
    op = await confirm(client, data, key=key)
    data["items"][0]["unit_price"] = "26.00"
    preview = (await client.post("/api/v1/operations/preview", json=data)).json()
    response = await client.post(
        "/api/v1/operations",
        json={"data": data, "preview_token": preview["preview_token"]},
        headers={"Idempotency-Key": key},
    )
    assert response.status_code == 409
    edit = correction(op)
    await confirm(client, edit, op["id"])
    assert (
        await client.post(f"/api/v1/operations/{op['id']}/preview", json=edit)
    ).status_code == 409
