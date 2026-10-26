# LGD Mantos

Sistema interno de gestão da loja LGD Mantos. A aplicação reúne cadastro de produtos, estoque, compras, vendas, despesas, análises e operações de marketing assistidas por IA.

## O que existe hoje

| Camada | Implementação |
| --- | --- |
| Interface | PWA React 18, TypeScript e Vite em `frontend_pwa/` |
| API | FastAPI em `backend/`, rotas sob `/api/v1` |
| Dados | PostgreSQL 16, SQLAlchemy assíncrono e migrações Alembic |
| IA | Agentes de marketing com Agno e Ollama, com aprovação humana para publicação |
| Produção | Docker Compose, Caddy como proxy HTTPS e servidor do PWA |

Os módulos da API ficam em `backend/app/modules/`: `auth`, `operational`, `analytics`, `agents`, `settings`, `system` e `export`. Modelos e schemas compartilhados ficam em `backend/app/shared/`. As telas do PWA ficam em `frontend_pwa/src/screens/`.

## Desenvolvimento local

1. Copie `.env.example` para `.env` e defina `DATABASE_URL`, `POSTGRES_PASSWORD`, `APP_PASSWORD` e `APP_SECRET`. A senha da URL do banco deve ser igual a `POSTGRES_PASSWORD`.
2. Inicie os serviços com `docker compose up --build`. Na primeira inicialização, o Ollama baixa o modelo configurado; isso pode demorar.
3. Abra `http://localhost:5173`. A documentação da API está em `http://localhost:8000/api/docs`.

O Compose de desenvolvimento executa `backend/init_db.py` ao iniciar. Para migrações explícitas, use Alembic em `backend/`; revise o estado do banco antes de aplicar migrações em produção. O Compose de produção está em `docker-compose.prod.yml` e requer `DOMAIN` e `CORS_ORIGINS` configurados.

## Verificação

```text
cd frontend_pwa && npm ci && npm run build
cd backend && pip install -r requirements-dev.txt && pytest -q
```

Os testes do backend cobrem principalmente os fluxos de agentes e aprovação. Ainda faltam testes automatizados para boa parte das rotas operacionais, análises, configurações e exportação. Não há pipeline de CI versionado neste repositório.

## Dados e backups

A tela **Mais → Configurações** exporta relatórios CSV resumidos, individualmente ou em ZIP. Eles servem para consulta e **não restauram o banco**: itens de vendas e compras, vínculos e outros dados não estão completos nesses arquivos. O backup operacional deve incluir o PostgreSQL e o volume de uploads (`uploads_data`), com rotina de restauração testada.

## Referências

- `STACK_LGD.md`: componentes e pontos de entrada.
- `specs/`: especificações de funcionalidades.
- `docs/`: decisões e planos históricos; confirme a implementação no código.
- `graphify-out/`: grafo local gerado para navegação com `graphify .`; a pasta não é versionada.
