"""Inventário somente de leitura: nunca remove arquivos, metadados ou órfãos.

Use com a configuração da implantação e sem uploads em andamento para obter
um inventário estável. Resultado não autoriza limpeza automática.
"""

import asyncio
import json

from app.core.database import AsyncSessionLocal, engine
from app.modules.photos.infrastructure.local_storage import storage
from app.modules.photos.repository import filenames
from sqlalchemy import text


async def inventory():
    async with AsyncSessionLocal() as db:
        await db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        referenced = await filenames(db)
        # Somente arquivos diretos gerenciados; não segue links nem percorre outros diretórios.
        existing = (
            {p.name for p in storage.root.iterdir() if p.is_file() and not p.is_symlink()}
            if storage.root.exists()
            else set()
        )
        report = {
            "referenced": len(referenced),
            "files": len(existing),
            "missing": sorted(referenced - existing),
            "orphans": sorted(existing - referenced),
            "read_only": True,
        }
        await db.rollback()
    return report


async def main():
    print(json.dumps(await inventory(), ensure_ascii=False, indent=2))
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
