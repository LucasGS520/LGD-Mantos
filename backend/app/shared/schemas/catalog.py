from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class SupplierCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class SupplierOut(BaseModel):
    id: str
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class VariantIn(BaseModel):
    size: str
    color: str = "Unico"
    stock_quantity: int = 0
    min_stock_alert: int = 3
    price_override: Optional[float] = None


class VariantOut(BaseModel):
    id: str
    product_id: str
    size: str
    color: str
    stock_quantity: int
    min_stock_alert: int
    price_override: Optional[float] = None

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
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
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    cost_price: Optional[float] = None
    sale_price: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
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
