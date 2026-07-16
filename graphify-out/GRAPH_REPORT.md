# Graph Report - LGD-Mantos  (2026-07-16)

## Corpus Check
- 161 files · ~162,298 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1311 nodes · 2717 edges · 91 communities (71 shown, 20 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 175 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `aeae6706`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- useNav
- KnowledgeDocument
- CatalogService
- CategoryAnalysisService
- repositories.py
- types.ts
- __init__.py
- CategoryDetail.tsx
- App.tsx
- entry.py
- Product
- PolicyEngine
- useData
- __init__.py
- catalog_routes.py
- package.json
- UI.tsx
- .queue_campaign
- PurchaseService
- SupervisorService
- nav.tsx
- DataAgentOutput
- compilerOptions
- ApprovalService
- data_quality_repository.py
- EntryForm.tsx
- routes.py
- create_run
- Base
- catalog.py
- schemas.py
- Icons.tsx
- operations.py
- Marketing.tsx
- compilerOptions
- ExpenseIn
- .stock_movement
- auth.py
- services.py
- ExpenseService
- schemas.py
- Approval
- StrategyAgentOutput
- agent_context_service.py
- .agent_context
- create_sale
- config.py
- Supplier
- schemas.py
- routes.py
- data_quality
- .marketing_intelligence
- common.py
- .dashboard
- finance.py
- products.py
- CategoryCreate
- SupplierCreate
- database.py
- add_variant
- update_product
- StockService
- main.py
- upload_photo
- tsconfig.json
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- routes.py
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- create_product
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- vercel.json

## God Nodes (most connected - your core abstractions)
1. `useNav()` - 68 edges
2. `useData()` - 39 edges
3. `AppBar()` - 37 edges
4. `ScreenBody()` - 36 edges
5. `api` - 35 edges
6. `Ico` - 31 edges
7. `fmtBRL()` - 29 edges
8. `LoadingBody()` - 27 edges
9. `Product` - 25 edges
10. `CatalogService` - 24 edges

## Surprising Connections (you probably didn't know these)
- `KnowledgeDocument` --uses--> `Base`  [INFERRED]
  backend/app/modules/agents/knowledge/models.py → backend/app/core/database.py
- `AgentRun` --uses--> `Base`  [INFERRED]
  backend/app/modules/agents/marketing_ops/models.py → backend/app/core/database.py
- `Approval` --uses--> `Base`  [INFERRED]
  backend/app/modules/agents/marketing_ops/models.py → backend/app/core/database.py
- `Campaign` --uses--> `Base`  [INFERRED]
  backend/app/modules/agents/marketing_ops/models.py → backend/app/core/database.py
- `CreativeBrief` --uses--> `Base`  [INFERRED]
  backend/app/modules/agents/marketing_ops/models.py → backend/app/core/database.py

## Import Cycles
- None detected.

## Communities (91 total, 20 thin omitted)

### Community 0 - "useNav"
Cohesion: 0.09
Nodes (22): App(), Input(), Nav, NavCtx, NavEntry, NavProvider(), TAB_ROOTS, TabId (+14 more)

### Community 1 - "KnowledgeDocument"
Cohesion: 0.05
Nodes (42): KnowledgeDocument, Modelo ORM para documentos da Knowledge Layer.  Armazena contexto de marca (to, Documento de conhecimento de marca consultado pelos agentes como contexto., create_document(), delete_document(), get_document(), list_documents(), AsyncSession (+34 more)

### Community 2 - "CatalogService"
Cohesion: 0.06
Nodes (32): create_channel(), Cria um canal de venda., Atualiza nome, descrição e cor de um canal., update_channel(), CatalogService, AsyncSession, Category, Product (+24 more)

### Community 3 - "CategoryAnalysisService"
Cohesion: 0.05
Nodes (45): category_buying_patterns(), category_performance(), category_size_distribution(), category_size_stock(), category_stock_coverage(), product_attribute_analysis(), AsyncSession, Rotas de análise centradas em categoria. (+37 more)

### Community 4 - "repositories.py"
Cohesion: 0.06
Nodes (47): get_category(), get_channel(), get_entry(), get_expense(), get_product(), get_product_by_sku(), get_product_variant(), get_sale() (+39 more)

### Community 5 - "types.ts"
Cohesion: 0.18
Nodes (8): classify(), ComprasReposicao(), EnrichedPattern, GROUP_META, GroupId, Signal, BuyingPattern, CategorySizeStock

### Community 6 - "__init__.py"
Cohesion: 0.10
Nodes (35): AgentContextResponse, AttentionBlock, OpportunitiesBlock, BaseModel, Contratos de resposta do payload de contexto para agentes de IA., ShopHealth, DailyRevenue, DashboardResponse (+27 more)

### Community 7 - "CategoryDetail.tsx"
Cohesion: 0.06
Nodes (46): AlertRow(), AlertRowProps, CovBadge(), MetricInfo(), MetricInfoProps, NavItem(), Period, periodLabel() (+38 more)

### Community 8 - "App.tsx"
Cohesion: 0.06
Nodes (35): BadgeProps, BadgeTone, Btn(), BtnKind, BtnProps, Card(), CardProps, ChannelChipProps (+27 more)

### Community 9 - "entry.py"
Cohesion: 0.11
Nodes (24): create_entry(), get_entry(), list_entries(), AsyncSession, Rotas HTTP para entrada de mercadoria., Registra entrada de mercadoria, criando produtos e variantes inline., Lista entradas de mercadoria recentes., Detalhe de uma entrada de mercadoria com todos os itens. (+16 more)

### Community 10 - "Product"
Cohesion: 0.13
Nodes (35): active_variants(), category_active_product_count(), category_performance(), category_size_distribution(), category_size_stock(), category_stock(), product_attribute_analysis(), AsyncSession (+27 more)

### Community 11 - "PolicyEngine"
Cohesion: 0.12
Nodes (17): PolicyEngine, PolicyResult, Policy Engine — código determinístico que bloqueia ações perigosas.  Regra: es, Bloqueia publicação sem aprovação humana., Bloqueia publicação em canal não autorizado., Agentes nunca podem alterar estoque., Agentes nunca podem alterar preço., Agentes nunca podem registrar vendas. (+9 more)

### Community 12 - "useData"
Cohesion: 0.15
Nodes (31): AppBar(), FAB(), OpSubNav(), ScreenBody(), Badge(), ErrorBody(), LoadingBody(), PhotoPlaceholder() (+23 more)

### Community 13 - "__init__.py"
Cohesion: 0.14
Nodes (29): expenses_by_category(), expenses_total(), monthly_cogs_evolution(), monthly_expenses_evolution(), monthly_revenue_evolution(), AsyncSession, datetime, Consultas financeiras sobre despesas. (+21 more)

### Community 14 - "catalog_routes.py"
Cohesion: 0.09
Nodes (30): deactivate_product(), delete_category(), delete_photo(), delete_supplier(), delete_variant(), get_category(), get_channel(), get_product() (+22 more)

### Community 15 - "package.json"
Cohesion: 0.07
Nodes (28): dependencies, react, react-dom, recharts, devDependencies, @types/react, @types/react-dom, typescript (+20 more)

### Community 16 - "UI.tsx"
Cohesion: 0.22
Nodes (10): do_run_migrations(), Ambiente do Alembic — conecta o Alembic aos modelos e ao banco do projeto.  A UR, Gera SQL sem conectar ao banco (modo --sql)., Executa as migrations dentro de uma conexão síncrona fornecida pelo engine assín, Cria engine assíncrono (asyncpg) e delega a execução das migrations., Ponto de entrada padrão — roda as migrations de forma assíncrona., run_async_migrations(), run_migrations_offline() (+2 more)

### Community 17 - ".queue_campaign"
Cohesion: 0.10
Nodes (20): PublishingQueue, Fila de publicação futura — inativa no MVP, campos preparados para o PublishingA, list_queue(), AsyncSession, queue_campaign(), Rotas da fila de publicação — ativa a tabela publishing_queue para uso real., Lista a fila de publicação com filtro opcional por status., Enfileira uma campanha aprovada para publicação.      Requer que a campanha te (+12 more)

### Community 18 - "PurchaseService"
Cohesion: 0.20
Nodes (8): build_creative_agent(), Agent, CreativeAgent — cria direção visual e prompts de imagem.  Recebe a estratégia,, Cria uma instância fresca do CreativeAgent para cada run., get_agent_model(), Configuração centralizada da camada de agentes — modelo e runtime Agno.  Ponto ú, Retorna o modelo LLM configurado para uso nos agentes., Ollama

### Community 19 - "SupervisorService"
Cohesion: 0.14
Nodes (20): AgentRun, Registro de uma execução do workflow multi-agente., _create_approval(), _extract_product_photos(), AgentRun, AsyncSession, Product, SupervisorService — orquestra o pipeline multi-agente de marketing.  Fluxo com (+12 more)

### Community 20 - "nav.tsx"
Cohesion: 0.10
Nodes (31): ChannelChip(), KPI(), fmtBRL(), fmtBRLshort(), useNav(), Alertas(), Categorias(), CategoryDetail() (+23 more)

### Community 21 - "DataAgentOutput"
Cohesion: 0.15
Nodes (15): build_data_agent(), build_data_agent_input(), Agent, DataAgent — identifica oportunidades de marketing nos dados operacionais.  Rec, Cria uma instância fresca do DataAgent para cada run., Monta o payload de entrada para o DataAgent., DataAgentOutput, build_strategy_agent() (+7 more)

### Community 22 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+13 more)

### Community 23 - "ApprovalService"
Cohesion: 0.16
Nodes (11): ApprovalService, AgentRun, AsyncSession, ApprovalService — lógica de negócio do human-in-the-loop.  Regras absolutas:, Rejeita a campanha. Comentário obrigatório., Solicita revisão. Comentário com o que deve ser ajustado é obrigatório., Retorna o estado atual de um agent_run para polling de status., Retorna todas as aprovações com status pending, com campaign carregada. (+3 more)

### Community 24 - "data_quality_repository.py"
Cohesion: 0.18
Nodes (17): count_active_products(), count_active_variants(), expenses_no_category(), products_no_category(), products_no_cost_price(), products_no_photo(), products_no_sale_price(), products_no_supplier() (+9 more)

### Community 25 - "EntryForm.tsx"
Cohesion: 0.15
Nodes (17): blankCard(), blankExtra(), blankVariant(), CardExtra, cellSelectStyle, EntryForm(), fieldLabelRow, parseNum() (+9 more)

### Community 26 - "routes.py"
Cohesion: 0.17
Nodes (16): approve(), get_approval(), list_approvals(), list_pending_approvals(), AsyncSession, Rotas do ApprovalAgent — human-in-the-loop da camada de agentes., Solicita revisão da campanha. Comentário com o que ajustar é obrigatório., Lista aprovações filtradas por status. Sem filtro retorna todas. (+8 more)

### Community 27 - "create_run"
Cohesion: 0.16
Nodes (15): create_run(), get_run(), list_runs(), AsyncSession, Rotas do Supervisor — entry point para criação e monitoramento de agent runs., Cria um agent run e dispara o pipeline de geração de campanha em background., Lista agent runs com paginação e filtro opcional por status., Retorna o status atual de um agent run — use para polling após criar um run. (+7 more)

### Community 28 - "Base"
Cohesion: 0.10
Nodes (24): Base, Classe base usada por todos os modelos ORM do projeto., EntryService, _generate_sku(), AsyncSession, Serviço de entrada de mercadoria — cria produtos, variantes e estoque atomicamen, Registra uma entrada de mercadoria criando produtos inline quando necessário., AsyncSession (+16 more)

### Community 29 - "catalog.py"
Cohesion: 0.16
Nodes (16): CategoryOut, ProductCreate, ProductOut, BaseModel, Schemas Pydantic usados pelas rotas de catálogo., Entrada para cadastrar produto e suas variantes iniciais., Resposta pública completa de produto, com fotos e variantes., Resposta pública de uma categoria cadastrada. (+8 more)

### Community 30 - "schemas.py"
Cohesion: 0.15
Nodes (20): build_content_agent(), build_content_agent_input(), Agent, ContentAgent — gera copy e textos para o post de marketing.  Recebe a estratég, Cria uma instância fresca do ContentAgent para cada run., Monta o payload de entrada para o ContentAgent., build_creative_agent_input(), Monta o payload de entrada para o CreativeAgent. (+12 more)

### Community 31 - "Icons.tsx"
Cohesion: 0.09
Nodes (27): AppBarProps, BottomNav(), FABProps, IcoFn, OP_TABS, OpScreen, ScreenBodyProps, TABS (+19 more)

### Community 32 - "operations.py"
Cohesion: 0.18
Nodes (14): ExpenseOut, BaseModel, Schemas Pydantic das operações de estoque, vendas, despesas e entrada de mercado, Resposta pública de movimentação de estoque registrada., Entrada de um item vendido em uma venda.      Nota: `unit_cost` enviado pelo c, Entrada para registrar uma venda com seus itens., Resposta pública de um item de venda., Resposta pública de venda com total e itens. (+6 more)

### Community 33 - "Marketing.tsx"
Cohesion: 0.17
Nodes (14): APPROVAL_FILTERS, ApprovalFilter, AprovacoesTab(), BadgeTone, CampanhasTab(), ConhecimentoTab(), DOC_TYPE_LABELS, fmtDt() (+6 more)

### Community 34 - "compilerOptions"
Cohesion: 0.13
Nodes (14): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+6 more)

### Community 35 - "ExpenseIn"
Cohesion: 0.21
Nodes (12): create_expense(), delete_expense(), list_expenses(), AsyncSession, Rotas HTTP para despesas operacionais., Lista despesas recentes., Registra uma despesa operacional., Atualiza uma despesa existente. (+4 more)

### Community 36 - ".stock_movement"
Cohesion: 0.18
Nodes (11): AsyncSession, Rotas HTTP para movimentações e histórico de estoque., Registra uma movimentação manual de estoque., Retorna movimentações recentes de uma variante., stock_history(), stock_movement(), AsyncSession, StockMovement (+3 more)

### Community 37 - "auth.py"
Cohesion: 0.17
Nodes (9): create_token(), Funções simples de autenticação baseada em token JWT., Cria um token de acesso para o usuário proprietário do sistema., Valida o token enviado no cabeçalho Authorization das rotas protegidas., verify_token(), login(), LoginIn, BaseModel (+1 more)

### Community 38 - "services.py"
Cohesion: 0.20
Nodes (8): caveman, Claude - Contexto e Instruções, graphify, Regras de economia para fluxos com subagentes (implementador/revisor, Explore, Plan), Regras, Instruções de Execução e Uso de Tools (NÃO IGNORAR), Regras obrigatórias de economia, Sobre o Projeto *LGD Mantos*, Uso de Tools

### Community 39 - "ExpenseService"
Cohesion: 0.21
Nodes (8): ExpenseService, AsyncSession, Expense, Serviços de negócio para despesas operacionais., Cria e remove despesas usadas nos controles financeiros., Registra uma despesa operacional., Atualiza campos de uma despesa existente., Remove uma despesa existente pelo identificador.

### Community 40 - "schemas.py"
Cohesion: 0.27
Nodes (10): ApprovalDetail, ApprovalListItem, CampaignSummary, CreativeBriefSummary, PostSummary, BaseModel, Schemas Pydantic para o módulo de aprovação (ApprovalAgent)., Detalhe completo de uma aprovação — inclui toda a campanha, post e briefing. (+2 more)

### Community 41 - "Approval"
Cohesion: 0.20
Nodes (9): Approval, Campaign, CreativeBrief, Post, Modelos ORM da camada Marketing Ops.  Estes modelos são o workspace dos agente, Briefing criativo com direção visual e prompt de imagem gerado pelo CreativeAgen, Registro de decisão humana sobre campanha, post ou briefing criativo., Campanha de marketing gerada pelo StrategyAgent. (+1 more)

### Community 42 - "StrategyAgentOutput"
Cohesion: 0.22
Nodes (7): ByChannel(), CHANNEL_FALLBACK, getViability(), LEVEL_COLOR, Viability, ViabilityLevel, ByChannelItem

### Community 43 - "agent_context_service.py"
Cohesion: 0.21
Nodes (9): AgentContextService, Empacota dados analíticos estruturados para consumo de agentes de IA.  Regra:, DashboardService, Indicadores do dashboard executivo., DataQualityService, Avalia completude e consistência dos dados operacionais da loja., MarketingIntelligenceService, Classifica produtos em listas de ação para decisões de conteúdo e promoção. (+1 more)

### Community 44 - ".agent_context"
Cohesion: 0.43
Nodes (4): AsyncSession, ProductAnalysisService, AsyncSession, Análise completa de produtos: margem, parados, risco de ruptura e categorias.

### Community 45 - "create_sale"
Cohesion: 0.28
Nodes (8): create_sale(), delete_sale(), list_sales(), AsyncSession, Rotas HTTP para consulta e registro de vendas., Lista vendas recentes respeitando o limite informado., Registra uma venda e delega a baixa de estoque ao serviço., Remove uma venda e estorna o estoque dos itens correspondentes.

### Community 47 - "config.py"
Cohesion: 0.14
Nodes (12): Config, Configurações carregadas do ambiente para o backend., Converte CORS_ORIGINS em lista, ignorando entradas vazias., Define o arquivo `.env` como fonte adicional de configuração local., Agrupa variáveis de ambiente usadas pela API.      Segurança: DATABASE_URL, APP_, Settings, _detect_state(), main() (+4 more)

### Community 48 - "Supplier"
Cohesion: 0.33
Nodes (7): get_supplier(), list_suppliers(), Supplier, Lista apenas fornecedores ativos, ordenados pelo nome., Busca um fornecedor pelo identificador interno., Fornecedor de produtos e compras da loja., Supplier

### Community 49 - "schemas.py"
Cohesion: 0.33
Nodes (6): OpsMetrics, BaseModel, Schemas de observabilidade da camada de agentes., Entrada resumida de um agent run para o log de operações., Métricas consolidadas do sistema de agentes., RunLogEntry

### Community 50 - "routes.py"
Cohesion: 0.22
Nodes (6): agent_context(), AsyncSession, Rota de contexto para agentes de IA — payload analítico agregado e curado., Retorna pacote estruturado com saúde da loja, alertas e oportunidades., Rotas de análise financeira e DRE., Roteador principal de analytics — agrega todos os sub-routers do módulo.

### Community 51 - "data_quality"
Cohesion: 0.29
Nodes (5): data_quality(), AsyncSession, Rota de qualidade dos dados — score e problemas detectados., Retorna score de qualidade dos dados e lista de inconsistências por tipo., AsyncSession

### Community 52 - ".marketing_intelligence"
Cohesion: 0.29
Nodes (5): marketing_intelligence(), AsyncSession, Rota de inteligência de marketing — classificação de produtos para ações., Classifica produtos em listas de ação: postar, promover, destacar, evitar., AsyncSession

### Community 53 - "common.py"
Cohesion: 0.33
Nodes (6): now(), datetime, Utilitários comuns para modelos persistidos no banco., Retorna o horário atual em UTC para campos de auditoria., Gera um identificador UUID textual para chaves primárias., uid()

### Community 54 - ".dashboard"
Cohesion: 0.33
Nodes (4): dashboard(), AsyncSession, Rota do dashboard executivo., AsyncSession

### Community 55 - "finance.py"
Cohesion: 0.29
Nodes (5): dre(), AsyncSession, FinanceService, AsyncSession, DRE e métricas financeiras.

### Community 56 - "products.py"
Cohesion: 0.40
Nodes (5): product_analysis(), AsyncSession, Rotas de análise de produtos., Análise completa de produtos: margem, parados e ruptura., top_products()

### Community 57 - "CategoryCreate"
Cohesion: 0.33
Nodes (6): create_category(), Cria uma categoria no catálogo., Atualiza nome e descrição de uma categoria existente., update_category(), CategoryCreate, Entrada para criação ou atualização de uma categoria.

### Community 58 - "SupplierCreate"
Cohesion: 0.33
Nodes (6): create_supplier(), Cria um fornecedor para vínculo com produtos e compras., Atualiza os dados de um fornecedor existente., update_supplier(), Entrada para criação ou atualização de fornecedor., SupplierCreate

### Community 59 - "database.py"
Cohesion: 0.40
Nodes (4): get_db(), AsyncSession, Configuração de conexão e sessão assíncrona com o banco de dados., Entrega uma sessão de banco por requisição e controla commit/rollback.

### Community 60 - "add_variant"
Cohesion: 0.50
Nodes (4): add_variant(), Adiciona variante de tamanho/cor a um produto., Entrada para criação de variante de produto., VariantIn

### Community 61 - "update_product"
Cohesion: 0.50
Nodes (4): Atualiza dados editáveis de um produto., update_product(), ProductUpdate, Entrada parcial para atualizar dados editáveis de um produto.

### Community 62 - "StockService"
Cohesion: 0.50
Nodes (3): Serviços de negócio para controle de estoque., Aplica movimentações de entrada e saída de estoque., StockService

### Community 64 - "main.py"
Cohesion: 0.50
Nodes (3): health(), Ponto de entrada HTTP da API LGD Mantos.  Este módulo configura a aplicação Fa, Retorna um status simples para checagens de disponibilidade da API.

### Community 65 - "upload_photo"
Cohesion: 0.67
Nodes (3): UploadFile, Recebe upload de foto e associa o arquivo ao produto., upload_photo()

## Knowledge Gaps
- **151 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+146 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Product` connect `Product` to `CatalogService`, `repositories.py`, `SupervisorService`, `data_quality_repository.py`, `Base`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `SupervisorService` connect `SupervisorService` to `Product`, `agent_context_service.py`, `PolicyEngine`, `DataAgentOutput`, `schemas.py`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `Base` connect `Base` to `KnowledgeDocument`, `repositories.py`, `Approval`, `Product`, `Supplier`, `.queue_campaign`, `SupervisorService`, `database.py`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **What connects `Pacote principal da aplicação backend LGD Mantos.`, `Infraestrutura central do backend, como configuração, banco e autenticação.`, `Funções simples de autenticação baseada em token JWT.` to the rest of the system?**
  _505 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `useNav` be split into smaller, more focused modules?**
  _Cohesion score 0.09359605911330049 - nodes in this community are weakly interconnected._
- **Should `KnowledgeDocument` be split into smaller, more focused modules?**
  _Cohesion score 0.05370101596516691 - nodes in this community are weakly interconnected._
- **Should `CatalogService` be split into smaller, more focused modules?**
  _Cohesion score 0.05959183673469388 - nodes in this community are weakly interconnected._