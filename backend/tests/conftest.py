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
    # Trava de segurança: a suíte trunca tabelas antes de cada teste. Se a
    # DATABASE_URL resolvida apontar para qualquer banco que não seja o de
    # testes, abortar antes de tocar em qualquer dado — um .env de
    # desenvolvimento carregado pelo shell faria a suíte apagar dados reais.
    from app.core.config import settings

    if "lgd_mantos_test" not in settings.DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL nao aponta para o banco de testes: "
            f"{settings.DATABASE_URL!r}. A suite trunca tabelas antes de cada "
            "teste e recusa rodar fora de 'lgd_mantos_test'."
        )

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
    """Trunca as tabelas usadas nos testes antes de cada caso — isolamento total.

    `sales`/`sale_items` entraram na lista na Fase 2: os testes de comparação
    de período (`?compare=true`) inserem vendas com datas específicas, e sem
    truncar elas se acumulariam a cada execução da suíte, contaminando o
    período "atual" de rodadas futuras. `categories` entrou junto com o teste
    de comparação de `categories/performance`, que cria categoria própria — o
    nome é `unique`, então sem truncar a segunda execução da suíte falharia
    na criação por duplicidade.
    """
    from app.core.database import engine

    async with engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE product_variants, products, sale_items, sales, categories, expenses RESTART IDENTITY CASCADE"
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


async def create_sale(db, sold_at, total=100.0, sale_channel_id=None):
    """Cria uma venda avulsa (sem itens) numa data específica.

    Usado pelos testes de comparação de período — não precisa de `SaleItem`
    porque `sales_by_channel` só lê `Sale`/`SaleChannel`.
    """
    from app.shared.models.operations import Sale

    sale = Sale(sold_at=sold_at, total=total, sale_channel_id=sale_channel_id)
    db.add(sale)
    await db.commit()
    return sale


async def create_expense(db, date, amount=100.0, category="Teste"):
    """Cria uma despesa numa data específica (string "YYYY-MM-DD").

    Usado pelos testes de janela do dashboard — `Expense.date` é string de
    dia (sem hora), então plantar nas bordas exatas é o jeito de travar
    regressão de teto assimétrico entre o lado atual e o anterior.
    """
    from app.shared.models.operations import Expense

    despesa = Expense(date=date, category=category, amount=amount)
    db.add(despesa)
    await db.commit()
    return despesa


async def create_category_sale(
    db, sold_at, category_name, quantity=1, unit_price=199.9, unit_cost=80.0
):
    """Cria uma venda completa (Sale -> SaleItem -> ProductVariant -> Product
    -> Category) numa categoria específica.

    Diferente de `create_sale`, que só grava `Sale` — `category_performance`
    precisa da cadeia inteira até `Category`, já que o repositório faz join
    por `Product.category_id`. Reaproveita a categoria se ela já existir
    (nome é `unique` no schema).
    """
    from sqlalchemy import select

    from app.shared.models.catalog import Category, Product, ProductVariant
    from app.shared.models.common import uid
    from app.shared.models.operations import Sale, SaleItem

    categoria = (
        await db.execute(select(Category).where(Category.name == category_name))
    ).scalar_one_or_none()
    if categoria is None:
        categoria = Category(name=category_name)
        db.add(categoria)
        await db.flush()

    product = Product(
        sku=f"SKU-{uid()}",
        name=category_name,
        category_id=categoria.id,
        cost_price=unit_cost,
        sale_price=unit_price,
    )
    db.add(product)
    await db.flush()
    variant = ProductVariant(product_id=product.id, size="M", stock_quantity=10)
    db.add(variant)
    await db.flush()

    sale = Sale(sold_at=sold_at, total=round(unit_price * quantity, 2))
    db.add(sale)
    await db.flush()
    db.add(SaleItem(
        sale_id=sale.id, variant_id=variant.id,
        quantity=quantity, unit_price=unit_price, unit_cost=unit_cost,
    ))
    await db.commit()
    return categoria
