"""Rota pública de status do sistema — usada pela tela web "Status do sistema"."""

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.version import API_VERSION

router = APIRouter(tags=["system"])

# Quando o banco está genuinamente inacessível (não só devolvendo erro, mas sem
# responder na rede), o driver pode ficar tentando conectar por bem mais que
# alguns segundos. Sem este limite, a rota trava a requisição inteira em vez de
# reportar "database: error" rápido — o ponto inteiro de um endpoint de saúde.
_DB_CHECK_TIMEOUT_SECONDS = 3.0


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """Verifica conectividade real com o banco e devolve a versão em vigor da API.

    Rota pública (sem verify_token de propósito) — o frontend usa para medir latência e
    confirmar que está falando com o servidor certo antes mesmo do login. Nunca
    expõe detalhes internos (host, credenciais, stack trace): uma falha no banco
    vira só `database: "error"`, com HTTP 200 — quem decide "isso é grave?" é a
    tela, não o status HTTP.
    """

    try:
        await asyncio.wait_for(db.execute(text("SELECT 1")), timeout=_DB_CHECK_TIMEOUT_SECONDS)
        database_status = "ok"
    except Exception:
        database_status = "error"
        # Deixa a sessão limpa para o commit automático do get_db não falhar
        # tentando confirmar uma transação que já quebrou.
        try:
            await db.rollback()
        except Exception:
            pass

    return {
        "status": "ok",
        "version": API_VERSION,
        "database": database_status,
        "server_time": datetime.now(timezone.utc).isoformat(),
    }
