from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.shared.models.catalog import Product, ProductVariant
from app.shared.models.operations import Sale, SaleItem


SYSTEM_PROMPT = """Voce e um assistente especializado exclusivamente na gestao da loja LGD Mantos.

Regras permanentes:
1. Responda sempre em portugues brasileiro, de forma direta e pratica.
2. Use dados da loja somente para apoiar decisoes humanas.
3. Nao afirme que alterou estoque, vendas, compras, produtos ou despesas.
4. Quando sugerir uma acao operacional, deixe claro que o usuario precisa confirmar e registrar no sistema.
5. Para marketing, escreva com energia comercial, mas sem prometer disponibilidade que os dados nao mostrem.
6. Para analises, destaque numeros, padroes e recomendacoes objetivas.
"""


class AIService:
    @staticmethod
    async def generate(
        db: AsyncSession,
        message: str,
        mode: str = "geral",
        module: str = "core",
        context_ids: list[str] | None = None,
    ) -> dict:
        if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("sk-ant-sua"):
            return {
                "response": "Configure sua ANTHROPIC_API_KEY no arquivo .env para usar o assistente de IA.",
                "mode": mode,
                "module": module,
            }

        context = await AIService.build_context(db, mode, module, context_ids or [])
        user_message = f"{context}\n\n---\nModulo: {module}\nModo: {mode}\nSolicitacao: {message}"

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": settings.ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-opus-4-5",
                        "max_tokens": 1024,
                        "system": SYSTEM_PROMPT,
                        "messages": [{"role": "user", "content": user_message}],
                    },
                )
            data = response.json()
            if response.status_code != 200:
                raise HTTPException(500, data.get("error", {}).get("message", "Erro na API de IA"))
            return {"response": data["content"][0]["text"], "mode": mode, "module": module}
        except httpx.TimeoutException:
            raise HTTPException(504, "Timeout na API de IA")

    @staticmethod
    async def build_context(
        db: AsyncSession,
        mode: str,
        module: str,
        context_ids: list[str],
    ) -> str:
        now = datetime.now(timezone.utc)
        since = now - timedelta(days=30)
        parts = [f"CONTEXTO DO MODULO: {module}"]

        if mode in ("geral", "analise", "compras", "marketing", "campanha"):
            rows = await AIService._top_variants(db, since)
            if rows:
                parts.append("VENDAS DOS ULTIMOS 30 DIAS (top 10 variantes):")
                for row in rows:
                    parts.append(f"- {row[0]} / {row[1]} / {row[2]}: {int(row[3])} unidades")

            alerts = await AIService._low_stock(db)
            if alerts:
                parts.append("ESTOQUE CRITICO:")
                for alert in alerts:
                    parts.append(f"- {alert[0]} / {alert[1]} / {alert[2]}: {alert[3]} unidades")

        if mode in ("geral", "descricao", "marketing", "campanha", "social"):
            products = await AIService._recent_products(db, context_ids)
            if products:
                parts.append("PRODUTOS ATIVOS/REFERENCIADOS:")
                for product in products:
                    parts.append(
                        f"- {product.name} (SKU: {product.sku}) | Venda: R${float(product.sale_price):.2f} | "
                        f"{product.description or 'sem descricao'}"
                    )

        if len(parts) == 1:
            parts.append("Loja com dados iniciais, sem historico suficiente para contexto detalhado.")
        return "\n".join(parts)

    @staticmethod
    async def _top_variants(db: AsyncSession, since: datetime):
        result = await db.execute(
            select(
                Product.name,
                ProductVariant.size,
                ProductVariant.color,
                func.sum(SaleItem.quantity).label("qty"),
            )
            .join(ProductVariant, SaleItem.variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .where(Sale.sold_at >= since)
            .group_by(Product.name, ProductVariant.size, ProductVariant.color)
            .order_by(func.sum(SaleItem.quantity).desc())
            .limit(10)
        )
        return result.all()

    @staticmethod
    async def _low_stock(db: AsyncSession):
        result = await db.execute(
            select(Product.name, ProductVariant.size, ProductVariant.color, ProductVariant.stock_quantity)
            .join(Product)
            .where(ProductVariant.stock_quantity <= ProductVariant.min_stock_alert)
        )
        return result.all()

    @staticmethod
    async def _recent_products(db: AsyncSession, context_ids: list[str]):
        query = select(Product).where(Product.is_active == True)
        if context_ids:
            query = query.where(Product.id.in_(context_ids))
        result = await db.execute(query.order_by(Product.created_at.desc()).limit(10))
        return list(result.scalars().all())
