# LGD Mantos

Sistema mobile-first de gestao operacional interna para a loja LGD Mantos.

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

O app mobile nunca acessa o banco diretamente.

## Modulos

### Operacional

Responsavel por produtos, categorias, variantes/tamanhos, fornecedores, estoque, vendas, compras, despesas e imagens.

### Analise

Responsavel por dashboard, DRE, lucro, margem, CMV, giro, top produtos, tamanhos mais vendidos, alertas e sugestoes de compra. Este modulo consulta e calcula, mas nao altera dados operacionais.

### Marketing

Responsavel por descricoes, copys, campanhas e sugestoes comerciais baseadas em produtos, estoque e vendas. Este modulo usa IA e nao altera estoque, vendas, compras ou produtos.

## Subir backend

Configure `.env` na raiz:

```env
DATABASE_URL=postgresql+asyncpg://postgres:lgdmantos123@db:5432/lgd_mantos
APP_PASSWORD=minhaloja123
APP_SECRET=dev-secret-change-in-production
ANTHROPIC_API_KEY=
```

Suba os servicos:

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

O app usa por padrao `http://localhost:8000/api/v1`.

## IA

Todos os modulos devem consumir a IA pelo servico central:

```python
AIService.generate(...)
```

A IA pode gerar texto, explicar dados e sugerir acoes, mas nao executa alteracoes operacionais sozinha.
