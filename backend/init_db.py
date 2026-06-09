"""Rotina de inicialização do banco local.

Cria as tabelas declaradas nos modelos SQLAlchemy e insere dados básicos de
categoria e fornecedor quando eles ainda não existem.
"""

import asyncio, sys
sys.path.insert(0, "/app")
from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal
import app.shared.models as M

async def init():
    """Cria a estrutura inicial do banco e popula registros mínimos de apoio."""

    print("Criando tabelas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Banco pronto. Acesse: http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(init())
