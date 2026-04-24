from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StockMoveIn(BaseModel):
    variant_id: str
    movement_type: str
    quantity: int
    unit_cost: Optional[float] = None
    notes: Optional[str] = None


class StockMoveOut(BaseModel):
    id: str
    variant_id: str
    movement_type: str
    quantity: int
    unit_cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SaleItemIn(BaseModel):
    variant_id: str
    quantity: int
    unit_price: float
    unit_cost: float = 0


class SaleIn(BaseModel):
    channel: str = "loja"
    notes: Optional[str] = None
    items: list[SaleItemIn]


class SaleItemOut(BaseModel):
    id: str
    variant_id: str
    quantity: int
    unit_price: float
    unit_cost: float

    model_config = {"from_attributes": True}


class SaleOut(BaseModel):
    id: str
    sold_at: datetime
    channel: str
    notes: Optional[str] = None
    total: float
    items: list[SaleItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ExpenseIn(BaseModel):
    date: str
    category: str
    amount: float
    description: Optional[str] = None
    supplier_id: Optional[str] = None


class ExpenseOut(BaseModel):
    id: str
    date: str
    category: str
    amount: float
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class POItemIn(BaseModel):
    variant_id: str
    quantity: int
    unit_cost: float


class POIn(BaseModel):
    supplier_id: str
    order_date: str
    notes: Optional[str] = None
    items: list[POItemIn]


class POOut(BaseModel):
    id: str
    supplier_id: str
    order_date: str
    status: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
