"""Contratos de resposta do DRE e análise financeira."""

from pydantic import BaseModel


class ExpenseByCategory(BaseModel):
    category: str
    total: float


class MonthEvolution(BaseModel):
    period: str
    revenue: float
    net_profit: float


class DREResponse(BaseModel):
    period: str
    revenue: float
    cogs: float
    gross_profit: float
    gross_margin_pct: float
    expenses: float
    expenses_by_category: list[ExpenseByCategory]
    net_profit: float
    margin_pct: float
    break_even: float | None
    evolution: list[MonthEvolution]
