"""Garante que a superfície HTTP do domínio de Marketing não existe mais.

Este teste é a trava contra reintrodução acidental: qualquer rota sob
/api/v1/agents deve responder 404, e o módulo Python não deve ser importável.
"""

import pytest


ROTAS_REMOVIDAS = [
    "/api/v1/agents/runs",
    "/api/v1/agents/approvals",
    "/api/v1/agents/approvals/pending",
    "/api/v1/agents/publishing",
    "/api/v1/agents/knowledge",
    "/api/v1/agents/ops/metrics",
    "/api/v1/analytics/agent-context",
]
# Nota: /api/v1/analytics/marketing-intelligence ainda existe neste ponto — só
# é renomeado na Task 5, que acrescenta a rota a esta lista.


@pytest.mark.parametrize("rota", ROTAS_REMOVIDAS)
async def test_rota_de_marketing_responde_404(auth_client, rota):
    resposta = await auth_client.get(rota)
    assert resposta.status_code == 404, f"{rota} ainda existe: {resposta.status_code}"


def test_modulo_de_agents_nao_e_importavel():
    with pytest.raises(ModuleNotFoundError):
        __import__("app.modules.agents")
