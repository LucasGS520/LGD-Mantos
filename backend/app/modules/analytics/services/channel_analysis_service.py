"""Análise de canais de venda e distribuição por tamanho."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo


class ChannelAnalysisService:
    @staticmethod
    async def sales_by_size(db: AsyncSession, days: int) -> list[dict]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await product_repo.sales_by_size(db, since)
        return [{"size": row[0], "qty": int(row[1] or 0)} for row in rows]

    @staticmethod
    async def sales_by_channel(db: AsyncSession, days: int) -> list[dict]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await sales_repo.sales_by_channel(db, since)
        return [{"channel": row[0], "count": int(row[1]), "total": float(row[2] or 0)} for row in rows]
