"""Indicadores do dashboard executivo."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import finance_repository as finance_repo
from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo


class DashboardService:
    @staticmethod
    async def dashboard(db: AsyncSession) -> dict:
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        revenue = await sales_repo.month_revenue(db, month_start)
        cogs = await sales_repo.month_cogs(db, month_start)
        expenses = await finance_repo.expenses_total(db, month_start.strftime("%Y-%m-%d"))
        today_count = await sales_repo.sales_count_since(db, today_start)
        today_revenue = await sales_repo.revenue_since(db, today_start)
        month_count = await sales_repo.sales_count_since(db, month_start)
        total_units = await sales_repo.units_sold_since(db, month_start)
        stock = await product_repo.stock_value(db)

        # Série diária dos últimos 30 dias em uma única query SQL.
        series_start = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        series_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        series = await sales_repo.daily_revenue_series(db, series_start, series_end)

        daily = []
        for index in range(29, -1, -1):
            day = now - timedelta(days=index)
            day_str = day.strftime("%Y-%m-%d")
            daily.append({"date": day.strftime("%d/%m"), "value": series.get(day_str, 0.0)})

        gross_profit = revenue - cogs
        net_profit = gross_profit - expenses
        avg_ticket = round(revenue / month_count, 2) if month_count else 0.0

        return {
            "today_revenue": today_revenue,
            "today_count": today_count,
            "month_revenue": revenue,
            "month_cogs": cogs,
            "month_expenses": expenses,
            "gross_profit": gross_profit,
            "net_profit": net_profit,
            "margin_pct": round(net_profit / revenue * 100, 1) if revenue else 0,
            "avg_ticket": avg_ticket,
            "total_units_sold": total_units,
            "stock_cost_value": float(stock[0]),
            "stock_sale_value": float(stock[1]),
            "stock_units": int(stock[2]),
            "daily_revenue": daily,
        }
