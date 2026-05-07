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

    # Lista produtos (smoke)
    r = httpx.get(API + "/products", headers=headers, timeout=10.0)
    assert r.status_code == 200

    # Cria fornecedor
    sup_payload = {"name": "Fornecedor Teste"}
    r = httpx.post(API + "/suppliers", json=sup_payload, headers=headers, timeout=10.0)
    assert r.status_code == 200
    supplier = r.json()
    assert "id" in supplier
    supplier_id = supplier["id"]

    # Cria produto com variante
    prod_payload = {
        "sku": "TESTSKU001",
        "name": "Produto Teste",
        "cost_price": 10.0,
        "sale_price": 20.0,
        "supplier_id": supplier_id,
        "variants": [{"size": "UNICO", "stock_quantity": 5}],
    }

    r = httpx.post(API + "/products", json=prod_payload, headers=headers, timeout=10.0)
    assert r.status_code == 200
    product = r.json()
    pid = product["id"]

    # Busca produto criado
    r = httpx.get(API + f"/products/{pid}", headers=headers, timeout=10.0)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == pid
    assert len(data.get("variants", [])) >= 1

    # Atualiza produto
    r = httpx.put(API + f"/products/{pid}", json={"name": "Produto Atualizado"}, headers=headers, timeout=10.0)
    assert r.status_code == 200
    assert r.json()["name"] == "Produto Atualizado"

    # Desativa produto
    r = httpx.delete(API + f"/products/{pid}", headers=headers, timeout=10.0)
    assert r.status_code == 200
    assert r.json().get("ok") is True

    # Verifica que está inativo
    r = httpx.get(API + f"/products/{pid}", headers=headers, timeout=10.0)
    assert r.status_code == 200
    assert r.json().get("is_active") is False
