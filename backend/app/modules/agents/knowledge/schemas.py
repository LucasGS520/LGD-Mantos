"""Schemas Pydantic para a Knowledge Layer — documentos de marca."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

KnowledgeDocType = Literal[
    "brand_voice",
    "persona",
    "commercial_rules",
    "visual_reference",
    "approved_caption",
    "approved_prompt",
    "campaign_context",
    "product_style_notes",
]


class KnowledgeDocCreate(BaseModel):
    """Payload para criar um novo documento de conhecimento."""

    doc_type: KnowledgeDocType
    title: str
    content: str
    is_active: bool = True


class KnowledgeDocUpdate(BaseModel):
    """Payload para atualizar um documento existente (campos opcionais)."""

    title: str | None = None
    content: str | None = None
    is_active: bool | None = None


class KnowledgeDocResponse(BaseModel):
    """Resposta completa de um documento de conhecimento."""

    id: str
    doc_type: str
    title: str
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
