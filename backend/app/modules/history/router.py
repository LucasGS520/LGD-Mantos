from app.core.auth import verify_token
from app.core.database import get_db
from fastapi import APIRouter, Depends

from .repository import history as get_history
from .repository import movements as get_movements

router = APIRouter(dependencies=[Depends(verify_token)])


@router.get("/history/{entity_id}")
async def history(entity_id: str, db=Depends(get_db)):
    return await get_history(db, entity_id)


@router.get("/movements")
async def movements(operation_id: str | None = None, db=Depends(get_db)):
    return await get_movements(db, operation_id)
