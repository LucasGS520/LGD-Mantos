"""Rota de classificação de produtos — situações de estoque para decisão de compra."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.product_classification_service import (
    ProductClassificationService,
)

router = APIRouter()


@router.get("/product-classification")
async def product_classification(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Classifica produtos em seis situações de estoque, margem e velocidade."""
    return await ProductClassificationService.product_classification(db)
