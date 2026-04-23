from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryCreate(BaseModel):
    name: str

class CategoryOut(BaseModel):
    id: str; name: str
    model_config = {"from_attributes": True}

class SupplierCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None

class SupplierOut(BaseModel):
    id: str; name: str; contact: Optional[str]=None; phone: Optional[str]=None
    email: Optional[str]=None; is_active: bool
    model_config = {"from_attributes": True}

class VariantIn(BaseModel):
    size: str
    color: str = "Único"
    stock_quantity: int = 0
    min_stock_alert: int = 3
    price_override: Optional[float] = None

class VariantOut(BaseModel):
    id: str; product_id: str; size: str; color: str
    stock_quantity: int; min_stock_alert: int; price_override: Optional[float]=None
    model_config = {"from_attributes": True}

class ProductCreate(BaseModel):
    sku: str; name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    cost_price: float = 0
    sale_price: float = 0
    notes: Optional[str] = None
    variants: List[VariantIn] = []

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
    id: str; sku: str; name: str; description: Optional[str]=None
    category_id: Optional[str]=None; supplier_id: Optional[str]=None
    cost_price: float; sale_price: float; notes: Optional[str]=None
    photos: Optional[list]=None; is_active: bool; created_at: datetime
    variants: List[VariantOut] = []
    model_config = {"from_attributes": True}

class StockMoveIn(BaseModel):
    variant_id: str; movement_type: str; quantity: int
    unit_cost: Optional[float] = None; notes: Optional[str] = None

class StockMoveOut(BaseModel):
    id: str; variant_id: str; movement_type: str; quantity: int
    unit_cost: Optional[float]=None; notes: Optional[str]=None; created_at: datetime
    model_config = {"from_attributes": True}

class SaleItemIn(BaseModel):
    variant_id: str; quantity: int; unit_price: float; unit_cost: float = 0

class SaleIn(BaseModel):
    channel: str = "loja"
    notes: Optional[str] = None
    items: List[SaleItemIn]

class SaleItemOut(BaseModel):
    id: str; variant_id: str; quantity: int; unit_price: float; unit_cost: float
    model_config = {"from_attributes": True}

class SaleOut(BaseModel):
    id: str; sold_at: datetime; channel: str; notes: Optional[str]=None
    total: float; items: List[SaleItemOut] = []
    model_config = {"from_attributes": True}

class ExpenseIn(BaseModel):
    date: str; category: str; amount: float
    description: Optional[str]=None; supplier_id: Optional[str]=None

class ExpenseOut(BaseModel):
    id: str; date: str; category: str; amount: float
    description: Optional[str]=None; created_at: datetime
    model_config = {"from_attributes": True}

class POItemIn(BaseModel):
    variant_id: str; quantity: int; unit_cost: float

class POIn(BaseModel):
    supplier_id: str; order_date: str
    notes: Optional[str]=None; items: List[POItemIn]

class POOut(BaseModel):
    id: str; supplier_id: str; order_date: str; status: str
    notes: Optional[str]=None; created_at: datetime
    model_config = {"from_attributes": True}
