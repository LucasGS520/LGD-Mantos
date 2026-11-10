"""Aplica somente a cadeia canônica; nunca limpa, converte ou presume um stamp."""

import asyncio
from pathlib import Path

from admin_config import migration_url
from alembic import command
from alembic.config import Config
from app.core.version import SCHEMA_REVISION
from app.shared.models.entities import Base
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine


async def verify_destination(url):
    engine = create_async_engine(url, hide_parameters=True)
    try:
        async with engine.connect() as connection:
            tables = set(
                await connection.run_sync(
                    lambda conn: inspect(conn).get_table_names(schema="public")
                )
            )
            if not tables:
                return
            revision = (
                await connection.scalar(text("SELECT version_num FROM alembic_version"))
                if "alembic_version" in tables
                else None
            )
            if revision != SCHEMA_REVISION:
                raise RuntimeError(
                    "Base antiga ou desconhecida: execute a reconstrução administrativa explícita. Nenhum dado foi alterado."
                )
            if tables != set(Base.metadata.tables) | {"alembic_version"}:
                raise RuntimeError("Schema divergente da baseline canônica; inicialização recusada")
    finally:
        await engine.dispose()


def main():
    url = migration_url()
    asyncio.run(verify_destination(url))
    root = Path(__file__).resolve().parent
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    command.upgrade(config, "head")
    print("Schema canônico pronto; inventário inicial ainda não confirmado")


if __name__ == "__main__":
    main()
