"""Integração exclusivamente no banco de teste, validado antes de qualquer DDL."""

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import pytest_asyncio

TEST_DATABASE = "lgd_mantos_alignment_test"
test_url = os.environ.get("TEST_DATABASE_URL")
if not test_url or urlsplit(test_url).path != "/" + TEST_DATABASE:
    raise RuntimeError("Defina TEST_DATABASE_URL apontando exclusivamente para lgd_mantos_alignment_test")
os.environ["DATABASE_URL"] = test_url
os.environ["APP_PASSWORD"] = "senha-testes"
os.environ["APP_SECRET"] = "segredo-exclusivo-de-testes"

from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from app.core.database import engine
from app.domain.models import Control


@pytest.fixture(scope="session", autouse=True)
def migrate_test_database():
    """A própria cadeia Alembic cria o esquema, em vez de create_all."""
    subprocess.run([sys.executable, "init_db.py"], cwd=Path(__file__).resolve().parents[1], check=True, env=os.environ.copy())


@pytest_asyncio.fixture(autouse=True)
async def clean_database(migrate_test_database, tmp_path):
    from app.domain import routes
    routes.PHOTO_ROOT = tmp_path / "photos"
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE lgd_requests, lgd_revisions, lgd_movements, lgd_operations, lgd_photos, lgd_variants, lgd_products, lgd_auxiliaries, lgd_control"))
    yield
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE lgd_requests, lgd_revisions, lgd_movements, lgd_operations, lgd_photos, lgd_variants, lgd_products, lgd_auxiliaries, lgd_control"))


@pytest_asyncio.fixture
async def client():
    import main
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", json={"password": "senha-testes"})
        client.headers["Authorization"] = "Bearer " + response.json()["token"]
        yield client


async def aux(client, kind, name=None):
    response = await client.post("/api/v1/auxiliaries", json={"kind": kind, "name": name or kind})
    assert response.status_code == 200, response.text
    return response.json()


async def setup(client, stock=10, cost="10.00"):
    refs = {kind: await aux(client, kind) for kind in ("supplier", "purchase_channel", "sale_channel", "payment_method")}
    response = await client.post("/api/v1/products", json={"name": "Camiseta", "print_name": "Estampa A", "brand": "LGD", "model": "Reta", "variants": [{"size": "M", "color": "Preto", "reference_cost": cost, "reference_price": "30.00"}]})
    assert response.status_code == 200, response.text
    product = response.json()
    vid = product["variants"][0]["id"]
    inventory = await confirm(client, {"kind": "inventory", "items": [{"variant_id": vid, "quantity": stock, "unit_cost": cost}]})
    return refs, product, vid, inventory


async def confirm(client, data, entity_id=None, key=None):
    from uuid import uuid4
    path = "/api/v1/operations" + ("/" + entity_id if entity_id else "")
    preview = await client.post(path + "/preview", json=data)
    assert preview.status_code == 200, preview.text
    response = await client.request("PUT" if entity_id else "POST", path, json={"data": data, "preview_token": preview.json()["preview_token"]}, headers={"Idempotency-Key": key or str(uuid4())})
    assert response.status_code == 200, response.text
    return response.json()["operation"]


def sale(refs, vid, quantity=1, payments=None):
    return {"kind": "sale", "channel_id": refs["sale_channel"]["id"], "items": [{"variant_id": vid, "quantity": quantity, "unit_price": "25.00"}], "payments": payments or []}


def correction(op, reason="Correção conferida"):
    payload = op["payload"]
    data = {key: value for key, value in payload.items() if key not in ("snapshots", "labels")}
    data["payments"] = [{key: p[key] for key in ("id", "amount", "method_id")} for p in payload["payments"]]
    return {**data, "version": op["version"], "reason": reason}
