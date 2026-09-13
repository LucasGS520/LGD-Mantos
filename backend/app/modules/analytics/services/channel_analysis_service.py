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
    ) -> list[dict] | dict:
        """Vendas agrupadas por canal.

        Sem `compare`, devolve a mesma lista de sempre — contrato preservado
        byte a byte. Com `compare=True`, a resposta muda de forma (lista vira
        objeto) só nesse caso: `{"channels": [...mesma lista...], "comparacao":
        {<canal>: {"total": Comparado, "count": Comparado}}}`. Os nomes
        "total"/"count" (não "revenue"/"qty") seguem os campos reais que este
        método já devolve para cada canal.
        """
        start, end = resolve_period(period, days)
        rows = await sales_repo.sales_by_channel(db, start, end)
        channels = [{"channel": row[0], "count": int(row[1]), "total": float(row[2] or 0)} for row in rows]

        if not compare:
            return channels

        _, (inicio_anterior, fim_anterior) = resolve_comparison_period(period, days)
        rows_ant = await sales_repo.sales_by_channel(db, inicio_anterior, fim_anterior)
        atual_por_canal = {row[0]: (int(row[1]), float(row[2] or 0)) for row in rows}
        anterior_por_canal = {row[0]: (int(row[1]), float(row[2] or 0)) for row in rows_ant}

        comparacao = {}
        for nome_canal in atual_por_canal.keys() | anterior_por_canal.keys():
            count_atual, total_atual = atual_por_canal.get(nome_canal, (0, 0.0))
            count_ant, total_ant = anterior_por_canal.get(nome_canal, (0, 0.0))
            comparacao[nome_canal] = {
                "total": Comparado.de(total_atual, total_ant).model_dump(),
                "count": Comparado.de(count_atual, count_ant).model_dump(),
            }

        return {"channels": channels, "comparacao": comparacao}
