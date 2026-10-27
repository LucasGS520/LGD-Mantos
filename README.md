# LGD Mantos

Sistema interno de gestão da loja LGD Mantos. A aplicação reúne cadastro de produtos, estoque, compras, vendas, despesas e análises. Os fluxos de marketing estão preservados para uma futura integração com IA externa.

## O que existe hoje

| Camada | Implementação |
| --- | --- |
| Interface | Frontend web com React 18, TypeScript e Vite em `frontend/` |
| API | FastAPI em `backend/`, rotas sob `/api/v1` |
| Dados | PostgreSQL 16, SQLAlchemy assíncrono e migrações Alembic |
| Marketing | Fluxos de campanhas e aprovação preservados; geração automática aguarda provedor externo de IA |
| Ambiente local | Docker Compose com PostgreSQL, API e frontend |

Os módulos da API ficam em `backend/app/modules/`: `auth`, `operational`, `analytics`, `agents`, `settings`, `system` e `export`. Modelos e schemas compartilhados ficam em `backend/app/shared/`. As telas web ficam em `frontend/src/screens/`.

## Verificação

```text
cd frontend && npm ci && npm run build
cd backend && pip install -r requirements.txt && pytest -q
```

Os testes do backend cobrem principalmente os fluxos de agentes e aprovação. Ainda faltam testes automatizados para boa parte das rotas operacionais, análises, configurações e exportação. Não há pipeline de CI versionado neste repositório.

## Dados e backups

A tela **Mais → Configurações** exporta relatórios CSV resumidos, individualmente ou em ZIP. Eles servem para consulta e **não restauram o banco**: itens de vendas e compras, vínculos e outros dados não estão completos nesses arquivos. O backup operacional deve incluir o PostgreSQL e o volume de uploads (`uploads_data`), com rotina de restauração testada.

## Referências

- `graphify-out/`: grafo local gerado para navegação com `graphify .`; a pasta não é versionada.
