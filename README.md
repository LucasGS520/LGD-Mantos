# LGD Mantos

Sistema mobile-first de gestão operacional interna para a loja LGD Mantos.

Este repositório reúne a API, o app mobile e a infraestrutura local necessários
para centralizar produtos, estoque, vendas, compras, despesas, análises e apoio
de IA em uma única base de dados.

## Arquitetura oficial

- Backend: FastAPI
- Banco: PostgreSQL
- Frontend oficial: app mobile Kivy
- Infra local: Docker Compose
- IA: camada transversal em `backend/app/core/ai`

Fluxo oficial:

```txt
Kivy App -> API Client -> FastAPI -> PostgreSQL
```

O app mobile nunca acessa o banco diretamente; toda leitura e escrita passa pela API.

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

## Rodar app Kivy

Em outro terminal:

```bash
cd frontend_mobile
python -m pip install -r requirements.txt
python main.py
```

O app usa por padrão `http://localhost:8000/api/v1`.

## IA

Todos os módulos devem consumir a IA pelo serviço central:

```python
AIService.generate(...)
```

A IA pode gerar texto, explicar dados e sugerir ações, mas não executa
alterações operacionais sozinha.
