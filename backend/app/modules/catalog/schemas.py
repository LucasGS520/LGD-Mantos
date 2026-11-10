from typing import Annotated

from app.shared.application.contracts import EntityId, Input, Money, Name
from pydantic import Field


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
    category_id: EntityId | None = None
    notes: str | None = None
    active: bool = True
    variants: list[VariantIn] = Field(default_factory=list)
    version: int | None = None
    reason: Name | None = None
    accept_similar: bool = False
