"""Ambiente do Alembic — conecta o Alembic aos modelos e ao banco do projeto.

A URL do banco vem de DATABASE_URL (mesma configuração usada pela aplicação),
garantindo que migrations e API sempre apontem para o mesmo banco.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.core.database import Base

# Importa todos os módulos de modelos para registrá-los em Base.metadata.
# Sem esses imports o autogenerate enxergaria um schema vazio.
import app.shared.models.catalog  # noqa: F401
import app.shared.models.operations  # noqa: F401
import app.modules.agents.knowledge.models  # noqa: F401
import app.modules.agents.marketing_ops.models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera SQL sem conectar ao banco (modo --sql)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Executa as migrations dentro de uma conexão síncrona fornecida pelo engine assíncrono."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Cria engine assíncrono (asyncpg) e delega a execução das migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Ponto de entrada padrão — roda as migrations de forma assíncrona."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
