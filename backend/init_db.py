"""Rotina de inicialização do banco — agora baseada em Alembic.

Cenários tratados:
1. Banco vazio (instalação nova): aplica todas as migrations até head.
2. Banco legado criado pelo antigo `create_all` (sem tabela alembic_version):
   registra o baseline (stamp 0001) e aplica as migrations seguintes.
3. Banco já gerenciado pelo Alembic: apenas aplica migrations pendentes.

Isso substitui o antigo `Base.metadata.create_all`, que não conseguia
evoluir tabelas existentes.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.core.database import engine

BASELINE_REVISION = "0001"


async def _detect_state() -> tuple[bool, bool]:
    """Verifica se o banco já tem controle do Alembic e se tem tabelas legadas."""
    async with engine.connect() as conn:
        def _check(sync_conn):
            inspector = inspect(sync_conn)
            return (
                inspector.has_table("alembic_version"),
                inspector.has_table("products"),
            )

        has_alembic, has_products = await conn.run_sync(_check)
    await engine.dispose()
    return has_alembic, has_products


def main() -> None:
    """Aplica migrations, registrando baseline em bancos legados quando necessário."""
    has_alembic, has_products = asyncio.run(_detect_state())

    cfg = Config(str(Path(__file__).parent / "alembic.ini"))
    cfg.set_main_option("script_location", str(Path(__file__).parent / "migrations"))

    if has_products and not has_alembic:
        # Banco criado pelo antigo create_all: o schema do baseline já existe,
        # então apenas registramos a revisão sem recriar tabelas.
        print(f"Banco legado detectado — registrando baseline {BASELINE_REVISION}...")
        command.stamp(cfg, BASELINE_REVISION)

    print("Aplicando migrations...")
    command.upgrade(cfg, "head")
    print("Banco pronto. Acesse: http://localhost:8000")


if __name__ == "__main__":
    main()
