"""Schemas de observabilidade da camada de agentes."""

from datetime import datetime

from pydantic import BaseModel


class OpsMetrics(BaseModel):
    """Métricas consolidadas do sistema de agentes."""

    total_runs: int
    runs_pending: int
    runs_running: int
    runs_completed: int
    runs_failed: int
    success_rate: float
    pending_approvals: int
    approved_campaigns: int
    rejected_campaigns: int
    knowledge_docs_active: int


class RunLogEntry(BaseModel):
    """Entrada resumida de um agent run para o log de operações."""

    run_id: str
    status: str
    objective: str
    created_at: datetime
    updated_at: datetime
    error: str | None
    result: dict | None

    model_config = {"from_attributes": True}
