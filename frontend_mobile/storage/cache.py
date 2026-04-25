"""Cache local simples com tempo de expiração para telas do app."""

import json
import time
from pathlib import Path


class LocalCache:
    """Armazena respostas da API em JSON para melhorar carregamento e modo degradado."""

    def __init__(self, filename: str = ".lgd_mantos_cache.json"):
        """Define o arquivo local que guarda todas as entradas de cache."""

        self.path = Path.home() / filename

    def _load_all(self) -> dict:
        """Carrega o cache completo, retornando vazio se não existir ou estiver inválido."""

        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_all(self, data: dict) -> None:
        """Persiste o cache completo ignorando falhas locais de escrita."""

        try:
            self.path.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass

    def set(self, key: str, data, ttl_seconds: int) -> None:
        """Salva uma entrada com tempo de vida em segundos."""

        all_data = self._load_all()
        all_data[key] = {"data": data, "expires_at": time.time() + ttl_seconds}
        self._save_all(all_data)

    def get(self, key: str):
        """Retorna `(data, is_stale)`; `data` é None se a chave nunca foi salva."""

        entry = self._load_all().get(key)
        if entry is None:
            return None, False
        is_stale = time.time() > entry["expires_at"]
        return entry["data"], is_stale

    def invalidate(self, key: str) -> None:
        """Remove uma entrada específica do cache."""

        all_data = self._load_all()
        if key in all_data:
            del all_data[key]
            self._save_all(all_data)

    def clear(self) -> None:
        """Apaga todo o arquivo de cache local."""

        if self.path.exists():
            self.path.unlink()
