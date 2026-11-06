from app.core.auth import verify_token
from app.core.database import get_db
from fastapi import APIRouter, Depends

from . import service
from .common.repository import list_all
from .schemas import AuxiliaryIn

router = APIRouter(dependencies=[Depends(verify_token)])


@router.get("/auxiliaries")
async def auxiliaries(db=Depends(get_db)):
    return await list_all(db)


@router.post("/auxiliaries")
async def create_auxiliary(data: AuxiliaryIn, db=Depends(get_db)):
    return await service.save(db, data)


@router.put("/auxiliaries/{entity_id}")
async def edit_auxiliary(entity_id: str, data: AuxiliaryIn, db=Depends(get_db)):
    return await service.save(db, data, entity_id)
