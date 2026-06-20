"""Re-exporta todas as funções de repositório para compatibilidade com imports existentes."""

from .finance_repository import (
    expenses_by_category,
    expenses_total,
    monthly_cogs_evolution,
    monthly_expenses_evolution,
    monthly_revenue_evolution,
)
from .product_repository import (
    active_variants,
    sales_by_size,
    stock_value,
    stopped_products,
    top_categories,
    top_products,
    top_products_by_margin,
)
from .sales_repository import (
    daily_revenue,
    daily_revenue_series,
    month_cogs,
    month_revenue,
    revenue_since,
    sales_by_channel,
    sales_count_since,
    units_sold_since,
    variant_velocity_30d,
)

__all__ = [
    "month_revenue",
    "month_cogs",
    "expenses_total",
    "expenses_by_category",
    "monthly_revenue_evolution",
    "monthly_cogs_evolution",
    "monthly_expenses_evolution",
    "sales_count_since",
    "revenue_since",
    "units_sold_since",
    "daily_revenue",
    "daily_revenue_series",
    "top_products",
    "top_products_by_margin",
    "stopped_products",
    "top_categories",
    "sales_by_size",
    "sales_by_channel",
    "variant_velocity_30d",
    "active_variants",
    "stock_value",
]
