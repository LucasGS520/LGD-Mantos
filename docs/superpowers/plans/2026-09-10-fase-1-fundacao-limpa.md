# Fase 1 — Fundação Limpa: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remover por completo o domínio de Marketing e a IA local do LGD Mantos, e reorganizar as onze telas analíticas em cinco áreas sob uma aba "Inteligência", sem introduzir nenhuma métrica nova.

**Architecture:** A remoção vem primeiro (backend, banco, infraestrutura, frontend), depois o rename `an` → `intel`, e por último a consolidação das telas. Cada tela nova consome exclusivamente endpoints que já existem hoje. A camada Analytics do backend não ganha nenhum service novo nesta fase — apenas um rename (`MarketingIntelligenceService` → `ProductClassificationService`) que preserva a lógica de classificação de produtos antes que ela caia junto com o vocabulário de marketing.

**Tech Stack:** FastAPI · SQLAlchemy 2.0 async · Alembic · PostgreSQL 16 · pytest + pytest-asyncio (`asyncio_mode = auto`) · React 18 + TypeScript + Vite · Recharts · Docker Compose.

**Spec:** `docs/superpowers/specs/2026-09-10-reformulacao-inteligencia-lgd-design.md`

## Global Constraints

- Comentários e docstrings **sempre em português (PT-BR)**, explicativos e voltados à manutenção.
- **Nenhuma métrica nova nesta fase.** Nenhum endpoint novo. Apenas remoção, rename e reorganização.
- **Nenhuma alteração no módulo Operacional** (`backend/app/modules/operational/`, `frontend_pwa/src/screens/op/`) nem na aba `mais`.
- Toda verificação exige **evidência real** — comando executado e saída colada no relatório. "A lógica é simples, deve funcionar" não é verificação.
- O banco de testes é `lgd_mantos_test` em `localhost:55432`, separado do banco de desenvolvimento. O schema de teste é criado por `Base.metadata.create_all`, **não** por migrations.
- Migration head atual: `0004`. A nova revision é `0005`, com `down_revision = '0004'`.
- Versões fixadas que não mudam nesta fase: `alembic==1.18.5`, `fastapi==0.115.5`, `SQLAlchemy==2.0.36`, `httpx==0.28.1`, `asyncpg==0.30.0`.
- Git: commits pequenos e frequentes, um por task no mínimo. Não fazer push sem pedido explícito.

## Decisão tomada neste plano (refinamento da spec)

A spec posiciona a tela `intel-health` (Saúde da Loja) na Fase 3. Ao mapear o
frontend ficou claro que `screens/an/Alertas.tsx` (253 linhas, alcançável a partir
do Dashboard) não tem destino na Fase 1 sem ela: seu conteúdo — risco de ruptura,
produtos parados e qualidade de dados — precisaria ser dobrado dentro de
`intel-overview` na Fase 1 e extraído de novo na Fase 3.

**Decisão:** `intel-health` nasce já na Fase 1, como porte direto de `Alertas.tsx`,
sem sinais e sem semáforo. A Fase 3 reescreve o interior da tela para consumir o
Motor de Sinais, mas a estrutura de navegação fica final desde já. Isso não
introduz métrica nova — todos os dados exibidos já existem em
`/analytics/products/analysis` e `/analytics/data-quality`.

A Fase 1 entrega portanto **sete telas** na aba `intel`. A oitava,
`intel-signal-detail`, continua na Fase 4.

## Achado: três telas órfãs

`top-products`, `by-size` e `suggestions` estão registradas em `nav.tsx` e
`App.tsx`, mas **nenhum ponto do aplicativo navega até elas**. Não há `navigate()`
nem `NavItem target=` apontando para nenhuma das três. São telas mortas.

- `TopProducts.tsx` (71 linhas) e `BySize.tsx` (62 linhas) têm conteúdo útil e
  viram seções dentro de `intel-products` (Task 9).
- `Suggestions.tsx` (107 linhas) consome `/analytics/categories/buying-patterns`,
  exatamente o mesmo endpoint que `ComprasReposicao.tsx` já usa, com apresentação
  inferior. É duplicata morta: apagada sem substituto (Task 10).

## Estrutura de arquivos

**Backend — apagados**

| Caminho | Observação |
| --- | --- |
| `backend/app/modules/agents/` | Diretório inteiro, 2.612 linhas |
| `backend/app/modules/analytics/routes/agent_context.py` | Lógica renasce na Fase 3 |
| `backend/app/modules/analytics/schemas/agent_context.py` | idem |
| `backend/app/modules/analytics/services/agent_context_service.py` | idem |
| `backend/tests/test_approval_service.py` | |
| `backend/tests/test_policy_engine.py` | |
| `backend/tests/test_publishing_service.py` | |
| `backend/tests/test_supervisor_workflows.py` | |
| `backend/tests/test_sku_resolution.py` | Importa `supervisor.service` |

**Backend — renomeados**

| De | Para |
| --- | --- |
| `analytics/services/marketing_intelligence_service.py` | `analytics/services/product_classification_service.py` |
| `analytics/routes/marketing_intelligence.py` | `analytics/routes/product_classification.py` |

**Backend — modificados**

| Caminho | Responsabilidade da mudança |
| --- | --- |
| `backend/main.py` | Remover import e registro de `agents_router` |
| `backend/migrations/env.py` | Remover os dois imports de modelos de agents |
| `backend/app/core/config.py` | Remover settings `OLLAMA_URL` e `OLLAMA_MODEL` |
| `backend/app/modules/analytics/routes/routes.py` | Remover `agent_context_router`, trocar `marketing_intelligence_router` por `product_classification_router` |
| `backend/tests/conftest.py` | Reescrita: sem env de Ollama, sem modelos de agents, `TRUNCATE` reduzido, sem `create_campaign_bundle` |
| `backend/requirements.txt` | Remover `agno`, `ollama`, `openai` |
| `requirements.txt` | idem |

**Backend — criados**

| Caminho | Responsabilidade |
| --- | --- |
| `backend/migrations/versions/0005_remove_marketing.py` | Drop das sete tabelas e dos cinco enums |
| `backend/tests/test_analytics_contracts.py` | Contrato dos endpoints de Analytics sobreviventes |
| `backend/tests/test_agents_removed.py` | Garante que rotas `/agents/*` não existem mais |
| `backend/tests/test_product_classification.py` | Classificação de produtos com o vocabulário novo |

**Infraestrutura — modificados**

`docker-compose.yml`, `docker-compose.prod.yml`, `.env.example`, `docs/DEPLOY.md`.

**Frontend — apagados**

`src/screens/Marketing.tsx`, `src/screens/mk/` (quatro arquivos), e ao fim da fase
`src/screens/intel/TopProducts.tsx`, `BySize.tsx`, `Suggestions.tsx`,
`MarketingIntel.tsx`.

**Frontend — renomeados (diretório `an` → `intel`)**

| De | Para |
| --- | --- |
| `screens/an/Dashboard.tsx` | `screens/intel/Overview.tsx` |
| `screens/an/Alertas.tsx` | `screens/intel/Health.tsx` |
| `screens/an/Categorias.tsx` | `screens/intel/Products.tsx` |
| `screens/an/CategoryDetail.tsx` | `screens/intel/CategoryDetail.tsx` |
| `screens/an/ComprasReposicao.tsx` | `screens/intel/Stock.tsx` |
| `screens/an/DRE.tsx` | `screens/intel/Finance.tsx` |
| `screens/an/ByChannel.tsx` | `screens/intel/Channels.tsx` |

**Frontend — modificados**

`src/nav.tsx`, `src/App.tsx`, `src/components/Chrome.tsx`, `src/services/api.ts`,
`src/services/types.ts`.

---

## Task 1: Remover o módulo de agents do backend

**Files:**
- Delete: `backend/app/modules/agents/` (diretório inteiro)
- Delete: `backend/app/modules/analytics/routes/agent_context.py`
- Delete: `backend/app/modules/analytics/schemas/agent_context.py`
- Delete: `backend/app/modules/analytics/services/agent_context_service.py`
- Delete: `backend/tests/test_approval_service.py`, `test_policy_engine.py`, `test_publishing_service.py`, `test_supervisor_workflows.py`, `test_sku_resolution.py`
- Modify: `backend/main.py`
- Modify: `backend/migrations/env.py`
- Modify: `backend/app/modules/analytics/routes/routes.py`

**Interfaces:**
- Consumes: nada de tasks anteriores.
- Produces: uma API que sobe sem o módulo `agents`. As tasks 2 e 3 dependem de
  `Base.metadata` não conter mais as tabelas `agent_runs`, `campaigns`, `posts`,
  `creative_briefs`, `approvals`, `publishing_queue` e `knowledge_documents`.

- [ ] **Step 1: Apagar o módulo e os arquivos órfãos de analytics**

```bash
git rm -r backend/app/modules/agents
git rm backend/app/modules/analytics/routes/agent_context.py
git rm backend/app/modules/analytics/schemas/agent_context.py
git rm backend/app/modules/analytics/services/agent_context_service.py
```

- [ ] **Step 2: Apagar os cinco arquivos de teste**

Todos importam `app.modules.agents`. Sem exceção — `test_sku_resolution.py`
também, porque importa `supervisor.service`.

```bash
git rm backend/tests/test_approval_service.py \
       backend/tests/test_policy_engine.py \
       backend/tests/test_publishing_service.py \
       backend/tests/test_supervisor_workflows.py \
       backend/tests/test_sku_resolution.py
```

