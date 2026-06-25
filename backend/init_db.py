""" Rotina de inicialização do banco local.

Cria as tabelas declaradas nos modelos SQLAlchemy e insere dados básicos de
categoria e fornecedor quando eles ainda não existem.
"""

import asyncio, sys
sys.path.insert(0, "/app")
from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal

# Importa todos os modelos para registrá-los em Base.metadata antes do create_all.
import app.shared.models as _shared_models  # noqa: F401 — catalog + operations

# Modelos da camada de agentes precisam ser importados explicitamente para evitar
# circular imports que ocorreriam se fossem re-exportados por shared.models.__init__.
import app.modules.agents.knowledge.models as _knowledge_models  # noqa: F401
import app.modules.agents.marketing_ops.models as _marketing_ops_models  # noqa: F401


async def init():
    """Cria a estrutura inicial do banco e popula registros mínimos de apoio."""

    print("Criando tabelas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Banco pronto. Acesse: http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(init())
