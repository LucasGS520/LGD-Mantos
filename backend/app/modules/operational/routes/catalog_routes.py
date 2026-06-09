"""Rotas HTTP para catálogo: categorias, fornecedores, produtos, variantes e fotos."""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.operational import repositories as repo
from app.modules.operational.services.catalog_service import CatalogService
from app.shared.schemas.catalog import (
    CategoryCreate,
    CategoryOut,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    SaleChannelCreate,
    SaleChannelOut,
    SupplierCreate,
    SupplierOut,
    VariantIn,
    VariantOut,
)

router = APIRouter(tags=["operational"])


@router.get("/channels", response_model=list[SaleChannelOut])
async def list_channels(active_only: bool = False, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista canais de venda; active_only=true retorna apenas os ativos."""

    return await repo.list_channels(db, active_only=active_only)


@router.post("/channels", response_model=SaleChannelOut)
async def create_channel(data: SaleChannelCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria um canal de venda."""

    return await CatalogService.create_channel(db, data)


@router.get("/channels/{cid}", response_model=SaleChannelOut)
async def get_channel(cid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna os dados de um canal pelo ID."""

    channel = await repo.get_channel(db, cid)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    return channel


@router.put("/channels/{cid}", response_model=SaleChannelOut)
async def update_channel(cid: str, data: SaleChannelCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Atualiza nome, descrição e cor de um canal."""

    return await CatalogService.update_channel(db, cid, data)


@router.patch("/channels/{cid}/toggle", response_model=SaleChannelOut)
async def toggle_channel(cid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Alterna ativo/inativo de um canal sem excluí-lo."""

    return await CatalogService.toggle_channel(db, cid)


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista categorias disponíveis para organização dos produtos."""

    return await repo.list_categories(db)


@router.post("/categories", response_model=CategoryOut)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria uma categoria no catálogo."""

    return await CatalogService.create_category(db, data)


@router.get("/categories/{cid}", response_model=CategoryOut)
async def get_category(cid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna os dados completos de uma categoria pelo ID."""

    category = await repo.get_category(db, cid)
    if not category:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return category


@router.put("/categories/{cid}", response_model=CategoryOut)
async def update_category(cid: str, data: CategoryCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Atualiza nome e descrição de uma categoria existente."""

    return await CatalogService.update_category(db, cid, data)


@router.delete("/categories/{cid}")
async def delete_category(cid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Exclui uma categoria, desvinculando produtos associados antes."""

    return await CatalogService.delete_category(db, cid)


@router.get("/suppliers", response_model=list[SupplierOut])
async def list_suppliers(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista fornecedores ativos."""

    return await repo.list_suppliers(db)


@router.post("/suppliers", response_model=SupplierOut)
async def create_supplier(data: SupplierCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria um fornecedor para vínculo com produtos e compras."""

    return await CatalogService.create_supplier(db, data)


@router.get("/suppliers/{sid}", response_model=SupplierOut)
async def get_supplier(sid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna os dados completos de um fornecedor pelo ID."""

    supplier = await repo.get_supplier(db, sid)
    if not supplier:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return supplier


@router.put("/suppliers/{sid}", response_model=SupplierOut)
async def update_supplier(sid: str, data: SupplierCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Atualiza os dados de um fornecedor existente."""

    return await CatalogService.update_supplier(db, sid, data)


@router.delete("/suppliers/{sid}")
async def delete_supplier(sid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Desativa um fornecedor pelo ID (soft delete)."""

    return await CatalogService.delete_supplier(db, sid)


@router.get("/products", response_model=list[ProductOut])
async def list_products(
    search: str | None = Query(None),
    category_id: str | None = Query(None),
    supplier_id: str | None = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Lista produtos com filtros opcionais de busca, categoria, fornecedor e status."""

    return await repo.list_products(db, search, category_id, supplier_id, active_only)


@router.post("/products", response_model=ProductOut)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Cria produto e variantes iniciais."""

    return await CatalogService.create_product(db, data)


@router.get("/products/{pid}", response_model=ProductOut)
async def get_product(pid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Busca um produto completo pelo identificador."""

    product = await repo.get_product(db, pid)
    if not product:
        raise HTTPException(404, "Produto nao encontrado")
    return product


@router.put("/products/{pid}", response_model=ProductOut)
async def update_product(pid: str, data: ProductUpdate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Atualiza dados editáveis de um produto."""

    return await CatalogService.update_product(db, pid, data)


@router.delete("/products/{pid}")
async def deactivate_product(pid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Desativa um produto sem remover seu histórico."""

    return await CatalogService.deactivate_product(db, pid)


@router.post("/products/{pid}/variants", response_model=VariantOut)
async def add_variant(pid: str, data: VariantIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Adiciona variante de tamanho/cor a um produto."""

    return await CatalogService.add_variant(db, pid, data)


@router.delete("/products/{pid}/variants/{vid}")
async def delete_variant(pid: str, vid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Remove uma variante vinculada a um produto."""

    return await CatalogService.delete_variant(db, pid, vid)


@router.post("/products/{pid}/photos")
async def upload_photo(
    pid: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Recebe upload de foto e associa o arquivo ao produto."""

    return await CatalogService.upload_photo(db, pid, file)


@router.delete("/products/{pid}/photos/{fname}")
async def delete_photo(pid: str, fname: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Remove uma foto associada ao produto."""

    return await CatalogService.delete_photo(db, pid, fname)
