"""Proteções reais do PostgreSQL, independentes das validações HTTP."""

from uuid import uuid4

import pytest
from app.core.database import engine
from app.shared.models.entities import Base
from conftest import admin_engine, confirm, correction, sale, setup
from sqlalchemy import inspect, text
from sqlalchemy.exc import DBAPIError


async def rejected(
    statement, parameters=None, states=("23503", "23505", "23514", "23502"), runtime=False
):
    with pytest.raises(DBAPIError) as failure:
        async with (engine if runtime else admin_engine).begin() as connection:
            await connection.execute(text(statement), parameters or {})
    assert failure.value.orig.sqlstate in states


async def test_schema_matches_metadata_and_permissions():
    from conftest import admin_url
    from database_inspect import diagnose

    result = await diagnose(admin_url)
    assert result["read_only"]
    assert result["drift"] == []
    assert result["missing_checks"] == {}
    assert set(result["tables"]) == set(Base.metadata.tables) | {"alembic_version"}
    for permission in result["permissions"]:
        assert permission["tableowner"] == "lgd_migrator"
        assert not permission["can_truncate"]
        if permission["tablename"] in {
            "alembic_version",
            "lgd_movements",
            "lgd_revisions",
            "lgd_requests",
        }:
            assert not permission["can_update"] and not permission["can_delete"]
    async with admin_engine.connect() as connection:

        def verify(sync):
            inspector = inspect(sync)
            for table in Base.metadata.tables:
                for foreign_key in inspector.get_foreign_keys(table):
                    assert foreign_key["options"]["ondelete"] == "RESTRICT"
                for column in inspector.get_columns(table):
                    if column["name"] == "id" and table != "lgd_control":
                        assert str(column["type"]) == "UUID"
            assert "payload" not in {
                column["name"] for column in inspector.get_columns("lgd_operations")
            }

        await connection.run_sync(verify)


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE lgd_movements SET reason=reason WHERE false",
        "DELETE FROM lgd_movements WHERE false",
        "UPDATE lgd_revisions SET reason=reason WHERE false",
        "DELETE FROM lgd_revisions WHERE false",
        "UPDATE lgd_requests SET fingerprint=fingerprint WHERE false",
        "DELETE FROM lgd_requests WHERE false",
        "DELETE FROM lgd_operations WHERE false",
        "DELETE FROM lgd_products WHERE false",
        "TRUNCATE lgd_movements",
        "CREATE TABLE public.not_allowed (id integer)",
        "CREATE TEMP TABLE not_allowed (id integer)",
        "ALTER TABLE lgd_products ADD COLUMN not_allowed integer",
        "SET ROLE lgd_migrator",
    ],
)
async def test_runtime_cannot_modify_history_or_schema(statement):
    async with engine.connect() as connection:
        assert await connection.scalar(text("SELECT current_user")) == "lgd_app"
    await rejected(statement, states=("42501",), runtime=True)


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE lgd_variants SET average_cost=-1",
        "UPDATE lgd_variants SET reference_cost='NaN'::numeric",
        "UPDATE lgd_variants SET version=0",
        "UPDATE lgd_control SET revision=-1",
        "UPDATE lgd_operation_items SET quantity=0",
        "UPDATE lgd_operation_items SET position=-1",
        "UPDATE lgd_operations SET document_version=0",
        "UPDATE lgd_operations SET labels='[]'::jsonb",
        "UPDATE lgd_operations SET cancelled=true WHERE kind='inventory'",
        "UPDATE lgd_movements SET delta=0",
        "UPDATE lgd_revisions SET action='unknown'",
        "UPDATE lgd_requests SET fingerprint='invalid'",
    ],
)
async def test_checks_reject_invalid_values(client, statement):
    await setup(client)
    await rejected(statement, states=("23514",))


