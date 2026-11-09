from collections import defaultdict
from datetime import datetime

from app.modules.operations.public import amount


def build_stock(variants, states, valid, aux, observed_at):
    stock = []
    issues = []
    origins_by_variant = defaultdict(list)
    for op in valid:
        for vid in op["result"].get("effects", {}):
            origins_by_variant[vid].append(op["id"])
    for vid, variant in variants.items():
        p, state = variant["product"], states[vid]

        def age(timestamp):
            return (
                max(0, (observed_at - datetime.fromisoformat(timestamp)).days)
                if timestamp
                else None
            )

        origins = origins_by_variant[vid]
        stock.append(
            {
                "variant_id": vid,
                "product_id": p["id"],
                "name": p["name"],
                "print_name": p["print_name"],
                "brand": p["brand"],
                "model": p["model"],
                "category": aux.get(p["category_id"]),
                "size": variant["size"],
                "color": variant["color"],
                "code": variant["code"],
                **state,
                "days_since_first_entry": age(state["first_entry"]),
                "days_since_last_sale": age(state["last_sale"]),
                "stock_value": amount(state["known_value"]) if not state["unknown"] else None,
                "known_stock_value": amount(state["known_value"]),
                "situation": "esgotado"
                if not state["stock"] and state["sold"]
                else "vendeu parcialmente"
                if state["sold"]
                else "ainda não vendeu",
                "operation_ids": origins,
            }
        )
        for field, label in (
            ("brand", "Marca ausente"),
            ("model", "Modelo ausente"),
            ("category_id", "Categoria ausente"),
        ):
            if not p[field]:
                issues.append({"product_id": p["id"], "variant_id": vid, "message": label})
        if variant["reference_price"] is None:
            issues.append(
                {
                    "product_id": p["id"],
                    "variant_id": vid,
                    "message": "Preço de referência desconhecido",
                }
            )
        if state["unknown"]:
            issues.append(
                {
                    "product_id": p["id"],
                    "variant_id": vid,
                    "message": f"{state['unknown']} unidades sem custo conhecido",
                }
            )
        if not p["photos"]:
            issues.append(
                {
                    "product_id": p["id"],
                    "variant_id": vid,
                    "message": "Foto opcional ainda não adicionada",
                    "optional": True,
                }
            )
    return stock, issues
