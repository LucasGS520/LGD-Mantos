from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.service import AIService
from app.modules.marketing.schemas.schemas import MarketingRequest, ProductDescriptionRequest


class MarketingService:
    @staticmethod
    async def product_description(db: AsyncSession, data: ProductDescriptionRequest) -> dict:
        context_ids = [data.product_id] if data.product_id else []
        return await AIService.generate(
            db=db,
            message=data.message,
            mode="descricao",
            module="marketing",
            context_ids=context_ids,
        )

    @staticmethod
    async def campaign_suggestion(db: AsyncSession, data: MarketingRequest) -> dict:
        return await AIService.generate(
            db=db,
            message=data.message,
            mode="campanha",
            module="marketing",
            context_ids=data.product_ids,
        )

    @staticmethod
    async def social_copy(db: AsyncSession, data: MarketingRequest) -> dict:
        return await AIService.generate(
            db=db,
            message=data.message,
            mode="social",
            module="marketing",
            context_ids=data.product_ids,
        )
