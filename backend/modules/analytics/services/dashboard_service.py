"""Serviço analítico para dashboards, rankings e DRE."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from modules.analytics.repositories import DashboardRepository


class DashboardService:
    """Coordena cálculos analíticos a partir dos dados de repositório."""

    def __init__(self, db: AsyncSession) -> None:
        self.repository = DashboardRepository(db)

    async def dashboard(self) -> dict:
        """Consolida indicadores financeiros e de estoque do mês."""
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        month_revenue = await self.repository.month_revenue(month_start)
        month_cogs = await self.repository.month_cogs(month_start)
        month_expenses = await self.repository.month_expenses(month_start.strftime("%Y-%m-%d"))

        today_count = await self.repository.today_count(today_start)
        today_revenue = await self.repository.today_revenue(today_start)

        alerts = await self.repository.stock_alerts()
        stock_cost_value, stock_sale_value, stock_units = await self.repository.stock_values()

        daily = []
        for i in range(29, -1, -1):
            d = now - timedelta(days=i)
            ds = d.replace(hour=0, minute=0, second=0, microsecond=0)
            de = d.replace(hour=23, minute=59, second=59, microsecond=999999)
            value = await self.repository.daily_revenue(ds, de)
            daily.append({"date": d.strftime("%d/%m"), "value": value})

        gross_profit = month_revenue - month_cogs
        net_profit = gross_profit - month_expenses

        return {
            "today_revenue": today_revenue,
            "today_count": today_count,
            "month_revenue": month_revenue,
            "month_cogs": month_cogs,
            "month_expenses": month_expenses,
            "gross_profit": gross_profit,
            "net_profit": net_profit,
            "margin_pct": round(net_profit / month_revenue * 100, 1) if month_revenue else 0,
            "stock_alerts": alerts,
            "stock_cost_value": stock_cost_value,
            "stock_sale_value": stock_sale_value,
            "stock_units": stock_units,
            "daily_revenue": daily,
        }

    async def top_products(self, days: int) -> list[dict]:
        """Retorna produtos mais vendidos no período."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await self.repository.top_products(since)
        return [
            {"name": x[0], "sku": x[1], "qty": int(x[2] or 0), "revenue": float(x[3] or 0), "profit": float(x[4] or 0)}
            for x in rows
        ]

    async def sales_by_size(self, days: int) -> list[dict]:
        """Agrupa vendas por tamanho."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await self.repository.sales_by_size(since)
        return [{"size": x[0], "qty": int(x[1] or 0)} for x in rows]

    async def sales_by_channel(self, days: int) -> list[dict]:
        """Agrupa vendas por canal."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await self.repository.sales_by_channel(since)
        return [{"channel": x[0], "count": int(x[1]), "total": float(x[2] or 0)} for x in rows]

    async def purchase_suggestions(self) -> list[dict]:
        """Calcula sugestões de compra com base em giro e estoque."""
        since = datetime.now(timezone.utc) - timedelta(days=30)
        velocity = await self.repository.velocity_30d(since)
        variants = await self.repository.active_variants()

        suggestions = []
        for v in variants:
            sold = velocity.get(v.id, 0)
            days_left = (v.stock_quantity / (sold / 30)) if sold > 0 else 999
            score = sold * 2 - v.stock_quantity
            if score > 0 or v.stock_quantity <= v.min_stock_alert:
                suggestions.append(
                    {
                        "variant_id": v.id,
                        "product_name": v.product.name,
                        "sku": v.product.sku,
                        "size": v.size,
                        "color": v.color,
                        "stock": v.stock_quantity,
                        "sold_30d": sold,
                        "days_remaining": round(days_left, 1) if days_left < 999 else None,
                        "urgency": "alta" if (v.stock_quantity <= v.min_stock_alert or days_left < 7) else "media",
                        "suggested_qty": max(10, sold * 2 - v.stock_quantity),
                    }
                )

        # Ordena por urgência e volume vendido para priorizar itens críticos.
        return sorted(suggestions, key=lambda x: (x["urgency"] == "alta", x["sold_30d"]), reverse=True)[:20]

    async def dre(self, month: int | None, year: int | None) -> dict:
        """Calcula DRE simplificado para mês/ano informado."""
        now = datetime.now(timezone.utc)
        m, y = month or now.month, year or now.year
        start = f"{y}-{m:02d}-01"
        end = f"{y}-{m + 1:02d}-01" if m < 12 else f"{y + 1}-01-01"
        start_dt = datetime(y, m, 1, tzinfo=timezone.utc)
        end_dt = datetime(y, m + 1, 1, tzinfo=timezone.utc) if m < 12 else datetime(y + 1, 1, 1, tzinfo=timezone.utc)

        revenue = await self.repository.dre_revenue(start_dt, end_dt)
        cogs_val = await self.repository.dre_cogs(start_dt, end_dt)
        expenses = await self.repository.dre_expenses(start, end)

        gross = revenue - cogs_val
        net = gross - expenses

        return {
            "period": f"{m:02d}/{y}",
            "revenue": revenue,
            "cogs": cogs_val,
            "gross_profit": gross,
            "expenses": expenses,
            "net_profit": net,
            "margin_pct": round(net / revenue * 100, 1) if revenue else 0,
        }
