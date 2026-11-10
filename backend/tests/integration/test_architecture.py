"""Contratos arquiteturais: snapshots, repetição, arquivos e falhas externas."""

import asyncio
import io
from uuid import uuid4

import pytest
from app.core.database import AsyncSessionLocal, engine, get_read_db
from app.modules.photos.infrastructure.local_storage import storage
from conftest import confirm, sale, setup
from PIL import Image
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def picture(color="red"):
    result = io.BytesIO()
    Image.new("RGB", (5, 5), color).save(result, "PNG")
    return result.getvalue()


async def test_snapshot_survives_confirmation_without_blocking_writer(client):
    refs, _, vid, _ = await setup(client)
    reader = get_read_db()
    db = await anext(reader)
    try:
        before = await db.scalar(text("SELECT stock FROM lgd_variants WHERE id=:id"), {"id": vid})
        await asyncio.wait_for(confirm(client, sale(refs, vid)), timeout=3)
        after = await db.scalar(text("SELECT stock FROM lgd_variants WHERE id=:id"), {"id": vid})
        assert before == after == 10
    finally:
        await reader.aclose()
    assert (await client.get("/api/v1/analytics")).json()["summary"]["stock_units"] == 9


async def test_management_does_not_mix_catalog_with_new_operations(client, monkeypatch):
    from app.modules.management import repository

    refs, _, vid, _ = await setup(client)
    original = repository.products

    async def interleave(db):
        result = await original(db)
        await asyncio.wait_for(confirm(client, sale(refs, vid)), timeout=3)
        return result

    with monkeypatch.context() as patch:
        patch.setattr(repository, "products", interleave)
        result = (await client.get("/api/v1/analytics")).json()
    assert result["summary"]["stock_units"] == 10
    assert result["summary"]["sold_units"] == 0
    current = (await client.get("/api/v1/analytics")).json()
    assert current["summary"]["stock_units"] == 9
    assert current["revision"] == result["revision"] + 1


async def test_same_key_concurrent_confirmations_have_one_effect(client):
    refs, _, vid, _ = await setup(client, stock=1)
    data = sale(refs, vid)
    preview = (await client.post("/api/v1/operations/preview", json=data)).json()
    key = str(uuid4())

    async def send():
        return await client.post(
            "/api/v1/operations",
            json={"data": data, "preview_token": preview["preview_token"]},
            headers={"Idempotency-Key": key},
        )

    first, second = await asyncio.gather(send(), send())
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    movements = (
        await client.get(
            "/api/v1/movements", params={"operation_id": first.json()["operation"]["id"]}
        )
    ).json()
    assert len(movements) == 1
    assert movements[0]["delta"] == -1


async def test_paginated_lists_keep_totals_and_origins(client):
    refs, product, vid, _ = await setup(client)
    first = await confirm(client, sale(refs, vid))
    second = await confirm(client, sale(refs, vid))
    response = (await client.get("/api/v1/operations", params={"kind": "sale", "limit": 1})).json()
    assert [op["id"] for op in response] == [second["id"]]
    next_page = (
        await client.get(
            "/api/v1/operations",
            params={"kind": "sale", "limit": 1, "before_sequence": response[0]["sequence"]},
        )
    ).json()
    assert [op["id"] for op in next_page] == [first["id"]]
    full = (await client.get("/api/v1/analytics")).json()
    page = (await client.get("/api/v1/analytics", params={"view": "sales", "limit": 1})).json()
    assert page["summary"] == full["summary"]
    assert page["groups"] == full["groups"]
    assert len(page["sales"]) == 1
    assert page["page"]["totals"]["sales"] == 2
    assert page["page"]["has_more"]
    assert (await client.get("/api/v1/products/" + product["id"])).json() == (
        await client.get("/api/v1/products")
    ).json()[0]
    assert (await client.get("/api/v1/products/missing")).status_code == 404


async def test_readiness_fails_but_process_is_alive(client, monkeypatch):
    from app.modules.system import service

    async def unavailable(db):
        return "error"

    monkeypatch.setattr(service, "database_status", unavailable)
    response = await client.get("/api/v1/health")
    assert response.status_code == 503
    assert response.json()["status"] == response.json()["database"] == "error"
    assert (await client.get("/")).status_code == 200
    assert len(response.headers["x-request-id"]) == 32


async def test_readiness_requires_expected_migration(client):
    from conftest import admin_engine

    async with admin_engine.begin() as db:
        await db.execute(text("UPDATE alembic_version SET version_num='0005'"))
    try:
        response = await client.get("/api/v1/health")
        assert response.status_code == 503
        assert response.json()["database"] == "error"
    finally:
        async with admin_engine.begin() as db:
            await db.execute(text("UPDATE alembic_version SET version_num='0007'"))
    assert (await client.get("/api/v1/health")).status_code == 200


