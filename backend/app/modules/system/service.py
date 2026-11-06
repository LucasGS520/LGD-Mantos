"""Estado público de disponibilidade, sem expor detalhes da infraestrutura."""

from datetime import datetime, timezone

from app.core.version import API_VERSION

from .repository import database_status


async def health(db):
    return {
        "status": "ok",
        "version": API_VERSION,
        "database": await database_status(db),
        "server_time": datetime.now(timezone.utc).isoformat(),
    }
