"""Serviço de recuperação de contexto de marca para os agentes.

Responsabilidade: buscar documentos de conhecimento relevantes e montar
o bloco de contexto textual que será injetado nos prompts dos agentes.

Regra: este serviço não chama LLM. É recuperação determinística de texto.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.knowledge.models import KnowledgeDocument


class KnowledgeService:
    """Recupera contexto de marca da Knowledge Layer para injeção nos agentes."""

    @staticmethod
    async def get_by_type(db: AsyncSession, doc_type: str) -> list[KnowledgeDocument]:
        """Retorna todos os documentos ativos de um tipo específico."""
        result = await db.execute(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.doc_type == doc_type)
            .where(KnowledgeDocument.is_active == True)
            .order_by(KnowledgeDocument.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_brand_context(db: AsyncSession) -> str:
        """Monta bloco textual de contexto de marca para injeção em agentes.

        Reúne brand_voice, persona e commercial_rules — o contexto mínimo
        necessário para que qualquer agente gere conteúdo alinhado à marca.
        """
        priority_types = ["brand_voice", "persona", "commercial_rules"]
        parts: list[str] = []

        for doc_type in priority_types:
            docs = await KnowledgeService.get_by_type(db, doc_type)
            if docs:
                parts.append(f"## {doc_type.replace('_', ' ').upper()}")
                for doc in docs:
                    parts.append(f"### {doc.title}\n{doc.content}")

        if not parts:
            return "Contexto de marca ainda não configurado. Adicione documentos na Knowledge Layer."

        return "\n\n".join(parts)

    @staticmethod
    async def get_strategy_context(db: AsyncSession) -> str:
        """Contexto estendido para o StrategyAgent — inclui campaign_context."""
        brand = await KnowledgeService.get_brand_context(db)
        campaign_docs = await KnowledgeService.get_by_type(db, "campaign_context")

        parts = [brand]
        if campaign_docs:
            parts.append("## CONTEXTOS DE CAMPANHA APROVADOS")
            for doc in campaign_docs[:3]:
                parts.append(f"### {doc.title}\n{doc.content}")

        return "\n\n".join(parts)

    @staticmethod
    async def get_creative_context(db: AsyncSession) -> str:
        """Contexto estendido para o CreativeAgent — inclui referências visuais e estilos."""
        brand = await KnowledgeService.get_brand_context(db)
        visual_docs = await KnowledgeService.get_by_type(db, "visual_reference")
        style_docs = await KnowledgeService.get_by_type(db, "product_style_notes")
        approved_prompts = await KnowledgeService.get_by_type(db, "approved_prompt")

        parts = [brand]
        for doc_type, docs, label in [
            ("visual_reference", visual_docs, "REFERÊNCIAS VISUAIS"),
            ("product_style_notes", style_docs, "NOTAS DE ESTILO DE PRODUTO"),
            ("approved_prompt", approved_prompts[:3], "PROMPTS APROVADOS ANTERIORES"),
        ]:
            if docs:
                parts.append(f"## {label}")
                for doc in docs:
                    parts.append(f"### {doc.title}\n{doc.content}")

        return "\n\n".join(parts)
