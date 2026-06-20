"""Schemas Pydantic das operações de estoque, vendas, despesas e entrada de mercadoria."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class StockMoveIn(BaseModel):
    """Entrada para registrar uma movimentação de estoque."""

    variant_id: str
    movement_type: Literal["entrada", "saida"]
    quantity: int
    unit_cost: Optional[float] = None
    notes: Optional[str] = None


class StockMoveOut(BaseModel):
    """Resposta pública de movimentação de estoque registrada."""

    id: str
    variant_id: str
    movement_type: str
    quantity: int
    unit_cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SaleItemIn(BaseModel):
    """Entrada de um item vendido em uma venda."""

    variant_id: str
    quantity: int
    unit_price: float
    unit_cost: float = 0


class SaleIn(BaseModel):
    """Entrada para registrar uma venda com seus itens."""

    sale_channel_id: Optional[str] = None
    notes: Optional[str] = None
    items: list[SaleItemIn]


class SaleItemOut(BaseModel):
    """Resposta pública de um item de venda."""

    id: str
    variant_id: str
    quantity: int
    unit_price: float
    unit_cost: float

    model_config = {"from_attributes": True}


class SaleOut(BaseModel):
    """Resposta pública de venda com total e itens."""

    id: str
    sold_at: datetime
    sale_channel_id: Optional[str] = None
    notes: Optional[str] = None
    total: float
    items: list[SaleItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ExpenseIn(BaseModel):
    """Entrada para registrar uma despesa."""

    date: str
    category: str
    amount: float
    description: Optional[str] = None
    supplier_id: Optional[str] = None


class ExpenseOut(BaseModel):
    """Resposta pública de despesa registrada."""

    id: str
    date: str
    category: str
    amount: float
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
