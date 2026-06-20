"""Roteador principal de analytics — agrega todos os sub-routers do módulo."""

from fastapi import APIRouter

from .agent_context import router as agent_context_router
from .categories import router as categories_router
from .channels import router as channels_router
from .dashboard import router as dashboard_router
from .data_quality import router as data_quality_router
from .finance import router as finance_router
from .marketing_intelligence import router as marketing_intelligence_router
from .products import router as products_router

router = APIRouter(prefix="/analytics", tags=["analytics"])

router.include_router(dashboard_router)
router.include_router(finance_router)
router.include_router(products_router)
router.include_router(categories_router)
router.include_router(channels_router)
router.include_router(marketing_intelligence_router)
router.include_router(data_quality_router)
router.include_router(agent_context_router)
