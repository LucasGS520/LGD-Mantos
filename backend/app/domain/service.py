"""Gravações transacionais, prévias de correção e histórico do dono."""

import hashlib
import hmac
import json
import unicodedata
from datetime import datetime, time, timezone
from difflib import SequenceMatcher
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.domain import repository as repo
from app.domain.ledger import RuleError, amount, replay
from app.domain.models import Auxiliary, Movement, Operation, Product, RequestReceipt, Revision, Variant
from app.shared.models.common import now, uid

LOCAL = ZoneInfo("America/Sao_Paulo")


def normalize(value):
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c)).casefold().split())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def audit(db, entity_type, entity_id, action, reason, before, after):
    db.add(Revision(entity_type=entity_type, entity_id=entity_id, action=action,
                    reason=reason, before=before, after=after))


def check_version(row, data):
    if data.version != row.version:
        raise HTTPException(409, "Registro alterado. Recarregue antes de corrigir")
    if not data.reason:
        raise HTTPException(422, "Informe o motivo da correção")


async def auxiliary(db, entity_id, kind, previous_id=None):
    row = await repo.require(db, Auxiliary, entity_id)
    if row.kind != kind or (not row.active and row.id != previous_id):
        raise HTTPException(422, "Cadastro auxiliar incompatível ou desativado")
    return row


async def save_auxiliary(db, data, entity_id=None):
    control = await repo.lock(db)
    row = await repo.require(db, Auxiliary, entity_id) if entity_id else None
    if row:
        check_version(row, data)
        if data.kind != row.kind:
            raise HTTPException(422, "O tipo do cadastro não pode ser alterado")
    duplicate = await db.scalar(select(Auxiliary).where(Auxiliary.kind == data.kind, Auxiliary.normalized_name == normalize(data.name)))
    if duplicate and duplicate.id != entity_id:
        raise HTTPException(409, "Nome já cadastrado após normalização")
    before = repo.serialize(row)
    if row is None:
        row = Auxiliary(id=uid(), kind=data.kind, version=1)
        db.add(row)
    else:
        row.version += 1
    row.name, row.normalized_name, row.notes, row.active = data.name, normalize(data.name), data.notes, data.active
    await db.flush()
    audit(db, "auxiliary", row.id, "edit" if before else "create", data.reason or "Cadastro inicial", before, repo.serialize(row))
    control.revision += 1
    return repo.serialize(row)


async def save_product(db, data, entity_id=None):
    control = await repo.lock(db)
    row = await repo.require(db, Product, entity_id) if entity_id else None
    if row:
        check_version(row, data)
        if data.variants:
            raise HTTPException(422, "Edite cada variante no seu próprio cadastro")
    if data.category_id:
        await auxiliary(db, data.category_id, "category", row.category_id if row else None)
    similar = [p for p in await repo.rows(db, Product) if p.id != entity_id and
               SequenceMatcher(None, normalize(p.name + " " + p.print_name), normalize(data.name + " " + data.print_name)).ratio() >= .85]
    if similar and not data.accept_similar:
        raise HTTPException(409, {"message": "Existem produtos semelhantes. Confirme se são peças distintas.",
                                  "similar_products": [{"id": p.id, "name": p.name, "print_name": p.print_name} for p in similar]})
    before = repo.serialize(row)
    if row is None:
        row = Product(id=uid(), version=1)
        db.add(row)
    else:
        row.version += 1
    for field in ("name", "print_name", "brand", "model", "category_id", "notes", "active"):
        setattr(row, field, getattr(data, field))
    await db.flush()
    for variant in data.variants:
        await _variant(db, row, variant)
    audit(db, "product", row.id, "edit" if before else "create", data.reason or "Cadastro inicial", before, repo.serialize(row))
    control.revision += 1
    return next(p for p in await repo.products(db) if p["id"] == row.id)


