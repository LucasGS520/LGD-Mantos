"""Re-exporta todos os schemas do módulo de analytics."""

from .dashboard import DailyRevenue, DashboardResponse
from .finance import DREResponse
from .products import ByChannelItem, BySizeItem, SuggestionItem, TopProductItem

__all__ = [
    "DailyRevenue",
    "DashboardResponse",
    "DREResponse",
    "TopProductItem",
    "SuggestionItem",
    "BySizeItem",
    "ByChannelItem",
]
