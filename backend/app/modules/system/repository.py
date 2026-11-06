"""Consulta de disponibilidade com limite de espera e limpeza da sessão."""

import asyncio

from sqlalchemy import text


async def database_status(db):
    try:
        await asyncio.wait_for(db.execute(text("SELECT 1")), timeout=3.0)
        return "ok"
    except Exception:
        try:
            await db.rollback()
        except Exception:
            # A conexão indisponível já está representada no status retornado.
            return "error"
        return "error"
