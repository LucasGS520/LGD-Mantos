from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    message: str
    mode: str = "geral"
    module: str = "core"
    context_ids: list[str] = Field(default_factory=list)


class AIResponse(BaseModel):
    response: str
    mode: str
    module: str
