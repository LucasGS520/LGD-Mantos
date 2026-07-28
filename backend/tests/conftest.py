"""Configuração compartilhada dos testes da camada de agentes.

Estratégia de banco:
- Usa um banco Postgres de TESTE isolado (`lgd_mantos_test`) no mesmo container
  Docker de desenvolvimento (porta 55432) — os modelos usam JSONB, então SQLite
  em memória não é compatível.
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
os.environ.setdefault("OLLAMA_URL", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "llama3.1:8b")

import asyncpg
import pytest_asyncio
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
    import app.modules.agents.knowledge.models  # noqa: F401
    import app.modules.agents.marketing_ops.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(_prepare_database):
    """Trunca as tabelas usadas nos testes antes de cada caso — isolamento total."""
    from app.core.database import engine

    async with engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE agent_runs, campaigns, posts, creative_briefs, approvals, "
            "publishing_queue, knowledge_documents, product_variants, products "
            "RESTART IDENTITY CASCADE"
        ))
    yield


@pytest_asyncio.fixture
async def db():
    """Sessão async do banco de teste para uso direto nos testes."""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        yield session


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


async def create_campaign_bundle(db, product=None, status="pending_approval"):
    """Cria AgentRun + Campaign + Post + CreativeBrief + Approval pendente."""
    from app.modules.agents.marketing_ops.models import (
        AgentRun, Approval, Campaign, CreativeBrief, Post,
    )

    run = AgentRun(objective="Teste", status="completed")
    db.add(run)
    await db.flush()

    campaign = Campaign(
        agent_run_id=run.id,
        name="Campanha Teste",
        objective="Testar o ciclo de aprovação",
        product_id=product.id if product else None,
        channel="Instagram",
        format="feed",
        angle="Ângulo de teste",
        cta="Chama na DM",
        risk_level="low",
        status=status,
    )
    db.add(campaign)
    await db.flush()

    post = Post(
        campaign_id=campaign.id,
        caption="Legenda original",
        headline="Headline original",
        cta_text="CTA original",
        format="feed",
        copy_variations=[],
        status=status,
    )
    brief = CreativeBrief(
        campaign_id=campaign.id,
        visual_briefing="Briefing original",
        image_prompt="Prompt original",
        status=status,
    )
    db.add_all([post, brief])
    await db.flush()

    approval = Approval(campaign_id=campaign.id, status="pending")
    db.add(approval)
    await db.commit()
    for obj in (run, campaign, post, brief, approval):
        await db.refresh(obj)
    return run, campaign, post, brief, approval
