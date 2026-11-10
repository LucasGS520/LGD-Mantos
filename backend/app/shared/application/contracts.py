"""Contratos estritos: valores ausentes são distintos de zero."""

from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def canonical_id(value: str) -> str:
    """Valida antes do SQL e mantém o contrato textual dos identificadores."""
    return str(UUID(value))


EntityId = Annotated[str, AfterValidator(canonical_id)]

Money = Annotated[Decimal, Field(ge=0, max_digits=14, decimal_places=2)]
PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]
Name = Annotated[str, Field(min_length=1, max_length=255)]
Quantity = Annotated[int, Field(gt=0, strict=True)]
AuxKind = Literal["supplier", "category", "purchase_channel", "sale_channel", "payment_method"]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
