"""Serviços de negócio para cadastro e manutenção do catálogo."""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operational import repositories as repo
from app.shared.models.catalog import Category, Product, ProductVariant, Supplier
from app.shared.schemas.catalog import (
    CategoryCreate,
    ProductCreate,
    ProductUpdate,
    SupplierCreate,
    VariantIn,
)

UPLOAD_DIR = str(Path(__file__).resolve().parents[3] / "static" / "uploads")


class CatalogService:
    """Centraliza operações que criam ou alteram categorias, fornecedores e produtos."""

    @staticmethod
    async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
        """Cria uma categoria de produto."""

        category = Category(name=data.name)
        db.add(category)
        await db.flush()
        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: str) -> dict:
        """Remove uma categoria existente."""

        category = await repo.get_category(db, category_id)
        if not category:
            raise HTTPException(404, "Nao encontrado")
        await db.delete(category)
        return {"ok": True}

    @staticmethod
    async def create_supplier(db: AsyncSession, data: SupplierCreate) -> Supplier:
        """Cria um fornecedor ativo com os dados informados."""

        supplier = Supplier(**data.model_dump())
        db.add(supplier)
        await db.flush()
        return supplier

    @staticmethod
    async def update_supplier(db: AsyncSession, supplier_id: str, data: SupplierCreate) -> Supplier:
        """Atualiza campos enviados de um fornecedor existente."""

        supplier = await repo.get_supplier(db, supplier_id)
        if not supplier:
            raise HTTPException(404, "Fornecedor nao encontrado")
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(supplier, key, value)
        return supplier

    @staticmethod
    async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
        """Cria um produto e suas variantes iniciais, validando SKU único."""

        existing = await repo.get_product_by_sku(db, data.sku)
        if existing:
            raise HTTPException(400, "SKU ja cadastrado")

        # As variantes são persistidas separadamente porque dependem do id do produto.
        product = Product(**{key: value for key, value in data.model_dump().items() if key != "variants"})
        db.add(product)
        await db.flush()

        for variant in data.variants:
            db.add(ProductVariant(product_id=product.id, **variant.model_dump()))

        await db.flush()
        await db.refresh(product, ["variants"])
        return product

    @staticmethod
    async def update_product(db: AsyncSession, product_id: str, data: ProductUpdate) -> Product:
        """Atualiza apenas os campos enviados para um produto."""

        product = await repo.get_product(db, product_id)
        if not product:
            raise HTTPException(404, "Produto nao encontrado")
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(product, key, value)
        return product

    @staticmethod
    async def deactivate_product(db: AsyncSession, product_id: str) -> dict:
        """Desativa um produto sem apagar seu histórico operacional."""

        product = await repo.get_product(db, product_id, with_variants=False)
        if not product:
            raise HTTPException(404, "Produto nao encontrado")
        product.is_active = False
        return {"ok": True}

    @staticmethod
    async def add_variant(db: AsyncSession, product_id: str, data: VariantIn) -> ProductVariant:
        """Adiciona uma nova variante vendável a um produto existente."""

        product = await repo.get_product(db, product_id, with_variants=False)
        if not product:
            raise HTTPException(404, "Produto nao encontrado")
        variant = ProductVariant(product_id=product_id, **data.model_dump())
        db.add(variant)
        await db.flush()
        return variant

    @staticmethod
    async def delete_variant(db: AsyncSession, product_id: str, variant_id: str) -> dict:
        """Remove uma variante garantindo vínculo com o produto informado."""

        variant = await repo.get_product_variant(db, product_id, variant_id)
        if not variant:
            raise HTTPException(404, "Variante nao encontrada")
        await db.delete(variant)
        return {"ok": True}

    @staticmethod
    async def upload_photo(db: AsyncSession, product_id: str, file: UploadFile) -> dict:
        """Salva uma foto no diretório de uploads e registra o nome no produto."""

        product = await repo.get_product(db, product_id, with_variants=False)
        if not product:
            raise HTTPException(404, "Produto nao encontrado")

        ext = os.path.splitext(file.filename or "photo.jpg")[1].lower() or ".jpg"
        filename = f"{product_id}_{uuid.uuid4().hex[:8]}{ext}"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(os.path.join(UPLOAD_DIR, filename), "wb") as target:
            shutil.copyfileobj(file.file, target)

        # O campo JSON guarda somente os nomes; a rota pública é montada em /uploads.
        photos = list(product.photos or [])
        photos.append(filename)
        product.photos = photos
        return {"filename": filename, "url": f"/uploads/{filename}"}

    @staticmethod
    async def delete_photo(db: AsyncSession, product_id: str, filename: str) -> dict:
        """Remove a referência da foto do produto e apaga o arquivo quando existir."""

        product = await repo.get_product(db, product_id, with_variants=False)
        if not product:
            raise HTTPException(404, "Produto nao encontrado")
        product.photos = [item for item in (product.photos or []) if item != filename]
        path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(path):
            os.remove(path)
        return {"ok": True}
