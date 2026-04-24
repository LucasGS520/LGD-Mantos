from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.schemas import AIRequest, AIResponse
from app.core.ai.service import AIService
from app.core.auth import verify_token
from app.core.database import get_db

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=AIResponse)
async def ai_chat(req: AIRequest, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    return await AIService.generate(
        db=db,
        message=req.message,
        mode=req.mode,
        module=req.module,
        context_ids=req.context_ids,
    )
