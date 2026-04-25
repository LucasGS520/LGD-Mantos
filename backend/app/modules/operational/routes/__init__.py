"""Agrega os roteadores do módulo operacional em um único APIRouter."""

from fastapi import APIRouter

from app.modules.operational.routes.catalog_routes import router as catalog_router
from app.modules.operational.routes.expense_routes import router as expense_router
from app.modules.operational.routes.purchase_routes import router as purchase_router
from app.modules.operational.routes.sales_routes import router as sales_router
from app.modules.operational.routes.stock_routes import router as stock_router

router = APIRouter()

# Cada arquivo de rota mantém um subconjunto do domínio operacional.
router.include_router(catalog_router)
router.include_router(expense_router)
router.include_router(purchase_router)
router.include_router(sales_router)
router.include_router(stock_router)
