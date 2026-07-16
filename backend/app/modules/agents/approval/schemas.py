"""Schemas Pydantic para o módulo de aprovação (ApprovalAgent)."""

from datetime import datetime

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Leitura — estruturas retornadas pelas rotas GET
# ---------------------------------------------------------------------------

class PostSummary(BaseModel):
    id: str
    caption: str | None
    headline: str | None
    cta_text: str | None
    format: str | None
    copy_variations: list | None
    status: str

    model_config = {"from_attributes": True}


class CreativeBriefSummary(BaseModel):
    id: str
    visual_briefing: str | None
    image_prompt: str | None
    carousel_idea: str | None
    reel_script: str | None
    photo_analysis: dict | None
    status: str

    model_config = {"from_attributes": True}


class CampaignSummary(BaseModel):
    id: str
    name: str
    objective: str
    channel: str | None
    format: str | None
    angle: str | None
    cta: str | None
    risk_level: str | None
    status: str
    posts: list[PostSummary] = []
    creative_briefs: list[CreativeBriefSummary] = []

    model_config = {"from_attributes": True}


class ApprovalDetail(BaseModel):
    """Detalhe completo de uma aprovação — inclui toda a campanha, post e briefing."""

    id: str
    status: str
    comment: str | None
    decided_at: datetime | None
    created_at: datetime
    campaign: CampaignSummary | None

    model_config = {"from_attributes": True}


class ApprovalListItem(BaseModel):
    """Item resumido para listagem de aprovações pendentes."""

    id: str
    status: str
    campaign_id: str | None
    campaign_name: str | None
    campaign_channel: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Escrita — payloads recebidos nas ações de decisão
# ---------------------------------------------------------------------------

class DecisionRequest(BaseModel):
    """Payload para decisões de aprovação, rejeição ou pedido de revisão."""

    comment: str | None = Field(
        default=None,
        description="Obrigatório para 'reject' e 'revision'. Opcional para 'approve'.",
    )


# ---------------------------------------------------------------------------
# Status de um agent_run — para polling assíncrono
# ---------------------------------------------------------------------------

class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    objective: str
    created_at: datetime
    updated_at: datetime
    error: str | None
    result: dict | None
