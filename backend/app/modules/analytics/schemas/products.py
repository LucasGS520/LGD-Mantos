"""Contratos de resposta para análise de produtos e canais."""

from pydantic import BaseModel


class TopProductItem(BaseModel):
    name: str
    sku: str
    qty: int
    revenue: float
    profit: float


class TopProductMarginItem(BaseModel):
    name: str
    sku: str
    qty: int
    revenue: float
    profit: float
    margin_pct: float


class StoppedProductItem(BaseModel):
    name: str
    sku: str
    total_stock: int


class RuptureRiskItem(BaseModel):
    product_name: str
    sku: str
    size: str | None
    color: str | None
    stock: int
    sold_30d: int
    days_remaining: float


class TopCategoryItem(BaseModel):
    category: str
    qty: int
    revenue: float


class ProductAnalysisResponse(BaseModel):
    period_days: int
    top_by_profit: list[TopProductItem]
    top_by_margin: list[TopProductMarginItem]
    stopped: list[StoppedProductItem]
    rupture_risk: list[RuptureRiskItem]
    top_categories: list[TopCategoryItem]


class SuggestionItem(BaseModel):
    variant_id: str
    product_name: str
    sku: str
    size: str | None
    color: str | None
    stock: int
    sold_30d: int
    days_remaining: float | None
    urgency: str
    suggested_qty: int


class BySizeItem(BaseModel):
    size: str | None
    qty: int


class ByChannelItem(BaseModel):
    channel: str | None
    count: int
    total: float
