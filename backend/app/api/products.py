import os, shutil, uuid
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.auth import verify_token
from app.models import Product, ProductVariant, Category, Supplier
from app.schemas import ProductCreate, ProductUpdate, ProductOut, CategoryCreate, CategoryOut, SupplierCreate, SupplierOut, VariantIn, VariantOut

router = APIRouter(tags=["products"])
UPLOAD_DIR = "/app/app/static/uploads"

# ── Categories ────────────────────────────────────────────────────────────────
@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Category).order_by(Category.name))
    return r.scalars().all()

@router.post("/categories", response_model=CategoryOut)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    c = Category(name=data.name); db.add(c); await db.flush(); return c

@router.delete("/categories/{cid}")
async def delete_category(cid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Category).where(Category.id == cid))
    c = r.scalar_one_or_none()
    if not c: raise HTTPException(404, "Não encontrado")
    await db.delete(c); return {"ok": True}

# ── Suppliers ─────────────────────────────────────────────────────────────────
@router.get("/suppliers", response_model=list[SupplierOut])
async def list_suppliers(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Supplier).where(Supplier.is_active==True).order_by(Supplier.name))
    return r.scalars().all()

@router.post("/suppliers", response_model=SupplierOut)
async def create_supplier(data: SupplierCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    s = Supplier(**data.model_dump()); db.add(s); await db.flush(); return s

@router.put("/suppliers/{sid}", response_model=SupplierOut)
async def update_supplier(sid: str, data: SupplierCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Supplier).where(Supplier.id == sid))
    s = r.scalar_one_or_none()
    if not s: raise HTTPException(404, "Fornecedor não encontrado")
    for k, v in data.model_dump(exclude_none=True).items(): setattr(s, k, v)
    return s

# ── Products ──────────────────────────────────────────────────────────────────
@router.get("/products", response_model=list[ProductOut])
async def list_products(
    search: str = Query(None), category_id: str = Query(None),
    supplier_id: str = Query(None), active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db), _=Depends(verify_token)
):
    q = select(Product).options(selectinload(Product.variants))
    if active_only: q = q.where(Product.is_active==True)
    if search: q = q.where(or_(Product.name.ilike(f"%{search}%"), Product.sku.ilike(f"%{search}%")))
    if category_id: q = q.where(Product.category_id==category_id)
    if supplier_id: q = q.where(Product.supplier_id==supplier_id)
    r = await db.execute(q.order_by(Product.name))
    return r.scalars().all()

@router.post("/products", response_model=ProductOut)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    ex = await db.execute(select(Product).where(Product.sku==data.sku))
    if ex.scalar_one_or_none(): raise HTTPException(400, "SKU já cadastrado")
    p = Product(**{k:v for k,v in data.model_dump().items() if k!="variants"})
    db.add(p); await db.flush()
    for v in data.variants:
        db.add(ProductVariant(product_id=p.id, **v.model_dump()))
    await db.flush(); await db.refresh(p, ["variants"]); return p

@router.get("/products/{pid}", response_model=ProductOut)
async def get_product(pid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Product).options(selectinload(Product.variants)).where(Product.id==pid))
    p = r.scalar_one_or_none()
    if not p: raise HTTPException(404, "Produto não encontrado")
    return p

@router.put("/products/{pid}", response_model=ProductOut)
async def update_product(pid: str, data: ProductUpdate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Product).options(selectinload(Product.variants)).where(Product.id==pid))
    p = r.scalar_one_or_none()
    if not p: raise HTTPException(404, "Produto não encontrado")
    for k, v in data.model_dump(exclude_none=True).items(): setattr(p, k, v)
    return p

@router.delete("/products/{pid}")
async def deactivate_product(pid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Product).where(Product.id==pid))
    p = r.scalar_one_or_none()
    if not p: raise HTTPException(404)
    p.is_active = False; return {"ok": True}

@router.post("/products/{pid}/variants", response_model=VariantOut)
async def add_variant(pid: str, data: VariantIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    v = ProductVariant(product_id=pid, **data.model_dump()); db.add(v); await db.flush(); return v

@router.delete("/products/{pid}/variants/{vid}")
async def delete_variant(pid: str, vid: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(ProductVariant).where(ProductVariant.id==vid, ProductVariant.product_id==pid))
    v = r.scalar_one_or_none()
    if not v: raise HTTPException(404)
    await db.delete(v); return {"ok": True}

# ── Photo upload ───────────────────────────────────────────────────────────────
@router.post("/products/{pid}/photos")
async def upload_photo(
    pid: str, file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db), _=Depends(verify_token)
):
    r = await db.execute(select(Product).where(Product.id==pid))
    p = r.scalar_one_or_none()
    if not p: raise HTTPException(404)
    ext = os.path.splitext(file.filename or "photo.jpg")[1].lower() or ".jpg"
    fname = f"{pid}_{uuid.uuid4().hex[:8]}{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(UPLOAD_DIR, fname), "wb") as f:
        shutil.copyfileobj(file.file, f)
    photos = list(p.photos or [])
    photos.append(fname)
    p.photos = photos
    return {"filename": fname, "url": f"/uploads/{fname}"}

@router.delete("/products/{pid}/photos/{fname}")
async def delete_photo(pid: str, fname: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    r = await db.execute(select(Product).where(Product.id==pid))
    p = r.scalar_one_or_none()
    if not p: raise HTTPException(404)
    photos = [x for x in (p.photos or []) if x != fname]
    p.photos = photos
    fpath = os.path.join(UPLOAD_DIR, fname)
    if os.path.exists(fpath): os.remove(fpath)
    return {"ok": True}
