"""Consultas financeiras sobre despesas."""

from datetime import datetime

from sqlalchemy import Date, cast, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.operations import Expense, Sale, SaleItem


async def expenses_total(db: AsyncSession, start: str, end: str | None = None) -> float:
    """Soma despesas por intervalo textual de datas."""
    query = select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.date >= start)
    if end:
        query = query.where(Expense.date < end)
    result = await db.execute(query)
    return float(result.scalar())


async def expenses_by_category(db: AsyncSession, start: str, end: str | None = None) -> list:
    """Despesas agrupadas por categoria no período."""
    query = (
        select(Expense.category, func.sum(Expense.amount).label("total"))
        .where(Expense.date >= start)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    )
    if end:
        query = query.where(Expense.date < end)
    result = await db.execute(query)
    return result.all()


async def monthly_revenue_evolution(db: AsyncSession, since: datetime) -> dict:
    """Receita mensal agrupada por ano/mês desde a data informada."""
    result = await db.execute(
        select(
            extract("year", Sale.sold_at).label("year"),
            extract("month", Sale.sold_at).label("month"),
            func.coalesce(func.sum(Sale.total), 0).label("revenue"),
        )
        .where(Sale.sold_at >= since)
        .group_by(extract("year", Sale.sold_at), extract("month", Sale.sold_at))
        .order_by(extract("year", Sale.sold_at), extract("month", Sale.sold_at))
    )
    return {(int(r.year), int(r.month)): float(r.revenue) for r in result}


async def monthly_cogs_evolution(db: AsyncSession, since: datetime) -> dict:
    """CMV mensal agrupado por ano/mês desde a data informada."""
    result = await db.execute(
        select(
            extract("year", Sale.sold_at).label("year"),
            extract("month", Sale.sold_at).label("month"),
            func.coalesce(func.sum(SaleItem.unit_cost * SaleItem.quantity), 0).label("cogs"),
        )
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.sold_at >= since)
        .group_by(extract("year", Sale.sold_at), extract("month", Sale.sold_at))
        .order_by(extract("year", Sale.sold_at), extract("month", Sale.sold_at))
    )
    return {(int(r.year), int(r.month)): float(r.cogs) for r in result}


async def monthly_expenses_evolution(db: AsyncSession, since_str: str) -> dict:
    """Despesas mensais agrupadas por ano/mês (date é string YYYY-MM-DD)."""
    date_col = cast(Expense.date, Date)
    year_expr = extract("year", date_col)
    month_expr = extract("month", date_col)
    result = await db.execute(
        select(
            year_expr.label("year"),
            month_expr.label("month"),
            func.sum(Expense.amount).label("expenses"),
        )
        .where(Expense.date >= since_str)
        .group_by(year_expr, month_expr)
        .order_by(year_expr, month_expr)
    )
    return {(int(r.year), int(r.month)): float(r.expenses) for r in result}
