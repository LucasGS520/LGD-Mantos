"""Borda HTTP do módulo de fotos."""

from app.core.auth import verify_token
from app.core.database import get_db
from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse

from . import service
from .infrastructure.local_storage import MAX_PHOTO_BYTES, storage
from .schemas import PhotoIn

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/products/{product_id}/photos")
async def upload_photo(product_id: str, file: UploadFile, db=Depends(get_db)):
    return await service.upload_photo(product_id, await file.read(MAX_PHOTO_BYTES + 1), db, storage)


@router.get("/photos/{entity_id}/content")
async def photo_content(entity_id: str, db=Depends(get_db)):
    return FileResponse(
        await service.photo_content(entity_id, db, storage),
        headers={"Cache-Control": "private, no-store"},
    )


@router.put("/photos/{entity_id}/content")
async def replace_photo(entity_id: str, file: UploadFile, db=Depends(get_db)):
    return await service.replace_photo(entity_id, await file.read(MAX_PHOTO_BYTES + 1), db, storage)


@router.put("/photos/{entity_id}")
async def edit_photo(entity_id: str, data: PhotoIn, db=Depends(get_db)):
    return await service.edit_photo(entity_id, data, db)


@router.delete("/photos/{entity_id}")
async def delete_photo(entity_id: str, db=Depends(get_db)):
    return await service.delete_photo(entity_id, db, storage)
