"""Borda pública de disponibilidade do sistema."""

from fastapi import APIRouter, Depends

from app.core.database import get_db

from . import service

router = APIRouter(tags=["system"])


@router.get("/health")
async def health(db=Depends(get_db)):
    return await service.health(db)
