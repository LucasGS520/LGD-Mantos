"""Borda pública de disponibilidade do sistema."""

from fastapi import APIRouter, Depends, Response

from app.core.database import get_db

from . import service

router = APIRouter(tags=["system"])


@router.get("/health")
async def health(response: Response, db=Depends(get_db)):
    result = await service.health(db)
    response.status_code = 200 if result["database"] == "ok" else 503
    return result
