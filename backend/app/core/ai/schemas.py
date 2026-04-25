"""Schemas Pydantic para chamadas ao assistente de IA."""

from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    """Entrada genérica para solicitar uma resposta da IA com contexto da loja."""

    message: str
    mode: str = "geral"
    module: str = "core"
    context_ids: list[str] = Field(default_factory=list)


class AIResponse(BaseModel):
    """Resposta padronizada retornada pelo serviço de IA."""

    response: str
    mode: str
    module: str