async def test_photo_replace_preserves_identity_metadata_and_retry(client):
    _, product, _, _ = await setup(client)
    photo = (
        await client.post(
            f"/api/v1/products/{product['id']}/photos",
            files={"file": ("a.png", picture(), "image/png")},
        )
    ).json()
    old = storage.path(photo["filename"])
    path = f"/api/v1/photos/{photo['id']}/content"
    replaced = await client.put(path, files={"file": ("b.png", picture("blue"), "image/png")})
    assert replaced.status_code == 200
    result = replaced.json()
    assert result["id"] == photo["id"] and result["primary"] == photo["primary"]
    assert not old.exists()
    revision = (await client.get("/api/v1/state")).json()["revision"]
    assert (
        await client.put(path, files={"file": ("b.png", picture("blue"), "image/png")})
    ).json() == result
    assert (await client.get("/api/v1/state")).json()["revision"] == revision
    assert (await client.get(path)).content == picture("blue")


async def test_replacement_commit_failure_preserves_previous_file(client, monkeypatch):
    _, product, _, _ = await setup(client)
    photo = (
        await client.post(
            f"/api/v1/products/{product['id']}/photos",
            files={"file": ("a.png", picture(), "image/png")},
        )
    ).json()

    async def unavailable(self):
        raise RuntimeError("commit indisponível")

    with monkeypatch.context() as patch:
        patch.setattr(AsyncSession, "commit", unavailable)
        with pytest.raises(RuntimeError):
            await client.put(
                f"/api/v1/photos/{photo['id']}/content",
                files={"file": ("b.png", picture("blue"), "image/png")},
            )
    assert (await client.get(f"/api/v1/photos/{photo['id']}/content")).content == picture()
    assert len(list(storage.root.iterdir())) == 1


async def test_interrupted_write_leaves_only_reportable_orphan(client, monkeypatch):
    from reconcile_photos import inventory

    class Interrupted(BaseException):
        pass

    _, product, _, _ = await setup(client)
    original = storage.write

    def interrupted(filename, content):
        original(filename, content)
        raise Interrupted()

    with monkeypatch.context() as patch:
        patch.setattr(storage, "write", interrupted)
        with pytest.raises(Interrupted):
            await client.post(
                f"/api/v1/products/{product['id']}/photos",
                files={"file": ("a.png", picture(), "image/png")},
            )
    report = await inventory()
    assert report["referenced"] == 0
    assert report["missing"] == []
    assert len(report["orphans"]) == 1


async def test_uncertain_photo_commit_keeps_committed_file(client, monkeypatch):
    _, product, _, _ = await setup(client)
    original = AsyncSession.commit

    async def commit_then_disconnect(self):
        await original(self)
        raise RuntimeError("resposta perdida após commit")

    with monkeypatch.context() as patch:
        patch.setattr(AsyncSession, "commit", commit_then_disconnect)
        try:
            await client.post(
                f"/api/v1/products/{product['id']}/photos",
                files={"file": ("a.png", picture(), "image/png")},
            )
        except RuntimeError:
            pass
    photos = (await client.get("/api/v1/products/" + product["id"])).json()["photos"]
    assert len(photos) == 1
    assert storage.path(photos[0]["filename"]).exists()


async def test_reconciliation_reports_without_deleting(client):
    from reconcile_photos import inventory

    _, product, _, _ = await setup(client)
    photo = (
        await client.post(
            f"/api/v1/products/{product['id']}/photos",
            files={"file": ("a.png", picture(), "image/png")},
        )
    ).json()
    storage.path(photo["filename"]).unlink()
    storage.path("orphan.png").write_bytes(picture())
    report = await inventory()
    assert report["missing"] == [photo["filename"]]
    assert report["orphans"] == ["orphan.png"]
    assert report["read_only"]
    assert storage.path("orphan.png").exists()


async def test_lock_timeout_is_recoverable_without_partial_effect(client):
    refs, _, vid, _ = await setup(client)
    async with engine.connect() as holder:
        await holder.execute(text("SELECT pg_advisory_xact_lock(741206031)"))
        response = await client.post("/api/v1/operations/preview", json=sale(refs, vid))
        assert response.status_code == 503
        await holder.rollback()
    assert (await client.get("/api/v1/analytics")).json()["summary"]["stock_units"] == 10
    async with AsyncSessionLocal() as db:
        assert await db.scalar(text("SELECT count(*) FROM lgd_requests")) == 1
