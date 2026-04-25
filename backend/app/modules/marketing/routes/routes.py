from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.marketing.schemas.schemas import (
    MarketingRequest,
    MarketingResponse,
    ProductDescriptionRequest,
)
from app.modules.marketing.services.services import MarketingService

router = APIRouter(prefix="/marketing", tags=["marketing"])


@router.post("/product-description", response_model=MarketingResponse)
async def product_description(
    data: ProductDescriptionRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    return await MarketingService.product_description(db, data)


@router.post("/campaign-suggestion", response_model=MarketingResponse)
async def campaign_suggestion(
    data: MarketingRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    return await MarketingService.campaign_suggestion(db, data)


@router.post("/social-copy", response_model=MarketingResponse)
async def social_copy(
    data: MarketingRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    return await MarketingService.social_copy(db, data)
