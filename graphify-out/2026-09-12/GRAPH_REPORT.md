# Graph Report - LGD-Mantos  (2026-09-10)

## Corpus Check
- 145 files · ~179,909 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1251 nodes · 3047 edges · 57 communities (42 shown, 11 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 191 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `61ccf78a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Product
- Chrome.tsx
- catalog_routes.py
- CategoryAnalysisService
- ByChannel.tsx
- Blueprint LGD Mantos — de três módulos para Operação + Inteligência
- Fase 1 — Fundação Limpa: Implementation Plan
- repositories.py
- SalesHistory.tsx
- CatalogService
- SaleChannelCreate
- entry_service.py
- analytics/schemas/__init__.py
- StockMoves.tsx
- types.ts
- CategoryCreate
- ProductList.tsx
- ExportService
- database.py
- nav.tsx
- devDependencies
- UI.tsx
- schemas/operations.py
- shared/schemas/__init__.py
- compilerOptions
- create_supplier
- do_run_migrations
- data_quality_repository.py
- EntryForm.tsx
- auth.py
- compilerOptions
- stock_routes.py
- main.py
- expense_routes.py
- pwa.ts
- Consolidação da Base de Código — 2026-07-16
- App.tsx
- Sale
- Regras, Instruções de Execução e Uso de Tools (NÃO IGNORAR)
- MarketingIntel.tsx
- PreferenceService
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
- add_variant

## God Nodes (most connected - your core abstractions)
1. `useNav()` - 68 edges
2. `CatalogService` - 41 edges
3. `useData()` - 39 edges
4. `AppBar()` - 38 edges
5. `api` - 38 edges
6. `Product` - 37 edges
7. `ScreenBody()` - 37 edges
8. `ProductVariant` - 35 edges
9. `Sale` - 35 edges
10. `Ico` - 33 edges

## Surprising Connections (you probably didn't know these)
- `Serviço web — Caddy (PWA + reverse proxy + HTTPS)` --shares_data_with--> `index.html — entrypoint do PWA LGD Mantos`  [INFERRED]
  docker-compose.prod.yml → frontend_pwa/index.html
- `Verificação manual ponta a ponta (seção 11)` --conceptually_related_to--> `FASE A — Validação E2E com Ollama real + Seed de Knowledge (concluída)`  [INFERRED]
  FABLE_CONSOLIDACAO_2026-07-16.md → docs/plans/PLAN-20260716-1846-consolidacao-agentes-marketing.md
- `PolicyEngine aplicado pelo Supervisor` --conceptually_related_to--> `Regra de ouro arquitetural — IA só na Agentic Layer`  [INFERRED]
  FABLE_CONSOLIDACAO_2026-07-16.md → docs/plans/PLAN-20260716-1846-consolidacao-agentes-marketing.md
- `FASE A — Validação E2E com Ollama real + Seed de Knowledge (concluída)` --conceptually_related_to--> `Serviço ollama — inferência local llama3.1:8b`  [INFERRED]
  docs/plans/PLAN-20260716-1846-consolidacao-agentes-marketing.md → docker-compose.prod.yml
- `Serviço ollama — inferência local llama3.1:8b` --shares_data_with--> `agno==2.6.19 (framework de agentes)`  [INFERRED]
  docker-compose.prod.yml → backend/requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **As três telas do bloco APP da seção Mais** — specs_bloco_app_mais_spec_configuracoes, specs_bloco_app_mais_spec_status_sistema, specs_bloco_app_mais_spec_sobre_app [EXTRACTED 1.00]
- **Fases do plano de consolidação da camada multi-agente de marketing** — docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fase0, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasea, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_faseb, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasec, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasee1, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fased, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasee2, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasee3 [EXTRACTED 1.00]
- **Correção do drift recharts v2→v3 no build do frontend** — fable_consolidacao_2026_07_16_recharts_v3_migration, frontend_pwa_src_screens_an_dre, frontend_pwa_src_screens_an_bychannel, frontend_pwa_src_screens_an_categorias, frontend_pwa_src_screens_an_categorydetail, frontend_pwa_src_screens_an_dashboard, frontend_pwa_src_components_analytics [EXTRACTED 1.00]

## Communities (57 total, 11 thin omitted)

### Community 0 - "Product"
Cohesion: 0.16
Nodes (34): active_variants(), category_active_product_count(), category_performance(), category_size_distribution(), category_size_stock(), category_stock(), product_attribute_analysis(), AsyncSession (+26 more)

### Community 1 - "Chrome.tsx"
Cohesion: 0.12
Nodes (30): AppBar(), AppBarProps, FABProps, IcoFn, OP_TABS, OpScreen, ScreenBody(), ScreenBodyProps (+22 more)

### Community 2 - "catalog_routes.py"
Cohesion: 0.17
Nodes (19): get_category(), get_channel(), get_product(), get_supplier(), list_categories(), list_channels(), list_products(), list_suppliers() (+11 more)

### Community 3 - "CategoryAnalysisService"
Cohesion: 0.06
Nodes (55): category_buying_patterns(), category_performance(), category_size_distribution(), category_size_stock(), category_stock_coverage(), product_attribute_analysis(), AsyncSession, get (+47 more)

### Community 4 - "ByChannel.tsx"
Cohesion: 0.09
Nodes (24): Correção do build — drift recharts v2→v3, AlertRow(), AlertRowProps, CovBadge(), MetricInfo(), MetricInfoProps, NavItem(), Period (+16 more)

### Community 5 - "Blueprint LGD Mantos — de três módulos para Operação + Inteligência"
Cohesion: 0.07
Nodes (29): 1. Problema, 2. Decisões, 3.1 Dois pilares, 3.2 Navegação, 3.3 Backend: o módulo `intelligence`, 3.4 O Sinal, 3.5 Endpoints, 3.6 Comparação de períodos (+21 more)

### Community 6 - "Fase 1 — Fundação Limpa: Implementation Plan"
Cohesion: 0.10
Nodes (19): Achado: três telas órfãs, Decisão tomada neste plano (refinamento da spec), Estrutura de arquivos, Fase 1 — Fundação Limpa: Implementation Plan, Global Constraints, Task 10: Tela Estoque & Compras (`intel-stock`), Task 11: Tela Saúde da Loja (`intel-health`), Task 12: Apagar as telas órfãs e fechar a navegação (+11 more)

### Community 7 - "repositories.py"
Cohesion: 0.06
Nodes (48): get_category(), get_channel(), get_entry(), get_expense(), get_product(), get_product_by_sku(), get_product_variant(), get_sale() (+40 more)

### Community 8 - "SalesHistory.tsx"
Cohesion: 0.14
Nodes (13): ChannelChip(), KPI(), fmtDate(), VariantInfo, fmtDateTime(), VariantInfo, fmtDate(), fmtTime() (+5 more)

### Community 9 - "CatalogService"
Cohesion: 0.09
Nodes (27): create_product(), deactivate_product(), delete_category(), delete_photo(), delete_supplier(), delete_variant(), delete, Desativa um fornecedor pelo ID (soft delete). (+19 more)

### Community 10 - "SaleChannelCreate"
Cohesion: 0.15
Nodes (13): create_channel(), Cria um canal de venda., Atualiza nome, descrição e cor de um canal., Alterna ativo/inativo de um canal sem excluí-lo., toggle_channel(), update_channel(), SaleChannel, Atualiza nome, descrição e cor de um canal existente. (+5 more)

### Community 11 - "entry_service.py"
Cohesion: 0.09
Nodes (36): Módulo operacional: catálogo, estoque, vendas, compras e despesas., create_entry(), get_entry(), list_entries(), AsyncSession, get, post, Rotas HTTP para entrada de mercadoria. (+28 more)

### Community 12 - "analytics/schemas/__init__.py"
Cohesion: 0.12
Nodes (29): DailyRevenue, DashboardResponse, BaseModel, Contratos de resposta do dashboard executivo., DataQualityIssues, DataQualityResponse, ExpenseIssue, ProductIssue (+21 more)

### Community 13 - "StockMoves.tsx"
Cohesion: 0.18
Nodes (12): CartItem, ALL_MOVE_META, fmtMoveDate(), HIST_TAB_TYPE, HIST_TABS, MOVE_LABELS, moveMeta, MoveType (+4 more)

### Community 14 - "types.ts"
Cohesion: 0.05
Nodes (50): classify(), EnrichedPattern, GROUP_META, GroupId, Signal, APPROVAL_FILTERS, ApprovalFilter, AprovacoesTab() (+42 more)

### Community 15 - "CategoryCreate"
Cohesion: 0.21
Nodes (10): create_category(), put, Cria uma categoria no catálogo., Atualiza nome e descrição de uma categoria existente., update_category(), Category, Cria uma categoria de produto., Atualiza nome e descrição de uma categoria existente. (+2 more)

### Community 16 - "ProductList.tsx"
Cohesion: 0.15
Nodes (16): FAB(), OpSubNav(), ErrorBody(), PhotoPlaceholder(), SearchBar(), Tabs(), fmtNum(), BySize() (+8 more)

### Community 17 - "ExportService"
Cohesion: 0.13
Nodes (21): export_backup(), export_dataset(), AsyncSession, get, Baixa um .zip com um CSV por conjunto — backup completo em um único arquivo.…, Baixa o CSV de um conjunto (produtos, vendas, compras, despesas, movimentacoes,…, _csv_bytes(), ExportService (+13 more)

### Community 18 - "database.py"
Cohesion: 0.10
Nodes (28): Base, Configuração de conexão e sessão assíncrona com o banco de dados., Classe base usada por todos os modelos ORM do projeto., Rotas de exportação de dados — backup manual do operador em CSV/ZIP., Serviço de exportação de dados — gera CSV/ZIP para backup manual do operador.…, Serviço de leitura e gravação das preferências de alerta do sistema. Regra de…, Modelos ORM do catálogo de produtos, fornecedores e variantes., Fornecedor de produtos e compras da loja. (+20 more)

### Community 19 - "nav.tsx"
Cohesion: 0.20
Nodes (9): Nav, NavCtx, NavEntry, NavProvider(), ScreenId, TAB_ROOTS, TabId, setUnauthorizedHandler() (+1 more)

### Community 20 - "devDependencies"
Cohesion: 0.06
Nodes (30): dependencies, react, react-dom, recharts, devDependencies, @types/node, @types/react, @types/react-dom (+22 more)

### Community 21 - "UI.tsx"
Cohesion: 0.07
Nodes (28): Badge(), BadgeProps, BadgeTone, Btn(), BtnKind, BtnProps, CardProps, ChannelChipProps (+20 more)

### Community 22 - "schemas/operations.py"
Cohesion: 0.08
Nodes (32): create_sale(), delete_sale(), list_sales(), AsyncSession, delete, get, post, Rotas HTTP para consulta e registro de vendas. (+24 more)

### Community 23 - "shared/schemas/__init__.py"
Cohesion: 0.14
Nodes (24): Serviços de negócio para cadastro e manutenção do catálogo., CategoryOut, ProductCreate, ProductOut, ProductUpdate, BaseModel, Schemas Pydantic usados pelas rotas de catálogo., Entrada para cadastrar produto e suas variantes iniciais. (+16 more)

### Community 24 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+13 more)

### Community 25 - "create_supplier"
Cohesion: 0.22
Nodes (7): create_supplier(), Cria um fornecedor para vínculo com produtos e compras., Atualiza os dados de um fornecedor existente., update_supplier(), Supplier, Cria um fornecedor ativo com os dados informados., Atualiza campos enviados de um fornecedor existente.

### Community 26 - "do_run_migrations"
Cohesion: 0.29
Nodes (7): do_run_migrations(), Executa as migrations dentro de uma conexão síncrona fornecida pelo engine…, Cria engine assíncrono (asyncpg) e delega a execução das migrations., Ponto de entrada padrão — roda as migrations de forma assíncrona., run_async_migrations(), run_migrations_online(), Connection

### Community 27 - "data_quality_repository.py"
Cohesion: 0.18
Nodes (17): count_active_products(), count_active_variants(), expenses_no_category(), products_no_category(), products_no_cost_price(), products_no_photo(), products_no_sale_price(), products_no_supplier() (+9 more)

### Community 28 - "EntryForm.tsx"
Cohesion: 0.13
Nodes (19): MerchandiseEntry — fluxo vivo de compras (/entries), Remoção do módulo PurchaseOrder morto, blankCard(), blankExtra(), blankVariant(), CardExtra, cellSelectStyle, EntryForm() (+11 more)

### Community 34 - "auth.py"
Cohesion: 0.11
Nodes (21): Funções simples de autenticação baseada em token JWT., Valida o token enviado no cabeçalho Authorization das rotas protegidas., verify_token(), get_db(), AsyncSession, Entrega uma sessão de banco por requisição e controla commit/rollback., Rotas de análise por canal de venda e por tamanho., Rota do dashboard executivo. (+13 more)

### Community 35 - "compilerOptions"
Cohesion: 0.13
Nodes (14): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+6 more)

### Community 37 - "stock_routes.py"
Cohesion: 0.12
Nodes (17): Agrega os roteadores do módulo operacional em um único APIRouter., AsyncSession, get, post, Rotas HTTP para movimentações e histórico de estoque., Registra uma movimentação manual de estoque., Retorna movimentações recentes de uma variante., stock_history() (+9 more)

### Community 38 - "main.py"
Cohesion: 0.06
Nodes (30): create_token(), Cria um token de acesso para o usuário proprietário do sistema., Config, Configurações carregadas do ambiente para o backend., Converte CORS_ORIGINS em lista, ignorando entradas vazias., Define o arquivo `.env` como fonte adicional de configuração local., Agrupa variáveis de ambiente usadas pela API. Segurança: DATABASE_URL,…, Settings (+22 more)

### Community 40 - "expense_routes.py"
Cohesion: 0.11
Nodes (24): create_expense(), delete_expense(), list_expenses(), AsyncSession, delete, get, post, put (+16 more)

### Community 42 - "pwa.ts"
Cohesion: 0.19
Nodes (11): index.html — entrypoint do PWA LGD Mantos, SystemStatus(), withTimeout(), applyServiceWorkerUpdate(), getSnapshot(), listeners, PwaUpdateState, registerServiceWorker() (+3 more)

### Community 44 - "Consolidação da Base de Código — 2026-07-16"
Cohesion: 0.06
Nodes (43): agno==2.6.19 (framework de agentes), alembic==1.18.5 (migrations), backend/requirements-dev.txt — dependências de teste, pytest==8.4.2 + pytest-asyncio==1.2.0, backend/requirements.txt — dependências de produção, ollama==0.6.2 (cliente Ollama), openai==2.44.0 (cliente compatível OpenAI usado pelo Ollama), Serviço backend — API FastAPI em modo produção (+35 more)

### Community 45 - "App.tsx"
Cohesion: 0.10
Nodes (43): App(), fmtBRL(), fmtBRLshort(), useData(), useNav(), Alertas(), ByChannel(), Categorias() (+35 more)

### Community 50 - "Sale"
Cohesion: 0.06
Nodes (58): expenses_by_category(), expenses_total(), monthly_cogs_evolution(), monthly_expenses_evolution(), monthly_revenue_evolution(), AsyncSession, datetime, Consultas financeiras sobre despesas. (+50 more)

### Community 52 - "Regras, Instruções de Execução e Uso de Tools (NÃO IGNORAR)"
Cohesion: 0.20
Nodes (8): caveman, Claude - Contexto e Instruções, graphify, Regras de economia para fluxos com subagentes (implementador/revisor, Explore, Plan), Regras, Instruções de Execução e Uso de Tools (NÃO IGNORAR), Regras obrigatórias de economia, Sobre o Projeto *LGD Mantos*, Uso de Tools

### Community 53 - "MarketingIntel.tsx"
Cohesion: 0.29
Nodes (4): GroupConfig, GROUPS, MarketingIntelligence, MarketingVariant

### Community 54 - "PreferenceService"
Cohesion: 0.11
Nodes (21): marketing_intelligence(), AsyncSession, get, Classifica produtos em listas de ação: postar, promover, destacar, evitar., MarketingIntelligenceService, AsyncSession, get_preferences(), AsyncSession (+13 more)

### Community 97 - "add_variant"
Cohesion: 0.18
Nodes (9): add_variant(), post, UploadFile, Adiciona variante de tamanho/cor a um produto., Recebe upload de foto e associa o arquivo ao produto., upload_photo(), UploadFile, Adiciona uma nova variante vendável a um produto existente. (+1 more)

## Knowledge Gaps
- **207 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+202 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 576 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Custo de venda resolvido no servidor (unit_cost)` connect `Consolidação da Base de Código — 2026-07-16` to `StockMoves.tsx`, `schemas/operations.py`?**
  _High betweenness centrality (0.202) - this node is a cross-community bridge._
- **Why does `Consolidação da Base de Código — 2026-07-16` connect `Consolidação da Base de Código — 2026-07-16` to `EntryForm.tsx`, `ByChannel.tsx`, `main.py`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `Correção do build — drift recharts v2→v3` connect `ByChannel.tsx` to `Consolidação da Base de Código — 2026-07-16`, `App.tsx`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `CatalogService` (e.g. with `add_variant()` and `create_category()`) actually correct?**
  _`CatalogService` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _207 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Chrome.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.12322695035460993 - nodes in this community are weakly interconnected._
- **Should `CategoryAnalysisService` be split into smaller, more focused modules?**
  _Cohesion score 0.05754527162977867 - nodes in this community are weakly interconnected._