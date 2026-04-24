"""Repositório de despesas para consultas e manutenção de lançamentos."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.shared.models import Expense


class ExpenseRepository:
    """Camada de persistência das despesas operacionais."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_expenses(self, limit: int = 200) -> list[Expense]:
        """Retorna despesas ordenadas da mais recente para mais antiga."""
        result = await self.db.execute(select(Expense).order_by(Expense.date.desc()).limit(limit))
        return list(result.scalars().all())

    async def create_expense(self, expense: Expense) -> None:
        """Adiciona uma nova despesa no contexto transacional."""
        self.db.add(expense)

    async def get_expense_by_id(self, expense_id: str) -> Expense | None:
        """Busca despesa por identificador."""
        result = await self.db.execute(select(Expense).where(Expense.id == expense_id))
        return result.scalar_one_or_none()

    async def delete_expense(self, expense: Expense) -> None:
        """Remove despesa da sessão atual."""
        await self.db.delete(expense)
