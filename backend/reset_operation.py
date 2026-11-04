"""Limpeza administrativa explícita, independente de inicialização/migrações.

Nunca aceita outro banco além de lgd_mantos, nem um host diferente do informado.
Não executa backup, não migra registros e não confirma inventário fictício.
"""

import argparse
import asyncio
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url

from app.core.config import settings
from app.core.database import engine
from app.domain.models import Base

LEGACY = {"app_preferences", "categories", "suppliers", "sale_channels", "products", "product_variants", "stock_movements", "sales", "sale_items", "expenses", "merchandise_entries", "merchandise_entry_items"}


async def reset(args):
    url = make_url(settings.DATABASE_URL)
    if args.database != "lgd_mantos" or url.database != args.database or url.host != args.host:
        raise RuntimeError("Destino não corresponde ao banco/host explicitamente informado")
    if args.confirm != f"LIMPAR {args.database}":
        raise RuntimeError("Confirmação literal incorreta")
    managed_root = (Path(__file__).resolve().parent / "app" / "static" / "uploads").resolve()
    files = []
    async with engine.begin() as conn:
        actual = (await conn.execute(text("SELECT current_database()"))).scalar_one()
        if actual != args.database:
            raise RuntimeError("Conexão aponta para outro banco")
        await conn.execute(text("SELECT pg_advisory_xact_lock(741206031)"))
        tables = set(await conn.run_sync(lambda c: inspect(c).get_table_names(schema="public")))
        owned = {name for name in Base.metadata.tables if name.startswith("lgd_")}
        if tables - owned - LEGACY - {"alembic_version"}:
            raise RuntimeError("Há tabelas não reconhecidas; limpeza recusada")
        if not owned.issubset(tables):
            raise RuntimeError("Aplique as migrações antes da limpeza administrativa")
        photos = (await conn.execute(text("SELECT filename FROM lgd_photos"))).scalars().all()
        files.extend(managed_root / "products" / name for name in photos if Path(name).name == name)
        if "products" in tables:
            for photos in (await conn.execute(text("SELECT photos FROM products"))).scalars():
                for name in photos or []:
                    if isinstance(name, str) and Path(name).name == name:
                        files.append(managed_root / name)
        counts = {name: (await conn.execute(text(f'SELECT count(*) FROM "{name}"'))).scalar_one() for name in sorted(tables - {"alembic_version"})}
        for name in sorted(tables & LEGACY):
            await conn.execute(text(f'DROP TABLE "{name}" CASCADE'))
        await conn.execute(text("DROP TYPE IF EXISTS mvt_type"))
        await conn.execute(text("TRUNCATE " + ", ".join('"' + name + '"' for name in sorted(owned))))
        print(f"Destino verificado: {args.host}/{actual}. Registros removidos: {sum(counts.values())}.")
    removed = 0
    for path in set(files):
        resolved = path.resolve()
        if not resolved.is_relative_to(managed_root) or not resolved.is_file():
            continue
        resolved.unlink()
        removed += 1
    await engine.dispose()
    print(f"Fotos associadas removidas: {removed}. Base vazia; inventário inicial ainda não confirmado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--confirm", required=True)
    asyncio.run(reset(parser.parse_args()))
