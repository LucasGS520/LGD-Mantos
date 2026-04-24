from pydantic import BaseModel, Field


class MarketingRequest(BaseModel):
    message: str
    product_ids: list[str] = Field(default_factory=list)


class ProductDescriptionRequest(BaseModel):
    product_id: str | None = None
    message: str = "Crie uma descricao comercial para este produto."


class MarketingResponse(BaseModel):
    response: str
    mode: str
    module: str = "marketing"
