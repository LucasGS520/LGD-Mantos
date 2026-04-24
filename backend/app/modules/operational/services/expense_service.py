from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operational import repositories as repo
from app.shared.models.operations import Expense
from app.shared.schemas.operations import ExpenseIn


class ExpenseService:
    @staticmethod
    async def create_expense(db: AsyncSession, data: ExpenseIn) -> Expense:
        expense = Expense(**data.model_dump())
        db.add(expense)
        await db.flush()
        return expense

    @staticmethod
    async def delete_expense(db: AsyncSession, expense_id: str) -> dict:
        expense = await repo.get_expense(db, expense_id)
        if not expense:
            raise HTTPException(404, "Despesa nao encontrada")
        await db.delete(expense)
        return {"ok": True}
