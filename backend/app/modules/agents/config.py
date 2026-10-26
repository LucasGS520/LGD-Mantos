"""Ponto de integração dos agentes com um futuro provedor externo de IA."""

from fastapi import HTTPException


MODEL_UNAVAILABLE_MESSAGE = (
    "Geração automática indisponível: nenhum provedor externo de IA foi integrado."
)


def require_agent_model() -> None:
    """Impede novos runs enquanto não existir um provedor externo configurado."""
    raise HTTPException(status_code=503, detail=MODEL_UNAVAILABLE_MESSAGE)


def get_agent_model():
    """Reserva a interface dos agentes para uma futura integração externa."""
    raise RuntimeError(MODEL_UNAVAILABLE_MESSAGE)
