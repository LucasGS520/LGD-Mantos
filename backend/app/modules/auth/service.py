"""Acesso do proprietário com comparação constante de senha."""

import hmac

from app.core.auth import create_token
from app.core.config import settings
from app.shared.application.errors import ApplicationError

from .attempts import LoginAttempts

attempts = LoginAttempts()


def login(password: str):
    if not attempts.allowed():
        raise ApplicationError(
            429, "Muitas tentativas. Aguarde um minuto antes de tentar novamente."
        )
    if not hmac.compare_digest(password.encode(), settings.APP_PASSWORD.encode()):
        attempts.failed()
        raise ApplicationError(401, "Senha incorreta")
    return {"token": create_token()}
