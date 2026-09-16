"""DRE e métricas financeiras."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import finance_repository as finance_repo
from app.modules.analytics.repositories import sales_repository as sales_repo
from app.modules.analytics.schemas.comparacao import Comparado


class FinanceService:
    @staticmethod
    async def dre(db: AsyncSession, month: int | None, year: int | None, compare: bool = False) -> dict:
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

        resultado = {
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

        if compare:
            resultado["comparacao"] = await FinanceService._comparacao(
                db, selected_month, selected_year, revenue, cogs, gross,
                gross_margin_pct, expenses, net, net_margin_pct,
            )

        return resultado

    @staticmethod
    async def _comparacao(
        db: AsyncSession,
        selected_month: int,
        selected_year: int,
        revenue: float,
        cogs: float,
        gross: float,
        gross_margin_pct: float,
        expenses: float,
        net: float,
        net_margin_pct: float,
    ) -> dict:
        """Recalcula o DRE do mês calendário imediatamente anterior ao informado.

        `dre` é parametrizado por mês/ano (não por período nomeado), então não
        usa `resolve_comparison_period` — o anterior aqui é sempre o mês
        fechado anterior, com virada de ano tratada explicitamente (janeiro
        compara contra dezembro do ano anterior).
        """
        if selected_month == 1:
            mes_ant, ano_ant = 12, selected_year - 1
        else:
            mes_ant, ano_ant = selected_month - 1, selected_year

        inicio_ant = datetime(ano_ant, mes_ant, 1, tzinfo=timezone.utc)
        fim_ant = datetime(selected_year, selected_month, 1, tzinfo=timezone.utc)
        inicio_ant_str = f"{ano_ant}-{mes_ant:02d}-01"
        fim_ant_str = f"{selected_year}-{selected_month:02d}-01"

        revenue_ant = await sales_repo.month_revenue(db, inicio_ant, fim_ant)
        cogs_ant = await sales_repo.month_cogs(db, inicio_ant, fim_ant)
        expenses_ant = await finance_repo.expenses_total(db, inicio_ant_str, fim_ant_str)
        gross_ant = revenue_ant - cogs_ant
        net_ant = gross_ant - expenses_ant
        gross_margin_pct_ant = round(gross_ant / revenue_ant * 100, 1) if revenue_ant else 0.0
        net_margin_pct_ant = round(net_ant / revenue_ant * 100, 1) if revenue_ant else 0.0

        return {
            "revenue": Comparado.de(revenue, revenue_ant).model_dump(),
            "cogs": Comparado.de(cogs, cogs_ant).model_dump(),
            "gross_profit": Comparado.de(gross, gross_ant).model_dump(),
            "gross_margin_pct": Comparado.de(gross_margin_pct, gross_margin_pct_ant).model_dump(),
            "expenses": Comparado.de(expenses, expenses_ant).model_dump(),
            "net_profit": Comparado.de(net, net_ant).model_dump(),
            "margin_pct": Comparado.de(net_margin_pct, net_margin_pct_ant).model_dump(),
        }
