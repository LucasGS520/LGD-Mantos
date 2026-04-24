"""Serviço de despesas com regras simples e fluxo transacional."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operational.repositories import ExpenseRepository
from modules.shared.models import Expense
from modules.shared.schemas import ExpenseIn


class ExpenseService:
    """Responsável pela manutenção de despesas operacionais."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = ExpenseRepository(db)

    async def list_expenses(self) -> list[Expense]:
        """Lista despesas em ordem decrescente de data."""
        return await self.repository.list_expenses()

    async def create_expense(self, data: ExpenseIn) -> Expense:
        """Cria despesa com commit controlado por serviço."""
        expense = Expense(**data.model_dump())
        await self.repository.create_expense(expense)

        try:
            await self.db.flush()
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        return expense

    async def delete_expense(self, expense_id: str) -> None:
        """Remove despesa existente por identificador."""
        expense = await self.repository.get_expense_by_id(expense_id)
        if not expense:
            raise HTTPException(404)

        try:
            await self.repository.delete_expense(expense)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
