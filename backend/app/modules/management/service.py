"""Consultas de gestão baseadas em evidências, sem metas ou períodos impostos."""

import asyncio
from datetime import date

from app.modules.operations.public import replay
from app.shared.application.errors import ApplicationError
from app.shared.application.telemetry import measured
from app.shared.models.common import now

from . import repository as repo
from .calculations.groups import build_groups
from .calculations.overview import build_summary
from .calculations.period import select_records
from .calculations.purchases import purchase_totals_for
from .calculations.stock import build_stock


async def report(
    db,
    start: date | None = None,
    end: date | None = None,
    view=None,
    offset=0,
    limit=50,
    supplier=None,
    sort="stock",
):
    if start and end and start > end:
        raise ApplicationError(422, "Data inicial deve ser anterior à data final")
    with measured("management_snapshot"):
        snapshot = await repo.snapshot(db)
    # Todos os valores já estão materializados; cálculo puro não retém conexão/trava.
    await db.rollback()
    with measured("management_calculate", records=len(snapshot[1])):
        result = await asyncio.to_thread(calculate, snapshot, start, end, now())
    return present(result, view, offset, limit, supplier, sort) if view else result


def calculate(snapshot, start, end, observed_at):
    products, operations, aux, control = snapshot
    variants = {v["id"]: {**v, "product": p} for p in products for v in p["variants"]}
    states, _ = replay(operations, list(variants))
    valid = [op for op in operations if not op["cancelled"]]
    sales, purchases, payments, pending, revenue, known_cost, unknown = select_records(
        valid, start, end
    )
    stock, issues = build_stock(variants, states, valid, aux, observed_at)
    groups = build_groups(stock, sales)
    purchase_totals = purchase_totals_for(purchases)
    return {
        **control,
        "start": str(start) if start else None,
        "end": str(end) if end else None,
        "summary": build_summary(stock, sales, payments, pending, revenue, known_cost, unknown),
        "stock": stock,
        "sales": sales,
        "purchases": purchases,
        "payments": payments,
        "pending_sales": pending,
        "groups": groups,
        "issues": issues,
        "purchase_totals": purchase_totals,
        "evidence": {
            "observed_since": control["started_at"],
            "sale_count": len(sales),
            "purchase_count": len(purchases),
            "message": "Sem vendas registradas: dados insuficientes para avaliar saída."
            if not sales
            else "Evidências descritivas do histórico registrado; quantidades recomendadas ainda não são calculadas.",
            "supplier_limitation": "Vendas não são atribuídas a lotes de fornecedores. Consulte compras efetivas e desempenho dos produtos relacionados.",
        },
    }


def present(result, view, offset, limit, supplier, sort):
    """Pagina detalhes após calcular totais integrais, sem cortar entrada do ledger."""
    if supplier:
        result["purchases"] = [
            op for op in result["purchases"] if op["payload"].get("supplier_id") == supplier
        ]
    result["supplier_variants"] = (
        sorted({item["variant_id"] for op in result["purchases"] for item in op["result"]["items"]})
        if supplier
        else []
    )
    collections = {
        "overview": set(),
        "stock": {"stock"},
        "sales": {"sales"},
        "receipts": {"payments", "pending_sales"},
        "purchases": {"purchases"},
        "buying": set(),
    }[view]
    totals = {}
    for field in ("sales", "purchases", "payments", "pending_sales", "stock"):
        values = result[field]
        if field in collections:
            totals[field] = len(values)
            if field == "stock":
                values = sorted(
                    values,
                    key=lambda row: (
                        -(float(row[sort]) if row.get(sort) is not None else -1),
                        row["variant_id"],
                    ),
                )
            else:
                values = list(reversed(values))
            result[field] = values[offset : offset + limit]
        elif field != "stock" or view not in {"overview", "purchases"}:
            result[field] = []
    if view not in {"sales", "buying"}:
        result["groups"] = []
    if view != "overview":
        result["issues"] = []
    if view in {"overview", "purchases"}:
        for row in result["stock"]:
            row["operation_ids"] = []
    result["page"] = {
        "offset": offset,
        "limit": limit,
        "totals": totals,
        "has_more": any(offset + limit < total for total in totals.values()),
    }
    return result
