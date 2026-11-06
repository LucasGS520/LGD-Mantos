from app.modules.catalog.public import products as products
from app.modules.operations.public import operations as operations
from app.shared.persistence.base import rows as rows
from sqlalchemy import text


async def read_lock(db):
    await db.execute(text("SELECT pg_advisory_xact_lock_shared(741206031)"))
