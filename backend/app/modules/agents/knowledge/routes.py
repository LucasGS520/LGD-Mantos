"""Rotas de gestão da Knowledge Layer — documentos de marca consultados pelos agentes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.agents.knowledge.models import KnowledgeDocument
from app.modules.agents.knowledge.schemas import (
    KnowledgeDocCreate,
    KnowledgeDocResponse,
    KnowledgeDocUpdate,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeDocResponse])
async def list_documents(
    doc_type: str | None = Query(default=None, description="Filtrar por tipo de documento"),
    active_only: bool = Query(default=True, description="Retornar apenas documentos ativos"),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Lista documentos de conhecimento com filtro por tipo e status."""
    q = select(KnowledgeDocument).order_by(KnowledgeDocument.doc_type, KnowledgeDocument.title)
    if doc_type:
        q = q.where(KnowledgeDocument.doc_type == doc_type)
    if active_only:
        q = q.where(KnowledgeDocument.is_active.is_(True))
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=KnowledgeDocResponse, status_code=201)
async def create_document(
    body: KnowledgeDocCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Cria um novo documento de conhecimento de marca."""
    doc = KnowledgeDocument(**body.model_dump())
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/{doc_id}", response_model=KnowledgeDocResponse)
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Retorna o detalhe de um documento pelo ID."""
    doc = await db.get(KnowledgeDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return doc


@router.put("/{doc_id}", response_model=KnowledgeDocResponse)
async def update_document(
    doc_id: str,
    body: KnowledgeDocUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Atualiza título, conteúdo ou status ativo de um documento."""
    doc = await db.get(KnowledgeDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(doc, field, value)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Remove permanentemente um documento de conhecimento."""
    doc = await db.get(KnowledgeDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    await db.delete(doc)
    await db.commit()