- [ ] **Step 3: Remover o registro do router em `backend/main.py`**

Apagar a linha de import:

```python
from app.modules.agents.routes import router as agents_router
```

E a linha de registro:

```python
app.include_router(agents_router, prefix="/api/v1")
```

- [ ] **Step 4: Remover os imports de modelos em `backend/migrations/env.py`**

O bloco atual é:

```python
# Importa todos os módulos de modelos para registrá-los em Base.metadata.
# Sem esses imports o autogenerate enxergaria um schema vazio.
import app.shared.models.catalog  # noqa: F401
import app.shared.models.operations  # noqa: F401
import app.modules.agents.knowledge.models  # noqa: F401
import app.modules.agents.marketing_ops.models  # noqa: F401
```

Passa a ser:

```python
# Importa todos os módulos de modelos para registrá-los em Base.metadata.
# Sem esses imports o autogenerate enxergaria um schema vazio.
import app.shared.models.catalog  # noqa: F401
import app.shared.models.operations  # noqa: F401
```

- [ ] **Step 5: Limpar o agregador de rotas de analytics**

Em `backend/app/modules/analytics/routes/routes.py`, remover o import
`from .agent_context import router as agent_context_router` e a linha
`router.include_router(agent_context_router)`.

O import e o include de `marketing_intelligence_router` **permanecem por
enquanto** — são tratados na Task 5.

- [ ] **Step 6: Verificar que a aplicação sobe**

```bash
cd backend && python -c "import main; print('imports ok')"
```

Esperado: `imports ok`, sem `ModuleNotFoundError`.

- [ ] **Step 7: Verificar que nenhuma referência sobrou**

```bash
grep -rn "modules.agents\|agents_router\|AgentContext" backend --include=*.py
```

Esperado: nenhuma saída.

- [ ] **Step 8: Commit**

```bash
git add -A backend
git commit -m "refactor: remove o modulo de agents de marketing do backend"
```

---

## Task 2: Reescrever o conftest e repor a cobertura de testes

**Files:**
- Create: `backend/tests/conftest.py` (a Task 1 apagou o arquivo antigo, que era
  inteiramente da camada de agents — este nasce do zero com o conteúdo abaixo)
- Create: `backend/tests/test_agents_removed.py`
- Create: `backend/tests/test_analytics_contracts.py`

**Interfaces:**
- Consumes: da Task 1, a ausência do módulo `agents` em `Base.metadata`.
- Produces: as fixtures `db` e o helper `create_product(db, sku, name, stock, active)`
  usados pelas tasks 5 e seguintes; e o helper `auth_client()` que devolve um
  `httpx.AsyncClient` já autenticado contra a aplicação ASGI.

- [ ] **Step 1: Criar `backend/tests/conftest.py`**

O arquivo antigo — que setava variáveis de ambiente do Ollama, importava modelos
de agents, truncava sete tabelas de marketing e expunha a fábrica
`create_campaign_bundle` — foi apagado na Task 1. Escrever este do zero, com o
conteúdo abaixo: o helper `create_product` volta, e um cliente HTTP autenticado
é acrescentado porque os testes de contrato precisam dele.

```python
"""Configuração compartilhada dos testes.

Estratégia de banco:
- Usa um banco Postgres de TESTE isolado (`lgd_mantos_test`) no mesmo container
  Docker de desenvolvimento (porta 55432) — o SQLite em memória não serve porque
  os modelos usam tipos específicos do Postgres.
- As variáveis de ambiente são definidas ANTES de qualquer import da aplicação:
  o `settings` exige APP_SECRET/APP_PASSWORD e o engine é criado no import.
- O schema é criado uma vez por sessão de testes via Base.metadata.create_all;
  as tabelas relevantes são truncadas antes de cada teste.
"""

import os

# Ambiente mínimo — precisa vir antes de importar qualquer módulo da aplicação.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:lgdmantos123@localhost:55432/lgd_mantos_test",
)
os.environ.setdefault("APP_PASSWORD", "senha-somente-testes")
os.environ.setdefault("APP_SECRET", "segredo-somente-testes")

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _prepare_database():
    """Cria o banco de teste (se não existir) e o schema completo dos modelos."""
    admin = await asyncpg.connect(
        user="postgres",
        password="lgdmantos123",
        host="localhost",
        port=55432,
        database="postgres",
    )
    try:
        await admin.execute("CREATE DATABASE lgd_mantos_test")
    except asyncpg.DuplicateDatabaseError:
        pass
    finally:
        await admin.close()

    # Importa todos os módulos de modelos para registrar as tabelas no metadata
    # (mesma lista usada pelo migrations/env.py para o autogenerate).
    from app.core.database import Base, engine
    import app.shared.models.catalog  # noqa: F401
    import app.shared.models.operations  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(_prepare_database):
    """Trunca as tabelas usadas nos testes antes de cada caso — isolamento total."""
    from app.core.database import engine

    async with engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE product_variants, products RESTART IDENTITY CASCADE"
        ))
    yield


@pytest_asyncio.fixture
async def db():
    """Sessão async do banco de teste para uso direto nos testes."""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """Cliente HTTP sem autenticação, falando direto com a app ASGI."""
    import main

    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client):
    """Cliente HTTP já autenticado — faz login e fixa o header Authorization."""
    resposta = await client.post(
        "/api/v1/auth/login", json={"password": "senha-somente-testes"}
    )
    assert resposta.status_code == 200, resposta.text
    token = resposta.json()["token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client


# ---------------------------------------------------------------------------
# Fábricas de dados — reduzem repetição na montagem de cenários
# ---------------------------------------------------------------------------

async def create_product(db, sku="MANTO-TESTE", name="Manto de Teste", stock=5, active=True):
    """Cria produto ativo com uma variante e o estoque informado."""
    from app.shared.models.catalog import Product, ProductVariant

    product = Product(
        sku=sku,
        name=name,
        cost_price=80.0,
        sale_price=199.9,
        is_active=active,
    )
    db.add(product)
    await db.flush()
    variant = ProductVariant(product_id=product.id, size="M", stock_quantity=stock)
    db.add(variant)
    await db.commit()
    await db.refresh(product)
    return product
```

- [ ] **Step 2: Escrever o teste que garante a remoção das rotas de agents**

Criar `backend/tests/test_agents_removed.py`:

```python
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
```

- [ ] **Step 3: Escrever os testes de contrato dos endpoints de Analytics**

Criar `backend/tests/test_analytics_contracts.py`. Estes testes são a rede de
segurança das Fases 2 a 4 — eles travam o formato de resposta dos services que
serão alterados depois.

```python
"""Contrato dos endpoints de Analytics que sobrevivem à Fase 1.

Estes testes não validam valores calculados — validam que cada rota existe,
exige autenticação e devolve a estrutura que o frontend consome. Servem de rede
de segurança para as fases seguintes, que vão mexer nesses mesmos services.
"""

import pytest

from tests.conftest import create_product


ROTAS_PROTEGIDAS = [
    "/api/v1/analytics/dashboard",
    "/api/v1/analytics/top-products",
    "/api/v1/analytics/by-size",
    "/api/v1/analytics/by-channel",
    "/api/v1/analytics/products/analysis",
    "/api/v1/analytics/data-quality",
    "/api/v1/analytics/finance/dre",
    "/api/v1/analytics/categories/performance",
    "/api/v1/analytics/categories/stock-coverage",
    "/api/v1/analytics/categories/size-distribution",
    "/api/v1/analytics/categories/buying-patterns",
    "/api/v1/analytics/categories/size-stock",
    "/api/v1/analytics/products/attributes",
]


@pytest.mark.parametrize("rota", ROTAS_PROTEGIDAS)
async def test_rota_exige_autenticacao(client, rota):
    resposta = await client.get(rota)
    assert resposta.status_code == 403, f"{rota} respondeu {resposta.status_code}"


@pytest.mark.parametrize("rota", ROTAS_PROTEGIDAS)
async def test_rota_responde_200_autenticada(auth_client, rota):
    resposta = await auth_client.get(rota)
    assert resposta.status_code == 200, f"{rota}: {resposta.text}"


async def test_dashboard_expoe_os_campos_consumidos_pelo_frontend(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/dashboard")
    corpo = resposta.json()
    for campo in (
        "today_revenue", "today_count", "month_revenue", "month_cogs",
        "month_expenses", "gross_profit", "net_profit", "margin_pct",
        "avg_ticket", "total_units_sold", "stock_cost_value",
        "stock_sale_value", "stock_units", "daily_revenue",
    ):
        assert campo in corpo, f"campo ausente no dashboard: {campo}"
    assert len(corpo["daily_revenue"]) == 30


async def test_product_analysis_expoe_as_listas_consumidas_pelo_frontend(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/products/analysis")
    corpo = resposta.json()
    for chave in ("rupture_risk", "stopped"):
        assert chave in corpo, f"chave ausente na analise de produtos: {chave}"
        assert isinstance(corpo[chave], list)


async def test_data_quality_expoe_score_e_total(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/data-quality")
    corpo = resposta.json()
    assert "score" in corpo
    assert "total_issues" in corpo


async def test_top_products_reflete_produto_existente(auth_client, db):
    await create_product(db, sku="CONTRATO-1", name="Manto Contrato")
    resposta = await auth_client.get("/api/v1/analytics/top-products")
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
```

- [ ] **Step 4: Subir o banco de desenvolvimento e rodar a suíte**

O banco de teste precisa do container Postgres no ar.

```bash
docker compose up -d db
cd backend && pytest -v
```

