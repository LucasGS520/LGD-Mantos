"""Rotas da fila de publicação — ativa a tabela publishing_queue para uso real."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.agents.publishing.schemas import PublishingQueueItem, QueueRequest
from app.modules.agents.publishing.service import PublishingService

router = APIRouter(prefix="/publishing", tags=["publishing"])


@router.get("", response_model=list[PublishingQueueItem])
async def list_queue(
    status: str | None = Query(default=None, description="waiting_approval | approved | published | failed"),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Lista a fila de publicação com filtro opcional por status."""
    return await PublishingService.list_queue(db, status=status)


@router.post("/queue", response_model=PublishingQueueItem, status_code=201)
async def queue_campaign(
    body: QueueRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Enfileira uma campanha aprovada para publicação.

    Requer que a campanha tenha aprovação humana com status 'approved'.
    PolicyEngine.validate_publish_requires_approval() bloqueia qualquer tentativa
    sem aprovação registrada.
    """
    return await PublishingService.queue_campaign(
        db, body.campaign_id, body.channel, body.scheduled_at
    )


@router.post("/{entry_id}/published", response_model=PublishingQueueItem)
async def mark_published(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Marca o item como publicado após a postagem manual no canal.

    Ação humana explícita — grava `published_at` e fecha o ciclo da campanha.
    """
    return await PublishingService.mark_published(db, entry_id)


@router.delete("/{entry_id}", status_code=204)
async def remove_from_queue(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Cancela (remove) um item ainda não publicado da fila."""
    await PublishingService.remove_from_queue(db, entry_id)
