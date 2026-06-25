"""DataAgent — identifica oportunidades de marketing nos dados operacionais.

Recebe dados pré-carregados (marketing intelligence + contexto da loja) e
seleciona as melhores oportunidades para a campanha solicitada.

Regras:
- Não gera conteúdo. Apenas analisa e seleciona dados.
- Não inventa dados. Só usa o que recebeu como input.
- Output sempre em português brasileiro.
"""

import json

from agno.agent import Agent

from app.modules.agents.agents.schemas import DataAgentOutput
from app.modules.agents.config import get_agent_model

_INSTRUCTIONS = [
    "Você é o DataAgent da LGD Mantos, uma loja de mantos e roupas esportivas.",
    "Sua única função é analisar os dados operacionais recebidos e identificar oportunidades de marketing.",
    "Selecione as melhores oportunidades considerando: estoque disponível, velocidade de venda, margem e aderência ao objetivo.",
    "Nunca invente dados. Use somente o que foi fornecido no input.",
    "Nunca gere legendas, textos de campanha ou direção visual. Isso não é sua função.",
    "Priorize produtos com estoque suficiente (>= 3 unidades) para não gerar campanha sem cobertura.",
    "Sempre responda em português brasileiro.",
]


def build_data_agent() -> Agent:
    """Cria uma instância fresca do DataAgent para cada run."""
    return Agent(
        name="data-agent",
        model=get_agent_model(),
        description="Analisa dados da loja LGD Mantos e identifica as melhores oportunidades de marketing.",
        instructions=_INSTRUCTIONS,
        output_schema=DataAgentOutput,
        markdown=False,
    )


def build_data_agent_input(
    objective: str,
    marketing_data: dict,
    agent_context: dict,
) -> str:
    """Monta o payload de entrada para o DataAgent."""

    post_candidates = marketing_data.get("post_candidates", [])[:8]
    highlight_candidates = marketing_data.get("highlight_candidates", [])[:5]
    promotion_candidates = marketing_data.get("promotion_candidates", [])[:5]
    restock_first = marketing_data.get("restock_first", [])[:3]
    avoid_post = marketing_data.get("avoid_post", [])[:3]

    shop_health = agent_context.get("shop_health", {})
    attention = agent_context.get("attention", {})

    return f"""OBJETIVO DA CAMPANHA:
{objective}

SAÚDE DA LOJA (mês atual):
- Receita: R$ {shop_health.get('month_revenue', 0):.2f}
- Margem líquida: {shop_health.get('margin_pct', 0):.1f}%
- Ticket médio: R$ {shop_health.get('avg_ticket', 0):.2f}

CANDIDATOS A POST (alta saída + estoque):
{json.dumps(post_candidates, ensure_ascii=False, indent=2)}

CANDIDATOS A DESTAQUE (alta margem + estoque):
{json.dumps(highlight_candidates, ensure_ascii=False, indent=2)}

CANDIDATOS A PROMOÇÃO (sem saída + estoque parado):
{json.dumps(promotion_candidates, ensure_ascii=False, indent=2)}

PRECISA REPOR ANTES DE POSTAR:
{json.dumps(restock_first, ensure_ascii=False, indent=2)}

EVITAR (sem estoque):
{json.dumps(avoid_post, ensure_ascii=False, indent=2)}

ATENÇÃO:
- Produtos com risco de ruptura: {len(attention.get('rupture_risk', []))}
- Produtos parados: {len(attention.get('stopped_products', []))}

Com base nesses dados e no objetivo da campanha, selecione e ranqueie as melhores oportunidades.
Identifique a principal recomendação (primary) e forneça um resumo do panorama atual."""
