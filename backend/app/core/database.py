"""Configuração de conexão e sessão assíncrona com o banco de dados."""

import time
from contextlib import asynccontextmanager

from sqlalchemy import event, text
from sqlalchemy.exc import DBAPIError, TimeoutError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session

from app.core.config import settings
from app.shared.application.errors import ApplicationError
from app.shared.application.telemetry import emit

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    hide_parameters=True,
    pool_timeout=settings.DB_POOL_TIMEOUT_SECONDS,
    connect_args={
        "server_settings": {
            "lock_timeout": str(settings.DB_LOCK_TIMEOUT_MS),
            "statement_timeout": str(settings.DB_STATEMENT_TIMEOUT_MS),
        }
    },
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@event.listens_for(Session, "after_transaction_end")
def transaction_ended(session, transaction):
    if transaction.parent is None:
        started = session.info.pop("lock_started", None)
        if started is not None:
            emit("lock_released", duration_ms=round((time.perf_counter() - started) * 1000, 2))


class Base(DeclarativeBase):
    """Classe base usada por todos os modelos ORM do projeto."""

    pass


@asynccontextmanager
async def session_scope():
    """Entrega uma sessão de banco por requisição e controla commit/rollback."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except (DBAPIError, TimeoutError) as exc:
            await session.rollback()
            state = getattr(exc.orig, "sqlstate", None) if isinstance(exc, DBAPIError) else None
            if isinstance(exc, TimeoutError) or state in {"55P03", "57014"}:
                emit("database_timeout", kind="pool" if state is None else state)
                raise ApplicationError(
                    503,
                    "Operação aguardou além do limite. Confira o resultado e tente novamente com os mesmos dados.",
                ) from exc
            raise
        except BaseException:
            # Qualquer erro na rota ou serviço desfaz a transação da requisição.
            await session.rollback()
            raise


async def get_db():
    async with session_scope() as session:
        yield session


async def get_read_db():
    """Snapshot consistente, somente leitura, sem advisory lock de gravação."""
    async with session_scope() as session:
        await session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        yield session
