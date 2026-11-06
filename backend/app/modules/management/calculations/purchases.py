from app.modules.operations.domain.ledger import ZERO, amount, money


def purchase_totals_for(purchases):
    purchase_totals = {}
    for supplier in {op["payload"]["supplier_id"] for op in purchases} | {"all"}:
        selected = [
            op for op in purchases if supplier == "all" or op["payload"]["supplier_id"] == supplier
        ]
        purchase_totals[supplier] = {
            "units": sum(i["quantity"] for op in selected for i in op["result"]["items"]),
            "total": amount(sum((money(op["result"]["total"]) for op in selected), ZERO)),
        }
    return purchase_totals
