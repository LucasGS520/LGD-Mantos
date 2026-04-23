from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings
from app.core.auth import create_token

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginIn(BaseModel):
    password: str

@router.post("/login")
async def login(data: LoginIn):
    if data.password != settings.APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    return {"token": create_token()}
