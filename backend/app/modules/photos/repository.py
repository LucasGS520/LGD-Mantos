"""Consultas de referência usadas na recuperação de falhas de armazenamento."""

from app.shared.models.entities import Photo
from sqlalchemy import select


async def file_referenced(db, filename):
    return await db.scalar(select(Photo.id).where(Photo.filename == filename)) is not None


async def filenames(db):
    return set((await db.scalars(select(Photo.filename))).all())
