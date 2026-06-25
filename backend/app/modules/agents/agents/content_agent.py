"""ContentAgent — gera copy e textos para o post de marketing.

Recebe a estratégia do StrategyAgent e o contexto de marca da Knowledge Layer.
Produz legenda, headline, CTA e variações de copy.

Regras:
- Não inventa preços, descontos ou disponibilidade.
- Tom de voz deve seguir exatamente o definido no contexto de marca.
- Gera 2 variações com estilos distintos além do copy principal.
- Output sempre em português brasileiro.
"""

from agno.agent import Agent

from app.modules.agents.agents.schemas import ContentAgentOutput, StrategyAgentOutput
from app.modules.agents.config import get_agent_model

_INSTRUCTIONS = [
    "Você é o ContentAgent da LGD Mantos, uma loja de mantos e roupas esportivas.",
    "Sua função é gerar copy textual para posts de marketing: legenda, headline, CTA e variações.",
    "Siga EXATAMENTE o tom de voz descrito no contexto de marca — não improvise personalidade.",
    "NUNCA mencione preços, descontos ou promoções sem que tenham sido explicitamente informados.",
    "NUNCA prometa tamanhos disponíveis ou estoque completo sem que os dados confirmem.",
    "Gere copy com energia comercial genuína — baseada no que o produto realmente oferece.",
    "Gere 2 variações alternativas com estilos diferentes: urgência, aspiracional ou informativo.",
    "Mantenha as legendas em tamanho adequado para o canal (Instagram: 150-300 chars principal).",
    "Sempre responda em português brasileiro com linguagem adequada ao público da loja.",
]


def build_content_agent() -> Agent:
    """Cria uma instância fresca do ContentAgent para cada run."""
    return Agent(
        name="content-agent",
        model=get_agent_model(),
        description="Gera copy e textos de marketing para a LGD Mantos seguindo o tom de voz da marca.",
        instructions=_INSTRUCTIONS,
        output_schema=ContentAgentOutput,
        markdown=False,
    )


def build_content_agent_input(
    strategy_output: StrategyAgentOutput,
    brand_context: str,
) -> str:
    """Monta o payload de entrada para o ContentAgent."""

    c = strategy_output.campaign
    return f"""ESTRATÉGIA DA CAMPANHA (StrategyAgent):
- Nome: {c.name}
- Produto: {c.product_name} (SKU: {c.product_sku})
- Objetivo: {c.objective}
- Canal: {c.channel}
- Formato: {c.format}
- Ângulo de venda: {c.angle}
- CTA definido: {c.cta}
- Justificativa: {c.reasoning}

CONTEXTO DE MARCA (Knowledge Layer):
{brand_context}

Com base na estratégia e no contexto de marca:
1. Gere a legenda principal otimizada para o canal ({c.channel}).
2. Gere um headline de impacto.
3. Escreva o texto do CTA.
4. Gere 2 variações de copy com estilos distintos.
5. Descreva o tom aplicado.

Lembre: não mencione preços, não prometa estoque que não foi confirmado."""
