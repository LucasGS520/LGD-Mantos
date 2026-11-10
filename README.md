# LGD Mantos

Central interna de um único dono para catálogo, inventário, estoque, compras,
vendas, recebimentos e gestão. React/TypeScript/Vite, FastAPI/Python 3.12,
SQLAlchemy assíncrono, PostgreSQL 16 e Alembic; produção com Docker Compose e Caddy.

## Uso

1. Cadastre fornecedores, categorias, canais e formas de pagamento em Mais.
2. Cadastre produtos e variantes por tamanho/cor.
3. Confirme o inventário físico conhecido, sem inventar custos ausentes.
4. Registre compras, vendas, recebimentos e ajustes quando acontecerem.
5. Consulte a gestão e siga os vínculos aos registros de origem.

Vender retira estoque mesmo sem recebimento. Correções exigem motivo e prévia
de impacto; anulações preservam histórico. Custo desconhecido não significa zero.

## Ambiente local

Copie `.env.example` para `.env` e preencha senhas e conexões distintas de
`lgd_app`, `lgd_migrator` e bootstrap, além de `APP_PASSWORD` e `APP_SECRET`.
No Docker, o host PostgreSQL é `db`. Não há segredo padrão de produção.

```sh
docker compose build backend migrate bootstrap
docker compose up -d db
docker compose run --rm bootstrap
docker compose run --rm migrate
docker compose up -d backend frontend
```

Interface: `http://localhost:5173`; API: `http://localhost:8000/api/v1`;
documentação HTTP: `http://localhost:8000/api/docs`.

A baseline 0007 instala 15 tabelas de negócio mais o controle do Alembic. Base
antiga é recusada; a reconstrução explícita está no Deploy. A API não migra ou
limpa dados ao iniciar e a instalação não confirma inventário.

## Verificação

Crie o banco dedicado `lgd_mantos_alignment_test`; o bootstrap provisiona as
roles, não cria o banco. Defina `TEST_DATABASE_URL` usando `lgd_app` e `TEST_MIGRATION_DATABASE_URL`
usando `lgd_migrator`, com o mesmo banco/host. Para o bootstrap, use uma
`BOOTSTRAP_DATABASE_URL` específica do teste e senhas correspondentes às URLs.

```sh
docker exec lgd_db psql -U postgres -d postgres -c "CREATE DATABASE lgd_mantos_alignment_test"
python -m pip install -r backend/requirements-dev.txt
python backend/bootstrap_database.py
python -m ruff check backend deploy
python backend/check_boundaries.py
python backend/check.py
cd frontend
npm ci
npm run build
npm run lint
npm run check:boundaries
npm test
npx playwright install chromium
```

Depois da suíte backend, execute na raiz, em outro terminal:

```sh
python backend/check.py --serve
```

Em `frontend/`, execute `npm run test:e2e`. Usa API 8001, Vite 5174 e fotos
temporárias. Não execute suítes/carga simultaneamente na mesma base. Antes de
repetir E2E, execute os testes backend para limpar seus registros. CI segue essa ordem.

Testes puros sem banco: `python -m pytest -c backend/pytest.ini backend/tests/unit`.
Testes de componentes/hooks ficam junto aos módulos frontend; jornadas ficam em
`frontend/e2e`. Traces locais Windows são opcionais com `E2E_TRACE=1`.

## Organização e higiene

Backend: `app/modules` por capacidade e `app/shared` para modelos/mecanismos
transversais. Frontend: `src/modules`, `src/shared` e composição em `src/app`.
Fronteiras/ciclos são verificados automaticamente.

Dependências instaladas, caches, builds, logs, grafos e resultados de ensaio
são locais e ignorados pelo Git. Guarde novas saídas de medições em `.verification/`;
essa pasta não é destino de backup operacional. Nunca versionar segredos ou uploads.
Mantenha as cinco referências documentais atualizadas, consolidando alterações
nos arquivos existentes em vez de criar um relatório permanente por tarefa.
