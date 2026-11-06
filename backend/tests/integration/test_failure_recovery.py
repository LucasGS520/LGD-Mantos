"""Falhas transacionais devem preservar a base e compensar arquivos."""

import io
from uuid import uuid4

import pytest
from app.modules.photos.infrastructure.local_storage import storage
from conftest import sale, setup
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession


def image_bytes():
    content = io.BytesIO()
    Image.new("RGB", (4, 4)).save(content, "PNG")
    return content.getvalue()


async def test_photo_is_compensated_when_commit_fails(client, monkeypatch):
    _, product, _, _ = await setup(client)

    async def fail_commit(self):
        raise RuntimeError("commit indisponível")

    with monkeypatch.context() as patch:
        patch.setattr(AsyncSession, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="commit indisponível"):
            await client.post(
                f"/api/v1/products/{product['id']}/photos",
                files={"file": ("a.png", image_bytes(), "image/png")},
            )
    assert list(storage.root.glob("*")) == []
    assert (await client.get("/api/v1/products")).json()[0]["photos"] == []


async def test_photo_removal_failure_does_not_restore_public_access(client, monkeypatch):
    _, product, _, _ = await setup(client)
    photo = (
        await client.post(
            f"/api/v1/products/{product['id']}/photos",
            files={"file": ("a.png", image_bytes(), "image/png")},
        )
    ).json()

    def fail_remove(filename):
        raise OSError("disco indisponível")

    with monkeypatch.context() as patch:
        patch.setattr(storage, "remove", fail_remove)
        response = await client.delete(f"/api/v1/photos/{photo['id']}")
    assert response.json() == {"removed": True}
    assert (await client.get(f"/api/v1/photos/{photo['id']}/content")).status_code == 404


async def test_operation_commit_failure_rolls_back_every_effect(client, monkeypatch):
    refs, _, vid, _ = await setup(client)
    data = sale(refs, vid)
    preview = (await client.post("/api/v1/operations/preview", json=data)).json()
    paths = [
        "/operations",
        "/movements",
        f"/history/{preview['operation']['id']}",
        "/products",
        "/state",
    ]
    before = [(await client.get("/api/v1" + path)).json() for path in paths]

    async def fail_commit(self):
        raise RuntimeError("falha na confirmação")

    key = str(uuid4())
    with monkeypatch.context() as patch:
        patch.setattr(AsyncSession, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="falha na confirmação"):
            await client.post(
                "/api/v1/operations",
                json={"data": data, "preview_token": preview["preview_token"]},
                headers={"Idempotency-Key": key},
            )
    after = [(await client.get("/api/v1" + path)).json() for path in paths]
    assert after == before
    response = await client.post(
        "/api/v1/operations",
        json={"data": data, "preview_token": preview["preview_token"]},
        headers={"Idempotency-Key": key},
    )
    assert response.status_code == 200
    assert (await client.get("/api/v1/analytics")).json()["summary"]["stock_units"] == 9


async def test_preview_does_not_write_an_operation(client):
    refs, _, vid, _ = await setup(client)
    before = (await client.get("/api/v1/operations")).json()
    assert (
        await client.post("/api/v1/operations/preview", json=sale(refs, vid))
    ).status_code == 200
    assert (await client.get("/api/v1/operations")).json() == before


@pytest.mark.parametrize(
    "kind", ["supplier", "category", "purchase_channel", "sale_channel", "payment_method"]
)
async def test_auxiliary_capability_preserves_kind_and_uniqueness(client, kind):
    record = (
        await client.post("/api/v1/auxiliaries", json={"kind": kind, "name": "Cadastro"})
    ).json()
    duplicate = await client.post("/api/v1/auxiliaries", json={"kind": kind, "name": "  CADÁSTRO "})
    assert duplicate.status_code == 409
    other_kind = "category" if kind == "supplier" else "supplier"
    assert (
        await client.post("/api/v1/auxiliaries", json={"kind": other_kind, "name": "Cadastro"})
    ).status_code == 200
    wrong = await client.put(
        f"/api/v1/auxiliaries/{record['id']}",
        json={
            "kind": other_kind,
            "name": "Outro",
            "version": record["version"],
            "reason": "Correção",
        },
    )
    assert wrong.status_code == 422
