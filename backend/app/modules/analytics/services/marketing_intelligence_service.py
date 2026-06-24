"""Classifica produtos em listas de ação para decisões de conteúdo e promoção."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo

_STOCK_SAFE = 5      # estoque mínimo para postar sem risco
_STOCK_CRITICAL = 3  # estoque que dispara alerta de reposição antes de postar
_VELOCITY_MIN = 3    # unidades/30d para considerar produto popular
_MARGIN_HIGH = 35.0  # margem % para considerar produto de destaque


class MarketingIntelligenceService:
    @staticmethod
    async def marketing_intelligence(db: AsyncSession) -> dict:
        since_30 = datetime.now(timezone.utc) - timedelta(days=30)
        velocity = await sales_repo.variant_velocity_30d(db, since_30)
        variants = await product_repo.active_variants(db)

        avoid_post: list[dict] = []
        restock_first: list[dict] = []
        post_candidates: list[dict] = []
        highlight_candidates: list[dict] = []
        promotion_candidates: list[dict] = []

        for variant in variants:
            sold = velocity.get(variant.id, 0)
            stock = variant.stock_quantity
            sale_price = float(variant.product.sale_price or 0)
            cost_price = float(variant.product.cost_price or 0)
            margin_pct = (
                round((sale_price - cost_price) / sale_price * 100, 1)
                if sale_price > 0
                else 0.0
            )

            item = {
                "product_name": variant.product.name,
                "sku": variant.product.sku,
                "size": variant.size,
                "color": variant.color,
                "stock": stock,
                "margin_pct": margin_pct,
                "sold_30d": sold,
            }

            if stock == 0:
                avoid_post.append({**item, "reason": "sem estoque"})
            elif sold >= _VELOCITY_MIN and stock <= _STOCK_CRITICAL:
                restock_first.append({**item, "reason": "boa saída, estoque crítico"})
            else:
                if sold >= _VELOCITY_MIN and stock >= _STOCK_SAFE:
                    post_candidates.append({**item, "reason": "alta saída e disponível"})
                if margin_pct >= _MARGIN_HIGH and stock >= _STOCK_SAFE:
                    highlight_candidates.append({**item, "reason": "alta margem e disponível"})
                if sold == 0 and stock > 0:
                    promotion_candidates.append({**item, "reason": "sem saída — queimar estoque"})

        post_candidates.sort(key=lambda x: x["sold_30d"], reverse=True)
        highlight_candidates.sort(key=lambda x: x["margin_pct"], reverse=True)
        promotion_candidates.sort(key=lambda x: x["stock"], reverse=True)
        restock_first.sort(key=lambda x: x["sold_30d"], reverse=True)

        return {
            "post_candidates": post_candidates,
            "promotion_candidates": promotion_candidates,
            "highlight_candidates": highlight_candidates,
            "avoid_post": avoid_post,
            "restock_first": restock_first,
        }
