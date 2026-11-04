"""Reprodução determinística dos acontecimentos, sem acesso ao banco.

Unidades sem custo são consumidas primeiro para que a incerteza nunca suma
numa nova compra. O restante utiliza custo médio ponderado em centavos.
"""

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

ZERO = Decimal("0.00")


class RuleError(ValueError):
    """Violação de consistência que deve cancelar toda a transação."""


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def amount(value) -> str | None:
    return None if value is None else str(money(value))


def replay(operations: list[dict], variant_ids: list[str]) -> tuple[dict, dict]:
    """Calcula custos/saldos e recusa impossibilidades inclusive no passado."""
    states = {vid: {"stock": 0, "unknown": 0, "known_value": ZERO, "average_cost": None, "last_known_cost": None,
                    "first_entry": None, "last_sale": None, "sold": 0} for vid in variant_ids}
    results = {}
    inventory = False
    for op in sorted(operations, key=lambda row: (row["effective_at"], row["sequence"])):
        payload, kind = op["payload"], op["kind"]
        if op["cancelled"]:
            lines = [{**item, **payload.get("snapshots", {}).get(item["variant_id"], {})} for item in payload["items"]]
            total = sum((money(i["unit_price"] if kind == "sale" else i.get("unit_cost") or 0) * i["quantity"] for i in lines), ZERO)
            results[op["id"]] = {"cancelled": True, "effects": {}, "items": lines, "total": amount(total)}
            continue
        if kind == "inventory":
            if inventory:
                raise RuleError("O inventário inicial só pode ser confirmado uma vez")
            inventory = True
        elif not inventory:
            raise RuleError("Confirme o inventário inicial antes desta operação")
        total, reference_total, cost_total = ZERO, ZERO, ZERO
        reference_complete, missing_units = True, 0
        lines, effects = [], defaultdict(int)
        for item in payload["items"]:
            vid, qty = item["variant_id"], item["quantity"]
            if vid not in states:
                raise RuleError("Variante inexistente")
            state = states[vid]
            line = {**item, **payload.get("snapshots", {}).get(vid, {})}
            incoming = kind in ("purchase", "inventory") or (kind == "adjustment" and payload["direction"] == "in")
            if incoming:
                cost = item.get("unit_cost")
                if kind == "adjustment":
                    cost = state["average_cost"] if state["average_cost"] is not None else cost
                    if cost is None:
                        raise RuleError("Entrada por ajuste sem custo atual exige custo informado")
                if cost is None:
                    state["unknown"] += qty
                else:
                    state["known_value"] += money(cost) * qty
                    total += money(cost) * qty
                state["stock"] += qty
                if state["first_entry"] is None:
                    state["first_entry"] = op["effective_at"]
                line["unit_cost"] = amount(cost)
                effects[vid] += qty
            else:
                if state["stock"] < qty:
                    raise RuleError(f"Estoque insuficiente na sequência histórica: {line.get('product_name', vid)} / {line.get('size', '')}")
                unknown = min(state["unknown"], qty)
                known_qty = state["stock"] - state["unknown"]
                known_cost = money(state["known_value"] / known_qty) if known_qty else ZERO
                if known_qty:
                    state["last_known_cost"] = amount(known_cost)
                consumed = money(known_cost * (qty - unknown))
                state["known_value"] = max(ZERO, state["known_value"] - consumed)
                state["unknown"] -= unknown
                state["stock"] -= qty
                effects[vid] -= qty
                if state["stock"] == 0:
                    state["known_value"] = ZERO
                if kind == "sale":
                    state["sold"] += qty
                    state["last_sale"] = op["effective_at"]
                    total += money(item["unit_price"]) * qty
                    cost_total += consumed
                    missing_units += unknown
                    line.update(unit_cost=None if unknown else amount(known_cost),
                                known_cost=amount(consumed), unknown_cost_units=unknown)
                    reference = line.get("reference_price")
                    if reference is None:
                        reference_complete = False
                    else:
                        reference_total += money(reference) * qty
            known_qty = state["stock"] - state["unknown"]
            if known_qty:
                state["last_known_cost"] = amount(state["known_value"] / known_qty)
            state["average_cost"] = (amount(state["known_value"] / known_qty)
                                     if state["stock"] and not state["unknown"] else state["last_known_cost"] if not state["stock"] else None)
            lines.append(line)
        result = {"items": lines, "total": amount(total), "effects": dict(effects)}
        if kind == "sale":
            paid = sum((money(p["amount"]) for p in payload.get("payments", [])), ZERO)
            if paid > total:
                raise RuleError("Pagamentos excedem o total da venda")
            result.update(received=amount(paid), balance=amount(total-paid),
                          financial_status="concluída" if paid == total else "pendente",
                          historical_cost=None if missing_units else amount(cost_total),
                          known_cost=amount(cost_total), unknown_cost_units=missing_units,
                          gross_result=None if missing_units else amount(total-cost_total),
                          gross_margin=None if missing_units else amount((total-cost_total)/total*100),
                          reference_total=amount(reference_total) if reference_complete else None,
                          commercial_difference=amount(reference_total-total) if reference_complete else None)
        results[op["id"]] = result
    for state in states.values():
        state["known_value"] = amount(state["known_value"])
        state.pop("last_known_cost")
    return states, results
