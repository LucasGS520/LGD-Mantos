"""Serviços de negócio para despesas operacionais."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operational import repositories as repo
from app.shared.models.operations import Expense
from app.shared.schemas.operations import ExpenseIn


class ExpenseService:
    """Cria e remove despesas usadas nos controles financeiros."""

    @staticmethod
    async def create_expense(db: AsyncSession, data: ExpenseIn) -> Expense:
        """Registra uma despesa operacional."""

        expense = Expense(**data.model_dump())
        db.add(expense)
        await db.flush()
        return expense

    @staticmethod
    async def update_expense(db: AsyncSession, expense_id: str, data: ExpenseIn) -> Expense:
        """Atualiza campos de uma despesa existente."""

        expense = await repo.get_expense(db, expense_id)
        if not expense:
            raise HTTPException(404, "Despesa nao encontrada")
        for k, v in data.model_dump().items():
            setattr(expense, k, v)
        db.add(expense)
        await db.flush()
        return expense

    @staticmethod
    async def delete_expense(db: AsyncSession, expense_id: str) -> dict:
        """Remove uma despesa existente pelo identificador."""

        expense = await repo.get_expense(db, expense_id)
        if not expense:
            raise HTTPException(404, "Despesa nao encontrada")
        await db.delete(expense)
        return {"ok": True}
