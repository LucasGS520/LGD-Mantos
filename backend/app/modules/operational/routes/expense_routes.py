from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.operational import repositories as repo
from backend.app.modules.operational.services.expense_service import ExpenseService
from app.shared.schemas.operations import ExpenseIn, ExpenseOut

router = APIRouter(tags=["operational"])


@router.get("/expenses", response_model=list[ExpenseOut])
async def list_expenses(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await repo.list_expenses(db)


@router.post("/expenses", response_model=ExpenseOut)
async def create_expense(data: ExpenseIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await ExpenseService.create_expense(db, data)


@router.delete("/expenses/{eid}")
async def delete_expense(eid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await ExpenseService.delete_expense(db, eid)
