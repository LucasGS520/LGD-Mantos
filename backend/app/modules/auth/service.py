"""Acesso do proprietário com comparação constante de senha."""

import hmac

from app.core.auth import create_token
from app.core.config import settings
from app.shared.application.errors import ApplicationError


def login(password: str):
    if not hmac.compare_digest(password.encode(), settings.APP_PASSWORD.encode()):
        raise ApplicationError(401, "Senha incorreta")
    return {"token": create_token()}
