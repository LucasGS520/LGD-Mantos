"""Contrato HTTP de acesso do proprietário."""

from fastapi import APIRouter

from . import service
from .schemas import LoginIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(data: LoginIn):
    return service.login(data.password)
