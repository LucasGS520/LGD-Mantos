from fastapi import APIRouter, HTTPException

from app.core.auth import create_token
from app.core.config import settings
from app.modules.auth.schemas import LoginIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(data: LoginIn):
    if data.password != settings.APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    return {"token": create_token()}
