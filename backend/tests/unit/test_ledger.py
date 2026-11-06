"""Regras puras verificadas sem banco e sem configuração HTTP."""

import pytest
from app.modules.operations.domain.ledger import RuleError, replay


def event(kind, items, sequence=1, **extra):
    return {
        "id": str(sequence),
        "kind": kind,
        "effective_at": f"2026-01-0{sequence}T12:00:00+00:00",
        "sequence": sequence,
        "cancelled": False,
        "payload": {"items": items, "payments": [], **extra},
    }


def item(quantity, **extra):
    return {"variant_id": "v", "quantity": quantity, **extra}


def test_empty_inventory_establishes_zero():
    state, result = replay([event("inventory", [])], ["v"])
    assert state["v"]["stock"] == 0
    assert result["1"]["effects"] == {}


def test_unknown_cost_is_consumed_before_known_units():
    events = [
        event("inventory", [item(2)]),
        event("purchase", [item(2, unit_cost="20.00")], 2),
        event("sale", [item(2, unit_price="30.00")], 3),
    ]
    state, result = replay(events, ["v"])
    assert result["3"]["unknown_cost_units"] == 2
    assert result["3"]["gross_result"] is None
    assert state["v"]["stock"] == 2
    assert state["v"]["average_cost"] == "20.00"


def test_purchase_recalculates_weighted_average():
    state, _ = replay(
        [
            event("inventory", [item(2, unit_cost="10.00")]),
            event("purchase", [item(2, unit_cost="20.00")], 2),
        ],
        ["v"],
    )
    assert state["v"]["average_cost"] == "15.00"


def test_stock_cannot_be_negative_even_for_old_operation():
    with pytest.raises(RuleError, match="Estoque insuficiente"):
        replay(
            [event("inventory", [item(1)]), event("sale", [item(2, unit_price="30.00")], 2)], ["v"]
        )


def test_cancelled_sale_has_no_stock_effect():
    sale = event("sale", [item(1, unit_price="30.00")], 2)
    sale["cancelled"] = True
    state, result = replay([event("inventory", [item(2, unit_cost="10.00")]), sale], ["v"])
    assert state["v"]["stock"] == 2
    assert result["2"]["effects"] == {}


def test_history_is_sorted_by_effective_time_and_inventory_is_unique():
    inventory = event("inventory", [item(2)])
    sale = event("sale", [item(1, unit_price="30.00")], 2)
    assert replay([sale, inventory], ["v"])[0]["v"]["stock"] == 1
    with pytest.raises(RuleError, match="uma vez"):
        replay([inventory, event("inventory", [], 2)], ["v"])
