"""Configuração de conexão e sessão assíncrona com o banco de dados."""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    """Classe base usada por todos os modelos ORM do projeto."""

    pass

async def get_db() -> AsyncSession:
    """Entrega uma sessão de banco por requisição e controla commit/rollback."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            # Qualquer erro na rota ou serviço desfaz a transação da requisição.
            await session.rollback()
            raise
