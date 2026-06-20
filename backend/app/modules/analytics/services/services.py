"""Mantido para compatibilidade. Importar dos services individuais."""

from .channel_analysis_service import ChannelAnalysisService
from .dashboard_service import DashboardService
from .finance_service import FinanceService
from .product_analysis_service import ProductAnalysisService


class AnalyticsService:
    dashboard = DashboardService.dashboard
    top_products = ProductAnalysisService.top_products
    sales_by_size = ChannelAnalysisService.sales_by_size
    sales_by_channel = ChannelAnalysisService.sales_by_channel
    purchase_suggestions = ProductAnalysisService.purchase_suggestions
    dre = FinanceService.dre
