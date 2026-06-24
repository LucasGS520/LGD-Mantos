"""Empacota dados analíticos estruturados para consumo de agentes de IA.

Regra: este service não acessa o banco diretamente.
Chama apenas services públicos da camada de Análise.
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from .dashboard_service import DashboardService
from .data_quality_service import DataQualityService
from .marketing_intelligence_service import MarketingIntelligenceService
from .product_analysis_service import ProductAnalysisService


class AgentContextService:
    @staticmethod
    async def agent_context(db: AsyncSession) -> dict:
        dashboard = await DashboardService.dashboard(db)
        marketing = await MarketingIntelligenceService.marketing_intelligence(db)
        product_analysis = await ProductAnalysisService.product_analysis(db)
        data_quality = await DataQualityService.data_quality(db)
        purchase_suggestions = await ProductAnalysisService.purchase_suggestions(db)

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "shop_health": {
                "net_profit": dashboard["net_profit"],
                "margin_pct": dashboard["margin_pct"],
                "avg_ticket": dashboard["avg_ticket"],
                "month_revenue": dashboard["month_revenue"],
                "data_quality_score": data_quality["score"],
            },
            "attention": {
                "rupture_risk": product_analysis["rupture_risk"][:5],
                "stopped_products": product_analysis["stopped"][:5],
                "data_issues_count": data_quality["total_issues"],
            },
            "opportunities": {
                "post_candidates": marketing["post_candidates"][:5],
                "promotion_candidates": marketing["promotion_candidates"][:5],
                "highlight_candidates": marketing["highlight_candidates"][:5],
            },
            "purchase_suggestions": purchase_suggestions[:5],
        }
