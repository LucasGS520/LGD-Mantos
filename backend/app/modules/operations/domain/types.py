"""Contratos internos do replay; projeções são distintas da entrada HTTP."""

from typing import TypedDict


class VariantState(TypedDict):
    stock: int
    unknown: int
    known_value: str
    average_cost: str | None
    first_entry: str | None
    last_sale: str | None
    sold: int
