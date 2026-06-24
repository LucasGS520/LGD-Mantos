"""Contratos de resposta para qualidade dos dados."""

from pydantic import BaseModel


class ProductIssue(BaseModel):
    name: str
    sku: str


class VariantIssue(BaseModel):
    name: str
    sku: str
    size: str
    color: str


class SaleIssue(BaseModel):
    id: str
    sold_at: str
    total: float


class ExpenseIssue(BaseModel):
    id: str
    date: str
    amount: float
    description: str | None


class DataQualityIssues(BaseModel):
    no_cost_price: list[ProductIssue]
    no_sale_price: list[ProductIssue]
    no_supplier: list[ProductIssue]
    no_category: list[ProductIssue]
    active_no_photo: list[ProductIssue]
    variants_without_info: list[VariantIssue]
    sales_without_channel: list[SaleIssue]
    expenses_without_category: list[ExpenseIssue]


class DataQualityResponse(BaseModel):
    score: float
    total_issues: int
    issues: DataQualityIssues
