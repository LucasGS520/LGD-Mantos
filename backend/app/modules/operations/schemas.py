from datetime import date
from typing import Literal

from app.shared.application.contracts import Input, Money, Name, PositiveMoney, Quantity
from pydantic import Field, model_validator

from .policies import POLICIES


class ItemIn(Input):
    variant_id: str
    quantity: Quantity
    unit_cost: Money | None = None
    unit_price: Money | None = None


class PaymentIn(Input):
    id: str | None = None
    amount: PositiveMoney
    method_id: str


class OperationIn(Input):
    kind: Literal["inventory", "purchase", "sale", "adjustment"]
    purchase_date: date | None = None
    supplier_id: str | None = None
    channel_id: str | None = None
    direction: Literal["in", "out"] | None = None
    items: list[ItemIn] = Field(default_factory=list)
    payments: list[PaymentIn] = Field(default_factory=list)
    notes: str | None = None
    reason: Name | None = None
    version: int | None = None
    cancelled: bool = False

    @model_validator(mode="after")
    def validate_kind(self):
        """Impede campos que misturam responsabilidades entre acontecimentos."""
        if not self.items and self.kind != "inventory":
            raise ValueError("Operação exige pelo menos um item")
        POLICIES[self.kind].validate(self)
        return self


class ConfirmIn(Input):
    data: OperationIn
    preview_token: str
