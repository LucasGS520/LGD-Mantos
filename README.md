# LGD Mantos

Sistema web-first de gestão operacional interna para a loja LGD Mantos.

Este repositório reúne a API, o frontend web e a infraestrutura local necessários
para centralizar produtos, estoque, vendas, compras, despesas, análises e apoio
de IA em uma única base de dados.

## Arquitetura oficial

- Backend: FastAPI
- Banco: PostgreSQL
- Frontend oficial: PWA React (Vite)
- Infra local: Docker Compose
- IA: camada transversal em `backend/app/core/ai`

Fluxo oficial:

```txt
PWA React -> FastAPI -> PostgreSQL
```

O frontend nunca acessa o banco diretamente; toda leitura e escrita passa pela API.

## Módulos

### Operacional

Responsável por produtos, categorias, variantes/tamanhos, fornecedores, estoque,
vendas, compras, despesas e imagens.

### Análise

Responsável por dashboard, DRE, lucro, margem, CMV, giro, top produtos,
tamanhos mais vendidos, alertas e sugestões de compra. Este módulo consulta e
calcula, mas não altera dados operacionais.

### Marketing

Responsável por descrições, copys, campanhas e sugestões comerciais baseadas em
produtos, estoque e vendas. Este módulo usa IA e não altera estoque, vendas,
compras ou produtos.

## Subir backend

Configure `.env` na raiz:

```env
DATABASE_URL=postgresql+asyncpg://postgres:lgdmantos123@db:5432/lgd_mantos
APP_PASSWORD=minhaloja123
APP_SECRET=dev-secret-change-in-production
ANTHROPIC_API_KEY=
```

Suba os serviços:

```bash
docker compose up --build
```

API:

- Backend: `http://localhost:8000`
- OpenAPI: `http://localhost:8000/api/docs`

## Deploy no Render

Erro comum de deploy:

```txt
socket.gaierror: [Errno -2] Name or service not known
```

Esse erro normalmente indica que o host definido em `DATABASE_URL` não existe
no ambiente do Render (por exemplo, `@db:5432`, que funciona apenas no
`docker-compose` local).

Configuração recomendada no serviço Web do Render:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
APP_PASSWORD=<senha-forte>
APP_SECRET=<secret-forte>
ANTHROPIC_API_KEY=
```

Notas:

- Use a URL do PostgreSQL criada no Render (Internal/External Database URL).
- Se a URL vier como `postgres://...`, troque para `postgresql+asyncpg://...`.
- Em produção no Render, mantenha `sslmode=require`.

## IA

Todos os módulos devem consumir a IA pelo serviço central:

```python
AIService.generate(...)
```

A IA pode gerar texto, explicar dados e sugerir ações, mas não executa
alterações operacionais sozinha.
