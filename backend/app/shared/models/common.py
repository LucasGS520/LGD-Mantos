"""Utilitários comuns para modelos persistidos no banco."""

import uuid
from datetime import datetime, timezone


def uid() -> str:
    """Gera um identificador UUID textual para chaves primárias."""

    return str(uuid.uuid4())


def now() -> datetime:
    """Retorna o horário atual em UTC para campos de auditoria."""

    return datetime.now(timezone.utc)