Esperado: todos os testes passam. Se o banco `lgd_mantos_test` tiver tabelas
antigas de marketing de execuções anteriores, elas são inofensivas — o `TRUNCATE`
não as referencia mais. Para começar limpo:
`docker exec lgd_db psql -U postgres -c "DROP DATABASE IF EXISTS lgd_mantos_test"`.

- [ ] **Step 5: Commit**

```bash
git add backend/tests
git commit -m "test: reescreve conftest e repoe cobertura de contrato de analytics"
```

---

## Task 3: Migration 0005 — remover as tabelas de marketing

**Files:**
- Create: `backend/migrations/versions/0005_remove_marketing.py`

**Interfaces:**
- Consumes: da Task 1, a ausência dos modelos em `Base.metadata` (senão o
  autogenerate futuro tentaria recriar as tabelas).
- Produces: banco de desenvolvimento sem as sete tabelas e sem os cinco tipos
  enum. Nenhuma task posterior depende disso.

- [ ] **Step 1: Criar o arquivo da migration**

Seguir exatamente o estilo de `0004_preferencias_de_alerta.py`: docstring
explicativa em português, identificadores no topo, `upgrade()` e `downgrade()`.

A ordem dos `DROP TABLE` respeita as chaves estrangeiras: `approvals`,
`creative_briefs`, `posts` e `publishing_queue` apontam para `campaigns`, que
aponta para `agent_runs`. Filhas primeiro.

```python
"""remove_marketing

Remove o domínio de Marketing por completo: as sete tabelas do workspace de
agentes (runs, campanhas, posts, briefings criativos, aprovações, fila de
publicação e documentos de conhecimento) e os cinco tipos enum que só elas
usavam.

Esta migration é irreversível quanto a DADOS. O downgrade() recria a estrutura
vazia para manter a cadeia de revisions navegável, mas não recupera conteúdo.
Exportar o que for relevante antes de aplicar em produção.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Identificadores desta revision, usados pelo Alembic.
revision: str = '0005'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tabelas na ordem de remoção — filhas antes das pais, por causa das FKs.
TABELAS = [
    'approvals',
    'creative_briefs',
    'posts',
    'publishing_queue',
    'campaigns',
    'agent_runs',
    'knowledge_documents',
]

# Tipos enum criados junto com as tabelas acima. O Postgres não os remove
# automaticamente no DROP TABLE, então precisam de DROP TYPE explícito.
ENUMS = [
    'agent_run_status',
    'content_status',
    'approval_status',
    'publishing_status',
    'knowledge_doc_type',
]


def upgrade() -> None:
    for tabela in TABELAS:
        op.execute(f'DROP TABLE IF EXISTS {tabela} CASCADE')
    for enum in ENUMS:
        op.execute(f'DROP TYPE IF EXISTS {enum}')


def downgrade() -> None:
    """Recria a estrutura vazia. Não restaura dados."""
    # create_type=False é obrigatório: sem ele, cada op.create_table() abaixo
    # emite seu próprio CREATE TYPE para a coluna de enum, colidindo com os
    # tipos que o bloco enum.create() logo adiante já criou. O erro seria
    # DuplicateObjectError: type "agent_run_status" already exists.
    agent_run_status = postgresql.ENUM(
        'pending', 'running', 'completed', 'failed', name='agent_run_status',
        create_type=False,
    )
    content_status = postgresql.ENUM(
        'draft', 'pending_approval', 'approved', 'rejected', name='content_status',
        create_type=False,
    )
    approval_status = postgresql.ENUM(
        'pending', 'approved', 'rejected', 'revision_requested', name='approval_status',
        create_type=False,
    )
    publishing_status = postgresql.ENUM(
        'approved', 'published', 'failed', name='publishing_status',
        create_type=False,
    )
    knowledge_doc_type = postgresql.ENUM(
        'brand_voice', 'persona', 'commercial_rules', 'visual_reference',
        'approved_caption', 'approved_prompt', 'campaign_context',
        'product_style_notes', name='knowledge_doc_type',
        create_type=False,
    )

    bind = op.get_bind()
    for enum in (agent_run_status, content_status, approval_status,
                 publishing_status, knowledge_doc_type):
        enum.create(bind, checkfirst=True)

    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('status', agent_run_status, nullable=False),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'knowledge_documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('doc_type', knowledge_doc_type, nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'campaigns',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('agent_run_id', sa.String(36), sa.ForeignKey('agent_runs.id')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('product_id', sa.String(36), nullable=True),
        sa.Column('channel', sa.String(50), nullable=True),
        sa.Column('format', sa.String(50), nullable=True),
        sa.Column('angle', sa.Text(), nullable=True),
        sa.Column('cta', sa.String(200), nullable=True),
        sa.Column('risk_level', sa.String(20), nullable=True),
        sa.Column('status', content_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'posts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id')),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('headline', sa.String(200), nullable=True),
        sa.Column('cta_text', sa.String(200), nullable=True),
        sa.Column('format', sa.String(50), nullable=True),
        sa.Column('copy_variations', postgresql.JSONB(), nullable=True),
        sa.Column('status', content_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'creative_briefs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id')),
        sa.Column('visual_briefing', sa.Text(), nullable=True),
        sa.Column('image_prompt', sa.Text(), nullable=True),
        sa.Column('status', content_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'approvals',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id')),
        sa.Column('status', approval_status, nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'publishing_queue',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id')),
        sa.Column('channel', sa.String(50), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', publishing_status, nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
```

- [ ] **Step 2: Aplicar a migration**

```bash
docker compose up -d db
cd backend && alembic upgrade head
```

Esperado: saída terminando em `Running upgrade 0004 -> 0005, remove_marketing`.

- [ ] **Step 3: Verificar no banco que as tabelas sumiram**

```bash
docker exec lgd_db psql -U postgres -d lgd_mantos -c "\dt" | grep -E "agent_runs|campaigns|posts|creative_briefs|approvals|publishing_queue|knowledge_documents"
```

Esperado: nenhuma saída.

- [ ] **Step 4: Verificar que os enums sumiram**

```bash
docker exec lgd_db psql -U postgres -d lgd_mantos -c "\dT" | grep -E "agent_run_status|content_status|approval_status|publishing_status|knowledge_doc_type"
```

Esperado: nenhuma saída.

- [ ] **Step 5: Verificar a cadeia completa num banco descartável**

`0001_baseline` cria as tabelas de marketing e `0005` as dropa. Se a cadeia
estiver quebrada, descobrir agora custa muito menos que na Task 13. O `downgrade()`
também precisa ser exercitado aqui — fora deste teste, ele nunca roda.

```bash
docker exec lgd_db psql -U postgres -c "DROP DATABASE IF EXISTS lgd_chain_check;"
docker exec lgd_db psql -U postgres -c "CREATE DATABASE lgd_chain_check;"
cd backend && export DATABASE_URL="postgresql+asyncpg://postgres:lgdmantos123@localhost:55432/lgd_chain_check" APP_PASSWORD="dummy" APP_SECRET="dummy"
alembic upgrade head        # esperado: 0001 -> 0002 -> 0003 -> 0004 -> 0005, sem erro
alembic downgrade 0004      # esperado: recria as 7 tabelas vazias, sem erro
alembic upgrade head        # esperado: dropa de novo, sem erro
docker exec lgd_db psql -U postgres -c "DROP DATABASE lgd_chain_check;"
```

Entre o `downgrade` e o `upgrade` de volta, conferir que as sete tabelas
reapareceram; ao final, que sumiram de novo.

- [ ] **Step 6: Commit**

```bash
git add backend/migrations/versions/0005_remove_marketing.py
git commit -m "feat(db): migration 0005 remove tabelas e enums de marketing"
```

---

## Task 4: Remover a IA local da infraestrutura e das dependências

**Files:**
- Modify: `docker-compose.yml`
- Modify: `docker-compose.prod.yml`
- Modify: `.env.example`
- Modify: `backend/app/core/config.py:17-18`
- Modify: `requirements.txt`
- Modify: `backend/requirements.txt`
- Modify: `docs/DEPLOY.md`

**Interfaces:**
- Consumes: da Task 1, a ausência de qualquer código que chame `get_agent_model()`.
- Produces: um ambiente Docker sem container de LLM. Nenhuma task posterior
  depende disso, mas a verificação final da fase checa.

- [ ] **Step 1: Remover o serviço `ollama` e o `model-init` do `docker-compose.yml`**

Apagar o bloco inteiro do serviço `ollama` (imagem `ollama/ollama`, container
`lgd_ollama`, porta 11434, volume `ollama_data`, healthcheck e o comentário sobre
GPU NVIDIA) e o bloco do serviço que faz `ollama pull llama3.1:8b`.

No serviço `backend`, o `depends_on` passa de:

```yaml
    depends_on:
      db:
        condition: service_healthy
      ollama:
        condition: service_healthy
```

para:

```yaml
    depends_on:
      db:
        condition: service_healthy
```

Na seção `volumes:` ao final do arquivo, apagar:

```yaml
  # Volume persistente com os pesos do modelo Ollama (~5 GB para llama3.1:8b).
  ollama_data:
```

- [ ] **Step 2: Aplicar as mesmas remoções em `docker-compose.prod.yml`**

Mesma coisa: bloco `ollama`, bloco `model-init`, o `depends_on: ollama` do
serviço `backend` e o volume `ollama_data`.

- [ ] **Step 3: Remover as variáveis de `.env.example`**

Apagar as três linhas:

```
# Servidor Ollama usado pelos agentes de IA (opcional — padrão localhost).
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b
```

