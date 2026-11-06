import hmac
import json
from datetime import datetime

from app.modules.catalog.public import locked_variants
from app.shared.application.audit import audit
from app.shared.application.errors import ApplicationError
from app.shared.models.common import now, uid
from app.shared.models.entities import Movement, Operation, RequestReceipt
from app.shared.persistence import base as repo

from .candidate import prepare
from .domain.ledger import RuleError, replay
from .repository import operations
from .repository import receipt as find_receipt
from .signing import digest, sign


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


async def _execute(db, data, entity_id=None, preview_token=None, request_key=None):
    control = await repo.lock(db)
    fingerprint = digest({"data": data.model_dump(mode="json"), "id": entity_id})
    if request_key:
        receipt = await find_receipt(db, request_key)
        if receipt:
            if receipt.fingerprint != fingerprint:
                raise ApplicationError(409, "Chave de requisição já utilizada com outros dados")
            return receipt.response
    candidate, old = await prepare(db, data, entity_id, control)
    token = sign(candidate, control.revision)
    if preview_token and not hmac.compare_digest(token, preview_token):
        raise ApplicationError(409, "A base mudou desde a prévia. Revise o impacto novamente")
    if preview_token and not request_key:
        raise ApplicationError(422, "Confirmação exige Idempotency-Key")
    all_rows = await operations(db)
    timestamp = now().isoformat()
    computed = materialize(candidate, timestamp, (entity_id or uid()) if preview_token else None)
    variants = await locked_variants(db)
    history = [row for row in all_rows if row["id"] != entity_id] + [computed]
    try:
        states, results = replay(history, [v.id for v in variants])
    except RuleError as exc:
        raise ApplicationError(422, str(exc)) from exc
    impacts = [
        {"id": row["id"], "kind": row["kind"], "before": row["result"], "after": results[row["id"]]}
        for row in all_rows
        if row["id"] != entity_id and row["result"] != results[row["id"]]
    ]
    response = {
        "operation": {**computed, "result": results[computed["id"]]},
        "affected": impacts,
        "stock": states,
        "preview_token": token,
    }
    if not preview_token:
        return response
    row = (
        await repo.require(db, Operation, entity_id) if entity_id else Operation(id=computed["id"])
    )
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
            db.add(
                Movement(
                    operation_id=row.id,
                    variant_id=vid,
                    version=row.version,
                    delta=delta,
                    reason=reason,
                )
            )
    audit(
        db,
        "operation",
        row.id,
        "cancel" if data.cancelled else "edit" if old else "create",
        reason,
        old,
        repo.serialize(row),
    )
    for impact in impacts:
        dependent = await repo.require(db, Operation, impact["id"])
        before = repo.serialize(dependent)
        dependent.result = impact["after"]
        dependent.version += 1
        dependent.updated_at = now()
        audit(
            db,
            "operation",
            dependent.id,
            "recalculate",
            reason + " — origem " + row.id,
            before,
            repo.serialize(dependent),
        )
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


async def preview(db, data, entity_id=None):
    return await _execute(db, data, entity_id)


async def confirm(db, data, preview_token, request_key, entity_id=None):
    if not preview_token:
        raise ApplicationError(422, "Confirmação exige prévia")
    return await _execute(db, data, entity_id, preview_token, request_key)
