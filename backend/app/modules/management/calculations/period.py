"""Recorte por ocorrência e recebimento, com pendência sempre atual."""

from datetime import datetime, time, timedelta

from app.modules.operations.public import ZERO, money
from app.shared.application.time import LOCAL


def in_range(timestamp, start, end):
    instant = datetime.fromisoformat(timestamp)
    return (not start or instant >= datetime.combine(start, time.min, LOCAL)) and (
        not end or instant < datetime.combine(end + timedelta(days=1), time.min, LOCAL)
    )


def select_records(valid, start, end):
    sales = [
        op for op in valid if op["kind"] == "sale" and in_range(op["effective_at"], start, end)
    ]
    purchases = [
        op for op in valid if op["kind"] == "purchase" and in_range(op["effective_at"], start, end)
    ]
    all_sales = [op for op in valid if op["kind"] == "sale"]
    payments = [
        {**p, "sale_id": op["id"]}
        for op in all_sales
        for p in op["payload"].get("payments", [])
        if in_range(p["created_at"], start, end)
    ]
    pending = [op for op in all_sales if money(op["result"]["balance"]) > 0]
    revenue = sum((money(op["result"]["total"]) for op in sales), ZERO)
    known_cost = sum((money(op["result"]["known_cost"]) for op in sales), ZERO)
    unknown = sum(op["result"]["unknown_cost_units"] for op in sales)
    return sales, purchases, payments, pending, revenue, known_cost, unknown
