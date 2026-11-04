"""HTTP do núcleo interno; todas as operações exigem o acesso do dono."""

from datetime import date
from pathlib import Path
import io
import os
import warnings

from fastapi import APIRouter, Depends, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError
from sqlalchemy import select

from app.core.auth import verify_token
from app.core.database import get_db
from app.domain import analytics, repository as repo, service
from app.domain.models import Auxiliary, Control, Movement, Operation, Photo, Product, Variant
from app.domain.schemas import AuxiliaryIn, ConfirmIn, OperationIn, PhotoIn, ProductIn, VariantIn
from app.shared.models.common import uid

router = APIRouter(dependencies=[Depends(verify_token)])
PHOTO_ROOT = Path(os.environ.get("PHOTO_ROOT", str(Path(__file__).resolve().parents[1] / "static" / "uploads" / "products")))
MAX_PHOTO_BYTES = 10 * 1024 * 1024


@router.get("/state")
async def state(db=Depends(get_db)):
    control = await db.get(Control, 1)
    return {"revision": control.revision if control else 0, "started_at": control.started_at if control else None}


@router.get("/auxiliaries")
async def auxiliaries(db=Depends(get_db)):
    return [repo.serialize(a) for a in await repo.rows(db, Auxiliary)]


@router.post("/auxiliaries")
async def create_auxiliary(data: AuxiliaryIn, db=Depends(get_db)):
    return await service.save_auxiliary(db, data)


@router.put("/auxiliaries/{entity_id}")
async def edit_auxiliary(entity_id: str, data: AuxiliaryIn, db=Depends(get_db)):
    return await service.save_auxiliary(db, data, entity_id)


@router.get("/products")
async def products(db=Depends(get_db)):
    return await repo.products(db)


@router.post("/products")
async def create_product(data: ProductIn, db=Depends(get_db)):
    return await service.save_product(db, data)


@router.put("/products/{entity_id}")
async def edit_product(entity_id: str, data: ProductIn, db=Depends(get_db)):
    return await service.save_product(db, data, entity_id)


@router.post("/products/{product_id}/variants")
async def create_variant(product_id: str, data: VariantIn, db=Depends(get_db)):
    return await service.save_variant(db, product_id, data)


@router.put("/products/{product_id}/variants/{entity_id}")
async def edit_variant(product_id: str, entity_id: str, data: VariantIn, db=Depends(get_db)):
    return await service.save_variant(db, product_id, data, entity_id)


@router.get("/operations")
async def operations(db=Depends(get_db)):
    return await repo.operations(db)


@router.get("/operations/{entity_id}")
async def operation(entity_id: str, db=Depends(get_db)):
    return repo.serialize(await repo.require(db, Operation, entity_id))


@router.post("/operations/preview")
async def preview(data: OperationIn, db=Depends(get_db)):
    return await service.operation(db, data)


@router.post("/operations")
async def confirm(data: ConfirmIn, idempotency_key: str = Header(min_length=1, max_length=100), db=Depends(get_db)):
    return await service.operation(db, data.data, preview_token=data.preview_token, request_key=idempotency_key)


@router.post("/operations/{entity_id}/preview")
async def preview_edit(entity_id: str, data: OperationIn, db=Depends(get_db)):
    return await service.operation(db, data, entity_id)


@router.put("/operations/{entity_id}")
async def confirm_edit(entity_id: str, data: ConfirmIn, idempotency_key: str = Header(min_length=1, max_length=100), db=Depends(get_db)):
    return await service.operation(db, data.data, entity_id, data.preview_token, idempotency_key)


@router.get("/history/{entity_id}")
async def history(entity_id: str, db=Depends(get_db)):
    return await repo.history(db, entity_id)


@router.get("/movements")
async def movements(db=Depends(get_db)):
    return [repo.serialize(m) for m in await repo.rows(db, Movement)]


@router.get("/analytics")
async def report(start: date | None = None, end: date | None = None, db=Depends(get_db)):
    return await analytics.report(db, start, end)


async def photo_link(db, product_id, data):
    if data.variant_id:
        variant = await repo.require(db, Variant, data.variant_id)
        if variant.product_id != product_id:
            raise HTTPException(422, "Foto deve apontar para variante do mesmo produto")
    if data.primary:
        for photo in await repo.rows(db, Photo):
            if photo.product_id == product_id:
                photo.primary = False


@router.post("/products/{product_id}/photos")
async def upload_photo(product_id: str, file: UploadFile, db=Depends(get_db)):
    """Aceita apenas imagens reconhecidas, com arquivo novo removido no rollback."""
    control = await repo.lock(db)
    await repo.require(db, Product, product_id)
    content = await file.read(MAX_PHOTO_BYTES + 1)
    if len(content) > MAX_PHOTO_BYTES:
        raise HTTPException(413, "Foto deve ter no máximo 10 MB")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as image:
                fmt = image.format
                image.verify()
        if fmt not in ("JPEG", "PNG", "WEBP"):
            raise ValueError()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(422, "Envie uma foto JPEG, PNG ou WebP válida")
    existing = [p for p in await repo.rows(db, Photo) if p.product_id == product_id]
    photo = Photo(id=uid(), product_id=product_id, filename=uid() + {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}[fmt],
                  position=max((p.position for p in existing), default=-1) + 1, primary=not existing)
    PHOTO_ROOT.mkdir(parents=True, exist_ok=True)
    path = PHOTO_ROOT / photo.filename
    try:
        path.write_bytes(content)
        db.add(photo)
        await db.flush()
        service.audit(db, "photo", photo.id, "create", "Foto adicionada", None, repo.serialize(photo))
        control.revision += 1
        # Confirma aqui para compensar o arquivo inclusive se o commit falhar.
        await db.commit()
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return repo.serialize(photo)


@router.get("/photos/{entity_id}/content")
async def photo_content(entity_id: str, db=Depends(get_db)):
    photo = await repo.require(db, Photo, entity_id)
    path = PHOTO_ROOT / photo.filename
    if not path.is_file():
        raise HTTPException(404, "Arquivo de foto indisponível")
    return FileResponse(path, headers={"Cache-Control": "private, max-age=60"})


@router.put("/photos/{entity_id}")
async def edit_photo(entity_id: str, data: PhotoIn, db=Depends(get_db)):
    control = await repo.lock(db)
    photo = await repo.require(db, Photo, entity_id)
    before = repo.serialize(photo)
    await photo_link(db, photo.product_id, data)
    for key, value in data.model_dump().items():
        setattr(photo, key, value)
    service.audit(db, "photo", photo.id, "edit", "Organização das fotos", before, repo.serialize(photo))
    control.revision += 1
    return repo.serialize(photo)


@router.delete("/photos/{entity_id}")
async def delete_photo(entity_id: str, db=Depends(get_db)):
    control = await repo.lock(db)
    photo = await repo.require(db, Photo, entity_id)
    path = PHOTO_ROOT / photo.filename
    service.audit(db, "photo", photo.id, "remove", "Foto removida", repo.serialize(photo), None)
    await db.delete(photo)
    await db.flush()
    remaining = [p for p in await repo.rows(db, Photo) if p.product_id == photo.product_id]
    if remaining and not any(p.primary for p in remaining):
        min(remaining, key=lambda p: (p.position, p.id)).primary = True
    control.revision += 1
    await db.commit()
    # Uma falha de limpeza não perde o registro; arquivo órfão fica sem acesso.
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
    return {"removed": True}
