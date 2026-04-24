"""Serviços centrais de IA reutilizados por APIs de IA e marketing."""

from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from modules.shared.models import Expense, Product, ProductVariant, Sale, SaleItem

SYSTEM_PROMPT = """Você é um assistente especializado exclusivamente na gestão desta loja de roupas brasileira que vende camisetas oversized e peruanas.

Seu papel é:
1. Ajudar na análise de vendas, estoque e decisões de compra
2. Criar descrições de produtos para Instagram, WhatsApp e site
3. Sugerir ideias de marketing, postagens e campanhas
4. Orientar sobre workflow de fotos de produto
5. Dar insights sobre quais produtos/tamanhos comprar mais
6. Auxiliar no copywriting de posts e legendas

Você responde SEMPRE em português brasileiro, de forma direta e prática.
Para descrições, escreva no estilo casual e engajante de e-commerce de moda brasileiro.
Para análises, seja objetivo com números e recomendações claras.
"""


async def build_context(db: AsyncSession, mode: str) -> str:
    """Monta contexto da loja para enriquecer os prompts enviados ao modelo."""
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=30)
    ctx_parts: list[str] = []

    if mode in ("geral", "analise", "compras"):
        r = await db.execute(
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
        rows = r.all()
        if rows:
            ctx_parts.append("VENDAS DOS ÚLTIMOS 30 DIAS (top 10 variantes):")
            for row in rows:
                ctx_parts.append(f"  - {row[0]} / {row[1]} / {row[2]}: {int(row[3])} unidades")

        sa = await db.execute(
            select(Product.name, ProductVariant.size, ProductVariant.color, ProductVariant.stock_quantity)
            .join(Product)
            .where(ProductVariant.stock_quantity <= ProductVariant.min_stock_alert)
        )
        alerts = sa.all()
        if alerts:
            ctx_parts.append("\nESTOQUE CRÍTICO (abaixo do mínimo):")
            for a in alerts:
                ctx_parts.append(f"  - {a[0]} / {a[1]} / {a[2]}: {a[3]} unidades")

    if mode in ("geral", "descricao", "marketing"):
        pr = await db.execute(
            select(Product).where(Product.is_active == True).order_by(Product.created_at.desc()).limit(10)
        )
        products = pr.scalars().all()
        if products:
            ctx_parts.append("\nPRODUTOS ATIVOS (recentes):")
            for p in products:
                ctx_parts.append(
                    f"  - {p.name} (SKU: {p.sku}) | Venda: R${float(p.sale_price):.2f} | {p.description or 'sem descrição'}"
                )

    return "\n".join(ctx_parts) if ctx_parts else "Loja com dados iniciais — sem histórico de vendas ainda."


async def generate_ai_response(message: str, db: AsyncSession, mode: str = "geral") -> str:
    """Envia requisição ao provedor de IA com contexto e retorna a resposta textual."""
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("sk-ant-sua"):
        return "⚠️ Configure sua ANTHROPIC_API_KEY no arquivo .env para usar o assistente de IA."

    context = await build_context(db, mode)
    user_msg = f"{context}\n\n---\nPergunta/solicitação: {message}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
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
                    "messages": [{"role": "user", "content": user_msg}],
                },
            )
        data = r.json()
        if r.status_code != 200:
            raise HTTPException(500, data.get("error", {}).get("message", "Erro na API"))
        return data["content"][0]["text"]
    except httpx.TimeoutException as exc:
        raise HTTPException(504, "Timeout na API de IA") from exc
