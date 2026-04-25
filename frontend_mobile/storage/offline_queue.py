"""Fila local para comandos que podem ser reenviados quando houver conexão."""

import json
import time
import uuid
from pathlib import Path

ELIGIBLE_COMMANDS = {"create_product", "create_sale"}


class OfflineQueue:
    """Persiste comandos offline em JSON no diretório do usuário."""

    def __init__(self, filename: str = ".lgd_mantos_queue.json"):
        """Define o arquivo local usado para armazenar a fila."""

        self.path = Path.home() / filename

    def _load(self) -> list:
        """Carrega todos os itens da fila, retornando lista vazia se houver erro."""

        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save(self, items: list) -> None:
        """Salva a fila inteira ignorando falhas de escrita locais."""

        try:
            self.path.write_text(json.dumps(items, default=str), encoding="utf-8")
        except Exception:
            pass

    def enqueue(self, command_type: str, payload: dict) -> str:
        """Adiciona um comando elegível à fila e retorna seu id local."""

        if command_type not in ELIGIBLE_COMMANDS:
            raise ValueError(f"Comando '{command_type}' nao elegivel para fila offline.")
        item = {
            "local_id": str(uuid.uuid4()),
            "command_type": command_type,
            "payload": payload,
            "created_at": time.time(),
            "attempts": 0,
            "status": "pending",
            "error_reason": None,
        }
        items = self._load()
        items.append(item)
        self._save(items)
        return item["local_id"]

    def get_pending(self) -> list:
        """Retorna apenas comandos ainda pendentes de sincronização."""

        return [i for i in self._load() if i["status"] == "pending"]

    def get_all(self) -> list:
        """Retorna todos os comandos salvos, independentemente do status."""

        return self._load()

    def mark_done(self, local_id: str) -> None:
        """Marca um comando como sincronizado com sucesso."""

        self._update(local_id, {"status": "done"})

    def mark_rejected(self, local_id: str, reason: str) -> None:
        """Marca um comando como rejeitado e guarda o motivo."""

        self._update(local_id, {"status": "rejected", "error_reason": reason})

    def increment_attempts(self, local_id: str) -> None:
        """Incrementa a contagem de tentativas após falha temporária."""

        items = self._load()
        for item in items:
            if item["local_id"] == local_id:
                item["attempts"] += 1
                break
        self._save(items)

    def _update(self, local_id: str, fields: dict) -> None:
        """Atualiza campos de um item específico da fila."""

        items = self._load()
        for item in items:
            if item["local_id"] == local_id:
                item.update(fields)
                break
        self._save(items)
