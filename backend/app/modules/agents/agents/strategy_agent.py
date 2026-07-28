"""StrategyAgent — transforma oportunidades de dados em estratégia de campanha.

Recebe as oportunidades selecionadas pelo DataAgent e o contexto de marca da
Knowledge Layer. Produz uma estratégia de campanha estruturada.

Regras:
- Define um único produto principal por campanha.
- Não cria desconto automático. Preço e desconto são decisão humana.
- Não promete disponibilidade sem confirmar com o DataAgent.
- Output sempre em português brasileiro.
"""

from agno.agent import Agent

from app.modules.agents.agents.schemas import DataAgentOutput, StrategyAgentOutput
from app.modules.agents.config import get_agent_model

_INSTRUCTIONS = [
    "Você é o StrategyAgent da LGD Mantos, uma loja de mantos e roupas esportivas.",
    "Sua função é criar uma estratégia concreta de campanha de marketing baseada nas oportunidades identificadas.",
    "Defina: produto principal, canal, formato, ângulo de venda, CTA e nível de risco.",
    "Nunca crie descontos automáticos. Preço e promoção são decisão exclusiva do usuário humano.",
    "Nunca prometa estoque ou tamanho que não foi confirmado pelos dados.",
    "O ângulo de venda deve ser genuíno — baseado no que os dados mostram sobre o produto.",
    "Escolha o canal mais adequado ao produto e ao momento (Instagram para visuais, WhatsApp para urgência, etc.).",
    "O campo product_sku deve ser copiado EXATAMENTE, caractere por caractere, do SKU da oportunidade escolhida. Nunca invente, reordene ou altere um SKU.",
    "O campo format deve conter APENAS o nome curto do formato (feed, story, reels, carrossel ou combinação breve) — nunca uma descrição ou frase. O campo channel deve ser só o nome do canal (Instagram, WhatsApp, TikTok).",
    "Sempre responda em português brasileiro.",
]


def build_strategy_agent() -> Agent:
    """Cria uma instância fresca do StrategyAgent para cada run."""
    return Agent(
        name="strategy-agent",
        model=get_agent_model(),
        description="Transforma oportunidades de dados em estratégia de campanha de marketing para a LGD Mantos.",
        instructions=_INSTRUCTIONS,
        output_schema=StrategyAgentOutput,
        markdown=False,
    )


def build_strategy_agent_input(
    objective: str,
    data_output: DataAgentOutput,
    brand_context: str,
    valid_skus: list[str] | None = None,
) -> str:
    """Monta o payload de entrada para o StrategyAgent.

    `valid_skus` vem do catálogo real (consultado pelo Supervisor) e é incluído
    no prompt como lista fechada — reduz alucinação de SKU pelo LLM.
    """

    primary = data_output.primary
    primary_block = ""
    if primary:
        primary_block = f"""
OPORTUNIDADE PRINCIPAL RECOMENDADA:
- Produto: {primary.product_name} (SKU: {primary.sku})
- Tipo: {primary.opportunity_type}
- Estoque: {primary.stock} unidades
- Vendido nos últimos 30 dias: {primary.sold_30d} unidades
- Margem: {primary.margin_pct:.1f}%
- Motivo: {primary.reason}
"""

    other_opportunities = [o for o in data_output.opportunities if o != primary][:4]
    other_block = ""
    if other_opportunities:
        other_block = "\nOUTRAS OPORTUNIDADES DISPONÍVEIS:\n"
        for op in other_opportunities:
            other_block += f"- {op.product_name} ({op.sku}): {op.opportunity_type} — {op.reason}\n"

    skus_block = ""
    if valid_skus:
        skus_block = (
            "\nSKUS VÁLIDOS DO CATÁLOGO (o campo product_sku DEVE ser exatamente um destes):\n"
            + "\n".join(f"- {sku}" for sku in valid_skus)
            + "\n"
        )

    return f"""OBJETIVO DA CAMPANHA:
{objective}

RESUMO DO PANORAMA (DataAgent):
{data_output.summary}
{primary_block}{other_block}{skus_block}

CONTEXTO DE MARCA (Knowledge Layer):
{brand_context}

Com base no objetivo, nas oportunidades identificadas e no contexto de marca,
crie uma estratégia completa para a campanha.
Defina produto, canal, formato, ângulo de venda, CTA e nível de risco."""
