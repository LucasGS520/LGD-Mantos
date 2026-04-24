import asyncio, sys
sys.path.insert(0, "/app")
from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal
import app.shared.models as M

async def init():
    print("Criando tabelas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as s:
        for name in ["Camisetas Oversized","Camisetas Peruanas","Moletons","Calças","Acessórios"]:
            r = await s.execute(select(M.Category).where(M.Category.name==name))
            if not r.scalar_one_or_none():
                s.add(M.Category(name=name))
        r = await s.execute(select(M.Supplier).where(M.Supplier.name=="Fornecedor Peru"))
        if not r.scalar_one_or_none():
            s.add(M.Supplier(name="Fornecedor Peru", contact="Carlos Mamani", phone="+55 11 9 9999-0000"))
        await s.commit()
    print("Banco pronto. Acesse: http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(init())
