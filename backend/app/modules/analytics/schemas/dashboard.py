"""Contratos de resposta do dashboard executivo."""

from pydantic import BaseModel


class DailyRevenue(BaseModel):
    date: str
    value: float


class DashboardResponse(BaseModel):
    today_revenue: float
    today_count: int
    month_revenue: float
    month_cogs: float
    month_expenses: float
    gross_profit: float
    net_profit: float
    margin_pct: float
    avg_ticket: float
    total_units_sold: int
    stock_cost_value: float
    stock_sale_value: float
    stock_units: int
    daily_revenue: list[DailyRevenue]
