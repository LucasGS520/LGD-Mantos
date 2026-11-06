from collections import defaultdict

from app.modules.operations.domain.ledger import ZERO, amount, money


def build_groups(stock, sales):
    groups = []
    for attr in ("brand", "model", "category", "size", "color"):
        buckets = defaultdict(
            lambda: {
                "sold": 0,
                "stock": 0,
                "revenue": ZERO,
                "known_cost": ZERO,
                "unknown_cost_units": 0,
                "sale_ids": set(),
                "product_ids": set(),
            }
        )
        for item in stock:
            key = item.get(attr) or "Não informado"
            buckets[key]["stock"] += item["stock"]
            buckets[key]["product_ids"].add(item["product_id"])
        for sale in sales:
            for item in sale["result"]["items"]:
                key = item.get(attr) or "Não informado"
                group = buckets[key]
                group["sold"] += item["quantity"]
                group["revenue"] += money(item["unit_price"]) * item["quantity"]
                group["known_cost"] += money(item["known_cost"])
                group["unknown_cost_units"] += item["unknown_cost_units"]
                group["sale_ids"].add(sale["id"])
        for label, group in buckets.items():
            value = group["revenue"] - group["known_cost"]
            groups.append(
                {
                    **group,
                    "attribute": attr,
                    "label": label,
                    "revenue": amount(group["revenue"]),
                    "known_cost": amount(group["known_cost"]),
                    "gross_result": amount(value) if not group["unknown_cost_units"] else None,
                    "gross_margin": amount(value / group["revenue"] * 100)
                    if group["revenue"] and not group["unknown_cost_units"]
                    else None,
                    "sale_ids": sorted(group["sale_ids"]),
                    "product_ids": sorted(group["product_ids"]),
                }
            )
    return groups
