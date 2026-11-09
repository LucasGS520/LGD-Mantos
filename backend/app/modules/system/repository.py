"""Consulta de disponibilidade com limite de espera e limpeza da sessão."""

import asyncio

from sqlalchemy import text

from app.core.version import SCHEMA_REVISION


async def database_status(db):
    try:
        revision = await asyncio.wait_for(
            db.scalar(text("SELECT version_num FROM alembic_version")), timeout=3.0
        )
        return "ok" if revision == SCHEMA_REVISION else "error"
    except Exception:
        try:
            await db.rollback()
        except Exception:
            # A conexão indisponível já está representada no status retornado.
            return "error"
        return "error"
