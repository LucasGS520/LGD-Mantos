"""Avalia completude e consistência dos dados operacionais da loja."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import data_quality_repository as dq_repo


class DataQualityService:
    @staticmethod
    async def data_quality(db: AsyncSession) -> dict:
        since_90 = datetime.now(timezone.utc) - timedelta(days=90)

        no_cost = await dq_repo.products_no_cost_price(db)
        no_sale = await dq_repo.products_no_sale_price(db)
        no_supplier = await dq_repo.products_no_supplier(db)
        no_category = await dq_repo.products_no_category(db)
        no_photo = await dq_repo.products_no_photo(db)
        no_variant_info = await dq_repo.variants_no_info(db)
        no_channel = await dq_repo.sales_no_channel(db, since_90)
        no_expense_cat = await dq_repo.expenses_no_category(db)

        total_products = await dq_repo.count_active_products(db)
        total_variants = await dq_repo.count_active_variants(db)

        # Total de slots verificados: 5 checks por produto + 1 por variante + 1 por venda + 1 por despesa
        total_entities = max(1, total_products * 5 + total_variants)
        total_issues = (
            len(no_cost)
            + len(no_sale)
            + len(no_supplier)
            + len(no_category)
            + len(no_photo)
            + len(no_variant_info)
            + len(no_channel)
            + len(no_expense_cat)
        )
        score = round(max(0.0, (total_entities - total_issues) / total_entities * 100), 1)

        return {
            "score": score,
            "total_issues": total_issues,
            "issues": {
                "no_cost_price": no_cost,
                "no_sale_price": no_sale,
                "no_supplier": no_supplier,
                "no_category": no_category,
                "active_no_photo": no_photo,
                "variants_without_info": no_variant_info,
                "sales_without_channel": no_channel,
                "expenses_without_category": no_expense_cat,
            },
        }
