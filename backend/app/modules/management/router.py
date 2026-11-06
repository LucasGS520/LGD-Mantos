from datetime import date

from app.core.auth import verify_token
from app.core.database import get_db
from fastapi import APIRouter, Depends

from .service import report as get_report

router = APIRouter(dependencies=[Depends(verify_token)])


@router.get("/analytics")
async def report(start: date | None = None, end: date | None = None, db=Depends(get_db)):
    return await get_report(db, start, end)
