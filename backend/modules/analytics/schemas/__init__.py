"""Schemas do contexto analítico usados como contratos de saída da API."""

from pydantic import BaseModel


class DailyRevenueOut(BaseModel):
    """Representa um ponto diário de faturamento para gráficos."""

    date: str
    value: float


class DashboardOut(BaseModel):
    """Resumo consolidado de indicadores do dashboard."""

    today_revenue: float
    today_count: int
    month_revenue: float
    month_cogs: float
    month_expenses: float
    gross_profit: float
    net_profit: float
    margin_pct: float
    stock_alerts: int
    stock_cost_value: float
    stock_sale_value: float
    stock_units: int
    daily_revenue: list[DailyRevenueOut]


class TopProductOut(BaseModel):
    """Indicador de performance por produto no período."""

    name: str
    sku: str
    qty: int
    revenue: float
    profit: float


class SalesBySizeOut(BaseModel):
    """Agrupamento de quantidade vendida por tamanho."""

    size: str
    qty: int


class SalesByChannelOut(BaseModel):
    """Agrupamento de vendas por canal comercial."""

    channel: str
    count: int
    total: float


class PurchaseSuggestionOut(BaseModel):
    """Sugestão de compra por variante com nível de urgência."""

    variant_id: str
    product_name: str
    sku: str
    size: str
    color: str
    stock: int
    sold_30d: int
    days_remaining: float | None
    urgency: str
    suggested_qty: int


class DreOut(BaseModel):
    """Modelo de saída do demonstrativo de resultado simplificado."""

    period: str
    revenue: float
    cogs: float
    gross_profit: float
    expenses: float
    net_profit: float
    margin_pct: float
