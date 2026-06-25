"""Schemas para entrada e saída do SupervisorService."""

from datetime import datetime

from pydantic import BaseModel


class RunRequest(BaseModel):
    """Entrada para criar e iniciar um agent run."""

    objective: str
    product_ids: list[str] | None = None


class RunStatus(BaseModel):
    """Status atual de um agent run — usado no polling de status."""

    run_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    error: str | None = None
    result: dict | None = None
