"""Exporta schemas Pydantic compartilhados entre rotas e serviços."""

from app.shared.schemas.catalog import (
    CategoryCreate,
    CategoryOut,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    SupplierCreate,
    SupplierOut,
    VariantIn,
    VariantOut,
    VariantUpdateIn,
)
from app.shared.schemas.entry import EntryIn, EntryOut
from app.shared.schemas.operations import (
    ExpenseIn,
    ExpenseOut,
    SaleIn,
    SaleOut,
    StockMoveIn,
    StockMoveOut,
)

__all__ = [
    "CategoryCreate",
    "CategoryOut",
    "EntryIn",
    "EntryOut",
    "ExpenseIn",
    "ExpenseOut",
    "ProductCreate",
    "ProductOut",
    "ProductUpdate",
    "SaleIn",
    "SaleOut",
    "StockMoveIn",
    "StockMoveOut",
    "SupplierCreate",
    "SupplierOut",
    "VariantIn",
    "VariantOut",
    "VariantUpdateIn",
]
