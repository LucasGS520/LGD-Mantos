"""Schemas de resposta para análises de categoria."""

from typing import Optional
from pydantic import BaseModel


class CategoryPerformance(BaseModel):
    category_id: str
    category_name: str
    units: int
    revenue: float
    cogs: float
    profit: float
    margin_pct: float
    daily_velocity: float


class SizeShare(BaseModel):
    size: str
    qty: int
    pct: float


class CategorySizeDistribution(BaseModel):
    category_name: str
    sizes: list[SizeShare]
    total_units: int


class CategoryCoverage(BaseModel):
    category_id: str
    category_name: str
    stock_units: int
    stock_value: float
    daily_velocity: float
    coverage_days: Optional[float]


class AttributeGroup(BaseModel):
    name: str
    units: int
    revenue: float
    profit: float
    margin_pct: float


class ProductAttributeAnalysis(BaseModel):
    by_brand: list[AttributeGroup]
    by_type: list[AttributeGroup]
