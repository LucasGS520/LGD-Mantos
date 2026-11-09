"""Inventário do contrato HTTP preservado da baseline anterior à extração."""

import main


def test_openapi_preserves_paths_methods_and_protected_operations():
    spec = main.app.openapi()
    expected = [
        ["get", "/api/v1/state"],
        ["get", "/api/v1/auxiliaries"],
        ["post", "/api/v1/auxiliaries"],
        ["put", "/api/v1/auxiliaries/{entity_id}"],
        ["get", "/api/v1/products"],
        ["get", "/api/v1/products/{entity_id}"],
        ["post", "/api/v1/products"],
        ["put", "/api/v1/products/{entity_id}"],
        ["post", "/api/v1/products/{product_id}/variants"],
        ["put", "/api/v1/products/{product_id}/variants/{entity_id}"],
        ["get", "/api/v1/operations"],
        ["get", "/api/v1/operations/{entity_id}"],
        ["post", "/api/v1/operations/preview"],
        ["post", "/api/v1/operations"],
        ["post", "/api/v1/operations/{entity_id}/preview"],
        ["put", "/api/v1/operations/{entity_id}"],
        ["get", "/api/v1/history/{entity_id}"],
        ["get", "/api/v1/movements"],
        ["get", "/api/v1/analytics"],
        ["post", "/api/v1/products/{product_id}/photos"],
        ["get", "/api/v1/photos/{entity_id}/content"],
        ["put", "/api/v1/photos/{entity_id}/content"],
        ["put", "/api/v1/photos/{entity_id}"],
        ["delete", "/api/v1/photos/{entity_id}"],
        ["post", "/api/v1/auth/login"],
        ["get", "/api/v1/health"],
    ]
    actual = [
        (method, path)
        for path, operation in spec["paths"].items()
        for method in operation
        if method in {"get", "post", "put", "delete", "patch"}
    ]
    assert set(actual) == {tuple(pair) for pair in expected}
    for method, path in expected:
        if path not in {"/api/v1/auth/login", "/api/v1/health"}:
            assert spec["paths"][path][method]["security"] == [{"HTTPBearer": []}]
    for method, path in [("post", "/api/v1/operations"), ("put", "/api/v1/operations/{entity_id}")]:
        headers = spec["paths"][path][method]["parameters"]
        assert any(
            header["name"] == "idempotency-key" and header["required"] and header["in"] == "header"
            for header in headers
        )
    assert spec["components"]["schemas"]["OperationIn"]["additionalProperties"] is False
    assert (
        spec["components"]["schemas"]["ItemIn"]["properties"]["quantity"]["exclusiveMinimum"] == 0
    )
