"""Análise de produtos: rankings, sugestões de compra e análise de estoque."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo
from app.modules.analytics.utils import resolve_period


class ProductAnalysisService:
    @staticmethod
    async def top_products(db: AsyncSession, period: str | None = None, days: int = 30) -> list[dict]:
        start, end = resolve_period(period, days)
        rows = await product_repo.top_products(db, start, end)
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
    async def product_analysis(db: AsyncSession, period: str | None = None, days: int = 30) -> dict:
        """Análise completa de produtos: margem, parados, risco de ruptura e categorias."""
        now = datetime.now(timezone.utc)
        since, end = resolve_period(period, days)
        since_60 = now - timedelta(days=60)
        since_30 = now - timedelta(days=30)

        # Top por lucro absoluto.
        profit_rows = await product_repo.top_products(db, since, end)
        top_by_profit = sorted(
            [
                {
                    "name": r[0], "sku": r[1],
                    "qty": int(r[2] or 0), "revenue": float(r[3] or 0), "profit": float(r[4] or 0),
                }
                for r in profit_rows
            ],
            key=lambda x: x["profit"],
            reverse=True,
        )

        # Top por margem percentual.
        margin_rows = await product_repo.top_products_by_margin(db, since, end)
        top_by_margin = [
            {
                "name": r[0], "sku": r[1],
                "qty": int(r[2] or 0), "revenue": float(r[3] or 0),
                "profit": float(r[4] or 0),
                "margin_pct": round(float(r[5] or 0), 1),
            }
            for r in margin_rows
        ]

        # Produtos parados (sem venda em 60 dias, com estoque) — janela fixa de negócio.
        stopped_rows = await product_repo.stopped_products(db, since_60)
        stopped = [
            {"name": r[0], "sku": r[1], "total_stock": int(r[2] or 0)}
            for r in stopped_rows
        ]

        # Risco de ruptura: variantes com menos de 15 dias de estoque — usa velocidade dos últimos 30d.
        velocity = await sales_repo.variant_velocity_30d(db, since_30)
        variants = await product_repo.active_variants(db)
        rupture_risk = []
        for variant in variants:
            sold = velocity.get(variant.id, 0)
            if sold == 0:
                continue
            days_left = variant.stock_quantity / (sold / 30)
            if days_left < 15:
                rupture_risk.append({
                    "product_name": variant.product.name,
                    "sku": variant.product.sku,
                    "size": variant.size,
                    "color": variant.color,
                    "stock": variant.stock_quantity,
                    "sold_30d": sold,
                    "days_remaining": round(days_left, 1),
                })
        rupture_risk.sort(key=lambda x: x["days_remaining"])

        # Categorias mais vendidas.
        cat_rows = await product_repo.top_categories(db, since, end)
        top_categories = [
            {"category": r[0], "qty": int(r[1] or 0), "revenue": float(r[2] or 0)}
            for r in cat_rows
        ]

        return {
            "period_days": days,
            "top_by_profit": top_by_profit,
            "top_by_margin": top_by_margin,
            "stopped": stopped,
            "rupture_risk": rupture_risk,
            "top_categories": top_categories,
        }
