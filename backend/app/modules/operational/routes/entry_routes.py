"""Rotas HTTP para entrada de mercadoria."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.operational import repositories as repo
from app.modules.operational.services.entry_service import EntryService
from app.shared.schemas.entry import EntryIn, EntryOut

router = APIRouter(tags=["operational"])


@router.post("/entries", response_model=EntryOut)
async def create_entry(data: EntryIn, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Registra entrada de mercadoria, criando produtos e variantes inline."""

    return await EntryService.create_entry(db, data)


@router.get("/entries", response_model=list[EntryOut])
async def list_entries(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Lista entradas de mercadoria recentes."""

    entries = await repo.list_entries(db)
    results = []
    for e in entries:
        total = sum(i.unit_cost * i.quantity for i in e.items)
        results.append(EntryOut(
            id=e.id,
            supplier_id=e.supplier_id,
            entry_date=e.entry_date,
            notes=e.notes,
            total_cost=round(total, 2),
            products_created=0,
            variants_added=len(e.items),
            created_at=e.created_at,
            items=[],
        ))
    return results


@router.get("/entries/{entry_id}", response_model=EntryOut)
async def get_entry(entry_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Detalhe de uma entrada de mercadoria com todos os itens."""

    from fastapi import HTTPException
    entry = await repo.get_entry(db, entry_id)
    if not entry:
        raise HTTPException(404, "Entrada não encontrada")

    total = sum(i.unit_cost * i.quantity for i in entry.items)
    return EntryOut(
        id=entry.id,
        supplier_id=entry.supplier_id,
        entry_date=entry.entry_date,
        notes=entry.notes,
        total_cost=round(total, 2),
        products_created=0,
        variants_added=len(entry.items),
        created_at=entry.created_at,
        items=[],
    )
