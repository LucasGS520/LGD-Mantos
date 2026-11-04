from fastapi import APIRouter, HTTPException
import hmac

from app.core.auth import create_token
from app.core.config import settings
from app.modules.auth.schemas import LoginIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(data: LoginIn):
    if not hmac.compare_digest(data.password.encode(), settings.APP_PASSWORD.encode()):
        raise HTTPException(status_code=401, detail="Senha incorreta")
    return {"token": create_token()}
