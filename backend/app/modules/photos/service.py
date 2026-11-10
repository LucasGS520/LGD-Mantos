"""Casos de uso de fotos e coordenação de commit/compensação."""

import asyncio
import hashlib

from app.shared.application.audit import audit
from app.shared.application.errors import ApplicationError
from app.shared.application.telemetry import emit
from app.shared.models.common import uid
from app.shared.models.entities import Photo, Product, Variant
from app.shared.persistence import base as repo
from sqlalchemy import update

from .repository import file_referenced
from .storage import PhotoStorage


def remove_file(storage, filename):
    """Falha de limpeza não transforma commit confirmado em erro de negócio."""
    try:
        storage.remove(filename)
    except OSError:
        emit("photo_cleanup_deferred")


async def compensate(db, storage, filename):
    """Só remove após comprovar ausência de referência, inclusive em commit incerto."""
    try:
        await db.rollback()
        # Repetições da substituição têm nome determinístico: proteger também
        # a conferência/remoção contra outra tentativa concorrente após rollback.
        await repo.lock(db)
        if not await file_referenced(db, filename):
            remove_file(storage, filename)
    except Exception:
        # Sem conexão não há prova segura: manter órfão para reconciliação.
        emit("photo_compensation_deferred")


async def photo_link(db, product_id, data):
    if data.variant_id:
        variant = await repo.require(db, Variant, data.variant_id)
        if variant.product_id != product_id:
            raise ApplicationError(422, "Foto deve apontar para variante do mesmo produto")
    if data.primary:
        await db.execute(
            update(Photo)
            .where(Photo.product_id == product_id, Photo.primary.is_(True))
            .values(primary=False)
        )
        await db.flush()


async def upload_photo(product_id: str, content: bytes, db, storage: PhotoStorage):
    """Aceita apenas imagens reconhecidas, com arquivo novo removido no rollback."""
    fmt = await asyncio.to_thread(storage.validate, content)
    control = await repo.lock(db)
    product_id = (await repo.require(db, Product, product_id)).id
    existing = [p for p in await repo.rows(db, Photo) if p.product_id == product_id]
    photo = Photo(
        id=uid(),
        product_id=product_id,
        filename=uid() + {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}[fmt],
        position=max((p.position for p in existing), default=-1) + 1,
        primary=not existing,
    )
    filename = photo.filename
    try:
        storage.write(filename, content)
        db.add(photo)
        await db.flush()
        audit(db, "photo", photo.id, "create", "Foto adicionada", None, repo.serialize(photo))
        control.revision += 1
        # Confirma aqui para compensar o arquivo inclusive se o commit falhar.
        await db.commit()
    except Exception:
        await compensate(db, storage, filename)
        raise
    return repo.serialize(photo)


async def photo_content(entity_id: str, db, storage: PhotoStorage):
    photo = await repo.require(db, Photo, entity_id)
    path = storage.path(photo.filename)
    if not storage.exists(photo.filename):
        raise ApplicationError(404, "Arquivo de foto indisponível")
    return path


async def edit_photo(entity_id: str, data, db):
    control = await repo.lock(db)
    photo = await repo.require(db, Photo, entity_id)
    before = repo.serialize(photo)
    await photo_link(db, photo.product_id, data)
    for key, value in data.model_dump().items():
        setattr(photo, key, value)
    audit(db, "photo", photo.id, "edit", "Organização das fotos", before, repo.serialize(photo))
    control.revision += 1
    return repo.serialize(photo)


async def delete_photo(entity_id: str, db, storage: PhotoStorage):
    control = await repo.lock(db)
    photo = await repo.require(db, Photo, entity_id)
    filename = photo.filename
    audit(db, "photo", photo.id, "remove", "Foto removida", repo.serialize(photo), None)
    await db.delete(photo)
    await db.flush()
    remaining = [p for p in await repo.rows(db, Photo) if p.product_id == photo.product_id]
    if remaining and not any(p.primary for p in remaining):
        min(remaining, key=lambda p: (p.position, p.id)).primary = True
    control.revision += 1
    await db.commit()
    # Uma falha de limpeza não perde o registro; arquivo órfão fica sem acesso.
    remove_file(storage, filename)
    return {"removed": True}


async def replace_photo(entity_id: str, content: bytes, db, storage: PhotoStorage):
    """Troca o arquivo do mesmo ID; conteúdo igual permite repetição segura."""
    fmt = await asyncio.to_thread(storage.validate, content)
    control = await repo.lock(db)
    photo = await repo.require(db, Photo, entity_id)
    filename = (
        photo.id
        + "-"
        + hashlib.sha256(content).hexdigest()[:32]
        + {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}[fmt]
    )
    if photo.filename == filename:
        if not storage.exists(filename):
            storage.write(filename, content)
        return repo.serialize(photo)
    previous = photo.filename
    before = repo.serialize(photo)
    try:
        storage.write(filename, content)
        photo.filename = filename
        audit(db, "photo", photo.id, "replace", "Foto substituída", before, repo.serialize(photo))
        control.revision += 1
        await db.commit()
    except Exception:
        await compensate(db, storage, filename)
        raise
    remove_file(storage, previous)
    return repo.serialize(photo)
