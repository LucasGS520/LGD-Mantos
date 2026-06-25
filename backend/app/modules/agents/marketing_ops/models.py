"""Modelos ORM da camada Marketing Ops.

Estes modelos são o workspace dos agentes: onde campanhas, posts, briefings
criativos, assets textuais, aprovações e a fila de publicação futura são
persistidos. Nenhuma rota de Operacional ou Análise escreve aqui.
"""

from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models.common import now, uid

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

AgentRunStatus = SAEnum(
    "pending", "running", "completed", "failed",
    name="agent_run_status",
)

ContentStatus = SAEnum(
    "draft", "pending_approval", "approved", "rejected",
    name="content_status",
)

ApprovalStatus = SAEnum(
    "pending", "approved", "rejected", "revision_requested",
    name="approval_status",
)

PublishingStatus = SAEnum(
    "waiting_approval", "approved", "published", "failed",
    name="publishing_status",
)


# ---------------------------------------------------------------------------
# AgentRun — rastreia cada execução de workflow de agentes
# ---------------------------------------------------------------------------

class AgentRun(Base):
    """Registro de uma execução do workflow multi-agente."""

    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(AgentRunStatus, nullable=False, default="pending")
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    campaigns = relationship("Campaign", back_populates="agent_run", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Campaign — estratégia de campanha gerada pelo StrategyAgent
# ---------------------------------------------------------------------------

class Campaign(Base):
    """Campanha de marketing gerada pelo StrategyAgent."""

    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    agent_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("agent_runs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    product_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("products.id"), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(100), nullable=True)
    format: Mapped[str | None] = mapped_column(String(100), nullable=True)
    angle: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(ContentStatus, nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    agent_run = relationship("AgentRun", back_populates="campaigns")
    posts = relationship("Post", back_populates="campaign", cascade="all, delete-orphan")
    creative_briefs = relationship("CreativeBrief", back_populates="campaign", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="campaign")
    publishing_queue = relationship("PublishingQueue", back_populates="campaign", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Post — copy textual gerado pelo ContentAgent
# ---------------------------------------------------------------------------

class Post(Base):
    """Post de marketing com copy gerado pelo ContentAgent."""

    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    headline: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    format: Mapped[str | None] = mapped_column(String(100), nullable=True)
    copy_variations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(ContentStatus, nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    campaign = relationship("Campaign", back_populates="posts")
    approvals = relationship("Approval", back_populates="post")


# ---------------------------------------------------------------------------
# CreativeBrief — direção visual gerada pelo CreativeAgent
# ---------------------------------------------------------------------------

class CreativeBrief(Base):
    """Briefing criativo com direção visual e prompt de imagem gerado pelo CreativeAgent."""

    __tablename__ = "creative_briefs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    visual_briefing: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    carousel_idea: Mapped[str | None] = mapped_column(Text, nullable=True)
    reel_script: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(ContentStatus, nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    campaign = relationship("Campaign", back_populates="creative_briefs")
    approvals = relationship("Approval", back_populates="creative_brief")


# ---------------------------------------------------------------------------
# Approval — human-in-the-loop gerenciado pelo ApprovalAgent
# ---------------------------------------------------------------------------

class Approval(Base):
    """Registro de decisão humana sobre campanha, post ou briefing criativo."""

    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    campaign_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=True)
    post_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("posts.id"), nullable=True)
    creative_brief_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("creative_briefs.id"), nullable=True)
    status: Mapped[str] = mapped_column(ApprovalStatus, nullable=False, default="pending")
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    campaign = relationship("Campaign", back_populates="approvals")
    post = relationship("Post", back_populates="approvals")
    creative_brief = relationship("CreativeBrief", back_populates="approvals")


# ---------------------------------------------------------------------------
# PublishingQueue — placeholder para PublishingAgent futuro
# ---------------------------------------------------------------------------

class PublishingQueue(Base):
    """Fila de publicação futura — inativa no MVP, campos preparados para o PublishingAgent."""

    __tablename__ = "publishing_queue"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(100), nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(PublishingStatus, nullable=False, default="waiting_approval")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    campaign = relationship("Campaign", back_populates="publishing_queue")
