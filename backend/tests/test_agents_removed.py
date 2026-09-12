"""Garante que o domínio de Marketing não existe mais.

Duas travas contra reintrodução acidental: qualquer rota sob /api/v1/agents deve
responder 404, e não deve existir código-fonte do módulo removido na árvore.
"""

from pathlib import Path

import pytest


ROTAS_REMOVIDAS = [
    "/api/v1/agents/runs",
    "/api/v1/agents/approvals",
    "/api/v1/agents/approvals/pending",
    "/api/v1/agents/publishing",
    "/api/v1/agents/knowledge",
    "/api/v1/agents/ops/metrics",
    "/api/v1/analytics/agent-context",
    "/api/v1/analytics/marketing-intelligence",
]


@pytest.mark.parametrize("rota", ROTAS_REMOVIDAS)
async def test_rota_de_marketing_responde_404(auth_client, rota):
    resposta = await auth_client.get(rota)
    assert resposta.status_code == 404, f"{rota} ainda existe: {resposta.status_code}"


def test_nao_existe_codigo_fonte_do_modulo_de_agents():
    """Trava contra reintrodução do módulo de agents removido.

    Assere a ausência de código-fonte, não a falha do import. A versão anterior
    deste teste usava `pytest.raises(ModuleNotFoundError)` e quebrava toda vez
    que sobrava um diretório órfão em `app/modules/agents/` — um `git checkout`
    de branch antiga basta, porque o git remove os `.py` rastreados mas deixa
    `__pycache__` para trás, e o Python trata qualquer diretório como *namespace
    package* (PEP 420, que não exige `__init__.py`). O import passava a
    funcionar e o teste falhava por resíduo de build, não por regressão real.

    O que importa é que não haja fonte Python do domínio removido na árvore.
    Sobra de `__pycache__` é lixo de build, não reintrodução de código.
    """
    raiz_do_backend = Path(__file__).resolve().parent.parent
    modulo_removido = raiz_do_backend / "app" / "modules" / "agents"

    fontes = sorted(str(p.relative_to(raiz_do_backend)) for p in modulo_removido.rglob("*.py"))
    assert not fontes, f"código-fonte do módulo de agents voltou à árvore: {fontes}"
