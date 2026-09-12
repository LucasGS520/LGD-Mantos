"""Rotas de preferências configuráveis do sistema — limiares de alerta."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.settings.schemas import PreferencesOut, PreferencesUpdate
from app.modules.settings.service import PreferenceService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/preferences", response_model=PreferencesOut)
async def get_preferences(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Retorna os limiares de alerta vigentes (valores padrão quando ainda não configurados)."""

    return await PreferenceService.get(db)


@router.put("/preferences", response_model=PreferencesOut)
async def update_preferences(
    body: PreferencesUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    """Atualiza os limiares de alerta usados pelas análises de estoque e ruptura."""

    return await PreferenceService.update(db, body)
