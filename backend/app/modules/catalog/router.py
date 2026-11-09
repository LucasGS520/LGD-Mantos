from app.core.auth import verify_token
from app.core.database import get_db, get_read_db
from app.shared.application.errors import ApplicationError
from fastapi import APIRouter, Depends

from . import products as product_service
from . import variants as variant_service
from .repository import products as list_products
from .schemas import ProductIn, VariantIn

router = APIRouter(dependencies=[Depends(verify_token)])


@router.get("/products")
async def products(db=Depends(get_read_db)):
    return await list_products(db)


@router.get("/products/{entity_id}")
async def product(entity_id: str, db=Depends(get_read_db)):
    result = await list_products(db, entity_id)
    if not result:
        raise ApplicationError(404, "Registro não encontrado")
    return result[0]


@router.post("/products")
async def create_product(data: ProductIn, db=Depends(get_db)):
    return await product_service.save_product(db, data)


@router.put("/products/{entity_id}")
async def edit_product(entity_id: str, data: ProductIn, db=Depends(get_db)):
    return await product_service.save_product(db, data, entity_id)


@router.post("/products/{product_id}/variants")
async def create_variant(product_id: str, data: VariantIn, db=Depends(get_db)):
    return await variant_service.save_variant(db, product_id, data)


@router.put("/products/{product_id}/variants/{entity_id}")
async def edit_variant(product_id: str, entity_id: str, data: VariantIn, db=Depends(get_db)):
    return await variant_service.save_variant(db, product_id, data, entity_id)
