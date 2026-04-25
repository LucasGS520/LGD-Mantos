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
)
from app.shared.schemas.operations import (
    ExpenseIn,
    ExpenseOut,
    POIn,
    POItemOut,
    POOut,
    SaleIn,
    SaleOut,
    StockMoveIn,
    StockMoveOut,
)

__all__ = [
    "CategoryCreate",
    "CategoryOut",
    "ExpenseIn",
    "ExpenseOut",
    "POIn",
    "POItemOut",
    "POOut",
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
]
