"""CreativeAgent — cria direção visual e prompts de imagem.

Recebe a estratégia, o copy gerado, as fotos reais do produto (com tipo:
frente/costas/detalhe) e o contexto criativo da Knowledge Layer.
Produz briefing visual, prompt de imagem e ideias de carrossel/reels.

Regras:
- Não gera imagens localmente. Apenas cria texto de direcionamento.
- Não aprova assets por conta própria.
- Considera o tipo de foto (frente/costas/detalhe) para sugerir uso adequado.
- Output sempre em português brasileiro.
"""

from agno.agent import Agent

from app.modules.agents.agents.schemas import (
    ContentAgentOutput,
    CreativeAgentOutput,
    StrategyAgentOutput,
)
from app.modules.agents.config import get_agent_model

_INSTRUCTIONS = [
    "Você é o CreativeAgent da LGD Mantos, uma loja de mantos e roupas esportivas.",
    "Sua função é criar direção visual e prompts de imagem para campanhas de marketing.",
    "Analise os metadados das fotos reais do produto (frente/costas/detalhe) e sugira o melhor uso de cada uma.",
    "Crie um briefing visual completo: composição, cores, mood, estilo fotográfico.",
    "Crie um prompt detalhado para geração ou direcionamento de imagem (para designer ou ferramenta de IA).",
    "NUNCA gere imagens localmente. Sua função é criar texto de direcionamento criativo.",
    "NUNCA aprove assets por conta própria. A aprovação é sempre do usuário humano.",
    "Se o formato for carrossel, crie uma ideia de sequência lógica de slides.",
    "Se o formato for reels, crie um roteiro resumido: gancho → corpo → CTA.",
    "Sempre responda em português brasileiro com vocabulário do universo de moda/esportes.",
]


def build_creative_agent() -> Agent:
    """Cria uma instância fresca do CreativeAgent para cada run."""
    return Agent(
        name="creative-agent",
        model=get_agent_model(),
        description="Cria direção visual e prompts de imagem para campanhas da LGD Mantos.",
        instructions=_INSTRUCTIONS,
        output_schema=CreativeAgentOutput,
        markdown=False,
    )


def build_creative_agent_input(
    strategy_output: StrategyAgentOutput,
    content_output: ContentAgentOutput,
    product_photos: list[dict],
    creative_context: str,
) -> str:
    """Monta o payload de entrada para o CreativeAgent."""

    c = strategy_output.campaign

    photos_block = "Nenhuma foto cadastrada para este produto."
    if product_photos:
        lines = []
        for photo in product_photos:
            photo_type = photo.get("type", "sem tipo")
            url = photo.get("url", "")
            lines.append(f"- Tipo: {photo_type} | URL: {url}")
        photos_block = "\n".join(lines)

    carousel_note = ""
    if "carrossel" in c.format.lower() or "carousel" in c.format.lower():
        carousel_note = "\nATENÇÃO: O formato é carrossel — crie uma ideia de sequência de slides."

    reel_note = ""
    if "reels" in c.format.lower() or "reel" in c.format.lower():
        reel_note = "\nATENÇÃO: O formato é reels — crie um roteiro resumido de vídeo curto."

    return f"""ESTRATÉGIA DA CAMPANHA:
- Produto: {c.product_name} (SKU: {c.product_sku})
- Canal: {c.channel}
- Formato: {c.format}
- Ângulo: {c.angle}
- CTA: {c.cta}
{carousel_note}{reel_note}

COPY GERADO (ContentAgent):
- Headline: {content_output.headline}
- Legenda: {content_output.caption}
- CTA: {content_output.cta_text}
- Tom aplicado: {content_output.tone_applied}

FOTOS REAIS DO PRODUTO:
{photos_block}

CONTEXTO CRIATIVO (Knowledge Layer):
{creative_context}

Com base em tudo acima:
1. Crie um briefing visual completo.
2. Crie um prompt de imagem detalhado.
3. Recomende como usar as fotos criadas e disponíveis.
4. Se aplicável: ideia de carrossel ou roteiro de reels."""
