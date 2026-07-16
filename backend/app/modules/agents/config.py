"""Configuração centralizada da camada de agentes — modelo e runtime Agno.

Ponto único de troca de provedor LLM: todos os agentes obtêm o modelo por
`get_agent_model()`. Para adicionar um provedor externo (ex.: Anthropic ou
OpenAI), basta tratar o novo valor de AGENT_LLM_PROVIDER aqui — nenhum
agente precisa ser alterado.

Atenção ao deploy: o provedor padrão (Ollama) exige um servidor Ollama
acessível em OLLAMA_URL. Em ambientes sem Ollama (ex.: Render), os runs de
agentes falharão com erro de conexão — o restante da API continua operando.
"""

import os

from agno.models.ollama import Ollama

from app.core.config import settings

# Provedor ativo. Hoje apenas "ollama" é suportado; o valor vem do ambiente
# para permitir a troca sem alterar código dos agentes.
AGENT_LLM_PROVIDER = os.environ.get("AGENT_LLM_PROVIDER", "ollama").lower()


def get_agent_model() -> Ollama:
    """Retorna o modelo LLM configurado para uso nos agentes."""
    if AGENT_LLM_PROVIDER == "ollama":
        return Ollama(id=settings.OLLAMA_MODEL, host=settings.OLLAMA_URL)

    raise ValueError(
        f"Provedor LLM '{AGENT_LLM_PROVIDER}' não suportado. "
        "Valores aceitos: 'ollama'. Para adicionar um provedor novo, "
        "implemente-o em app/modules/agents/config.py."
    )
