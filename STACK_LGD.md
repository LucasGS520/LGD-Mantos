# Stack e mapa do código

| Área | Tecnologia | Entrada principal |
| --- | --- | --- |
| Frontend | React 18, TypeScript, Vite, Vite PWA, Recharts | `frontend_pwa/src/main.tsx`, `App.tsx` |
| API | Python 3.11+, FastAPI, Pydantic | `backend/main.py` |
| Persistência | PostgreSQL 16, SQLAlchemy async, Alembic | `backend/app/core/database.py`, `backend/migrations/` |
| IA de marketing | Agno, Ollama | `backend/app/modules/agents/` |
| Implantação | Docker Compose, Caddy | `docker-compose.prod.yml`, `deploy/` |

## Fluxo principal

O PWA chama a API em `/api/v1` com token de sessão. As rotas de `operational` registram e consultam cadastros, estoque, entradas, vendas e despesas. As rotas de `analytics` calculam indicadores a partir desses dados. O módulo `agents` usa o contexto operacional para propostas de marketing, mantendo aprovação humana nos fluxos de publicação. `settings` armazena limiares de alerta; `system` expõe o estado da API e do banco; `export` gera relatórios CSV para consulta.

## Limites atuais

- `README.md` descreve o início local, verificações e o limite dos CSVs.
- A cobertura automatizada é concentrada em agentes; não comprova todos os módulos.
- Os relatórios ZIP/CSV não constituem backup restaurável.
- `graphify-out/` é saída gerada localmente e não é mantida no Git.
