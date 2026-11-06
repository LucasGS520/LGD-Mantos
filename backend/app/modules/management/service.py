"""Consultas de gestão baseadas em evidências, sem metas ou períodos impostos."""

from datetime import date

from app.modules.operations.domain.ledger import replay
from app.shared.application.errors import ApplicationError
from app.shared.models.common import now
from app.shared.models.entities import Auxiliary, Control

from . import repository as repo
from .calculations.groups import build_groups
from .calculations.overview import build_summary
from .calculations.period import select_records
from .calculations.purchases import purchase_totals_for
from .calculations.stock import build_stock


async def report(db, start: date | None = None, end: date | None = None):
    if start and end and start > end:
        raise ApplicationError(422, "Data inicial deve ser anterior à data final")
    # Uma leitura gerencial não pode misturar catálogo anterior com operações
    # posteriores de uma gravação concorrente. A trava compartilhada só lê.
    await repo.read_lock(db)
    products, operations = await repo.products(db), await repo.operations(db)
    variants = {v["id"]: {**v, "product": p} for p in products for v in p["variants"]}
    states, _ = replay(operations, list(variants))
    valid = [op for op in operations if not op["cancelled"]]
    sales, purchases, payments, pending, revenue, known_cost, unknown = select_records(
        valid, start, end
    )
    aux = {a.id: a for a in await repo.rows(db, Auxiliary)}
    stock, issues = build_stock(variants, states, valid, aux, now())
    groups = build_groups(stock, sales)
    control = await db.get(Control, 1)
    purchase_totals = purchase_totals_for(purchases)
    return {
        "started_at": control.started_at.isoformat() if control and control.started_at else None,
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
            "observed_since": control.started_at.isoformat()
            if control and control.started_at
            else None,
            "sale_count": len(sales),
            "purchase_count": len(purchases),
            "message": "Sem vendas registradas: dados insuficientes para avaliar saída."
            if not sales
            else "Evidências descritivas do histórico registrado; quantidades recomendadas ainda não são calculadas.",
            "supplier_limitation": "Vendas não são atribuídas a lotes de fornecedores. Consulte compras efetivas e desempenho dos produtos relacionados.",
        },
    }
