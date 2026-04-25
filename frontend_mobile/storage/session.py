"""Persistência local do token de sessão do app mobile."""

import base64
import json
import time
from pathlib import Path


class SessionStore:
    """Salva, carrega e valida superficialmente o token JWT da sessão."""

    def __init__(self, filename: str = ".lgd_mantos_session.json"):
        """Define o arquivo local usado para guardar a sessão."""

        self.path = Path.home() / filename

    def load_token(self) -> str | None:
        """Carrega o token salvo, se existir e puder ser lido."""

        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data.get("token")
        except Exception:
            return None

    def save_token(self, token: str) -> None:
        """Persiste o token retornado pelo backend após login."""

        self.path.write_text(json.dumps({"token": token}), encoding="utf-8")

    def clear(self) -> None:
        """Remove a sessão local."""

        if self.path.exists():
            self.path.unlink()

    def is_valid(self) -> bool:
        """Verifica se existe token e se a expiração JWT ainda não passou."""

        token = self.load_token()
        if not token:
            return False
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return False
            # base64url decode com padding
            payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))
            exp = payload.get("exp")
            if exp is None:
                return True
            return time.time() < exp
        except Exception:
            return False
