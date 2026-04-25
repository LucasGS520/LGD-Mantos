"""Schemas Pydantic usados pelas rotas de catálogo."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Entrada para criação de uma categoria."""

    name: str


class CategoryOut(BaseModel):
    """Resposta pública de uma categoria cadastrada."""

    id: str
    name: str

    # Permite construir o schema diretamente a partir de instâncias SQLAlchemy.
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
    is_active: bool

    model_config = {"from_attributes": True}


class VariantIn(BaseModel):
    """Entrada para criação de variante de produto."""

    size: str
    color: str = "Unico"
    stock_quantity: int = 0
    min_stock_alert: int = 3
    price_override: Optional[float] = None


class VariantOut(BaseModel):
    """Resposta pública de uma variante, incluindo seu saldo de estoque."""

    id: str
    product_id: str
    size: str
    color: str
    stock_quantity: int
    min_stock_alert: int
    price_override: Optional[float] = None

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    """Entrada para cadastrar produto e suas variantes iniciais."""

    sku: str
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
