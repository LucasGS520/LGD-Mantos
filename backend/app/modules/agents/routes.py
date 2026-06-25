"""Roteador principal da camada de agentes — agrega ApprovalAgent e status de runs."""

from fastapi import APIRouter

from app.modules.agents.approval.routes import router as approval_router

router = APIRouter(prefix="/agents", tags=["agents"])

router.include_router(approval_router)
