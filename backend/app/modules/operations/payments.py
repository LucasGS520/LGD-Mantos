"""Recebimentos preservam IDs, nomes e instantes."""

from app.modules.auxiliaries.public import auxiliary_many
from app.shared.application.errors import ApplicationError


async def prepare_payments(db, payments, previous, payload):
    old_payments = {p["id"]: p for p in previous.get("payments", [])}
    methods = await auxiliary_many(
        db, [payment.method_id for payment in payments], "payment_method"
    )
    seen_payments = set()
    for index, payment in enumerate(payments):
        prior = old_payments.get(payment.id)
        if payment.id and prior is None:
            raise ApplicationError(422, "Pagamento desconhecido nesta venda")
        if payment.id and payment.id in seen_payments:
            raise ApplicationError(422, "Pagamento repetido")
        seen_payments.add(payment.id)
        method = methods[payment.method_id]
        if not method.active and (not prior or prior["method_id"] != method.id):
            raise ApplicationError(422, "Cadastro auxiliar incompatível ou desativado")
        payload["payments"][index].update(
            id=payment.id or f"new-{index}",
            created_at=prior["created_at"] if prior else "confirmation",
            method_name=prior["method_name"]
            if prior and prior["method_id"] == method.id
            else method.name,
        )
