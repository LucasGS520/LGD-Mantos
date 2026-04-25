"""Serviços que transformam consultas analíticas em respostas para o app."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics import repositories as repo


class AnalyticsService:
    """Monta indicadores, rankings, sugestões de compra e DRE."""

    @staticmethod
    async def dashboard(db: AsyncSession) -> dict:
        """Retorna um resumo operacional e financeiro do dia, mês e estoque."""

        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        revenue = await repo.month_revenue(db, month_start)
        cogs = await repo.month_cogs(db, month_start)
        expenses = await repo.expenses_total(db, month_start.strftime("%Y-%m-%d"))
        today_count = await repo.sales_count_since(db, today_start)
        today_revenue = await repo.revenue_since(db, today_start)
        alerts = await repo.stock_alert_count(db)
        stock = await repo.stock_value(db)

        # A série diária alimenta gráficos simples dos últimos 30 dias.
        daily = []
        for index in range(29, -1, -1):
            day = now - timedelta(days=index)
            start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            daily.append({"date": day.strftime("%d/%m"), "value": await repo.daily_revenue(db, start, end)})

        gross_profit = revenue - cogs
        net_profit = gross_profit - expenses
        return {
            "today_revenue": today_revenue,
            "today_count": today_count,
            "month_revenue": revenue,
            "month_cogs": cogs,
            "month_expenses": expenses,
            "gross_profit": gross_profit,
            "net_profit": net_profit,
            "margin_pct": round(net_profit / revenue * 100, 1) if revenue else 0,
            "stock_alerts": alerts,
            "stock_cost_value": float(stock[0]),
            "stock_sale_value": float(stock[1]),
            "stock_units": int(stock[2]),
            "daily_revenue": daily,
        }

    @staticmethod
    async def top_products(db: AsyncSession, days: int) -> list[dict]:
        """Lista produtos mais vendidos no intervalo escolhido."""

        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await repo.top_products(db, since)
        return [
            {
                "name": row[0],
                "sku": row[1],
                "qty": int(row[2] or 0),
                "revenue": float(row[3] or 0),
                "profit": float(row[4] or 0),
            }
            for row in rows
        ]

    @staticmethod
    async def sales_by_size(db: AsyncSession, days: int) -> list[dict]:
        """Resume a venda por tamanho para apoiar compras e grade."""

        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await repo.sales_by_size(db, since)
        return [{"size": row[0], "qty": int(row[1] or 0)} for row in rows]

    @staticmethod
    async def sales_by_channel(db: AsyncSession, days: int) -> list[dict]:
        """Resume desempenho de vendas por canal comercial."""

        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await repo.sales_by_channel(db, since)
        return [{"channel": row[0], "count": int(row[1]), "total": float(row[2] or 0)} for row in rows]

    @staticmethod
    async def purchase_suggestions(db: AsyncSession) -> list[dict]:
        """Sugere reposição com base em vendas recentes e estoque mínimo."""

        since = datetime.now(timezone.utc) - timedelta(days=30)
        velocity = await repo.variant_velocity_30d(db, since)
        variants = await repo.active_variants(db)

        suggestions = []
        for variant in variants:
            sold = velocity.get(variant.id, 0)
            # Sem venda recente, a variante não recebe previsão de dias restantes.
            days_left = (variant.stock_quantity / (sold / 30)) if sold > 0 else 999
            score = sold * 2 - variant.stock_quantity
            if score > 0 or variant.stock_quantity <= variant.min_stock_alert:
                suggestions.append(
                    {
                        "variant_id": variant.id,
                        "product_name": variant.product.name,
                        "sku": variant.product.sku,
                        "size": variant.size,
                        "color": variant.color,
                        "stock": variant.stock_quantity,
                        "sold_30d": sold,
                        "days_remaining": round(days_left, 1) if days_left < 999 else None,
                        "urgency": "alta"
                        if (variant.stock_quantity <= variant.min_stock_alert or days_left < 7)
                        else "media",
                        "suggested_qty": max(10, sold * 2 - variant.stock_quantity),
                    }
                )

        return sorted(
            suggestions,
            key=lambda item: (item["urgency"] == "alta", item["sold_30d"]),
            reverse=True,
        )[:20]

    @staticmethod
    async def dre(db: AsyncSession, month: int | None, year: int | None) -> dict:
        """Calcula um DRE simplificado para o mês e ano informados."""

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

        revenue = await repo.month_revenue(db, start_dt, next_month)
        cogs = await repo.month_cogs(db, start_dt, next_month)
        expenses = await repo.expenses_total(db, start, end)
        gross = revenue - cogs
        net = gross - expenses
        return {
            "period": f"{selected_month:02d}/{selected_year}",
            "revenue": revenue,
            "cogs": cogs,
            "gross_profit": gross,
            "expenses": expenses,
            "net_profit": net,
            "margin_pct": round(net / revenue * 100, 1) if revenue else 0,
        }
