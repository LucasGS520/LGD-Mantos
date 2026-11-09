from datetime import date
from typing import Literal

from app.core.auth import verify_token
from app.core.database import get_read_db
from fastapi import APIRouter, Depends, Query

from .service import report as get_report

router = APIRouter(dependencies=[Depends(verify_token)])


@router.get("/analytics")
async def report(
    start: date | None = None,
    end: date | None = None,
    view: Literal["overview", "stock", "sales", "receipts", "purchases", "buying"] | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    supplier: str | None = None,
    sort: Literal[
        "stock", "days_since_first_entry", "days_since_last_sale", "stock_value"
    ] = "stock",
    db=Depends(get_read_db),
):
    return await get_report(db, start, end, view, offset, limit, supplier, sort)
