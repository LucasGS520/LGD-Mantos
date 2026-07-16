"""Schemas Pydantic de output para cada agente da camada de Marketing.

Cada schema define exatamente o que o agente deve retornar.
O SupervisorService usa esses modelos para persistir resultados no Marketing Ops.
"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# DataAgent — oportunidades de marketing identificadas nos dados
# ---------------------------------------------------------------------------

class MarketingOpportunity(BaseModel):
    product_name: str
    sku: str
    opportunity_type: str = Field(
        description="post_candidate | highlight_candidate | promotion_candidate | restock_first"
    )
    stock: int
    sold_30d: int
    margin_pct: float
    reason: str


class DataAgentOutput(BaseModel):
    opportunities: list[MarketingOpportunity]
    primary: MarketingOpportunity | None = Field(
        default=None,
        description="Melhor oportunidade para a campanha principal"
    )
    summary: str = Field(description="Resumo do panorama atual de marketing em 2-3 frases")


# ---------------------------------------------------------------------------
# StrategyAgent — estratégia de campanha
# ---------------------------------------------------------------------------

class CampaignStrategy(BaseModel):
    name: str = Field(description="Nome curto da campanha")
    objective: str = Field(description="Objetivo principal da campanha")
    product_name: str
    product_sku: str
    channel: str = Field(description="Canal sugerido: Instagram, WhatsApp, TikTok, etc.")
    format: str = Field(description="Formato: feed, story, reels, carrossel, etc.")
    angle: str = Field(description="Ângulo de venda — o que torna este produto atraente agora")
    cta: str = Field(description="Call-to-action: o que o cliente deve fazer")
    risk_level: str = Field(description="Nível de risco: low | medium | high")
    reasoning: str = Field(description="Justificativa da estratégia em 2-3 frases")


class StrategyAgentOutput(BaseModel):
    campaign: CampaignStrategy


# ---------------------------------------------------------------------------
# ContentAgent — copy e textos para o post
# ---------------------------------------------------------------------------

class CopyVariation(BaseModel):
    style: str = Field(description="Estilo do copy: urgência | aspiracional | informativo | casual")
    caption: str
    headline: str


class ContentAgentOutput(BaseModel):
    caption: str = Field(description="Legenda principal do post")
    headline: str = Field(description="Título ou frase de impacto")
    cta_text: str = Field(description="Texto do CTA")
    format: str = Field(description="Formato do conteúdo: feed | story | reels | carrossel")
    variations: list[CopyVariation] = Field(
        description="2 variações alternativas do copy"
    )
    tone_applied: str = Field(description="Descrição do tom aplicado")


# ---------------------------------------------------------------------------
# CreativeAgent — direção visual e prompts de imagem
# ---------------------------------------------------------------------------

class CreativeAgentOutput(BaseModel):
    visual_briefing: str = Field(
        description="Direção visual completa: composição, cores, mood, estilo fotográfico"
    )
    image_prompt: str = Field(
        description="Prompt detalhado para geração ou direcionamento de imagem"
    )
    photo_recommendations: str = Field(
        description="Como usar as fotos reais do produto (frente/costas/detalhe)"
    )
    carousel_idea: str | None = Field(
        default=None,
        description="Ideia de sequência para carrossel (slides 1→N)"
    )
    reel_script_outline: str | None = Field(
        default=None,
        description="Roteiro resumido para reels: gancho, corpo, CTA"
    )
