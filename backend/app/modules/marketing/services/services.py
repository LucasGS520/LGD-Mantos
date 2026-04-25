"""Serviços de marketing que reutilizam a camada central de IA."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.service import AIService
from app.modules.marketing.schemas.schemas import MarketingRequest, ProductDescriptionRequest


class MarketingService:
    """Orquestra solicitações de descrição, campanha e copy social."""

    @staticmethod
    async def product_description(db: AsyncSession, data: ProductDescriptionRequest) -> dict:
        """Gera descrição comercial com contexto opcional de um produto."""

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
        """Gera sugestão de campanha usando produtos selecionados como contexto."""

        return await AIService.generate(
            db=db,
            message=data.message,
            mode="campanha",
            module="marketing",
            context_ids=data.product_ids,
        )

    @staticmethod
    async def social_copy(db: AsyncSession, data: MarketingRequest) -> dict:
        """Gera texto curto para redes sociais com apoio dos dados da loja."""

        return await AIService.generate(
            db=db,
            message=data.message,
            mode="social",
            module="marketing",
            context_ids=data.product_ids,
        )
