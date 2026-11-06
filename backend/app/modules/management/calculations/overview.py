"""Indicadores derivados dos registros já selecionados."""

from app.modules.operations.domain.ledger import ZERO, amount, money


def build_summary(stock, sales, payments, pending, revenue, known_cost, unknown):
    return {
        "stock_units": sum(s["stock"] for s in stock),
        "sold_units": sum(i["quantity"] for op in sales for i in op["result"]["items"]),
        "sold": amount(revenue),
        "received": amount(sum((money(p["amount"]) for p in payments), ZERO)),
        "pending": amount(sum((money(op["result"]["balance"]) for op in pending), ZERO)),
        "known_cost": amount(known_cost),
        "unknown_cost_units": unknown,
        "historical_cost": None if unknown else amount(known_cost),
        "gross_result": None if unknown else amount(revenue - known_cost),
        "gross_margin": amount((revenue - known_cost) / revenue * 100)
        if revenue and not unknown
        else None,
        "stock_value": amount(sum((money(s["known_stock_value"]) for s in stock), ZERO)),
        "unknown_stock_units": sum(s["unknown"] for s in stock),
    }
