"""Schemas Pydantic usados pelas rotas de marketing."""

from pydantic import BaseModel, Field


class MarketingRequest(BaseModel):
    """Entrada para campanhas e copys que podem referenciar produtos."""

    message: str
    product_ids: list[str] = Field(default_factory=list)


class ProductDescriptionRequest(BaseModel):
    """Entrada para gerar descrição comercial de um produto específico ou genérico."""

    product_id: str | None = None
    message: str = "Crie uma descricao comercial para este produto."


class MarketingResponse(BaseModel):
    """Resposta de marketing gerada pela camada central de IA."""

    response: str
    mode: str
    module: str = "marketing"
