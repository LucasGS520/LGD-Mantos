"""Recorte, margem incompleta e evidências sem banco ou relógio global."""

from datetime import date
from decimal import Decimal

from app.modules.management.calculations.groups import build_groups
from app.modules.management.calculations.overview import build_summary
from app.modules.management.calculations.period import in_range, select_records
from app.modules.management.calculations.purchases import purchase_totals_for


def test_interval_includes_local_days_not_utc_days():
    day = date(2026, 1, 2)
    assert not in_range("2026-01-02T02:59:59+00:00", day, day)
    assert in_range("2026-01-02T03:00:00+00:00", day, day)
    assert in_range("2026-01-03T02:59:59+00:00", day, day)
    assert not in_range("2026-01-03T03:00:00+00:00", day, day)


def test_payments_follow_own_time_and_pending_is_current():
    sale = {
        "id": "s",
        "kind": "sale",
        "effective_at": "2026-01-01T12:00:00+00:00",
        "payload": {"payments": [{"amount": "5.00", "created_at": "2026-01-03T12:00:00+00:00"}]},
        "result": {
            "balance": "15.00",
            "total": "20.00",
            "known_cost": "10.00",
            "unknown_cost_units": 0,
        },
    }
    sales, purchases, payments, pending, revenue, known, unknown = select_records(
        [sale], date(2026, 1, 3), date(2026, 1, 3)
    )
    assert sales == purchases == []
    assert payments == [
        {"amount": "5.00", "created_at": "2026-01-03T12:00:00+00:00", "sale_id": "s"}
    ]
    assert pending == [sale]
    assert revenue == known == Decimal("0.00")
    assert unknown == 0


def test_group_preserves_origins_and_unknown_cost():
    stock = [{"brand": "LGD", "stock": 2, "product_id": "p"}]
    sale = {
        "id": "s",
        "result": {
            "items": [
                {
                    "brand": "LGD",
                    "quantity": 1,
                    "unit_price": "30.00",
                    "known_cost": "0.00",
                    "unknown_cost_units": 1,
                }
            ]
        },
    }
    group = next(row for row in build_groups(stock, [sale]) if row["attribute"] == "brand")
    assert group["revenue"] == "30.00"
    assert group["gross_result"] is None
    assert group["sale_ids"] == ["s"]
    assert group["product_ids"] == ["p"]


def test_summary_does_not_present_partial_cost_as_margin():
    summary = build_summary([], [], [], [], Decimal("30.00"), Decimal("0.00"), 1)
    assert summary["gross_result"] is None
    assert summary["gross_margin"] is None
    assert summary["historical_cost"] is None
    assert summary["known_cost"] == "0.00"


def test_purchase_totals_are_by_supplier_and_all():
    purchases = [
        {"payload": {"supplier_id": "a"}, "result": {"items": [{"quantity": 2}], "total": "40.00"}},
        {"payload": {"supplier_id": "b"}, "result": {"items": [{"quantity": 1}], "total": "10.00"}},
    ]
    assert purchase_totals_for(purchases) == {
        "a": {"units": 2, "total": "40.00"},
        "b": {"units": 1, "total": "10.00"},
        "all": {"units": 3, "total": "50.00"},
    }
