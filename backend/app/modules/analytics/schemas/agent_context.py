"""Contratos de resposta do payload de contexto para agentes de IA."""

from pydantic import BaseModel


class ShopHealth(BaseModel):
    net_profit: float
    margin_pct: float
    avg_ticket: float
    month_revenue: float
    data_quality_score: float


class AttentionBlock(BaseModel):
    rupture_risk: list[dict]
    stopped_products: list[dict]
    data_issues_count: int


class OpportunitiesBlock(BaseModel):
    post_candidates: list[dict]
    promotion_candidates: list[dict]
    highlight_candidates: list[dict]


class AgentContextResponse(BaseModel):
    generated_at: str
    shop_health: ShopHealth
    attention: AttentionBlock
    opportunities: OpportunitiesBlock
    purchase_suggestions: list[dict]
