"""Persistência relacional e adaptação explícita para o contrato do ledger/API."""

from collections import defaultdict
from datetime import date, datetime

from app.shared.models.entities import Operation, OperationItem, RequestReceipt, SalePayment
from app.shared.persistence.base import document_version, require, value
from sqlalchemy import delete, select


def operation_values(computed):
    """Uma única representação canônica; payload não é coluna persistida."""
    payload, kind = computed["payload"], computed["kind"]
    return {
        **{key: computed[key] for key in ("id", "sequence", "kind", "version", "cancelled")},
        "effective_at": datetime.fromisoformat(computed["effective_at"]),
        "created_at": datetime.fromisoformat(computed["created_at"]),
        "purchase_date": date.fromisoformat(payload["purchase_date"])
        if payload.get("purchase_date")
        else None,
        "supplier_id": payload.get("supplier_id"),
        "purchase_channel_id": payload.get("channel_id") if kind == "purchase" else None,
        "sale_channel_id": payload.get("channel_id") if kind == "sale" else None,
        "direction": payload.get("direction"),
        "reason": payload.get("reason"),
        "notes": payload.get("notes"),
        "labels": payload.get("labels", {}),
    }


def item_values(operation):
    return [
        {
            "operation_id": operation["id"],
            "operation_kind": operation["kind"],
            "position": position,
            "variant_id": item["variant_id"],
            "quantity": item["quantity"],
            "unit_cost": item.get("unit_cost"),
            "unit_price": item.get("unit_price"),
            "snapshot": operation["payload"]["snapshots"][item["variant_id"]],
        }
        for position, item in enumerate(operation["payload"]["items"])
    ]


def payment_values(operation):
    return [
        {
            "id": payment["id"],
            "operation_id": operation["id"],
            "operation_kind": "sale",
            "position": position,
            "method_id": payment["method_id"],
            "amount": payment["amount"],
            "method_name": payment["method_name"],
            "created_at": datetime.fromisoformat(payment["created_at"]),
        }
        for position, payment in enumerate(operation["payload"].get("payments", []))
    ]


async def documents(db, parents, complete=False):
    if not parents:
        return []
    items, payments = defaultdict(list), defaultdict(list)
    ids = [row["id"] for row in parents]
    batches = (
        [None] if complete else [ids[start : start + 500] for start in range(0, len(ids), 500)]
    )
    for batch in batches:
        for model, target in ((OperationItem, items), (SalePayment, payments)):
            query = select(model.__table__).order_by(model.operation_id, model.position)
            if batch is not None:
                query = query.where(model.operation_id.in_(batch))
            for row in (await db.execute(query)).mappings():
                target[row["operation_id"]].append(dict(row))
    result = []
    for row in parents:
        document_version(row["document_version"])
        lines = items[row["id"]]
        payload = {
            "kind": row["kind"],
            "purchase_date": value(row["purchase_date"]),
            "supplier_id": row["supplier_id"],
            "channel_id": row["purchase_channel_id"] or row["sale_channel_id"],
            "direction": row["direction"],
            "reason": row["reason"],
            "notes": row["notes"],
            "labels": row["labels"],
            "items": [
                {
                    "variant_id": item["variant_id"],
                    "quantity": item["quantity"],
                    "unit_cost": value(item["unit_cost"]),
                    "unit_price": value(item["unit_price"]),
                }
                for item in lines
            ],
            "snapshots": {item["variant_id"]: item["snapshot"] for item in lines},
            "payments": [
                {
                    key: value(payment[key])
                    for key in ("id", "amount", "method_id", "method_name", "created_at")
                }
                for payment in payments[row["id"]]
            ],
        }
        result.append(
            {
                **{
                    key: value(row[key])
                    for key in (
                        "id",
                        "sequence",
                        "kind",
                        "effective_at",
                        "created_at",
                        "updated_at",
                        "version",
                        "cancelled",
                    )
                },
                "payload": payload,
                "result": row["result"],
            }
        )
    return result


async def operations(db):
    parents = list(
        (
            await db.execute(
                select(Operation.__table__).order_by(Operation.effective_at, Operation.sequence)
            )
        ).mappings()
    )
    return await documents(db, parents, complete=True)


async def detail(db, entity_id):
    row = await require(db, Operation, entity_id)
    return (
        await documents(
            db, [{column.name: getattr(row, column.name) for column in row.__table__.columns}]
        )
    )[0]


async def receipt(db, key):
    row = await db.get(RequestReceipt, key)
    if row:
        document_version(row.document_version)
    return row


async def affected_operations(db, ids):
    result = {}
    for start in range(0, len(ids), 500):
        for row in (
            await db.scalars(select(Operation).where(Operation.id.in_(ids[start : start + 500])))
        ).all():
            result[row.id] = row
    return result


async def page(db, kind, limit, before_sequence):
    query = select(Operation.__table__).order_by(Operation.sequence.desc()).limit(limit)
    if kind is not None:
        query = query.where(Operation.kind == kind)
    if before_sequence is not None:
        query = query.where(Operation.sequence < before_sequence)
    return await documents(db, list((await db.execute(query)).mappings()))


async def save_children(db, computed):
    """Substitui linhas e concilia pagamentos por ID na mesma transação do pai."""
    await db.execute(delete(OperationItem).where(OperationItem.operation_id == computed["id"]))
    db.add_all([OperationItem(**item) for item in item_values(computed)])
    current = {
        payment.id: payment
        for payment in (
            await db.scalars(select(SalePayment).where(SalePayment.operation_id == computed["id"]))
        ).all()
    }
    incoming = payment_values(computed)
    keep = {payment["id"] for payment in incoming}
    for payment_id, row in current.items():
        if payment_id not in keep:
            await db.delete(row)
    for payment in incoming:
        row = current.get(payment["id"])
        if row is None:
            row = SalePayment(**payment)
            db.add(row)
        else:
            for key, field_value in payment.items():
                setattr(row, key, field_value)
