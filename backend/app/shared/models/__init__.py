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
from app.shared.models.settings import AppPreference

__all__ = [
    "AppPreference",
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
