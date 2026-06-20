"""Análises centradas em categoria — pivô principal do sistema de analytics."""

from datetime import datetime, timedelta, timezone
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo
from app.modules.analytics.schemas.categories import (
    AttributeGroup,
    CategoryCoverage,
    CategoryPerformance,
    CategorySizeDistribution,
    ProductAttributeAnalysis,
    SizeShare,
)


class CategoryAnalysisService:
    @staticmethod
    async def performance(db: AsyncSession, days: int) -> list[CategoryPerformance]:
        """Performance de cada categoria no período: receita, margem e velocidade."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await product_repo.category_performance(db, since)
        return [
            CategoryPerformance(
                category_id=str(row.category_id),
                category_name=row.category_name,
                units=int(row.units or 0),
                revenue=round(float(row.revenue or 0), 2),
                cogs=round(float(row.cogs or 0), 2),
                profit=round(float(row.profit or 0), 2),
                margin_pct=round(float(row.margin_pct or 0), 1),
                daily_velocity=round(float(row.units or 0) / days, 2),
            )
            for row in rows
        ]

    @staticmethod
    async def size_distribution(db: AsyncSession, days: int) -> list[CategorySizeDistribution]:
        """Distribuição de vendas por tamanho dentro de cada categoria."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await product_repo.category_size_distribution(db, since)

        grouped: dict[str, list] = defaultdict(list)
        for row in rows:
            grouped[row.category_name].append((row.size, int(row.qty or 0)))

        result = []
        for cat_name, sizes in grouped.items():
            total = sum(q for _, q in sizes)
            result.append(CategorySizeDistribution(
                category_name=cat_name,
                total_units=total,
                sizes=[
                    SizeShare(size=s, qty=q, pct=round(q / total * 100, 1) if total else 0)
                    for s, q in sizes
                ],
            ))
        return result

    @staticmethod
    async def stock_coverage(db: AsyncSession) -> list[CategoryCoverage]:
        """Cobertura de estoque por categoria em dias, baseada na velocidade dos últimos 30d."""
        since_30 = datetime.now(timezone.utc) - timedelta(days=30)

        stock_rows = await product_repo.category_stock(db)
        velocity_rows = await product_repo.category_performance(db, since_30)

        velocity_map: dict[str, float] = {
            row.category_name: float(row.units or 0) / 30 for row in velocity_rows
        }

        result = []
        for row in stock_rows:
            daily_v = velocity_map.get(row.category_name, 0.0)
            coverage = round(float(row.stock_units) / daily_v, 1) if daily_v > 0 else None
            result.append(CategoryCoverage(
                category_id=str(row.category_id),
                category_name=row.category_name,
                stock_units=int(row.stock_units or 0),
                stock_value=round(float(row.stock_value or 0), 2),
                daily_velocity=round(daily_v, 2),
                coverage_days=coverage,
            ))
        result.sort(key=lambda x: (x.coverage_days is None, x.coverage_days or 0))
        return result

    @staticmethod
    async def buying_patterns(db: AsyncSession) -> list[dict]:
        """Padrões de compra por categoria baseados nos últimos 90 dias."""
        since_90 = datetime.now(timezone.utc) - timedelta(days=90)
        since_30 = datetime.now(timezone.utc) - timedelta(days=30)

        perf_90 = await product_repo.category_performance(db, since_90)
        size_rows = await product_repo.category_size_distribution(db, since_90)
        stock_rows = await product_repo.category_stock(db)

        stock_map = {r.category_name: int(r.stock_units or 0) for r in stock_rows}
        velocity_30 = {r.category_name: float(r.units or 0) / 30 for r in (
            await product_repo.category_performance(db, since_30)
        )}

        size_grouped: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for row in size_rows:
            size_grouped[row.category_name].append((row.size, int(row.qty or 0)))

        patterns = []
        for row in perf_90:
            cat = row.category_name
            total_sizes = sum(q for _, q in size_grouped.get(cat, []))
            top_sizes = sorted(size_grouped.get(cat, []), key=lambda x: x[1], reverse=True)[:4]
            monthly_velocity = float(row.units or 0) / 3
            daily_v = velocity_30.get(cat, monthly_velocity / 30)
            stock = stock_map.get(cat, 0)
            coverage = round(stock / daily_v, 0) if daily_v > 0 else None

            patterns.append({
                "category_name": cat,
                "monthly_sales_avg": round(monthly_velocity, 1),
                "coverage_days": coverage,
                "suggested_batch": round(monthly_velocity * 1.5),
                "top_sizes": [
                    {
                        "size": s,
                        "pct": round(q / total_sizes * 100, 1) if total_sizes else 0,
                    }
                    for s, q in top_sizes
                ],
                "avg_margin_pct": round(float(row.margin_pct or 0), 1),
            })

        patterns.sort(key=lambda x: x["monthly_sales_avg"], reverse=True)
        return patterns

    @staticmethod
    async def attribute_analysis(db: AsyncSession, days: int) -> ProductAttributeAnalysis:
        """Análise por marca e tipo de produto como drill-down secundário."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        by_brand_rows, by_type_rows = await product_repo.product_attribute_analysis(db, since)

        def to_group(rows) -> list[AttributeGroup]:
            result = []
            for row in rows:
                revenue = float(row.revenue or 0)
                profit = float(row.profit or 0)
                margin_pct = round(profit / revenue * 100, 1) if revenue else 0.0
                result.append(AttributeGroup(
                    name=row[0],
                    units=int(row.units or 0),
                    revenue=round(revenue, 2),
                    profit=round(profit, 2),
                    margin_pct=margin_pct,
                ))
            return result

        return ProductAttributeAnalysis(
            by_brand=to_group(by_brand_rows),
            by_type=to_group(by_type_rows),
        )
