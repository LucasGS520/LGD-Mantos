# Graph Report - LGD-Mantos  (2026-09-12)

## Corpus Check
- 141 files · ~174,706 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1237 nodes · 2854 edges · 68 communities (52 shown, 12 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 192 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6128d306`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Product
- Chrome.tsx
- catalog_routes.py
- CategoryAnalysisService
- Channels.tsx
- Blueprint LGD Mantos — de três módulos para Operação + Inteligência
- Fase 1 — Fundação Limpa: Implementation Plan
- repositories.py
- SalesHistory.tsx
- CatalogService
- Expense
- shared/schemas/__init__.py
- analytics/schemas/__init__.py
- StockMoves.tsx
- types.ts
- CategoryCreate
- auth.py
- ExportService
- database.py
- nav.tsx
- devDependencies
- UI.tsx
- sales_routes.py
- schemas/catalog.py
- compilerOptions
- SupplierCreate
- do_run_migrations
- Settings
- EntryForm.tsx
- routes/products.py
- verify_token
- get_db
- routes/data_quality.py
- product_classification.py
- settings/routes.py
- compilerOptions
- channels.py
- schemas/operations.py
- main.py
- .create_product
- expense_routes.py
- test_analytics_contracts.py
- pwa.ts
- list_stock_history
- Consolidação da Base de Código — 2026-07-16
- App.tsx
- ProductUpdate
- Spec — Bloco App da seção Mais
- test_agents_removed.py
- 0005_remove_marketing.py
- Sale
- Regras, Instruções de Execução e Uso de Tools (NÃO IGNORAR)
- vite.config.ts
- tsconfig.json
- core/__init__.py
- app/__init__.py
- analytics/__init__.py
- auth/__init__.py
- export/__init__.py
- modules/__init__.py
- settings/__init__.py
- system/__init__.py
- shared/__init__.py
- VariantIn

## God Nodes (most connected - your core abstractions)
1. `useNav()` - 53 edges
2. `CatalogService` - 41 edges
3. `Product` - 39 edges
4. `ProductVariant` - 37 edges
5. `Sale` - 35 edges
6. `AppBar()` - 29 edges
7. `fmtBRL()` - 29 edges
8. `useData()` - 29 edges
9. `api` - 29 edges
10. `ScreenBody()` - 28 edges

## Surprising Connections (you probably didn't know these)
- `Serviço web — Caddy (PWA + reverse proxy + HTTPS)` --shares_data_with--> `index.html — entrypoint do PWA LGD Mantos`  [INFERRED]
  docker-compose.prod.yml → frontend_pwa/index.html
- `Verificação manual ponta a ponta (seção 11)` --conceptually_related_to--> `FASE A — Validação E2E com Ollama real + Seed de Knowledge (concluída)`  [INFERRED]
  FABLE_CONSOLIDACAO_2026-07-16.md → docs/plans/PLAN-20260716-1846-consolidacao-agentes-marketing.md
- `Serviço ollama — inferência local llama3.1:8b` --shares_data_with--> `agno==2.6.19 (framework de agentes)`  [INFERRED]
  docker-compose.prod.yml → backend/requirements.txt
- `Estrutura Alembic (migrations de schema)` --references--> `alembic==1.18.5 (migrations)`  [EXTRACTED]
  FABLE_CONSOLIDACAO_2026-07-16.md → backend/requirements.txt
- `Serviço ollama — inferência local llama3.1:8b` --shares_data_with--> `ollama==0.6.2 (cliente Ollama)`  [INFERRED]
  docker-compose.prod.yml → backend/requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **As três telas do bloco APP da seção Mais** — specs_bloco_app_mais_spec_configuracoes, specs_bloco_app_mais_spec_status_sistema, specs_bloco_app_mais_spec_sobre_app [EXTRACTED 1.00]
- **Fases do plano de consolidação da camada multi-agente de marketing** — docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fase0, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasea, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_faseb, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasec, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasee1, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fased, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasee2, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasee3 [EXTRACTED 1.00]

## Communities (68 total, 12 thin omitted)

### Community 0 - "Product"
Cohesion: 0.06
Nodes (71): count_active_products(), count_active_variants(), expenses_no_category(), products_no_category(), products_no_cost_price(), products_no_photo(), products_no_sale_price(), products_no_supplier() (+63 more)

### Community 1 - "Chrome.tsx"
Cohesion: 0.12
Nodes (35): AppBar(), AppBarProps, FAB(), FABProps, IcoFn, OP_TABS, OpScreen, OpSubNav() (+27 more)

### Community 2 - "catalog_routes.py"
Cohesion: 0.15
Nodes (22): get_category(), get_channel(), get_product(), get_supplier(), list_categories(), list_channels(), list_products(), list_suppliers() (+14 more)

### Community 3 - "CategoryAnalysisService"
Cohesion: 0.08
Nodes (40): category_buying_patterns(), category_performance(), category_size_distribution(), category_size_stock(), category_stock_coverage(), product_attribute_analysis(), AsyncSession, get (+32 more)

### Community 4 - "Channels.tsx"
Cohesion: 0.08
Nodes (25): AlertRow(), AlertRowProps, MetricInfo(), MetricInfoProps, NavItem(), Period, PERIODS, PeriodSelect() (+17 more)

### Community 5 - "Blueprint LGD Mantos — de três módulos para Operação + Inteligência"
Cohesion: 0.07
Nodes (29): 1. Problema, 2. Decisões, 3.1 Dois pilares, 3.2 Navegação, 3.3 Backend: o módulo `intelligence`, 3.4 O Sinal, 3.5 Endpoints, 3.6 Comparação de períodos (+21 more)

### Community 6 - "Fase 1 — Fundação Limpa: Implementation Plan"
Cohesion: 0.10
Nodes (19): Achado: três telas órfãs, Decisão tomada neste plano (refinamento da spec), Estrutura de arquivos, Fase 1 — Fundação Limpa: Implementation Plan, Global Constraints, Task 10: Tela Estoque & Compras (`intel-stock`), Task 11: Tela Saúde da Loja (`intel-health`), Task 12: Apagar as telas órfãs e fechar a navegação (+11 more)

### Community 7 - "repositories.py"
Cohesion: 0.07
Nodes (45): get_category(), get_channel(), get_entry(), get_expense(), get_product(), get_product_by_sku(), get_product_variant(), get_sale() (+37 more)

### Community 8 - "SalesHistory.tsx"
Cohesion: 0.12
Nodes (16): ChannelChip(), KPI(), PhotoPlaceholder(), fmtDate(), VariantInfo, fmtDateTime(), VariantInfo, CartItem (+8 more)

### Community 9 - "CatalogService"
Cohesion: 0.09
Nodes (29): create_channel(), deactivate_product(), delete_category(), delete_photo(), delete_supplier(), delete_variant(), delete, Desativa um fornecedor pelo ID (soft delete). (+21 more)

### Community 10 - "Expense"
Cohesion: 0.20
Nodes (15): expenses_by_category(), expenses_total(), monthly_cogs_evolution(), monthly_expenses_evolution(), monthly_revenue_evolution(), AsyncSession, datetime, Consultas financeiras sobre despesas. (+7 more)

### Community 11 - "shared/schemas/__init__.py"
Cohesion: 0.10
Nodes (32): create_entry(), get_entry(), list_entries(), AsyncSession, get, post, Rotas HTTP para entrada de mercadoria., Registra entrada de mercadoria, criando produtos e variantes inline. (+24 more)

### Community 12 - "analytics/schemas/__init__.py"
Cohesion: 0.12
Nodes (29): DailyRevenue, DashboardResponse, BaseModel, Contratos de resposta do dashboard executivo., DataQualityIssues, DataQualityResponse, ExpenseIssue, ProductIssue (+21 more)

### Community 13 - "StockMoves.tsx"
Cohesion: 0.14
Nodes (14): BottomNav(), IconBaseProps, IcoProps, Tabs(), ItemProps, ALL_MOVE_META, fmtMoveDate(), HIST_TAB_TYPE (+6 more)

### Community 14 - "types.ts"
Cohesion: 0.07
Nodes (31): CovBadge(), SECOES, classify(), EnrichedPattern, GROUP_META, GroupId, Signal, BASE (+23 more)

### Community 15 - "CategoryCreate"
Cohesion: 0.21
Nodes (10): create_category(), put, Cria uma categoria no catálogo., Atualiza nome e descrição de uma categoria existente., update_category(), Category, Cria uma categoria de produto., Atualiza nome e descrição de uma categoria existente. (+2 more)

### Community 16 - "auth.py"
Cohesion: 0.22
Nodes (9): create_token(), Funções simples de autenticação baseada em token JWT., Cria um token de acesso para o usuário proprietário do sistema., Configurações carregadas do ambiente para o backend., login(), post, LoginIn, BaseModel (+1 more)

### Community 17 - "ExportService"
Cohesion: 0.12
Nodes (22): export_backup(), export_dataset(), AsyncSession, get, Rotas de exportação de dados — backup manual do operador em CSV/ZIP., Baixa um .zip com um CSV por conjunto — backup completo em um único arquivo.…, Baixa o CSV de um conjunto (produtos, vendas, compras, despesas, movimentacoes,…, _csv_bytes() (+14 more)

### Community 18 - "database.py"
Cohesion: 0.08
Nodes (38): Base, Configuração de conexão e sessão assíncrona com o banco de dados., Classe base usada por todos os modelos ORM do projeto., Serviço de exportação de dados — gera CSV/ZIP para backup manual do operador.…, Serviços de negócio para cadastro e manutenção do catálogo., PreferenceService, AsyncSession, Serviço de leitura e gravação das preferências de alerta do sistema. Regra de… (+30 more)

### Community 19 - "nav.tsx"
Cohesion: 0.20
Nodes (9): Nav, NavCtx, NavEntry, NavProvider(), ScreenId, TAB_ROOTS, TabId, setUnauthorizedHandler() (+1 more)

### Community 20 - "devDependencies"
Cohesion: 0.06
Nodes (30): dependencies, react, react-dom, recharts, devDependencies, @types/node, @types/react, @types/react-dom (+22 more)

### Community 21 - "UI.tsx"
Cohesion: 0.08
Nodes (21): BadgeProps, BadgeTone, BtnKind, BtnProps, Card(), CardProps, ChannelChipProps, ErrorBodyProps (+13 more)

### Community 22 - "sales_routes.py"
Cohesion: 0.11
Nodes (21): Agrega os roteadores do módulo operacional em um único APIRouter., create_sale(), delete_sale(), list_sales(), AsyncSession, delete, get, post (+13 more)

### Community 23 - "schemas/catalog.py"
Cohesion: 0.18
Nodes (14): CategoryOut, ProductOut, BaseModel, Schemas Pydantic usados pelas rotas de catálogo., Resposta pública completa de produto, com fotos e variantes., Resposta pública de uma categoria cadastrada., Resposta pública de fornecedor., Resposta pública de canal de venda. (+6 more)

### Community 24 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+13 more)

### Community 25 - "SupplierCreate"
Cohesion: 0.24
Nodes (9): create_supplier(), Cria um fornecedor para vínculo com produtos e compras., Atualiza os dados de um fornecedor existente., update_supplier(), Supplier, Cria um fornecedor ativo com os dados informados., Atualiza campos enviados de um fornecedor existente., Entrada para criação ou atualização de fornecedor. (+1 more)

### Community 26 - "do_run_migrations"
Cohesion: 0.29
Nodes (7): do_run_migrations(), Executa as migrations dentro de uma conexão síncrona fornecida pelo engine…, Cria engine assíncrono (asyncpg) e delega a execução das migrations., Ponto de entrada padrão — roda as migrations de forma assíncrona., run_async_migrations(), run_migrations_online(), Connection

### Community 27 - "Settings"
Cohesion: 0.17
Nodes (11): Config, Converte CORS_ORIGINS em lista, ignorando entradas vazias., Define o arquivo `.env` como fonte adicional de configuração local., Agrupa variáveis de ambiente usadas pela API. Segurança: DATABASE_URL,…, Settings, _detect_state(), main(), Rotina de inicialização do banco — agora baseada em Alembic. Cenários tratados:… (+3 more)

### Community 28 - "EntryForm.tsx"
Cohesion: 0.15
Nodes (17): blankCard(), blankExtra(), blankVariant(), CardExtra, cellSelectStyle, EntryForm(), fieldLabelRow, parseNum() (+9 more)

### Community 29 - "routes/products.py"
Cohesion: 0.27
Nodes (9): product_analysis(), AsyncSession, get, Rotas de análise de produtos., Análise completa de produtos: margem, parados e ruptura., top_products(), ProductAnalysisService, AsyncSession (+1 more)

### Community 30 - "verify_token"
Cohesion: 0.22
Nodes (9): Valida o token enviado no cabeçalho Authorization das rotas protegidas., verify_token(), dashboard(), AsyncSession, get, Rota do dashboard executivo., DashboardService, AsyncSession (+1 more)

### Community 31 - "get_db"
Cohesion: 0.22
Nodes (9): get_db(), AsyncSession, Entrega uma sessão de banco por requisição e controla commit/rollback., dre(), AsyncSession, get, Rotas de análise financeira e DRE., FinanceService (+1 more)

### Community 32 - "routes/data_quality.py"
Cohesion: 0.22
Nodes (8): data_quality(), AsyncSession, get, Rota de qualidade dos dados — score e problemas detectados., Retorna score de qualidade dos dados e lista de inconsistências por tipo., DataQualityService, AsyncSession, Avalia completude e consistência dos dados operacionais da loja.

### Community 33 - "product_classification.py"
Cohesion: 0.22
Nodes (8): product_classification(), AsyncSession, get, Rota de classificação de produtos — situações de estoque para decisão de compra., Classifica produtos em cinco situações de estoque, margem e velocidade. A sexta…, Roteador principal de analytics — agrega todos os sub-routers do módulo., ProductClassificationService, AsyncSession

### Community 34 - "settings/routes.py"
Cohesion: 0.17
Nodes (14): get_preferences(), AsyncSession, get, put, Rotas de preferências configuráveis do sistema — limiares de alerta., Retorna os limiares de alerta vigentes (valores padrão quando ainda não…, Atualiza os limiares de alerta usados pelas análises de estoque e ruptura., update_preferences() (+6 more)

### Community 35 - "compilerOptions"
Cohesion: 0.13
Nodes (14): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+6 more)

### Community 36 - "channels.py"
Cohesion: 0.36
Nodes (7): AsyncSession, get, Rotas de análise por canal de venda e por tamanho., sales_by_channel(), sales_by_size(), ChannelAnalysisService, AsyncSession

### Community 37 - "schemas/operations.py"
Cohesion: 0.09
Nodes (26): Módulo operacional: catálogo, estoque, vendas, compras e despesas., post, Rotas HTTP para movimentações e histórico de estoque., Registra uma movimentação manual de estoque., stock_movement(), Serviços de negócio para despesas operacionais., AsyncSession, StockMovement (+18 more)

### Community 38 - "main.py"
Cohesion: 0.15
Nodes (11): Versão da API — fonte única de verdade. Usada tanto em `FastAPI(version=...)`…, health(), AsyncSession, get, Rota pública de status do sistema — usada pela tela "Status do sistema" do PWA., Verifica conectividade real com o banco e devolve a versão em vigor da API.…, health(), get (+3 more)

### Community 39 - ".create_product"
Cohesion: 0.29
Nodes (6): create_product(), Cria produto e variantes iniciais., Gera um SKU curto único no formato LGD-XXXXXXXX., Cria um produto e suas variantes iniciais, validando referências e unicidade de…, ProductCreate, Entrada para cadastrar produto e suas variantes iniciais.

### Community 40 - "expense_routes.py"
Cohesion: 0.12
Nodes (23): create_expense(), delete_expense(), list_expenses(), AsyncSession, delete, get, post, put (+15 more)

### Community 41 - "test_analytics_contracts.py"
Cohesion: 0.29
Nodes (4): parametrize, Contrato dos endpoints de Analytics que sobrevivem à Fase 1. Estes testes não…, test_rota_exige_autenticacao(), test_rota_responde_200_autenticada()

### Community 42 - "pwa.ts"
Cohesion: 0.19
Nodes (11): index.html — entrypoint do PWA LGD Mantos, SystemStatus(), withTimeout(), applyServiceWorkerUpdate(), getSnapshot(), listeners, PwaUpdateState, registerServiceWorker() (+3 more)

### Community 43 - "list_stock_history"
Cohesion: 0.29
Nodes (7): list_stock_history(), StockMovement, Retorna o histórico recente de movimentações de uma variante., AsyncSession, get, Retorna movimentações recentes de uma variante., stock_history()

### Community 44 - "Consolidação da Base de Código — 2026-07-16"
Cohesion: 0.06
Nodes (46): agno==2.6.19 (framework de agentes), alembic==1.18.5 (migrations), backend/requirements-dev.txt — dependências de teste, pytest==8.4.2 + pytest-asyncio==1.2.0, backend/requirements.txt — dependências de produção, ollama==0.6.2 (cliente Ollama), openai==2.44.0 (cliente compatível OpenAI usado pelo Ollama), Serviço backend — API FastAPI em modo produção (+38 more)

### Community 45 - "App.tsx"
Cohesion: 0.14
Nodes (33): App(), fmtBRL(), fmtBRLshort(), fmtNum(), useData(), useNav(), CategoryDetail(), ByChannel() (+25 more)

### Community 46 - "ProductUpdate"
Cohesion: 0.33
Nodes (6): Atualiza dados editáveis de um produto., update_product(), Product, Atualiza campos do produto e, se enviadas, aplica atualizações de variantes., ProductUpdate, Entrada parcial para atualizar dados editáveis de um produto.

### Community 47 - "Spec — Bloco App da seção Mais"
Cohesion: 0.43
Nodes (7): Modelo AppPreference (migration 0004_preferencias_de_alerta), Tela Configurações (alertas, exportação, segurança), Spec — Bloco App da seção Mais, Serviço de exportação de dados (CSV por conjunto + ZIP), Endpoint GET /api/v1/health, Tela Sobre o app (versão única de build), Tela Status do sistema (conexão, versão, atualização PWA)

### Community 48 - "test_agents_removed.py"
Cohesion: 0.33
Nodes (5): parametrize, Garante que a superfície HTTP do domínio de Marketing não existe mais. Este…, Trava contra reimportação do módulo de agents removido. Teste frágil por…, test_modulo_de_agents_nao_e_importavel(), test_rota_de_marketing_responde_404()

### Community 50 - "Sale"
Cohesion: 0.17
Nodes (22): Re-exporta todas as funções de repositório para compatibilidade com imports…, daily_revenue(), daily_revenue_series(), month_cogs(), month_revenue(), AsyncSession, datetime, Consultas sobre vendas, receita e velocidade de variantes. (+14 more)

### Community 52 - "Regras, Instruções de Execução e Uso de Tools (NÃO IGNORAR)"
Cohesion: 0.20
Nodes (8): caveman, Claude - Contexto e Instruções, graphify, Regras de economia para fluxos com subagentes (implementador/revisor, Explore, Plan), Regras, Instruções de Execução e Uso de Tools (NÃO IGNORAR), Regras obrigatórias de economia, Sobre o Projeto *LGD Mantos*, Uso de Tools

### Community 97 - "VariantIn"
Cohesion: 0.17
Nodes (11): add_variant(), post, UploadFile, Adiciona variante de tamanho/cor a um produto., Recebe upload de foto e associa o arquivo ao produto., upload_photo(), UploadFile, Adiciona uma nova variante vendável a um produto existente. (+3 more)

## Knowledge Gaps
- **189 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+184 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 575 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Custo de venda resolvido no servidor (unit_cost)` connect `Consolidação da Base de Código — 2026-07-16` to `SalesHistory.tsx`, `sales_routes.py`?**
  _High betweenness centrality (0.220) - this node is a cross-community bridge._
- **Why does `Consolidação da Base de Código — 2026-07-16` connect `Consolidação da Base de Código — 2026-07-16` to `auth.py`, `main.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `ProductVariant` connect `Product` to `VariantIn`, `repositories.py`, `.create_product`, `CatalogService`, `shared/schemas/__init__.py`, `ProductUpdate`, `ExportService`, `database.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `CatalogService` (e.g. with `add_variant()` and `create_category()`) actually correct?**
  _`CatalogService` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `Product` (e.g. with `count_active_products()` and `count_active_variants()`) actually correct?**
  _`Product` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `ProductVariant` (e.g. with `count_active_variants()` and `variants_no_info()`) actually correct?**
  _`ProductVariant` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `Sale` (e.g. with `sales_no_channel()` and `monthly_cogs_evolution()`) actually correct?**
  _`Sale` has 24 INFERRED edges - model-reasoned connections that need verification._