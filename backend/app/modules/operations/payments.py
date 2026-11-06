"""Recebimentos preservam IDs, nomes e instantes."""

from app.modules.auxiliaries.public import auxiliary
from app.shared.application.errors import ApplicationError


async def prepare_payments(db, payments, previous, payload):
    old_payments = {p["id"]: p for p in previous.get("payments", [])}
    seen_payments = set()
    for index, payment in enumerate(payments):
        prior = old_payments.get(payment.id)
        if payment.id and prior is None:
            raise ApplicationError(422, "Pagamento desconhecido nesta venda")
        if payment.id and payment.id in seen_payments:
            raise ApplicationError(422, "Pagamento repetido")
        seen_payments.add(payment.id)
        method = await auxiliary(
            db, payment.method_id, "payment_method", prior.get("method_id") if prior else None
        )
        payload["payments"][index].update(
            id=payment.id or f"new-{index}",
            created_at=prior["created_at"] if prior else "confirmation",
            method_name=prior["method_name"]
            if prior and prior["method_id"] == method.id
            else method.name,
        )