- [ ] **Step 4: Remover as settings de `backend/app/core/config.py`**

Apagar as linhas 17 e 18:

```python
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
```

- [ ] **Step 5: Remover as dependências dos dois arquivos de requirements**

Em `requirements.txt` (raiz), apagar o bloco:

```
# Framework de agentes IA e cliente Ollama.
# O pacote `openai` é exigido pelo Agno para o modelo Ollama (cliente compatível).
agno==2.6.19
ollama==0.6.2
openai==2.45.0
```

Em `backend/requirements.txt`, apagar as três linhas `agno==2.6.19`,
`ollama==0.6.2` e `openai==2.44.0`, preservando a ordem alfabética das demais.

- [ ] **Step 6: Atualizar `docs/DEPLOY.md`**

Sete pontos citam Ollama. Ajustar cada um:

- Linha 4: a frase de abertura descreve a stack como "PWA React + Ollama" —
  remover a menção ao Ollama.
- Linha 15: o diagrama diz `backend ──▶ db (Postgres 16) e ollama (llama3.1:8b)`
  — passa a `backend ──▶ db (Postgres 16)`.
- Linha 28: o requisito de RAM menciona "o llama3.1:8b consome ~6-8 GB de RAM
  durante a inferência" — remover a frase e reduzir o requisito de memória
  declarado da VPS, já que esse era o item dominante.
- Linha 66: remover a linha da tabela de variáveis referente a `OLLAMA_URL`.
- Linha 95: o comando `docker compose -f docker-compose.prod.yml logs -f backend model-init`
  perde o `model-init`.
- Linhas 104 e 105: remover as duas linhas da tabela de verificação pós-deploy
  (`docker exec lgd_ollama ollama list` e "Aba Marketing → Novo Run").

- [ ] **Step 7: Verificar que nenhuma referência sobrou**

```bash
grep -rni "ollama\|agno\|llama3" --include=* . \
  | grep -v graphify-out | grep -v node_modules | grep -v "\.git/" \
  | grep -v FABLE_CONSOLIDACAO | grep -v "docs/plans/PLAN-"
```

Esperado: nenhuma saída. Os dois documentos históricos excluídos do grep
(`FABLE_CONSOLIDACAO_2026-07-16.md` e `docs/plans/PLAN-...marketing.md`)
permanecem intocados de propósito, como registro.

- [ ] **Step 8: Verificar que o compose é válido e não tem container de LLM**

```bash
docker compose config --services
docker compose -f docker-compose.prod.yml config --services
```

Esperado: em ambos, a lista de serviços sai sem `ollama` e sem `model-init`, e
sem erro de parse.

- [ ] **Step 9: Verificar que a aplicação sobe sem as variáveis**

```bash
cd backend && python -c "from app.core.config import settings; print('config ok')"
```

Esperado: `config ok`.

- [ ] **Step 10: Commit**

```bash
git add -A
git commit -m "chore: remove ollama e a camada de IA local da infraestrutura"
```

---

## Task 5: Renomear a classificação de produtos

**Files:**
- Rename: `backend/app/modules/analytics/services/marketing_intelligence_service.py` → `product_classification_service.py`
- Rename: `backend/app/modules/analytics/routes/marketing_intelligence.py` → `product_classification.py`
- Modify: `backend/app/modules/analytics/routes/routes.py`
- Create: `backend/tests/test_product_classification.py`

**Interfaces:**
- Consumes: da Task 2, o helper `create_product(db, sku, name, stock, active)` e a
  fixture `auth_client`.
- Produces: o endpoint `GET /api/v1/analytics/product-classification`, consumido
  pelas tasks 9 e 10 do frontend. O corpo da resposta tem exatamente estas cinco
  chaves, todas listas: `alta_saida_estoque_saudavel`, `margem_alta`,
  `baixa_saida_estoque_alto`, `estoque_critico`, `sem_estoque`. Cada item tem os
  campos `product_name`, `sku`, `size`, `color`, `stock`, `margin_pct`,
  `sold_30d`, `reason`.

**Por que cinco e não seis.** A spec lista seis situações de estoque, mas a sexta
— `produto_parado` — já é calculada por `ProductAnalysisService.product_analysis`
sob a chave `stopped`, com janela configurável (`prefs.stopped_days`).
Reproduzi-la aqui duplicaria a regra em dois services. Além disso o formato é
outro: `stopped` devolve `{name, sku, total_stock}`, enquanto as cinco situações
deste endpoint devolvem `{product_name, sku, size, color, stock, margin_pct,
sold_30d, reason}`. A sexta situação continua vindo de
`/analytics/products/analysis`, e a Task 9 a exibe a partir de lá.

- [ ] **Step 1: Escrever o teste antes do rename**

Criar `backend/tests/test_product_classification.py`. O teste falha agora porque
o endpoint ainda se chama `/marketing-intelligence`.

```python
"""Classificação de produtos em situações de estoque.

O service cruza velocidade de venda em 30 dias, estoque e margem para dizer em
que situação cada variante está. É a lógica que a Fase 3 vai transformar em
regras do Motor de Sinais — aqui ela só perde o vocabulário de marketing.
"""

from tests.conftest import create_product


CHAVES_ESPERADAS = {
    "alta_saida_estoque_saudavel",
    "margem_alta",
    "baixa_saida_estoque_alto",
    "estoque_critico",
    "sem_estoque",
}


async def test_endpoint_responde_com_as_cinco_situacoes(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/product-classification")
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert set(corpo.keys()) == CHAVES_ESPERADAS
    for chave in CHAVES_ESPERADAS:
        assert isinstance(corpo[chave], list), f"{chave} deveria ser lista"


async def test_produto_sem_estoque_cai_em_sem_estoque(auth_client, db):
    await create_product(db, sku="ZERADO", name="Manto Zerado", stock=0)
    resposta = await auth_client.get("/api/v1/analytics/product-classification")
    skus = [item["sku"] for item in resposta.json()["sem_estoque"]]
    assert "ZERADO" in skus


async def test_produto_sem_saida_com_estoque_cai_em_baixa_saida(auth_client, db):
    await create_product(db, sku="PARADO", name="Manto Parado", stock=12)
    resposta = await auth_client.get("/api/v1/analytics/product-classification")
    skus = [item["sku"] for item in resposta.json()["baixa_saida_estoque_alto"]]
    assert "PARADO" in skus


async def test_item_classificado_traz_os_campos_consumidos_pelo_frontend(auth_client, db):
    await create_product(db, sku="CAMPOS", name="Manto Campos", stock=0)
    resposta = await auth_client.get("/api/v1/analytics/product-classification")
    item = resposta.json()["sem_estoque"][0]
    for campo in ("product_name", "sku", "size", "color", "stock",
                  "margin_pct", "sold_30d", "reason"):
        assert campo in item, f"campo ausente no item classificado: {campo}"
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

```bash
cd backend && pytest tests/test_product_classification.py -v
```

Esperado: FAIL. O primeiro teste falha com `assert 404 == 200`, porque a rota
ainda não existe com esse nome.

- [ ] **Step 3: Renomear o arquivo do service e reescrevê-lo**

```bash
git mv backend/app/modules/analytics/services/marketing_intelligence_service.py \
       backend/app/modules/analytics/services/product_classification_service.py
```

Conteúdo novo do arquivo — a lógica de classificação é idêntica à atual; o que
muda são o nome da classe, o nome do método, os nomes das listas e os textos de
`reason`, que deixam de falar em postagem:

```python
"""Classifica produtos em situações de estoque para apoiar decisões de compra e giro."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo
from app.modules.settings.service import PreferenceService

_STOCK_SAFE = 5      # estoque mínimo para considerar a disponibilidade saudável
_VELOCITY_MIN = 3    # unidades/30d para considerar o produto de alta saída
_MARGIN_HIGH = 35.0  # margem % a partir da qual o produto é de margem alta


class ProductClassificationService:
    @staticmethod
    async def product_classification(db: AsyncSession) -> dict:
        # O limiar de estoque crítico é configurável pelo operador na tela de
        # Configurações — ver app.modules.settings.
        prefs = await PreferenceService.get_safe(db)
        since_30 = datetime.now(timezone.utc) - timedelta(days=30)
        velocity = await sales_repo.variant_velocity_30d(db, since_30)
        variants = await product_repo.active_variants(db)

        sem_estoque: list[dict] = []
        estoque_critico: list[dict] = []
        alta_saida_estoque_saudavel: list[dict] = []
        margem_alta: list[dict] = []
        baixa_saida_estoque_alto: list[dict] = []

        for variant in variants:
            sold = velocity.get(variant.id, 0)
            stock = variant.stock_quantity
            sale_price = float(variant.product.sale_price or 0)
            cost_price = float(variant.product.cost_price or 0)
            margin_pct = (
                round((sale_price - cost_price) / sale_price * 100, 1)
                if sale_price > 0
                else 0.0
            )

            item = {
                "product_name": variant.product.name,
                "sku": variant.product.sku,
                "size": variant.size,
                "color": variant.color,
                "stock": stock,
                "margin_pct": margin_pct,
                "sold_30d": sold,
            }

            if stock == 0:
                sem_estoque.append({**item, "reason": "sem estoque"})
            elif sold >= _VELOCITY_MIN and stock <= prefs.critical_stock:
                estoque_critico.append({**item, "reason": "boa saída, estoque crítico"})
            else:
                if sold >= _VELOCITY_MIN and stock >= _STOCK_SAFE:
                    alta_saida_estoque_saudavel.append(
                        {**item, "reason": "alta saída e estoque saudável"}
                    )
                if margin_pct >= _MARGIN_HIGH and stock >= _STOCK_SAFE:
                    margem_alta.append({**item, "reason": "margem alta e disponível"})
                if sold == 0 and stock > 0:
                    baixa_saida_estoque_alto.append(
                        {**item, "reason": "sem saída no período — estoque encalhado"}
                    )

        alta_saida_estoque_saudavel.sort(key=lambda x: x["sold_30d"], reverse=True)
        margem_alta.sort(key=lambda x: x["margin_pct"], reverse=True)
        baixa_saida_estoque_alto.sort(key=lambda x: x["stock"], reverse=True)
        estoque_critico.sort(key=lambda x: x["sold_30d"], reverse=True)

        # A sexta situação de estoque — produto parado — NÃO é calculada aqui.
        # Ela já existe em ProductAnalysisService.product_analysis sob a chave
        # `stopped`, com janela configurável (prefs.stopped_days). Duplicar a
        # regra em dois services criaria duas fontes de verdade para o mesmo
        # conceito. O frontend lê essa situação de /analytics/products/analysis.
        return {
            "alta_saida_estoque_saudavel": alta_saida_estoque_saudavel,
            "margem_alta": margem_alta,
            "baixa_saida_estoque_alto": baixa_saida_estoque_alto,
            "estoque_critico": estoque_critico,
            "sem_estoque": sem_estoque,
        }
```

- [ ] **Step 4: Renomear o arquivo da rota e reescrevê-lo**

```bash
git mv backend/app/modules/analytics/routes/marketing_intelligence.py \
       backend/app/modules/analytics/routes/product_classification.py
```

Conteúdo novo:

```python
"""Rota de classificação de produtos — situações de estoque para decisão de compra."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.analytics.services.product_classification_service import (
    ProductClassificationService,
)

