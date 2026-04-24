import json
from pathlib import Path


class SessionStore:
    def __init__(self, filename: str = ".lgd_mantos_session.json"):
        self.path = Path.home() / filename

    def load_token(self) -> str | None:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data.get("token")
        except Exception:
            return None

    def save_token(self, token: str) -> None:
        self.path.write_text(json.dumps({"token": token}), encoding="utf-8")

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
