import uuid

import httpx

BASE_URL = "http://localhost:8000"
API = BASE_URL + "/api/v1"


def test_health():
    r = httpx.get(BASE_URL + "/")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def get_token():
    r = httpx.post(API + "/auth/login", json={"password": "lgdmantos123"}, timeout=10.0)
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    return data["token"]


def test_login_and_product_crud_flow():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = httpx.get(API + "/products", headers=headers, timeout=10.0)
    assert r.status_code == 200

    r = httpx.post(API + "/suppliers", json={"name": "Fornecedor Teste"}, headers=headers, timeout=10.0)
    assert r.status_code == 200
    supplier_id = r.json()["id"]

    prod_payload = {
        "sku": f"TEST-{uuid.uuid4().hex[:6].upper()}",
        "name": "Produto Teste",
        "cost_price": 10.0,
        "sale_price": 20.0,
        "supplier_id": supplier_id,
        "variants": [{"size": "M", "color": "Preto", "stock_quantity": 5}],
    }

    r = httpx.post(API + "/products", json=prod_payload, headers=headers, timeout=10.0)
    assert r.status_code == 200
    product = r.json()
    pid = product["id"]

    r = httpx.get(API + f"/products/{pid}", headers=headers, timeout=10.0)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == pid
    assert len(data.get("variants", [])) >= 1

    r = httpx.put(API + f"/products/{pid}", json={"name": "Produto Atualizado"}, headers=headers, timeout=10.0)
    assert r.status_code == 200
    assert r.json()["name"] == "Produto Atualizado"

    r = httpx.delete(API + f"/products/{pid}", headers=headers, timeout=10.0)
    assert r.status_code == 200
    assert r.json().get("ok") is True

    r = httpx.get(API + f"/products/{pid}", headers=headers, timeout=10.0)
    assert r.status_code == 200
    assert r.json().get("is_active") is False


def test_invalid_category_id_returns_400():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = httpx.post(API + "/products", json={
        "name": "Produto Cat Invalida",
        "category_id": str(uuid.uuid4()),
        "cost_price": 10.0,
        "sale_price": 20.0,
    }, headers=headers, timeout=10.0)

    assert r.status_code == 400, f"Esperado 400, recebeu {r.status_code}: {r.text}"
    assert "categoria" in r.json().get("detail", "").lower()


def test_invalid_supplier_id_returns_400():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = httpx.post(API + "/products", json={
        "name": "Produto Fornecedor Invalido",
        "supplier_id": str(uuid.uuid4()),
        "cost_price": 10.0,
        "sale_price": 20.0,
    }, headers=headers, timeout=10.0)

    assert r.status_code == 400, f"Esperado 400, recebeu {r.status_code}: {r.text}"
    assert "fornecedor" in r.json().get("detail", "").lower()


def test_duplicate_sku_returns_400():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    sku = f"DUP-{uuid.uuid4().hex[:6].upper()}"

    r = httpx.post(API + "/products", json={
        "sku": sku,
        "name": "Produto Original",
        "cost_price": 5.0,
        "sale_price": 10.0,
    }, headers=headers, timeout=10.0)
    assert r.status_code == 200, f"Primeiro produto falhou: {r.text}"
    pid = r.json()["id"]

    r = httpx.post(API + "/products", json={
        "sku": sku,
        "name": "Produto Duplicado",
        "cost_price": 5.0,
        "sale_price": 10.0,
    }, headers=headers, timeout=10.0)
    assert r.status_code == 400, f"Esperado 400 para SKU duplicado, recebeu {r.status_code}: {r.text}"
    assert "sku" in r.json().get("detail", "").lower()

    httpx.delete(API + f"/products/{pid}", headers=headers, timeout=10.0)


def test_auto_sku_on_creation():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = httpx.post(API + "/products", json={
        "name": "Produto SKU Automatico",
        "cost_price": 8.0,
        "sale_price": 16.0,
    }, headers=headers, timeout=10.0)

    assert r.status_code == 200, f"Esperado 200, recebeu {r.status_code}: {r.text}"
    product = r.json()
    assert product.get("sku"), "SKU deve ser gerado automaticamente"
    assert product["sku"].startswith("LGD-"), f"Formato de SKU invalido: {product['sku']}"

    httpx.delete(API + f"/products/{product['id']}", headers=headers, timeout=10.0)


def test_negative_stock_rejected():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = httpx.post(API + "/products", json={
        "name": "Produto Estoque Negativo",
        "cost_price": 5.0,
        "sale_price": 10.0,
        "variants": [{"size": "M", "color": "Preto", "stock_quantity": -1}],
    }, headers=headers, timeout=10.0)

    assert r.status_code in (400, 422), f"Esperado 400 ou 422, recebeu {r.status_code}: {r.text}"