async def test_typed_foreign_keys_and_single_inventory(client):
    refs, product, vid, inventory = await setup(client)
    await rejected(
        "UPDATE lgd_products SET category_id=:id", {"id": refs["supplier"]["id"]}, states=("23503",)
    )
    await rejected(
        "INSERT INTO lgd_operations(id,sequence,kind,effective_at) VALUES (:id,99999,'inventory',now())",
        {"id": str(uuid4())},
        states=("23505",),
    )
    await rejected(
        "UPDATE lgd_operation_items SET operation_kind='sale', unit_cost=NULL, unit_price=20",
        states=("23503",),
    )
    op = await confirm(
        client,
        sale(refs, vid, payments=[{"amount": "5.00", "method_id": refs["payment_method"]["id"]}]),
    )
    await rejected(
        "UPDATE lgd_sale_payments SET operation_id=:id", {"id": inventory["id"]}, states=("23503",)
    )
    await rejected("UPDATE lgd_sale_payments SET operation_kind='purchase'", states=("23514",))
    await rejected(
        "UPDATE lgd_sale_payments SET method_id=:id",
        {"id": refs["supplier"]["id"]},
        states=("23503",),
    )
    await rejected("UPDATE lgd_sale_payments SET amount='NaN'::numeric", states=("23514",))
    before = op["payload"]["payments"][0]
    edit = correction(op)
    edit["payments"][0]["amount"] = "10.00"
    corrected = await confirm(client, edit, op["id"])
    after = corrected["payload"]["payments"][0]
    assert (before["id"], before["created_at"], before["method_name"]) == (
        after["id"],
        after["created_at"],
        after["method_name"],
    )
    async with admin_engine.connect() as connection:
        assert await connection.scalar(text("SELECT count(*) FROM lgd_sale_payments")) == 1


async def test_unknown_document_version_is_not_silently_processed(client):
    _, _, _, inventory = await setup(client)
    async with admin_engine.begin() as connection:
        await connection.execute(text("UPDATE lgd_operations SET document_version=2"))
    assert (await client.get("/api/v1/operations/" + inventory["id"])).status_code == 503


async def test_photo_composite_reference_and_unique_primary(client):
    from test_architecture import picture

    _, product, vid, _ = await setup(client)
    other = (
        await client.post(
            "/api/v1/products",
            json={"name": "Outra peça", "print_name": "Outra", "accept_similar": True},
        )
    ).json()
    await rejected(
        "INSERT INTO lgd_photos(id,product_id,variant_id,filename) VALUES (:id,:product,:variant,'wrong.png')",
        {"id": str(uuid4()), "product": other["id"], "variant": vid},
        states=("23503",),
    )
    photos = [
        (
            await client.post(
                f"/api/v1/products/{product['id'].upper()}/photos",
                files={"file": ("a.png", picture(), "image/png")},
            )
        ).json()
        for _ in range(2)
    ]
    await rejected('UPDATE lgd_photos SET "primary"=true', states=("23505",))
    replaced = []
    for photo_id in (photos[0]["id"].upper(), photos[0]["id"]):
        response = await client.put(
            f"/api/v1/photos/{photo_id}/content",
            files={"file": ("a.png", picture(), "image/png")},
        )
        assert response.status_code == 200
        replaced.append(response.json()["filename"])
    assert replaced[0] == replaced[1]
    # Alternar nos dois sentidos cobre qualquer ordem lexicográfica dos UUIDs.
    for photo in (photos[1], photos[0]):
        response = await client.put(
            "/api/v1/photos/" + photo["id"], json={"position": 0, "primary": True}
        )
        assert response.status_code == 200
    async with admin_engine.connect() as connection:
        assert await connection.scalar(text('SELECT count(*) FROM lgd_photos WHERE "primary"')) == 1


async def test_initializer_refuses_old_revision_without_mutation(client):
    from conftest import admin_url
    from init_db import verify_destination

    async with admin_engine.begin() as connection:
        await connection.execute(text("UPDATE alembic_version SET version_num='0006'"))
    try:
        with pytest.raises(RuntimeError, match="Base antiga"):
            await verify_destination(admin_url)
        async with admin_engine.connect() as connection:
            assert (
                await connection.scalar(text("SELECT version_num FROM alembic_version")) == "0006"
            )
    finally:
        async with admin_engine.begin() as connection:
            await connection.execute(text("UPDATE alembic_version SET version_num='0007'"))


