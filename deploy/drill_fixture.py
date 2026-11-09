"""Cria somente dados sintéticos na API local fixa do ensaio (porta 8002)."""

import io
import json
from uuid import uuid4

import httpx
from PIL import Image


def main():
    with httpx.Client(base_url="http://127.0.0.1:8002/api/v1", timeout=30) as client:

        def request(method, path, **kwargs):
            response = client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()

        token = request("POST", "/auth/login", json={"password": "isolated-drill-only"})["token"]
        client.headers["Authorization"] = "Bearer " + token
        state = request("GET", "/state")
        if state["revision"]:
            raise RuntimeError("O ensaio exige uma base vazia; nada foi removido")
        refs = {
            kind: request("POST", "/auxiliaries", json={"kind": kind, "name": "Sintético " + kind})[
                "id"
            ]
            for kind in ("supplier", "purchase_channel", "sale_channel", "payment_method")
        }
        product = request(
            "POST",
            "/products",
            json={
                "name": "Peça do ensaio",
                "print_name": "Teste",
                "variants": [{"size": "M", "color": "Preto", "reference_price": "30.00"}],
            },
        )
        vid = product["variants"][0]["id"]

        def confirm(data, identifier=None):
            path = "/operations" + ("/" + identifier if identifier else "")
            preview = request("POST", path + "/preview", json=data)
            return request(
                "PUT" if identifier else "POST",
                path,
                json={"data": data, "preview_token": preview["preview_token"]},
                headers={"Idempotency-Key": str(uuid4())},
            )["operation"]

        inventory = confirm({"kind": "inventory", "items": [{"variant_id": vid, "quantity": 3}]})
        confirm(
            {
                "kind": "purchase",
                "supplier_id": refs["supplier"],
                "channel_id": refs["purchase_channel"],
                "items": [{"variant_id": vid, "quantity": 2, "unit_cost": "10.00"}],
            }
        )
        confirm(
            {
                "kind": "sale",
                "channel_id": refs["sale_channel"],
                "items": [{"variant_id": vid, "quantity": 2, "unit_price": "20.00"}],
                "payments": [{"amount": "5.00", "method_id": refs["payment_method"]}],
            }
        )
        confirm(
            {
                "kind": "inventory",
                "version": inventory["version"],
                "reason": "Custo conferido",
                "items": [{"variant_id": vid, "quantity": 3, "unit_cost": "12.00"}],
            },
            inventory["id"],
        )
        content = io.BytesIO()
        Image.new("RGB", (4, 4), "blue").save(content, "PNG")
        photo = request(
            "POST",
            f"/products/{product['id']}/photos",
            files={"file": ("test.png", content.getvalue(), "image/png")},
        )
        print(
            json.dumps(
                {
                    "summary": request("GET", "/analytics")["summary"],
                    "photo": photo["id"],
                    "synthetic": True,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
