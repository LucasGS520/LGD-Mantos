from typing import Literal

from app.core.auth import verify_token
from app.core.database import get_db
from fastapi import APIRouter, Depends, Header, Query

from . import queries, service
from .repository import operations as list_operations
from .repository import page
from .schemas import ConfirmIn, OperationIn

router = APIRouter(dependencies=[Depends(verify_token)])


@router.get("/state")
async def state(db=Depends(get_db)):
    return await queries.state(db)


@router.get("/operations")
async def operations(
    kind: Literal["inventory", "purchase", "sale", "adjustment"] | None = None,
    limit: int | None = Query(default=None, ge=1, le=100),
    before_sequence: int | None = Query(default=None, ge=1),
    db=Depends(get_db),
):
    if limit is not None or kind is not None or before_sequence is not None:
        return await page(db, kind, limit or 50, before_sequence)
    return await list_operations(db)


@router.get("/operations/{entity_id}")
async def operation(entity_id: str, db=Depends(get_db)):
    return await queries.detail(db, entity_id)


@router.post("/operations/preview")
async def preview(data: OperationIn, db=Depends(get_db)):
    return await service.preview(db, data)


@router.post("/operations")
async def confirm(
    data: ConfirmIn, idempotency_key: str = Header(min_length=1, max_length=100), db=Depends(get_db)
):
    return await service.confirm(db, data.data, data.preview_token, idempotency_key)


@router.post("/operations/{entity_id}/preview")
async def preview_edit(entity_id: str, data: OperationIn, db=Depends(get_db)):
    return await service.preview(db, data, entity_id)


@router.put("/operations/{entity_id}")
async def confirm_edit(
    entity_id: str,
    data: ConfirmIn,
    idempotency_key: str = Header(min_length=1, max_length=100),
    db=Depends(get_db),
):
    return await service.confirm(db, data.data, data.preview_token, idempotency_key, entity_id)
