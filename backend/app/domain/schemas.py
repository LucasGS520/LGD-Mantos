"""Contratos estritos: valores ausentes são distintos de zero."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Money = Annotated[Decimal, Field(ge=0, max_digits=14, decimal_places=2)]
PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]
Name = Annotated[str, Field(min_length=1, max_length=255)]
Quantity = Annotated[int, Field(gt=0, strict=True)]
AuxKind = Literal["supplier", "category", "purchase_channel", "sale_channel", "payment_method"]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AuxiliaryIn(Input):
    kind: AuxKind
    name: Name
    notes: str | None = None
    active: bool = True
    version: int | None = None
    reason: Name | None = None


class VariantIn(Input):
    size: Annotated[str, Field(min_length=1, max_length=50)]
    color: Annotated[str, Field(min_length=1, max_length=100)]
    reference_cost: Money | None = None
    reference_price: Money | None = None
    active: bool = True
    version: int | None = None
    reason: Name | None = None


class ProductIn(Input):
    name: Name
    print_name: Name
    brand: str | None = None
    model: str | None = None
    category_id: str | None = None
    notes: str | None = None
    active: bool = True
    variants: list[VariantIn] = Field(default_factory=list)
    version: int | None = None
    reason: Name | None = None
    accept_similar: bool = False


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
        if self.kind == "purchase":
            if not self.supplier_id or not self.channel_id:
                raise ValueError("Compra exige fornecedor e canal de compra")
            if self.payments or self.direction:
                raise ValueError("Compra não registra pagamentos ou direção")
            if any(i.unit_cost is None or i.unit_cost <= 0 or i.unit_price is not None for i in self.items):
                raise ValueError("Compra exige custo positivo e não recebe preço praticado")
        elif self.kind == "sale":
            if not self.channel_id or self.supplier_id or self.purchase_date or self.direction:
                raise ValueError("Venda exige canal e não recebe fornecedor, data ou direção")
            if any(i.unit_price is None or i.unit_price <= 0 or i.unit_cost is not None for i in self.items):
                raise ValueError("Venda exige preço positivo; custo é obtido pelo servidor")
        else:
            if self.payments or self.channel_id or self.supplier_id or self.purchase_date:
                raise ValueError("Inventário/ajuste não recebe campos de compra ou venda")
            if any(i.unit_price is not None for i in self.items):
                raise ValueError("Inventário/ajuste não recebe preço praticado")
            if self.kind == "adjustment" and (not self.direction or not self.reason):
                raise ValueError("Ajuste exige direção e motivo")
            if self.kind == "inventory" and self.direction:
                raise ValueError("Inventário não recebe direção")
        return self


class ConfirmIn(Input):
    data: OperationIn
    preview_token: str


class PhotoIn(Input):
    position: int = Field(ge=0)
    primary: bool = False
    variant_id: str | None = None
    color: str | None = None
