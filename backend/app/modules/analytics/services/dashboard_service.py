"""Indicadores do dashboard executivo."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import finance_repository as finance_repo
from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo
from app.modules.analytics.schemas.comparacao import Comparado
from app.modules.analytics.utils import resolve_comparison_period


class DashboardService:
    @staticmethod
    async def dashboard(db: AsyncSession, compare: bool = False) -> dict:
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Teto explícito em `now`/"amanhã" nos três indicadores: sem isso o lado
        # atual ficava sem teto (contava venda/despesa com data futura por
        # inteiro) enquanto o lado anterior (`_comparacao`) já é uma janela
        # fechada — a assimetria enviesava toda comparação de lucro/margem.
        revenue = await sales_repo.month_revenue(db, month_start, now)
        cogs = await sales_repo.month_cogs(db, month_start, now)
        # `Expense.date` é string "YYYY-MM-DD" (sem hora), então o teto tem que
        # ser por dia — "amanhã" — pra incluir despesas lançadas hoje e ainda
        # assim excluir qualquer data futura.
        expenses_end = (today_start.date() + timedelta(days=1)).strftime("%Y-%m-%d")
        expenses = await finance_repo.expenses_total(db, month_start.strftime("%Y-%m-%d"), expenses_end)
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
        margin_pct = round(net_profit / revenue * 100, 1) if revenue else 0

        resultado = {
            "today_revenue": today_revenue,
            "today_count": today_count,
            "month_revenue": revenue,
            "month_cogs": cogs,
            "month_expenses": expenses,
            "gross_profit": gross_profit,
            "net_profit": net_profit,
            "margin_pct": margin_pct,
            "avg_ticket": avg_ticket,
            "total_units_sold": total_units,
            "stock_cost_value": float(stock[0]),
            "stock_sale_value": float(stock[1]),
            "stock_units": int(stock[2]),
            "daily_revenue": daily,
        }

        if compare:
            resultado["comparacao"] = await DashboardService._comparacao(db, now, revenue, gross_profit, net_profit, margin_pct, avg_ticket, total_units)

        return resultado

    @staticmethod
    async def _comparacao(
        db: AsyncSession,
        now: datetime,
        revenue: float,
        gross_profit: float,
        net_profit: float,
        margin_pct: float,
        avg_ticket: float,
        total_units: int,
    ) -> dict:
        """Recalcula os mesmos seis indicadores para o mês anterior (mesmos dias decorridos).

        `sales_count_since` e `units_sold_since` não aceitam janela fechada
        (só `since`), então o total de vendas e de unidades do período
        anterior é obtido somando as quebras por canal/tamanho — que já
        aceitam `since` e `end` — em vez de estender esses dois repositórios.
        """
        _, (inicio_anterior, fim_anterior) = resolve_comparison_period("current_month", agora=now)

        revenue_ant = await sales_repo.month_revenue(db, inicio_anterior, fim_anterior)
        cogs_ant = await sales_repo.month_cogs(db, inicio_anterior, fim_anterior)
        # Mesma correção do lado atual: `Expense.date` é string de dia, e o
        # filtro é `< end`, então usar `fim_anterior` puro excluía o dia inteiro
        # em que ele cai. Soma-se 1 dia pro teto cobrir o mesmo número de dias
        # que o lado atual (que vai até "amanhã" em relação a hoje).
        expenses_end_ant = (fim_anterior.date() + timedelta(days=1)).strftime("%Y-%m-%d")
        expenses_ant = await finance_repo.expenses_total(
            db, inicio_anterior.strftime("%Y-%m-%d"), expenses_end_ant
        )
        gross_profit_ant = revenue_ant - cogs_ant
        net_profit_ant = gross_profit_ant - expenses_ant
        margin_pct_ant = round(net_profit_ant / revenue_ant * 100, 1) if revenue_ant else 0

        canais_ant = await sales_repo.sales_by_channel(db, inicio_anterior, fim_anterior)
        vendas_count_ant = sum(int(row[1] or 0) for row in canais_ant)
        avg_ticket_ant = round(revenue_ant / vendas_count_ant, 2) if vendas_count_ant else 0.0

        tamanhos_ant = await product_repo.sales_by_size(db, inicio_anterior, fim_anterior)
        total_units_ant = sum(int(row[1] or 0) for row in tamanhos_ant)

        return {
            "month_revenue": Comparado.de(revenue, revenue_ant).model_dump(),
            "gross_profit": Comparado.de(gross_profit, gross_profit_ant).model_dump(),
            "net_profit": Comparado.de(net_profit, net_profit_ant).model_dump(),
            "margin_pct": Comparado.de(margin_pct, margin_pct_ant).model_dump(),
            "avg_ticket": Comparado.de(avg_ticket, avg_ticket_ant).model_dump(),
            "total_units_sold": Comparado.de(total_units, total_units_ant).model_dump(),
        }
