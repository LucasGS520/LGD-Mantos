"""Schemas Pydantic das operações de estoque, vendas, despesas e compras."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class StockMoveIn(BaseModel):
    """Entrada para registrar uma movimentação de estoque."""

    variant_id: str
    movement_type: Literal["entrada", "saida", "ajuste", "devolucao"]
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

    channel: str = "loja"
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
    channel: str
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


class POItemIn(BaseModel):
    """Entrada de item de pedido de compra."""

    variant_id: str
    quantity: int
    unit_cost: float


class POItemOut(BaseModel):
    """Resposta pública de item de pedido de compra."""

    id: str
    variant_id: str
    quantity: int
    unit_cost: float

    model_config = {"from_attributes": True}


class POIn(BaseModel):
    """Entrada para criar um pedido de compra."""

    supplier_id: str
    order_date: str
    notes: Optional[str] = None
    items: list[POItemIn]


class POOut(BaseModel):
    """Resposta pública de pedido de compra com seus itens."""

    id: str
    supplier_id: str
    order_date: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    items: list[POItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}