async def _variant(db, product, data, entity_id=None):
    row = await repo.require(db, Variant, entity_id) if entity_id else None
    if row:
        if row.product_id != product.id:
            raise HTTPException(422, "Variante não pertence ao produto")
        check_version(row, data)
    key = (normalize(data.size), normalize(data.color))
    duplicate = await db.scalar(select(Variant).where(Variant.product_id == product.id, Variant.normalized_size == key[0], Variant.normalized_color == key[1]))
    if duplicate and duplicate.id != entity_id:
        raise HTTPException(409, "Combinação de tamanho e cor já cadastrada")
    before = repo.serialize(row)
    if row is None:
        row = Variant(id=uid(), product_id=product.id, code="LGD-" + uid().replace("-", "").upper(), stock=0, version=1)
        db.add(row)
    else:
        row.version += 1
    for field in ("size", "color", "reference_cost", "reference_price", "active"):
        setattr(row, field, getattr(data, field))
    row.normalized_size, row.normalized_color = key
    await db.flush()
    audit(db, "variant", row.id, "edit" if before else "create", data.reason or "Cadastro inicial", before, repo.serialize(row))
    return repo.serialize(row)


async def save_variant(db, product_id, data, entity_id=None):
    control = await repo.lock(db)
    result = await _variant(db, await repo.require(db, Product, product_id), data, entity_id)
    control.revision += 1
    return result


async def prepare(db, data, entity_id, control):
    """Monta candidato sem escrever, preservando referências e instantes antigos."""
    old_row = await repo.require(db, Operation, entity_id) if entity_id else None
    old = repo.serialize(old_row)
    if old_row:
        check_version(old_row, data)
        if old_row.kind != data.kind or old_row.cancelled:
            raise HTTPException(422, "Operação anulada ou tipo incompatível")
        if data.kind == "inventory" and data.cancelled:
            raise HTTPException(422, "Corrija o inventário; seu ponto zero não pode ser anulado")
    elif data.version is not None or data.cancelled:
        raise HTTPException(422, "Nova operação não aceita versão ou anulação")
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
        payload["labels"][field] = previous.get("labels", {}).get(field, ref.name) if previous.get(field) == ref.id else ref.name
    seen = set()
    for item in data.items:
        if item.variant_id in seen:
            raise HTTPException(422, "Agrupe a quantidade de cada variante em uma única linha")
        seen.add(item.variant_id)
        variant = await repo.require(db, Variant, item.variant_id)
        product = await repo.require(db, Product, variant.product_id)
        prior = previous.get("snapshots", {}).get(variant.id)
        if (not product.active or not variant.active) and prior is None:
            raise HTTPException(422, "Produto ou variante desativado")
        category = await db.get(Auxiliary, product.category_id) if product.category_id else None
        payload["snapshots"][variant.id] = prior or {
            "product_id": product.id, "product_name": product.name, "print_name": product.print_name,
            "brand": product.brand, "model": product.model, "category": category.name if category else None,
            "category_id": product.category_id, "size": variant.size, "color": variant.color,
            "code": variant.code, "reference_price": amount(variant.reference_price)}
    old_payments = {p["id"]: p for p in previous.get("payments", [])}
    seen_payments = set()
    for index, payment in enumerate(data.payments):
        prior = old_payments.get(payment.id)
        if payment.id and prior is None:
            raise HTTPException(422, "Pagamento desconhecido nesta venda")
        if payment.id and payment.id in seen_payments:
            raise HTTPException(422, "Pagamento repetido")
        seen_payments.add(payment.id)
        method = await auxiliary(db, payment.method_id, "payment_method", prior.get("method_id") if prior else None)
        payload["payments"][index].update(id=payment.id or f"new-{index}",
                                         created_at=prior["created_at"] if prior else "confirmation",
                                         method_name=prior["method_name"] if prior and prior["method_id"] == method.id else method.name)
    timestamp = old["effective_at"] if old else "confirmation"
    if data.kind == "purchase":
        purchase_day = data.purchase_date or (datetime.fromisoformat(old["effective_at"]).astimezone(LOCAL).date() if old else now().astimezone(LOCAL).date())
        payload["purchase_date"] = purchase_day.isoformat()
        if purchase_day > now().astimezone(LOCAL).date():
            raise HTTPException(422, "Compra não pode ter data futura")
        timestamp = datetime.combine(purchase_day, time.min, LOCAL).astimezone(timezone.utc).isoformat()
        # Compras no dia do inventário não podem anteceder seu ponto zero.
        if control.started_at and purchase_day == control.started_at.astimezone(LOCAL).date():
            timestamp = control.started_at.isoformat()
    candidate = {"id": entity_id or "new-operation", "sequence": old["sequence"] if old else control.revision + 1,
                 "kind": data.kind, "effective_at": timestamp, "created_at": old["created_at"] if old else "confirmation",
                 "version": old["version"] + 1 if old else 1, "cancelled": data.cancelled, "payload": payload}
    return candidate, old


