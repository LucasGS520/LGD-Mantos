"""Análise de canais de venda e distribuição por tamanho."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo
from app.modules.analytics.schemas.comparacao import Comparado
from app.modules.analytics.utils import resolve_comparison_period, resolve_period


class ChannelAnalysisService:
    @staticmethod
    async def sales_by_size(db: AsyncSession, period: str | None = None, days: int = 30) -> list[dict]:
        start, end = resolve_period(period, days)
        rows = await product_repo.sales_by_size(db, start, end)
        return [{"size": row[0], "qty": int(row[1] or 0)} for row in rows]

    @staticmethod
    async def sales_by_channel(
        db: AsyncSession, period: str | None = None, days: int = 30, compare: bool = False
    ) -> list[dict]:
        """Vendas agrupadas por canal.

        Sempre devolve uma lista — sem `compare`, idêntica à de sempre. Com
        `compare=True`, cada item ganha uma chave `comparacao` com os
        indicadores daquele canal ("total"/"count", os nomes reais que este
        método já usa) frente ao período anterior. Um canal que só vendeu no
        período anterior continua aparecendo na lista, com `count`/`total`
        zerados — removê-lo esconderia justamente a informação mais relevante
        (um canal que parou de vender).
        """
        start, end = resolve_period(period, days)
        rows = await sales_repo.sales_by_channel(db, start, end)
        channels = [{"channel": row[0], "count": int(row[1]), "total": float(row[2] or 0)} for row in rows]

        if not compare:
            return channels

        _, (inicio_anterior, fim_anterior) = resolve_comparison_period(period, days)
        rows_ant = await sales_repo.sales_by_channel(db, inicio_anterior, fim_anterior)
        anterior_por_canal = {row[0]: (int(row[1]), float(row[2] or 0)) for row in rows_ant}
        atual_por_canal = {item["channel"]: item for item in channels}

        for nome_canal, (count_ant, total_ant) in anterior_por_canal.items():
            if nome_canal not in atual_por_canal:
                novo = {"channel": nome_canal, "count": 0, "total": 0.0}
                channels.append(novo)
                atual_por_canal[nome_canal] = novo

        for item in channels:
            count_ant, total_ant = anterior_por_canal.get(item["channel"], (0, 0.0))
            item["comparacao"] = {
                "total": Comparado.de(item["total"], total_ant).model_dump(),
                "count": Comparado.de(item["count"], count_ant).model_dump(),
            }

        return channels
