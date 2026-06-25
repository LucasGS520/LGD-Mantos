"""Configuração centralizada da camada de agentes — modelo e runtime Agno/Ollama."""

from agno.models.ollama import Ollama

from app.core.config import settings


def get_agent_model() -> Ollama:
    """Retorna o modelo Ollama configurado para uso nos agentes."""
    return Ollama(id=settings.OLLAMA_MODEL, host=settings.OLLAMA_URL)