def sign(candidate, revision):
    return hmac.new(settings.APP_SECRET.encode(), (str(revision) + digest(candidate)).encode(), hashlib.sha256).hexdigest()


def materialize(candidate, timestamp, operation_id=None):
    """A prévia usa um instante fixo do request; a confirmação ganha IDs reais."""
    value = json.loads(json.dumps(candidate))
    if operation_id:
        value["id"] = operation_id
    for field in ("effective_at", "created_at"):
        if value[field] == "confirmation":
            value[field] = timestamp
    for payment in value["payload"].get("payments", []):
        if payment["created_at"] == "confirmation":
            payment["created_at"] = timestamp
        if operation_id and payment["id"].startswith("new-"):
            payment["id"] = uid()
    return value


async def operation(db, data, entity_id=None, preview_token=None, request_key=None):
    control = await repo.lock(db)
    fingerprint = digest({"data": data.model_dump(mode="json"), "id": entity_id})
    if request_key:
        receipt = await db.get(RequestReceipt, request_key)
        if receipt:
            if receipt.fingerprint != fingerprint:
                raise HTTPException(409, "Chave de requisição já utilizada com outros dados")
            return receipt.response
    candidate, old = await prepare(db, data, entity_id, control)
    token = sign(candidate, control.revision)
    if preview_token and not hmac.compare_digest(token, preview_token):
        raise HTTPException(409, "A base mudou desde a prévia. Revise o impacto novamente")
    if preview_token and not request_key:
        raise HTTPException(422, "Confirmação exige Idempotency-Key")
    all_rows = await repo.operations(db)
    timestamp = now().isoformat()
    computed = materialize(candidate, timestamp, (entity_id or uid()) if preview_token else None)
    variants = list((await db.scalars(select(Variant).order_by(Variant.id).with_for_update())).all())
    history = [row for row in all_rows if row["id"] != entity_id] + [computed]
    try:
        states, results = replay(history, [v.id for v in variants])
    except RuleError as exc:
        raise HTTPException(422, str(exc)) from exc
    impacts = [{"id": row["id"], "kind": row["kind"], "before": row["result"], "after": results[row["id"]]}
               for row in all_rows if row["id"] != entity_id and row["result"] != results[row["id"]]]
    response = {"operation": {**computed, "result": results[computed["id"]]}, "affected": impacts,
                "stock": states, "preview_token": token}
    if not preview_token:
        return response
    row = await repo.require(db, Operation, entity_id) if entity_id else Operation(id=computed["id"])
    if not entity_id:
        db.add(row)
    for field in ("sequence", "kind", "version", "cancelled", "payload"):
        setattr(row, field, computed[field])
    row.effective_at = datetime.fromisoformat(computed["effective_at"])
    row.created_at = datetime.fromisoformat(computed["created_at"])
    row.updated_at = now()
    row.result = results[row.id]
    await db.flush()
    before_effects = old["result"].get("effects", {}) if old else {}
    effects = row.result.get("effects", {})
    reason = data.reason or "Registro inicial"
    for vid in sorted(set(before_effects) | set(effects)):
        delta = effects.get(vid, 0) - before_effects.get(vid, 0)
        if delta:
            db.add(Movement(operation_id=row.id, variant_id=vid, version=row.version, delta=delta, reason=reason))
    audit(db, "operation", row.id, "cancel" if data.cancelled else "edit" if old else "create", reason, old, repo.serialize(row))
    for impact in impacts:
        dependent = await repo.require(db, Operation, impact["id"])
        before = repo.serialize(dependent)
        dependent.result = impact["after"]
        dependent.version += 1
        dependent.updated_at = now()
        audit(db, "operation", dependent.id, "recalculate", reason + " — origem " + row.id, before, repo.serialize(dependent))
    for variant in variants:
        variant.stock = states[variant.id]["stock"]
        variant.average_cost = states[variant.id]["average_cost"]
    if data.kind == "inventory" and control.started_at is None:
        control.started_at = row.effective_at
    control.revision += 1
    response["operation"] = repo.serialize(row)
    db.add(RequestReceipt(key=request_key, fingerprint=fingerprint, response=response))
    await db.flush()
    return response
