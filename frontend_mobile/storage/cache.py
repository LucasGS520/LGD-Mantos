import json
import time
from pathlib import Path


class LocalCache:
    def __init__(self, filename: str = ".lgd_mantos_cache.json"):
        self.path = Path.home() / filename

    def _load_all(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_all(self, data: dict) -> None:
        try:
            self.path.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass

    def set(self, key: str, data, ttl_seconds: int) -> None:
        all_data = self._load_all()
        all_data[key] = {"data": data, "expires_at": time.time() + ttl_seconds}
        self._save_all(all_data)

    def get(self, key: str):
        """Returns (data, is_stale). data is None if key never cached."""
        entry = self._load_all().get(key)
        if entry is None:
            return None, False
        is_stale = time.time() > entry["expires_at"]
        return entry["data"], is_stale

    def invalidate(self, key: str) -> None:
        all_data = self._load_all()
        if key in all_data:
            del all_data[key]
            self._save_all(all_data)

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
