"""Modelo ORM para documentos da Knowledge Layer.

Armazena contexto de marca (tom de voz, persona, regras comerciais, referências
visuais, captions aprovados) que os agentes consultam para gerar conteúdo
alinhado à identidade da LGD Mantos.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.models.common import now, uid

KnowledgeDocType = SAEnum(
    "brand_voice",
    "persona",
    "commercial_rules",
    "visual_reference",
    "approved_caption",
    "approved_prompt",
    "campaign_context",
    "product_style_notes",
    name="knowledge_doc_type",
)


class KnowledgeDocument(Base):
    """Documento de conhecimento de marca consultado pelos agentes como contexto."""

    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    doc_type: Mapped[str] = mapped_column(KnowledgeDocType, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
