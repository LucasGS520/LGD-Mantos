"""Schemas da fila de publicação."""

from datetime import datetime

from pydantic import BaseModel


class QueueRequest(BaseModel):
    """Payload para enfileirar uma campanha aprovada para publicação."""

    campaign_id: str
    channel: str
    scheduled_at: datetime | None = None


class PublishingQueueItem(BaseModel):
    """Item da fila de publicação."""

    id: str
    campaign_id: str
    channel: str
    scheduled_at: datetime | None
    status: str
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
