"""Endpoints de conteúdo e comunicação com apoio de IA."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from modules.shared.services import get_db, verify_token
from modules.shared.services.ai_core import generate_ai_response

router = APIRouter(prefix="/marketing", tags=["marketing"])


class MarketingRequest(BaseModel):
    """Entrada da API de marketing para tarefas de copy e conteúdo."""

    message: str
    mode: str = "marketing"  # marketing | descricao


@router.post("/content")
async def generate_content(req: MarketingRequest, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Gera conteúdo para comunicação usando o núcleo central de IA."""
    # Restringimos modos para preservar escopo do módulo e evitar confusão com análise.
    mode = req.mode if req.mode in {"marketing", "descricao"} else "marketing"
    response = await generate_ai_response(message=req.message, db=db, mode=mode)
    return {"response": response, "mode": mode}
