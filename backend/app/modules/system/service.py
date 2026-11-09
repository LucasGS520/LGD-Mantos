"""Estado público de disponibilidade, sem expor detalhes da infraestrutura."""

from datetime import datetime, timezone

from app.core.version import API_VERSION

from .repository import database_status


async def health(db):
    database = await database_status(db)
    return {
        "status": "ok" if database == "ok" else "error",
        "version": API_VERSION,
        "database": database,
        "server_time": datetime.now(timezone.utc).isoformat(),
    }
