"""Consultas de gestão baseadas em evidências, sem metas ou períodos impostos."""

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException

from app.domain import repository as repo
from app.domain.ledger import ZERO, amount, money, replay
from app.domain.models import Auxiliary, Control
from app.domain.service import LOCAL
from app.shared.models.common import now


def in_range(timestamp, start, end):
    instant = datetime.fromisoformat(timestamp)
    return (not start or instant >= datetime.combine(start, time.min, LOCAL)) and (
        not end or instant < datetime.combine(end + timedelta(days=1), time.min, LOCAL))


async def report(db, start: date | None = None, end: date | None = None):
    if start and end and start > end:
        raise HTTPException(422, "Data inicial deve ser anterior à data final")
    # Uma leitura gerencial não pode misturar catálogo anterior com operações
    # posteriores de uma gravação concorrente. A trava compartilhada só lê.
    from sqlalchemy import text
    await db.execute(text("SELECT pg_advisory_xact_lock_shared(741206031)"))
    products, operations = await repo.products(db), await repo.operations(db)
    variants = {v["id"]: {**v, "product": p} for p in products for v in p["variants"]}
    states, _ = replay(operations, list(variants))
    valid = [op for op in operations if not op["cancelled"]]
    sales = [op for op in valid if op["kind"] == "sale" and in_range(op["effective_at"], start, end)]
    purchases = [op for op in valid if op["kind"] == "purchase" and in_range(op["effective_at"], start, end)]
    all_sales = [op for op in valid if op["kind"] == "sale"]
    payments = [{**p, "sale_id": op["id"]} for op in all_sales for p in op["payload"].get("payments", []) if in_range(p["created_at"], start, end)]
    pending = [op for op in all_sales if money(op["result"]["balance"]) > 0]
    revenue = sum((money(op["result"]["total"]) for op in sales), ZERO)
    known_cost = sum((money(op["result"]["known_cost"]) for op in sales), ZERO)
    unknown = sum(op["result"]["unknown_cost_units"] for op in sales)
    stock = []
    issues = []
    aux = {a.id: a for a in await repo.rows(db, Auxiliary)}
    for vid, variant in variants.items():
        p, state = variant["product"], states[vid]
        def age(timestamp):
            return max(0, (now() - datetime.fromisoformat(timestamp)).days) if timestamp else None
        origins = [op["id"] for op in valid if vid in op["result"].get("effects", {})]
        stock.append({"variant_id": vid, "product_id": p["id"], "name": p["name"], "print_name": p["print_name"],
                      "brand": p["brand"], "model": p["model"], "category": aux[p["category_id"]].name if p["category_id"] in aux else None,
                      "size": variant["size"], "color": variant["color"], "code": variant["code"],
                      **state, "days_since_first_entry": age(state["first_entry"]), "days_since_last_sale": age(state["last_sale"]),
                      "stock_value": amount(state["known_value"]) if not state["unknown"] else None,
                      "known_stock_value": amount(state["known_value"]),
                      "situation": "esgotado" if not state["stock"] and state["sold"] else "vendeu parcialmente" if state["sold"] else "ainda não vendeu",
                      "operation_ids": origins})
        for field, label in (("brand", "Marca ausente"), ("model", "Modelo ausente"), ("category_id", "Categoria ausente")):
            if not p[field]:
                issues.append({"product_id": p["id"], "variant_id": vid, "message": label})
        if variant["reference_price"] is None:
            issues.append({"product_id": p["id"], "variant_id": vid, "message": "Preço de referência desconhecido"})
        if state["unknown"]:
            issues.append({"product_id": p["id"], "variant_id": vid, "message": f"{state['unknown']} unidades sem custo conhecido"})
        if not p["photos"]:
            issues.append({"product_id": p["id"], "variant_id": vid, "message": "Foto opcional ainda não adicionada", "optional": True})
    groups = []
    for attr in ("brand", "model", "category", "size", "color"):
        buckets = defaultdict(lambda: {"sold": 0, "stock": 0, "revenue": ZERO, "known_cost": ZERO,
                                       "unknown_cost_units": 0, "sale_ids": set(), "product_ids": set()})
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
            groups.append({**group, "attribute": attr, "label": label, "revenue": amount(group["revenue"]),
                           "known_cost": amount(group["known_cost"]), "gross_result": amount(value) if not group["unknown_cost_units"] else None,
                           "gross_margin": amount(value / group["revenue"] * 100) if group["revenue"] and not group["unknown_cost_units"] else None,
                           "sale_ids": sorted(group["sale_ids"]), "product_ids": sorted(group["product_ids"])})
    control = await db.get(Control, 1)
    purchase_totals = {}
    for supplier in {op["payload"]["supplier_id"] for op in purchases} | {"all"}:
        selected = [op for op in purchases if supplier == "all" or op["payload"]["supplier_id"] == supplier]
        purchase_totals[supplier] = {"units": sum(i["quantity"] for op in selected for i in op["result"]["items"]),
                                     "total": amount(sum((money(op["result"]["total"]) for op in selected), ZERO))}
    return {"started_at": control.started_at.isoformat() if control and control.started_at else None,
            "start": str(start) if start else None, "end": str(end) if end else None,
            "summary": {"stock_units": sum(s["stock"] for s in stock), "sold_units": sum(i["quantity"] for op in sales for i in op["result"]["items"]),
                        "sold": amount(revenue), "received": amount(sum((money(p["amount"]) for p in payments), ZERO)),
                        "pending": amount(sum((money(op["result"]["balance"]) for op in pending), ZERO)),
                        "known_cost": amount(known_cost), "unknown_cost_units": unknown,
                        "historical_cost": None if unknown else amount(known_cost),
                        "gross_result": None if unknown else amount(revenue-known_cost),
                        "gross_margin": amount((revenue-known_cost)/revenue*100) if revenue and not unknown else None,
                        "stock_value": amount(sum((money(s["known_stock_value"]) for s in stock), ZERO)),
                        "unknown_stock_units": sum(s["unknown"] for s in stock)},
            "stock": stock, "sales": sales, "purchases": purchases, "payments": payments, "pending_sales": pending,
            "groups": groups, "issues": issues, "purchase_totals": purchase_totals,
            "evidence": {"observed_since": control.started_at.isoformat() if control and control.started_at else None,
                         "sale_count": len(sales), "purchase_count": len(purchases),
                         "message": "Sem vendas registradas: dados insuficientes para avaliar saída." if not sales else "Evidências descritivas do histórico registrado; quantidades recomendadas ainda não são calculadas.",
                         "supplier_limitation": "Vendas não são atribuídas a lotes de fornecedores. Consulte compras efetivas e desempenho dos produtos relacionados."}}
