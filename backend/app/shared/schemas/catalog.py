"""Schemas Pydantic usados pelas rotas de catálogo."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Entrada para criação ou atualização de uma categoria."""

    name: str
    description: Optional[str] = None


class CategoryOut(BaseModel):
    """Resposta pública de uma categoria cadastrada."""

    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SupplierCreate(BaseModel):
    """Entrada para criação ou atualização de fornecedor."""

    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class SupplierOut(BaseModel):
    """Resposta pública de fornecedor."""

    id: str
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SaleChannelCreate(BaseModel):
    """Entrada para criação ou atualização de canal de venda."""

    name: str
    description: Optional[str] = None
    color: str = "#D4A847"
    fee_pct: float = 0.0
    monthly_goal: Optional[float] = None


class SaleChannelOut(BaseModel):
    """Resposta pública de canal de venda."""

    id: str
    name: str
    description: Optional[str] = None
    color: str
    fee_pct: float
    monthly_goal: Optional[float] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class VariantIn(BaseModel):
    """Entrada para criação de variante de produto."""

    size: str
    color: str = "Unico"
    stock_quantity: int = Field(default=0, ge=0)
    price_override: Optional[float] = None


class VariantOut(BaseModel):
    """Resposta pública de uma variante, incluindo seu saldo de estoque."""

    id: str
    product_id: str
    size: str
    color: str
    stock_quantity: int
    price_override: Optional[float] = None

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    """Entrada para cadastrar produto e suas variantes iniciais."""

    sku: Optional[str] = None
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    cost_price: float = 0
    sale_price: float = 0
    notes: Optional[str] = None
    variants: list[VariantIn] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    """Entrada parcial para atualizar dados editáveis de um produto."""

    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    cost_price: Optional[float] = None
    sale_price: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    """Resposta pública completa de produto, com fotos e variantes."""

    id: str
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    cost_price: float
    sale_price: float
    notes: Optional[str] = None
    photos: Optional[list] = None
    is_active: bool
    created_at: datetime
    variants: list[VariantOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}
