"""Exporta os modelos ORM compartilhados para facilitar imports no backend."""

from app.shared.models.catalog import Category, Product, ProductVariant, SaleChannel, Supplier
from app.shared.models.operations import (
    Expense,
    MerchandiseEntry,
    MerchandiseEntryItem,
    Sale,
    SaleItem,
    StockMovement,
)

__all__ = [
    "Category",
    "Expense",
    "MerchandiseEntry",
    "MerchandiseEntryItem",
    "Product",
    "ProductVariant",
    "Sale",
    "SaleChannel",
    "SaleItem",
    "StockMovement",
    "Supplier",
]
