"""API central de IA para consultas gerais, análise e compras."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from modules.shared.services import get_db, verify_token
from modules.shared.services.ai_core import generate_ai_response

router = APIRouter(prefix="/ai", tags=["ai"])


class AIRequest(BaseModel):
    """Payload de entrada para o chat central de IA."""

    message: str
    mode: str = "geral"  # geral | analise | compras


@router.post("/chat")
async def ai_chat(req: AIRequest, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Processa interações gerais de IA mantendo o core centralizado."""
    # Mantemos escopo desta API focado em operações e análise.
    mode = req.mode if req.mode in {"geral", "analise", "compras"} else "geral"
    response = await generate_ai_response(message=req.message, db=db, mode=mode)
    return {"response": response, "mode": mode}
