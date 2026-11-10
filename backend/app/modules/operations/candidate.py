from datetime import datetime, time, timezone

from app.modules.auxiliaries.public import auxiliary
from app.modules.catalog.public import variant_context
from app.shared.application.errors import ApplicationError
from app.shared.application.time import LOCAL
from app.shared.application.versioning import check_version
from app.shared.models.common import now
from app.shared.models.entities import Operation
from app.shared.persistence import base as repo

from .domain.ledger import amount
from .payments import prepare_payments
from .repository import detail


async def prepare(db, data, entity_id, control):
    """Monta candidato sem escrever, preservando referências e instantes antigos."""
    old_row = await repo.require(db, Operation, entity_id) if entity_id else None
    old = await detail(db, entity_id) if old_row else None
    if old_row:
        check_version(old_row, data)
        if old_row.kind != data.kind or old_row.cancelled:
            raise ApplicationError(422, "Operação anulada ou tipo incompatível")
        if data.kind == "inventory" and data.cancelled:
            raise ApplicationError(422, "Corrija o inventário; seu ponto zero não pode ser anulado")
    elif data.version is not None or data.cancelled:
        raise ApplicationError(422, "Nova operação não aceita versão ou anulação")
    payload = data.model_dump(mode="json", exclude={"version", "cancelled"})
    payload["snapshots"] = {}
    payload["labels"] = {}
    previous = old["payload"] if old else {}
    refs = []
    if data.kind == "purchase":
        refs = [("supplier_id", "supplier"), ("channel_id", "purchase_channel")]
    elif data.kind == "sale":
        refs = [("channel_id", "sale_channel")]
    for field, kind in refs:
        ref = await auxiliary(db, getattr(data, field), kind, previous.get(field))
        payload["labels"][field] = (
            previous.get("labels", {}).get(field, ref.name)
            if previous.get(field) == ref.id
            else ref.name
        )
    seen = set()
    variants, products, categories = await variant_context(
        db, [item.variant_id for item in data.items]
    )
    for item in data.items:
        if item.variant_id in seen:
            raise ApplicationError(422, "Agrupe a quantidade de cada variante em uma única linha")
        seen.add(item.variant_id)
        variant = variants.get(item.variant_id)
        if variant is None:
            raise ApplicationError(404, "Registro não encontrado")
        product = products[variant.product_id]
        prior = previous.get("snapshots", {}).get(variant.id)
        if (not product.active or not variant.active) and prior is None:
            raise ApplicationError(422, "Produto ou variante desativado")
        category = categories.get(product.category_id)
        payload["snapshots"][variant.id] = prior or {
            "product_id": product.id,
            "product_name": product.name,
            "print_name": product.print_name,
            "brand": product.brand,
            "model": product.model,
            "category": category.name if category else None,
            "category_id": product.category_id,
            "size": variant.size,
            "color": variant.color,
            "code": variant.code,
            "reference_price": amount(variant.reference_price),
        }
    await prepare_payments(db, data.payments, previous, payload)
    timestamp = old["effective_at"] if old else "confirmation"
    if data.kind == "purchase":
        purchase_day = data.purchase_date or (
            datetime.fromisoformat(old["effective_at"]).astimezone(LOCAL).date()
            if old
            else now().astimezone(LOCAL).date()
        )
        payload["purchase_date"] = purchase_day.isoformat()
        if purchase_day > now().astimezone(LOCAL).date():
            raise ApplicationError(422, "Compra não pode ter data futura")
        timestamp = (
            datetime.combine(purchase_day, time.min, LOCAL).astimezone(timezone.utc).isoformat()
        )
        # Compras no dia do inventário não podem anteceder seu ponto zero.
        if control.started_at and purchase_day == control.started_at.astimezone(LOCAL).date():
            timestamp = control.started_at.isoformat()
    candidate = {
        "id": entity_id or "new-operation",
        "sequence": old["sequence"] if old else control.revision + 1,
        "kind": data.kind,
        "effective_at": timestamp,
        "created_at": old["created_at"] if old else "confirmation",
        "version": old["version"] + 1 if old else 1,
        "cancelled": data.cancelled,
        "payload": payload,
    }
    return candidate, old
