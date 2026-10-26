# LGD Mantos

Sistema interno de gestão da loja LGD Mantos. A aplicação reúne cadastro de produtos, estoque, compras, vendas, despesas e análises. Os fluxos de marketing estão preservados para uma futura integração com IA externa.

## O que existe hoje

| Camada | Implementação |
| --- | --- |
| Interface | PWA React 18, TypeScript e Vite em `frontend_pwa/` |
| API | FastAPI em `backend/`, rotas sob `/api/v1` |
| Dados | PostgreSQL 16, SQLAlchemy assíncrono e migrações Alembic |
| Marketing | Fluxos de campanhas e aprovação preservados; geração automática aguarda provedor externo de IA |
| Produção | Docker Compose, Caddy como proxy HTTPS e servidor do PWA |

Os módulos da API ficam em `backend/app/modules/`: `auth`, `operational`, `analytics`, `agents`, `settings`, `system` e `export`. Modelos e schemas compartilhados ficam em `backend/app/shared/`. As telas do PWA ficam em `frontend_pwa/src/screens/`.

## Verificação

```text
cd frontend_pwa && npm ci && npm run build
cd backend && pip install -r requirements-dev.txt && pytest -q
```

Os testes do backend cobrem principalmente os fluxos de agentes e aprovação. Ainda faltam testes automatizados para boa parte das rotas operacionais, análises, configurações e exportação. Não há pipeline de CI versionado neste repositório.

## Dados e backups

A tela **Mais → Configurações** exporta relatórios CSV resumidos, individualmente ou em ZIP. Eles servem para consulta e **não restauram o banco**: itens de vendas e compras, vínculos e outros dados não estão completos nesses arquivos. O backup operacional deve incluir o PostgreSQL e o volume de uploads (`uploads_data`), com rotina de restauração testada.

## Referências

- `specs/`: especificações de funcionalidades.
- `docs/AGENTES_MARKETING_SPEC.md`: especificação de produto para a futura integração de IA externa.
- `graphify-out/`: grafo local gerado para navegação com `graphify .`; a pasta não é versionada.