router = APIRouter()


@router.get("/product-classification")
async def product_classification(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Classifica produtos em cinco situações de estoque, margem e velocidade.

    A sexta situação — produto parado — vem de /analytics/products/analysis
    (chave `stopped`), que já a calcula com janela configurável. Ver a nota de
    interfaces da Task 5 no plano.
    """
    return await ProductClassificationService.product_classification(db)
```

- [ ] **Step 5: Atualizar o agregador de rotas**

Em `backend/app/modules/analytics/routes/routes.py`, trocar

```python
from .marketing_intelligence import router as marketing_intelligence_router
```

por

```python
from .product_classification import router as product_classification_router
```

e a linha

```python
router.include_router(marketing_intelligence_router)
```

por

```python
router.include_router(product_classification_router)
```

- [ ] **Step 6: Fechar a lista de rotas removidas**

Agora que a rota antiga deixou de existir, acrescentá-la à lista
`ROTAS_REMOVIDAS` em `backend/tests/test_agents_removed.py`, junto com o
comentário que a Task 2 deixou no lugar:

```python
    "/api/v1/agents/ops/metrics",
    "/api/v1/analytics/agent-context",
    "/api/v1/analytics/marketing-intelligence",
]
```

- [ ] **Step 7: Rodar os testes e confirmar que passam**

```bash
cd backend && pytest tests/test_product_classification.py tests/test_agents_removed.py -v
```

Esperado: todos PASS. Se `test_agents_removed.py` passar com a rota antiga na
lista, o rename foi completo.

- [ ] **Step 8: Rodar a suíte inteira**

```bash
cd backend && pytest -v
```

Esperado: tudo verde.

- [ ] **Step 9: Commit**

```bash
git add -A backend
git commit -m "refactor: MarketingIntelligenceService vira ProductClassificationService"
```

---

## Task 6: Remover o Marketing do frontend

**Files:**
- Delete: `frontend_pwa/src/screens/Marketing.tsx`
- Delete: `frontend_pwa/src/screens/mk/` (ApprovalDetail.tsx, KnowledgeDocForm.tsx, NewRun.tsx, RunDetail.tsx)
- Modify: `frontend_pwa/src/nav.tsx`
- Modify: `frontend_pwa/src/components/Chrome.tsx`
- Modify: `frontend_pwa/src/App.tsx`
- Modify: `frontend_pwa/src/services/api.ts`
- Modify: `frontend_pwa/src/services/types.ts`

**Interfaces:**
- Consumes: da Task 5, o endpoint `/analytics/product-classification` e o formato
  das seis chaves.
- Produces: o tipo `ProductClassification` e a função `api.getProductClassification()`,
  consumidos pelas tasks 9 e 10. `TabId` passa a ser `'op' | 'an' | 'mais'` — o
  rename de `an` para `intel` é a Task 7.

- [ ] **Step 1: Apagar as telas**

```bash
git rm frontend_pwa/src/screens/Marketing.tsx
git rm -r frontend_pwa/src/screens/mk
```

- [ ] **Step 2: Limpar `src/nav.tsx`**

No tipo `ScreenId`, apagar as duas linhas:

```typescript
  | 'marketing'
  | 'mk-new-run' | 'mk-run-detail' | 'mk-approval-detail' | 'mk-knowledge-form'
```

O tipo `TabId` passa a:

```typescript
export type TabId = 'op' | 'an' | 'mais'
```

E `TAB_ROOTS` perde a entrada `mk`:

```typescript
export const TAB_ROOTS: Record<TabId, ScreenId> = {
  op: 'product-list',
  an: 'dashboard',
  mais: 'more',
}
```

- [ ] **Step 3: Limpar a barra de abas em `src/components/Chrome.tsx`**

A constante `TABS` perde a entrada de Marketing:

```typescript
const TABS: { id: TabId; label: string; icon: (p: IcoProps) => JSX.Element }[] = [
  { id: 'op',   label: 'Operação',  icon: Ico.box },
  { id: 'an',   label: 'Análise',   icon: Ico.chart },
  { id: 'mais', label: 'Mais',      icon: Ico.more },
]
```

E o grid do `BottomNav` passa de quatro para três colunas:

```typescript
      display: 'grid', gridTemplateColumns: 'repeat(3,1fr)',
```

- [ ] **Step 4: Limpar `src/App.tsx`**

Apagar os cinco imports:

```typescript
import Marketing from './screens/Marketing'
import NewRun from './screens/mk/NewRun'
import RunDetail from './screens/mk/RunDetail'
import ApprovalDetail from './screens/mk/ApprovalDetail'
import KnowledgeDocForm from './screens/mk/KnowledgeDocForm'
```

E as cinco entradas correspondentes do mapa `screens`:

```typescript
    'marketing':           <Marketing />,
    'mk-new-run':          <NewRun />,
    'mk-run-detail':       <RunDetail />,
    'mk-approval-detail':  <ApprovalDetail />,
    'mk-knowledge-form':   <KnowledgeDocForm />,
```

- [ ] **Step 5: Limpar `src/services/api.ts`**

Apagar o bloco inteiro que começa no comentário
`// ─── Agents / Marketing Ops ──────────────────────────────────` e vai até a
última função de knowledge (`deleteKnowledgeDoc`). São dezesseis funções:
`getAgentRuns`, `createAgentRun`, `getAgentRun`, `getPendingApprovals`,
`getApprovals`, `getApprovalDetail`, `approveApproval`, `rejectApproval`, a
função de revisão, `regenerateApproval`, `getPublishingQueue`,
`queueCampaignForPublishing`, a de marcar como publicado, a de remover da fila,
`getOpsMetrics`, `getKnowledgeDocs`, `createKnowledgeDoc`, `updateKnowledgeDoc` e
`deleteKnowledgeDoc`.

Substituir a função `getMarketingIntelligence` por:

```typescript
  getProductClassification: () =>
    req<ProductClassification>('GET', '/analytics/product-classification'),
```

No bloco de imports de tipos no topo do arquivo, trocar `MarketingIntelligence`
por `ProductClassification` e apagar `AgentRun`, `AgentApprovalItem`,
`AgentApprovalDetail`, `OpsMetrics`, `KnowledgeDoc` e `PublishingQueueItem`.

- [ ] **Step 6: Limpar `src/services/types.ts`**

Apagar as interfaces `AgentRun`, `AgentApprovalItem`, `AgentApprovalDetail`,
`OpsMetrics`, `KnowledgeDoc` e `PublishingQueueItem`, junto com o comentário de
seção `// Marketing` que as precede.

Renomear `MarketingVariant` para `ClassifiedVariant` (a forma dos campos não
muda) e substituir a interface `MarketingIntelligence` por:

```typescript
/** Cinco situações de estoque devolvidas por GET /analytics/product-classification.
 *  A sexta situação — produto parado — vem de ProductAnalysis.stopped. */
export interface ProductClassification {
  alta_saida_estoque_saudavel: ClassifiedVariant[]
  margem_alta: ClassifiedVariant[]
  baixa_saida_estoque_alto: ClassifiedVariant[]
  estoque_critico: ClassifiedVariant[]
  sem_estoque: ClassifiedVariant[]
}
```

- [ ] **Step 7: Corrigir as referências quebradas**

`screens/an/MarketingIntel.tsx` consome `api.getMarketingIntelligence` e o tipo
antigo; `screens/an/Alertas.tsx` navega para `an-marketing-intel`. Ambos são
reescritos nas tasks 9 a 11, mas o build precisa passar agora. Ação mínima:

- Em `screens/an/MarketingIntel.tsx`, trocar a chamada por
  `api.getProductClassification()`, o tipo por `ProductClassification` e as cinco
  chaves antigas pelas novas, conforme a tabela da Task 5.
- Em `screens/an/Alertas.tsx` linha 193, o botão que navega para
  `an-marketing-intel` permanece — a tela ainda existe até a Task 12.

- [ ] **Step 8: Verificar que o build passa**

```bash
cd frontend_pwa && npm run build
```

Esperado: build concluído sem erro de TypeScript. Qualquer `Cannot find name` ou
`has no exported member` indica referência esquecida.

- [ ] **Step 9: Verificar que nenhuma referência sobrou**

```bash
grep -rn "mk-\|Marketing\|AgentRun\|KnowledgeDoc\|PublishingQueue\|approvals" frontend_pwa/src
```

Esperado: nenhuma saída, exceto ocorrências dentro de `MarketingIntel.tsx`, que
ainda existe até a Task 12.

- [ ] **Step 10: Commit**

```bash
git add -A frontend_pwa
git commit -m "refactor(pwa): remove a aba e as telas de Marketing"
```

---

## Task 7: Renomear a aba `an` para `intel`

**Files:**
- Rename: `frontend_pwa/src/screens/an/` → `frontend_pwa/src/screens/intel/`
- Rename dos arquivos internos conforme a tabela de estrutura
- Modify: `frontend_pwa/src/nav.tsx`
- Modify: `frontend_pwa/src/components/Chrome.tsx`
- Modify: `frontend_pwa/src/App.tsx`

**Interfaces:**
- Consumes: da Task 6, o `TabId` já sem `mk`.
- Produces: `TabId = 'op' | 'intel' | 'mais'`, `TAB_ROOTS.intel = 'intel-overview'`,
  e os sete `ScreenId` finais da aba: `intel-overview`, `intel-health`,
  `intel-products`, `intel-category-detail`, `intel-stock`, `intel-finance`,
  `intel-channels`. As tasks 8 a 11 escrevem o conteúdo dessas telas; aqui elas
  apenas trocam de nome e continuam renderizando o que renderizavam.

- [ ] **Step 1: Renomear o diretório e os arquivos que já têm destino final**

```bash
git mv frontend_pwa/src/screens/an frontend_pwa/src/screens/intel
git mv frontend_pwa/src/screens/intel/Dashboard.tsx        frontend_pwa/src/screens/intel/Overview.tsx
git mv frontend_pwa/src/screens/intel/Alertas.tsx          frontend_pwa/src/screens/intel/Health.tsx
git mv frontend_pwa/src/screens/intel/Categorias.tsx       frontend_pwa/src/screens/intel/Products.tsx
git mv frontend_pwa/src/screens/intel/ComprasReposicao.tsx frontend_pwa/src/screens/intel/Stock.tsx
git mv frontend_pwa/src/screens/intel/DRE.tsx              frontend_pwa/src/screens/intel/Finance.tsx
git mv frontend_pwa/src/screens/intel/ByChannel.tsx        frontend_pwa/src/screens/intel/Channels.tsx
```

`CategoryDetail.tsx`, `TopProducts.tsx`, `BySize.tsx`, `Suggestions.tsx` e
`MarketingIntel.tsx` mantêm o nome por ora. Os quatro últimos são apagados na
Task 12.

- [ ] **Step 2: Atualizar `src/nav.tsx`**

O tipo `TabId`:

```typescript
export type TabId = 'op' | 'intel' | 'mais'
```

No tipo `ScreenId`, as duas linhas atuais da aba de análise

```typescript
  | 'dashboard' | 'top-products' | 'by-size' | 'by-channel' | 'suggestions' | 'dre'
  | 'an-categorias' | 'an-category-detail' | 'an-alertas' | 'an-marketing-intel' | 'an-compras'
```

passam a ser (as quatro telas órfãs continuam listadas até a Task 12, senão o
build quebra):

```typescript
  | 'intel-overview' | 'intel-health' | 'intel-products' | 'intel-category-detail'
  | 'intel-stock' | 'intel-finance' | 'intel-channels'
  | 'top-products' | 'by-size' | 'suggestions' | 'an-marketing-intel'
```

E `TAB_ROOTS`:

```typescript
export const TAB_ROOTS: Record<TabId, ScreenId> = {
  op: 'product-list',
  intel: 'intel-overview',
  mais: 'more',
}
```

- [ ] **Step 3: Atualizar a barra de abas em `src/components/Chrome.tsx`**

```typescript
const TABS: { id: TabId; label: string; icon: (p: IcoProps) => JSX.Element }[] = [
  { id: 'op',    label: 'Operação',     icon: Ico.box },
  { id: 'intel', label: 'Inteligência', icon: Ico.chart },
  { id: 'mais',  label: 'Mais',         icon: Ico.more },
]
```

- [ ] **Step 4: Atualizar `src/App.tsx`**

Os imports da aba passam a:

```typescript
import Overview from './screens/intel/Overview'
import Health from './screens/intel/Health'
import Products from './screens/intel/Products'
import CategoryDetail from './screens/intel/CategoryDetail'
import Stock from './screens/intel/Stock'
import Finance from './screens/intel/Finance'
import Channels from './screens/intel/Channels'
import TopProducts from './screens/intel/TopProducts'
import BySize from './screens/intel/BySize'
import Suggestions from './screens/intel/Suggestions'
import MarketingIntel from './screens/intel/MarketingIntel'
```

E as entradas do mapa `screens`:

```typescript
    'intel-overview':        <Overview />,
    'intel-health':          <Health />,
    'intel-products':        <Products />,
    'intel-category-detail': <CategoryDetail />,
    'intel-stock':           <Stock />,
    'intel-finance':         <Finance />,
    'intel-channels':        <Channels />,
    'top-products':          <TopProducts />,
    'by-size':               <BySize />,
    'suggestions':           <Suggestions />,
    'an-marketing-intel':    <MarketingIntel />,
```

- [ ] **Step 5: Atualizar as referências internas de navegação**

Trocar em todo o diretório `screens/intel/`:

| Referência antiga | Nova |
| --- | --- |
| `<BottomNav active="an" />` | `<BottomNav active="intel" />` |
| `navigate('an-alertas')` / `target="an-alertas"` | `'intel-health'` |
| `navigate('an-categorias')` / `target="an-categorias"` | `'intel-products'` |
| `navigate('an-category-detail')` | `'intel-category-detail'` |
| `navigate('an-compras')` / `target="an-compras"` | `'intel-stock'` |
| `target="by-channel"` | `'intel-channels'` |
| `target="dre"` | `'intel-finance'` |

Os pontos exatos: `Overview.tsx` linhas 77, 86 e 112 a 117; `Health.tsx` linha
193 (que aponta para `an-marketing-intel` e só é removido na Task 11);
`Products.tsx` linha 68.

- [ ] **Step 6: Verificar que o build passa**

```bash
cd frontend_pwa && npm run build
```

Esperado: sem erros.

- [ ] **Step 7: Verificar que nenhuma referência antiga sobrou**

```bash
grep -rn "screens/an\|'an-categorias'\|'an-alertas'\|'an-compras'\|'dashboard'\|active=\"an\"" frontend_pwa/src
```

Esperado: nenhuma saída.

- [ ] **Step 8: Commit**

```bash
git add -A frontend_pwa
git commit -m "refactor(pwa): renomeia a aba Analise para Inteligencia"
```

---

## Task 8: Tela Visão Geral (`intel-overview`)

**Files:**
- Modify: `frontend_pwa/src/screens/intel/Overview.tsx`

**Interfaces:**
- Consumes: da Task 7, os `ScreenId` finais e `TAB_ROOTS.intel`.
- Produces: a tela raiz da aba, que é o único ponto de entrada para as outras
  seis. Se um `NavItem` não existir aqui, a tela correspondente fica órfã — foi
  exatamente o defeito encontrado em `top-products`, `by-size` e `suggestions`.

- [ ] **Step 1: Ajustar o cabeçalho e os dados carregados**

O arquivo já carrega `api.getDashboard` e `api.getProductAnalysis('current_month')`
via `useData`. Nenhuma chamada nova. Só o título muda:

```typescript
      <AppBar title="Inteligência" subtitle={`Hoje, ${today}`} />
```

- [ ] **Step 2: Reescrever o bloco de navegação**

O bloco atual, ao final do `ScreenBody` (linhas 110 a 118), tem seis `NavItem`,
um deles apontando para a análise de marketing. O novo tem cinco, cobrindo as
cinco áreas restantes:

```tsx
          {/* Navegação — as cinco áreas da Inteligência */}
          <div style={{ borderTop: '1px solid var(--line-1)', paddingTop: 4 }}>
            <NavItem
              icon={<Ico.pie size={18} stroke="var(--gold-500)" />}
              label="Produtos"
              sub="Mix, ranking, tamanhos e situação de cada item"
              target="intel-products"
            />
            <NavItem
              icon={<Ico.truck size={18} stroke="var(--gold-500)" />}
              label="Estoque & Compras"
              sub="Cobertura, reposição e excesso de estoque"
              target="intel-stock"
              badge={(analysis?.rupture_risk?.length ?? 0) > 0 ? analysis!.rupture_risk.length : undefined}
            />
            <NavItem
              icon={<Ico.doc size={18} stroke="var(--gold-500)" />}
              label="Financeiro"
              sub="DRE do mês, receita, CMV e despesas"
              target="intel-finance"
            />
            <NavItem
              icon={<Ico.store size={18} stroke="var(--gold-500)" />}
              label="Canais"
              sub="Distribuição e taxas por canal de venda"
              target="intel-channels"
            />
            <NavItem
              icon={<Ico.alert size={18} stroke="#F5847B" />}
              label="Saúde da Loja"
              sub="Ruptura, produtos parados e qualidade de dados"
              target="intel-health"
              badge={alertCount > 0 ? alertCount : undefined}
            />
          </div>
```

- [ ] **Step 3: Apontar os avisos de alerta para a nova tela**

Nos dois `AlertRow` do bloco de alertas (linhas 77 e 86), o `onCta` passa de
`() => navigate('an-alertas')` para `() => navigate('intel-health')`.

- [ ] **Step 4: Verificar que o build passa**

```bash
cd frontend_pwa && npm run build
```

Esperado: sem erros.

- [ ] **Step 5: Verificar no navegador**

```bash
docker compose up -d
```

Abrir `http://localhost:5173`, entrar com a senha do `.env`, e conferir: a aba
Inteligência abre na Visão Geral, os cinco itens de navegação aparecem, e clicar
em cada um leva à tela certa sem tela em branco.

- [ ] **Step 6: Commit**

```bash
git add frontend_pwa/src/screens/intel/Overview.tsx
git commit -m "feat(pwa): tela Visao Geral com as cinco areas da Inteligencia"
```

---

## Task 9: Tela Produtos (`intel-products`)

**Files:**
- Modify: `frontend_pwa/src/screens/intel/Products.tsx`

**Interfaces:**
- Consumes: da Task 5, `api.getProductClassification()` e o tipo
  `ProductClassification` (cinco chaves). Da Task 7, o `ScreenId`
  `intel-category-detail`. De `types.ts`, o tipo `ProductAnalysis`, do qual a tela
  usa apenas a lista `stopped` para a sexta situação.
- Produces: nada consumido por tasks posteriores.

A tela absorve três origens: `Products.tsx` (ex-`Categorias.tsx`, 115 linhas,
base), `TopProducts.tsx` (71 linhas) e `BySize.tsx` (62 linhas), mais as
classificações de produto.

- [ ] **Step 1: Trocar o cabeçalho e adicionar o seletor de seções**

O `AppBar` passa a `<AppBar back title="Produtos" subtitle="Mix, ranking e situação" />`.

Logo abaixo dele, usar o componente `Tabs` (já existe em `components/UI`, e
`TopProducts.tsx` o utiliza hoje) para alternar entre três seções:

```tsx
const SECOES = ['Categorias', 'Ranking', 'Tamanhos'] as const

export default function Products() {
  const [secao, setSecao] = useState<string>('Categorias')
  // ... hooks de dados abaixo
```

```tsx
      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <Tabs items={[...SECOES]} active={secao} onChange={setSecao} />
      </div>
```

- [ ] **Step 2: Declarar os três carregamentos de dados**

Os três endpoints já existem e já são usados hoje pelas telas de origem:

```typescript
  const { data: categorias, loading, error, reload } =
    useData<CategoryPerformance[]>(() => api.getCategoryPerformance('current_month'))
  const { data: ranking } =
    useData<TopProduct[]>(() => api.get('/analytics/top-products?days=30'))
  const { data: tamanhos } =
    useData<BySizeItem[]>(() => api.get('/analytics/by-size?days=30'))
  const { data: classificacao } =
    useData<ProductClassification>(api.getProductClassification)
  // A sexta situação (produto parado) vem daqui, não da classificação — ver a
  // nota de interfaces da Task 5.
  const { data: analise } =
    useData<ProductAnalysis>(() => api.getProductAnalysis('current_month'))
```

- [ ] **Step 3: Montar a seção "Categorias"**

Mover verbatim o corpo atual de `Products.tsx` (o mapa sobre `categorias` com os
cards de performance e o `onClick` que navega para `intel-category-detail`),
envolvendo-o em `{secao === 'Categorias' && ( ... )}`.

- [ ] **Step 4: Montar a seção "Ranking"**

Mover verbatim o corpo de `TopProducts.tsx` — a lista de produtos com
`PhotoPlaceholder`, nome, SKU, quantidade e receita — envolvendo em
`{secao === 'Ranking' && ( ... )}`. O seletor de 7/30/90 dias que existia lá
**não** é reproduzido nesta fase: o período fixo de 30 dias basta, e período
configurável é assunto da Fase 2.

- [ ] **Step 5: Montar a seção "Tamanhos"**

Mover verbatim o corpo de `BySize.tsx` — as barras proporcionais por tamanho —
envolvendo em `{secao === 'Tamanhos' && ( ... )}`.

- [ ] **Step 6: Acrescentar o bloco de situação dos produtos**

Abaixo do conteúdo da seção ativa, sempre visível, um resumo compacto das seis
situações. Cada linha mostra o nome da situação e a contagem:

```tsx
          {classificacao && (
            <div style={{ marginTop: 16, borderTop: '1px solid var(--line-1)', paddingTop: 12 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: 1.2, marginBottom: 8 }}>
                Situação dos produtos
              </div>
              {([
                ['Alta saída, estoque saudável', classificacao.alta_saida_estoque_saudavel.length],
                ['Margem alta', classificacao.margem_alta.length],
                ['Baixa saída, estoque alto', classificacao.baixa_saida_estoque_alto.length],
                ['Estoque crítico', classificacao.estoque_critico.length],
                ['Sem estoque', classificacao.sem_estoque.length],
                ['Produto parado', analise?.stopped?.length ?? 0],
              ] as [string, number][]).map(([rotulo, quantidade]) => (
                <div key={rotulo} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--line-1)' }}>
                  <span style={{ fontSize: 13, color: 'var(--text-2)' }}>{rotulo}</span>
                  <span className="tnum" style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-1)' }}>{quantidade}</span>
                </div>
              ))}
            </div>
          )}
```

- [ ] **Step 7: Verificar que o build passa**

```bash
cd frontend_pwa && npm run build
```

Esperado: sem erros.

- [ ] **Step 8: Verificar no navegador**

Com `docker compose up -d` no ar, abrir a aba Inteligência → Produtos e conferir:
as três seções alternam, cada uma mostra dado real, o bloco de situação lista as
seis linhas com contagens, e clicar numa categoria abre o detalhe.

- [ ] **Step 9: Commit**

```bash
git add frontend_pwa/src/screens/intel/Products.tsx
git commit -m "feat(pwa): tela Produtos consolida categorias, ranking, tamanhos e situacao"
```

---

## Task 10: Tela Estoque & Compras (`intel-stock`)

**Files:**
- Modify: `frontend_pwa/src/screens/intel/Stock.tsx`

**Interfaces:**
- Consumes: da Task 5, `api.getProductClassification()` e o tipo
  `ProductClassification`.
- Produces: nada consumido por tasks posteriores.

A base é `Stock.tsx` (ex-`ComprasReposicao.tsx`, 394 linhas), que já consome
`api.getCategoryBuyingPatterns` e navega para `purchase-form`. A tela ganha as
listas de estoque vindas da classificação de produtos.

- [ ] **Step 1: Trocar o cabeçalho**

```tsx
      <AppBar back title="Estoque & Compras" subtitle="Cobertura, reposição e excesso" />
```

- [ ] **Step 2: Carregar a classificação de produtos**

Acrescentar ao lado do `useData` existente:

```typescript
  const { data: classificacao } = useData<ProductClassification>(api.getProductClassification)
```

- [ ] **Step 3: Acrescentar o bloco de recomendações de estoque**

Três listas com nome de produto, tamanho e estoque, cada uma num tom diferente.
Inserir acima do conteúdo atual de padrões de compra, porque é a informação mais
acionável da tela:

```tsx
          {classificacao && (
            <div style={{ marginBottom: 16 }}>
              <ListaDeSituacao
                titulo="Repor primeiro"
                descricao="Boa saída e estoque crítico"
                cor="#F5847B"
                itens={classificacao.estoque_critico}
              />
              <ListaDeSituacao
                titulo="Sem estoque"
                descricao="Zerado — venda perdida enquanto não repõe"
                cor="#F5847B"
                itens={classificacao.sem_estoque}
              />
              <ListaDeSituacao
                titulo="Estoque encalhado"
                descricao="Sem saída no período, com estoque parado"
                cor="var(--text-3)"
                itens={classificacao.baixa_saida_estoque_alto}
              />
            </div>
          )}
```

E o componente auxiliar, no final do arquivo:

```tsx
/** Lista compacta de variantes de uma situação de estoque. Mostra no máximo
 *  cinco itens para não empurrar o resto da tela para baixo. */
function ListaDeSituacao({ titulo, descricao, cor, itens }: {
  titulo: string; descricao: string; cor: string; itens: ClassifiedVariant[]
}) {
  if (itens.length === 0) return null
  return (
    <div style={{ marginBottom: 12, padding: 14, borderRadius: 14, background: 'var(--bg-1)', border: '1px solid var(--line-1)' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 14, fontWeight: 700, color: cor }}>{titulo}</span>
        <span className="tnum" style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-2)' }}>{itens.length}</span>
      </div>
      <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 2, marginBottom: 8 }}>{descricao}</div>
      {itens.slice(0, 5).map((item, i) => (
        <div key={`${item.sku}-${item.size}-${i}`} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderTop: '1px solid var(--line-1)' }}>
          <span style={{ fontSize: 12.5, color: 'var(--text-2)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {item.product_name} · {item.size}
          </span>
          <span className="tnum" style={{ fontSize: 12.5, color: 'var(--text-3)', flexShrink: 0, marginLeft: 8 }}>
            {item.stock} un
          </span>
        </div>
      ))}
      {itens.length > 5 && (
        <div style={{ fontSize: 11.5, color: 'var(--text-4)', marginTop: 6 }}>
          e mais {itens.length - 5}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Verificar que o build passa**

```bash
cd frontend_pwa && npm run build
```

Esperado: sem erros.

- [ ] **Step 5: Verificar no navegador**

Abrir Inteligência → Estoque & Compras. Conferir que as três listas aparecem com
dado real (ou somem, quando vazias), que os padrões de compra por categoria
continuam abaixo delas, e que o botão de registrar compra continua levando a
`purchase-form`.

- [ ] **Step 6: Commit**

```bash
git add frontend_pwa/src/screens/intel/Stock.tsx
git commit -m "feat(pwa): tela Estoque e Compras ganha as situacoes de reposicao"
```

---

## Task 11: Tela Saúde da Loja (`intel-health`)

**Files:**
- Modify: `frontend_pwa/src/screens/intel/Health.tsx`

**Interfaces:**
- Consumes: da Task 7, os `ScreenId` finais.
- Produces: nada consumido por tasks posteriores. A Fase 3 reescreve o interior
  desta tela para consumir o Motor de Sinais; a estrutura de navegação já é final.

A base é `Health.tsx` (ex-`Alertas.tsx`, 253 linhas), que já consome
`api.getProductAnalysis` e navega para telas do Operacional.

- [ ] **Step 1: Trocar o cabeçalho**

```tsx
      <AppBar back title="Saúde da Loja" subtitle="Ruptura, parados e qualidade de dados" />
```

- [ ] **Step 2: Acrescentar a qualidade de dados**

A tela hoje carrega apenas `api.getProductAnalysis`. Acrescentar:

```typescript
  const { data: qualidade } = useData<DataQuality>(api.getDataQuality)
```

E exibir o score no topo do corpo, usando o componente `ScoreBar` que já existe
em `components/Analytics`:

```tsx
          {qualidade && (
            <div style={{ marginBottom: 14, padding: 14, borderRadius: 14, background: 'var(--bg-1)', border: '1px solid var(--line-1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 8 }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-2)' }}>Qualidade do cadastro</span>
                <span className="tnum" style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-1)' }}>{qualidade.score}%</span>
              </div>
              <ScoreBar value={qualidade.score} />
              <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 6 }}>
                {qualidade.total_issues} inconsistência{qualidade.total_issues !== 1 ? 's' : ''} detectada{qualidade.total_issues !== 1 ? 's' : ''}
              </div>
            </div>
          )}
```

- [ ] **Step 3: Remover o botão que levava à análise de marketing**

Na linha 193, o `Btn` com `icon={Ico.sparkle}` e texto sobre marketing navega para
`an-marketing-intel`. Apagar o botão inteiro — o conteúdo dele agora vive em
Produtos e em Estoque & Compras.

- [ ] **Step 4: Verificar que o build passa**

```bash
cd frontend_pwa && npm run build
```

Esperado: sem erros.

- [ ] **Step 5: Verificar no navegador**

Abrir Inteligência → Saúde da Loja. Conferir que o score de qualidade aparece no
topo, que as listas de ruptura e parados continuam funcionando, que os atalhos
para o Operacional continuam navegando, e que não há mais botão de marketing.

- [ ] **Step 6: Commit**

```bash
git add frontend_pwa/src/screens/intel/Health.tsx
git commit -m "feat(pwa): tela Saude da Loja absorve a qualidade de dados"
```

---

## Task 12: Apagar as telas órfãs e fechar a navegação

**Files:**
- Delete: `frontend_pwa/src/screens/intel/TopProducts.tsx`
- Delete: `frontend_pwa/src/screens/intel/BySize.tsx`
- Delete: `frontend_pwa/src/screens/intel/Suggestions.tsx`
- Delete: `frontend_pwa/src/screens/intel/MarketingIntel.tsx`
- Modify: `frontend_pwa/src/nav.tsx`
- Modify: `frontend_pwa/src/App.tsx`

**Interfaces:**
- Consumes: das tasks 9 e 10, o conteúdo de `TopProducts.tsx`, `BySize.tsx` e
  `MarketingIntel.tsx` já reaproveitado nas telas novas.
- Produces: o enum `ScreenId` final, com trinta entradas.

- [ ] **Step 1: Confirmar que o conteúdo já foi reaproveitado**

Antes de apagar, conferir que a seção "Ranking" de `Products.tsx` reproduz o que
`TopProducts.tsx` mostrava, que a seção "Tamanhos" reproduz `BySize.tsx`, e que
as listas de `Stock.tsx` cobrem o que `MarketingIntel.tsx` exibia.
`Suggestions.tsx` não precisa de conferência: consome o mesmo endpoint que
`Stock.tsx` já consome.

- [ ] **Step 2: Apagar os quatro arquivos**

```bash
git rm frontend_pwa/src/screens/intel/TopProducts.tsx \
       frontend_pwa/src/screens/intel/BySize.tsx \
       frontend_pwa/src/screens/intel/Suggestions.tsx \
       frontend_pwa/src/screens/intel/MarketingIntel.tsx
```

- [ ] **Step 3: Fechar o enum `ScreenId` em `src/nav.tsx`**

A linha provisória da Task 7 com as quatro telas órfãs é removida. O bloco da aba
fica:

```typescript
  | 'intel-overview' | 'intel-health' | 'intel-products' | 'intel-category-detail'
  | 'intel-stock' | 'intel-finance' | 'intel-channels'
```

- [ ] **Step 4: Limpar `src/App.tsx`**

Apagar os quatro imports (`TopProducts`, `BySize`, `Suggestions`,
`MarketingIntel`) e as quatro entradas correspondentes do mapa `screens`.

- [ ] **Step 5: Conferir a contagem de `ScreenId`**

```bash
grep -c "|" frontend_pwa/src/nav.tsx
```

Contar manualmente as entradas do tipo `ScreenId`: devem ser vinte e nove — `login`,
onze de `op`, sete de `intel` e dez de `mais`.

- [ ] **Step 6: Verificar que o build passa**

```bash
cd frontend_pwa && npm run build
```

Esperado: sem erros.

- [ ] **Step 7: Commit**

```bash
git add -A frontend_pwa
git commit -m "chore(pwa): apaga telas orfas e fecha o enum de navegacao"
```

---

## Task 13: Verificação da fase

**Files:** nenhum arquivo de código. Esta task é de verificação e execução direta,
sem par implementador e revisor.

**Interfaces:**
- Consumes: tudo das tasks 1 a 12.
- Produces: evidência de que a Fase 1 está completa.

- [ ] **Step 1: Subir o ambiente do zero**

```bash
docker compose down -v
docker compose up -d
docker compose ps
```

Esperado: os serviços `db`, `backend` e `frontend_pwa` no ar. Nenhum container de
LLM na lista.

- [ ] **Step 2: Aplicar as migrations em banco limpo**

```bash
docker exec lgd_mantos alembic upgrade head
```

Esperado: a cadeia `0001` até `0005` aplica sem erro.

- [ ] **Step 3: Confirmar que a API responde**

```bash
curl -s http://localhost:8000/
```

Esperado: `{"status":"ok","service":"LGD Mantos API"}`.

- [ ] **Step 4: Confirmar que as rotas de agents sumiram**

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/agents/runs
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/analytics/marketing-intelligence
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/analytics/agent-context
```

Esperado: `404` nas três.

- [ ] **Step 5: Confirmar que a classificação de produtos responde**

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password":"SENHA_DO_ENV"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")
curl -s http://localhost:8000/api/v1/analytics/product-classification \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool | head -5
```

Esperado: JSON com as cinco chaves novas (`alta_saida_estoque_saudavel`,
`margem_alta`, `baixa_saida_estoque_alto`, `estoque_critico`, `sem_estoque`).
Substituir `SENHA_DO_ENV` pelo valor de `APP_PASSWORD` no arquivo `.env`.

- [ ] **Step 6: Rodar a suíte de testes completa**

```bash
cd backend && pytest -v
```

Esperado: verde, e com contagem maior que zero. Uma suíte vazia reprova a fase.

- [ ] **Step 7: Navegar pelas sete telas no PWA**

Abrir `http://localhost:5173`, entrar, e percorrer: Visão Geral → Produtos (as
três seções) → detalhe de uma categoria → voltar → Estoque & Compras →
Financeiro → Canais → Saúde da Loja. Nenhuma tela em branco, nenhum erro no
console do navegador.

- [ ] **Step 8: Confirmar a barra de abas com três alvos**

Visualmente: Operação, Inteligência, Mais. Sem Marketing.

- [ ] **Step 9: Atualizar o grafo de conhecimento**

```bash
graphify update .
```

- [ ] **Step 10: Commit final da fase**

```bash
git add -A
git commit -m "chore(graphify): atualiza grafo apos a Fase 1 da reformulacao"
```

---

## Verificações que reprovam a fase

Qualquer uma destas condições significa que a Fase 1 não está pronta:

- `pytest` reporta zero testes coletados.
- Alguma rota sob `/api/v1/agents/` responde algo diferente de 404.
- `grep -rni "ollama\|agno" --include=* .` retorna algo fora dos dois documentos
  históricos.
- `npm run build` falha.
- Alguma das sete telas da aba Inteligência fica inalcançável a partir da Visão
  Geral — foi o defeito original de `top-products`, `by-size` e `suggestions`, e
  não pode se repetir.
- O enum `ScreenId` tem mais de vinte e nove entradas.
