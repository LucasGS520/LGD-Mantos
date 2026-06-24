"""Schemas Pydantic para entrada de mercadoria."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NewVariantIn(BaseModel):
    """Tamanho e quantidade de uma variante nova a ser criada."""

    size: str
    color: str = "Unico"
    quantity: int = Field(ge=1)
    unit_cost: float = Field(ge=0)


class NewProductIn(BaseModel):
    """Produto novo criado inline durante a entrada de mercadoria."""

    name: str
    category_id: Optional[str] = None
    cost_price: float = Field(default=0, ge=0)
    sale_price: float = Field(default=0, ge=0)
    description: Optional[str] = None
    brand: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    variants: list[NewVariantIn] = Field(min_length=1)


class ExistingVariantIn(BaseModel):
    """Recompra rara: adiciona estoque a uma variante já existente."""

    variant_id: str
    quantity: int = Field(ge=1)
    unit_cost: float = Field(ge=0)


class EntryItemIn(BaseModel):
    """Item da entrada — produto novo ou variante existente (mutual exclusive)."""

    new_product: Optional[NewProductIn] = None
    existing_variant: Optional[ExistingVariantIn] = None


class EntryIn(BaseModel):
    """Corpo da requisição para registrar uma entrada de mercadoria."""

    supplier_id: Optional[str] = None
    entry_date: str
    notes: Optional[str] = None
    items: list[EntryItemIn] = Field(min_length=1)


class EntryItemOut(BaseModel):
    """Resumo de um item da entrada (variante criada ou reforçada)."""

    variant_id: str
    product_name: str
    size: str
    quantity: int
    unit_cost: float


class EntryOut(BaseModel):
    """Resposta pública de entrada de mercadoria registrada."""

    id: str
    supplier_id: Optional[str] = None
    entry_date: str
    notes: Optional[str] = None
    total_cost: float
    products_created: int
    variants_added: int
    created_at: datetime
    items: list[EntryItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}
