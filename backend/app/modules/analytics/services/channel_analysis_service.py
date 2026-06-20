"""Análise de canais de venda e distribuição por tamanho."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo
from app.modules.analytics.utils import resolve_period


class ChannelAnalysisService:
    @staticmethod
    async def sales_by_size(db: AsyncSession, period: str | None = None, days: int = 30) -> list[dict]:
        start, end = resolve_period(period, days)
        rows = await product_repo.sales_by_size(db, start, end)
        return [{"size": row[0], "qty": int(row[1] or 0)} for row in rows]

    @staticmethod
    async def sales_by_channel(db: AsyncSession, period: str | None = None, days: int = 30) -> list[dict]:
        start, end = resolve_period(period, days)
        rows = await sales_repo.sales_by_channel(db, start, end)
        return [{"channel": row[0], "count": int(row[1]), "total": float(row[2] or 0)} for row in rows]