async def test_payment_order_can_change_without_changing_identity(client):
    refs, product, vid, _ = await setup(client)
    operation = await confirm(
        client,
        sale(
            refs,
            vid,
            payments=[
                {"amount": value, "method_id": refs["payment_method"]["id"]}
                for value in ("2.00", "3.00")
            ],
        ),
    )
    before = operation["payload"]["payments"]
    edit = correction(operation)
    edit["payments"].reverse()
    updated = await confirm(client, edit, operation["id"])
    assert [p["id"] for p in updated["payload"]["payments"]] == [p["id"] for p in reversed(before)]
    assert [p["created_at"] for p in updated["payload"]["payments"]] == [
        p["created_at"] for p in reversed(before)
    ]


async def test_readiness_does_not_accept_administrative_role():
    from app.modules.system.service import health
    from sqlalchemy.ext.asyncio import AsyncSession

    async with AsyncSession(admin_engine) as session:
        assert (await health(session))["status"] == "error"


async def test_unknown_receipt_and_revision_versions_are_rejected(client):
    _, _, _, inventory = await setup(client)
    async with admin_engine.begin() as connection:
        await connection.execute(text("UPDATE lgd_revisions SET document_version=2"))
    assert (await client.get("/api/v1/history/" + inventory["id"])).status_code == 503
    async with admin_engine.begin() as connection:
        key = await connection.scalar(text("SELECT key FROM lgd_requests LIMIT 1"))
        await connection.execute(text("UPDATE lgd_requests SET document_version=2"))
    payload = {k: v for k, v in inventory["payload"].items() if k not in {"snapshots", "labels"}}
    response = await client.post(
        "/api/v1/operations",
        json={"data": payload, "preview_token": "existing"},
        headers={"Idempotency-Key": key},
    )
    assert response.status_code == 503


async def test_identifiers_are_normalized_before_sql(client):
    refs, product, vid, _ = await setup(client)
    data = sale(refs, vid.upper())
    data["channel_id"] = data["channel_id"].upper()
    operation = await confirm(client, data)
    assert operation["payload"]["items"][0]["variant_id"] == vid
    corrected = await confirm(client, correction(operation), operation["id"].upper())
    assert corrected["id"] == operation["id"]
    assert corrected["version"] == 2
    supplier = refs["supplier"]
    response = await client.put(
        "/api/v1/auxiliaries/" + supplier["id"].upper(),
        json={
            "kind": "supplier",
            "name": supplier["name"],
            "version": supplier["version"],
            "reason": "Conferido",
        },
    )
    assert response.status_code == 200
    response = await client.put(
        "/api/v1/products/" + product["id"].upper(),
        json={
            "name": product["name"],
            "print_name": product["print_name"],
            "version": product["version"],
            "reason": "Conferido",
        },
    )
    assert response.status_code == 200
    variant = product["variants"][0]
    response = await client.put(
        f"/api/v1/products/{product['id'].upper()}/variants/{vid.upper()}",
        json={
            "size": variant["size"],
            "color": variant["color"],
            "version": variant["version"],
            "reason": "Conferido",
        },
    )
    assert response.status_code == 200
    data["items"][0]["variant_id"] = "invalid"
    assert (await client.post("/api/v1/operations/preview", json=data)).status_code == 422
    assert (await client.get("/api/v1/operations/invalid")).status_code == 404


async def test_preview_loads_catalog_in_batches(client):
    from app.shared.models.entities import Variant
    from sqlalchemy import event, insert

    _, product, _, inventory = await setup(client)
    ids = [str(uuid4()) for _ in range(50)]
    async with admin_engine.begin() as connection:
        await connection.execute(
            insert(Variant),
            [
                {
                    "id": uid,
                    "product_id": product["id"],
                    "code": "BATCH-" + str(index),
                    "size": str(index),
                    "color": "Azul",
                    "normalized_size": str(index),
                    "normalized_color": "azul",
                }
                for index, uid in enumerate(ids)
            ],
        )
    data = correction(inventory)
    data["items"].extend({"variant_id": uid, "quantity": 1, "unit_cost": "1.00"} for uid in ids)
    selects = []

    def observe(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            selects.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", observe)
    try:
        response = await client.post(f"/api/v1/operations/{inventory['id']}/preview", json=data)
        assert response.status_code == 200
        assert len(selects) <= 20
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", observe)
