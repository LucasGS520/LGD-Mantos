"""Contratos estritos: valores ausentes são distintos de zero."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Money = Annotated[Decimal, Field(ge=0, max_digits=14, decimal_places=2)]
PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]
Name = Annotated[str, Field(min_length=1, max_length=255)]
Quantity = Annotated[int, Field(gt=0, strict=True)]
AuxKind = Literal["supplier", "category", "purchase_channel", "sale_channel", "payment_method"]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
