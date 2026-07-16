"""Roteador principal da camada de agentes — agrega todos os sub-roteadores."""

from fastapi import APIRouter

from app.modules.agents.approval.routes import router as approval_router
from app.modules.agents.knowledge.routes import router as knowledge_router
from app.modules.agents.ops.routes import router as ops_router
from app.modules.agents.publishing.routes import router as publishing_router
from app.modules.agents.supervisor.routes import router as supervisor_router

router = APIRouter(prefix="/agents", tags=["agents"])

router.include_router(supervisor_router)
router.include_router(approval_router)
router.include_router(knowledge_router)
router.include_router(ops_router)
router.include_router(publishing_router)
