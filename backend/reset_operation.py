"""Reconstrução administrativa autorizada, restrita ao banco e uploads do LGD.

Não migra registros antigos nem roda no startup. A API deve estar parada.
"""

import argparse
import asyncio
from pathlib import Path

from admin_config import environment, migration_url
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine


def target(args):
    url = migration_url()
    parsed = make_url(url)
    if (
        args.database not in {"lgd_mantos", "lgd_mantos_alignment_test"}
        or parsed.database != args.database
        or parsed.host != args.host
    ):
        raise RuntimeError("Destino não corresponde ao banco e host explicitamente informados")
    if args.confirm != "RECRIAR " + args.database:
        raise RuntimeError("Confirmação literal incorreta")
    root = Path(
        environment().get("PHOTO_ROOT")
        or Path(__file__).resolve().parent / "app/static/uploads/products"
    ).resolve()
    if root.name != "products" or root == Path(root.anchor):
        raise RuntimeError("Armazenamento gerenciado deve ser o diretório products")
    return url, root


async def reset(args):
    url, root = target(args)
    engine = create_async_engine(url, hide_parameters=True)
    try:
        async with engine.begin() as connection:
            if await connection.scalar(text("SELECT current_database()")) != args.database:
                raise RuntimeError("Banco conectado divergente")
            active = await connection.scalar(
                text(
                    "SELECT count(*) FROM pg_stat_activity WHERE datname=current_database() AND application_name='lgd_api' AND pid<>pg_backend_pid()"
                )
            )
            if active:
                raise RuntimeError("Pare a API antes de reconstruir o banco")
            await connection.execute(text("SELECT pg_advisory_xact_lock(741206031)"))
            await connection.execute(text("DROP SCHEMA public CASCADE"))
            await connection.execute(text("CREATE SCHEMA public AUTHORIZATION lgd_migrator"))
            await connection.execute(text("REVOKE CREATE ON SCHEMA public FROM PUBLIC"))
            await connection.execute(text("GRANT USAGE ON SCHEMA public TO lgd_app"))
        roots = [root]
        if not environment().get("PHOTO_ROOT"):
            roots.append(root.parent)
        for managed in roots:
            if not managed.exists():
                continue
            for path in managed.iterdir():
                if (
                    path.is_file()
                    and not path.is_symlink()
                    and path.resolve().is_relative_to(managed)
                ):
                    path.unlink()
        print(
            "Schema e fotos gerenciadas reconstruídos. Execute init_db.py; inventário não confirmado."
        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--confirm", required=True)
    asyncio.run(reset(parser.parse_args()))
