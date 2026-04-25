"""Funções simples de autenticação baseada em token JWT."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from app.core.config import settings

bearer = HTTPBearer()

def create_token() -> str:
    """Cria um token de acesso para o usuário proprietário do sistema."""

    exp = datetime.now(timezone.utc) + timedelta(days=30)
    return jwt.encode({"sub": "owner", "exp": exp}, settings.APP_SECRET, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """Valida o token enviado no cabeçalho Authorization das rotas protegidas."""

    try:
        jwt.decode(credentials.credentials, settings.APP_SECRET, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Não autorizado")
