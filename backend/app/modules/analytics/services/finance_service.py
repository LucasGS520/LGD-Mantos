"""DRE e métricas financeiras."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import finance_repository as finance_repo
from app.modules.analytics.repositories import sales_repository as sales_repo


class FinanceService:
    @staticmethod
    async def dre(db: AsyncSession, month: int | None, year: int | None) -> dict:
        now = datetime.now(timezone.utc)
        selected_month = month or now.month
        selected_year = year or now.year
        next_month = (
            datetime(selected_year, selected_month + 1, 1, tzinfo=timezone.utc)
            if selected_month < 12
            else datetime(selected_year + 1, 1, 1, tzinfo=timezone.utc)
        )
        start_dt = datetime(selected_year, selected_month, 1, tzinfo=timezone.utc)
        start = f"{selected_year}-{selected_month:02d}-01"
        end = (
            f"{selected_year}-{selected_month + 1:02d}-01"
            if selected_month < 12
            else f"{selected_year + 1}-01-01"
        )

        revenue = await sales_repo.month_revenue(db, start_dt, next_month)
        cogs = await sales_repo.month_cogs(db, start_dt, next_month)
        expenses = await finance_repo.expenses_total(db, start, end)
        gross = revenue - cogs
        net = gross - expenses
        gross_margin_pct = round(gross / revenue * 100, 1) if revenue else 0.0
        net_margin_pct = round(net / revenue * 100, 1) if revenue else 0.0

        # Ponto de equilíbrio: quanto precisa faturar para cobrir todas as despesas.
        break_even = round(expenses / (gross_margin_pct / 100), 2) if gross_margin_pct > 0 else None

        # Despesas detalhadas por categoria.
        cat_rows = await finance_repo.expenses_by_category(db, start, end)
        expenses_by_category = [
            {"category": row[0], "total": float(row[1])} for row in cat_rows
        ]

        # Evolução dos últimos 6 meses.
        six_months_ago = now - timedelta(days=180)
        six_months_ago_str = six_months_ago.strftime("%Y-%m-%d")
        rev_map = await finance_repo.monthly_revenue_evolution(db, six_months_ago)
        cogs_map = await finance_repo.monthly_cogs_evolution(db, six_months_ago)
        exp_map = await finance_repo.monthly_expenses_evolution(db, six_months_ago_str)

        evolution = []
        for i in range(5, -1, -1):
            ref = now - timedelta(days=30 * i)
            key = (ref.year, ref.month)
            rev = rev_map.get(key, 0.0)
            cg = cogs_map.get(key, 0.0)
            ex = exp_map.get(key, 0.0)
            evolution.append({
                "period": f"{ref.month:02d}/{ref.year}",
                "revenue": rev,
                "net_profit": rev - cg - ex,
            })

        return {
            "period": f"{selected_month:02d}/{selected_year}",
            "revenue": revenue,
            "cogs": cogs,
            "gross_profit": gross,
            "gross_margin_pct": gross_margin_pct,
            "expenses": expenses,
            "expenses_by_category": expenses_by_category,
            "net_profit": net,
            "margin_pct": net_margin_pct,
            "break_even": break_even,
            "evolution": evolution,
        }
