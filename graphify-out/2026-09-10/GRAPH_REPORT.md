# Graph Report - LGD-Mantos  (2026-09-03)

## Corpus Check
- 3 files · ~180,518 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1654 nodes · 3419 edges · 102 communities (67 shown, 29 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 183 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Repositorios de Produtos e Financeiro
- Componentes de UI e Tipos Compartilhados
- CRUD de Catalogo (Servico)
- Rotas e Schemas de Analise de Categoria/Canal
- Tipos e Componentes de Analytics (frontend)
- Modelos ORM e Fixtures de Teste - Marketing Ops
- Knowledge Layer (Modelo, Rotas, Schemas)
- Repositorio Operacional (Getters)
- Agentes Agno (build_* e content/creative_agent.py)
- Servico de Catalogo (Metodos)
- Servico e Testes da Fila de Publicacao
- Entrada de Mercadoria e Modelos de Operacoes
- Schemas Pydantic de Analytics
- Tipos TypeScript de Operacoes e Marketing (types.ts)
- Tipos TypeScript de Navegacao e Agentes (types.ts)
- Pipeline do SupervisorService
- Telas de Cadastros e Operacional (frontend)
- Servico de Exportacao (CSV/ZIP)
- Core: Banco, Migrations e Modelos de Catalogo
- Testes de Resolucao de SKU e Workflow
- package.json - Dependencias Frontend
- Tipos TypeScript dos Componentes de UI
- Servico de Estoque e Schemas Operacionais
- Schemas Pydantic de Catalogo
- tsconfig.app.json - Compiler Options
- Servico de Aprovacao (Human-in-the-loop)
- Servicos de Analise e Preferencias (usam PreferenceService)
- Repositorio de Qualidade de Dados
- Tela EntryForm (Entrada de Mercadoria)
- Core get_db e Rotas HTTP de Vendas
- Rotas do ApprovalAgent
- PolicyEngine - Regras Absolutas
- Rotas e Schemas do Supervisor
- Rotas e Servico do Dashboard/Contexto
- Rotas e Schemas de Preferencias de Alerta
- tsconfig.node.json - Compiler Options
- Autenticacao - Login e Token
- Core Auth e Rotas de Estoque
- Config do Backend e init_db.py
- Schemas de Aprovacao
- Rotas de Despesas
- Servico de Despesas
- Navegacao e Service Worker (main.tsx, pwa.ts, nav.tsx)
- Doc Consolidacao 2026-07-16 (decisoes e fixes)
- Doc Plano de Consolidacao Multi-Agente (fases e bugs)
- Tela de Sugestao de Reposicao de Compras
- PolicyEngine - Teste Preco Inventado
- Doc Docker Compose de Producao e Dependencias
- PolicyEngine - Teste de Campanha
- PolicyEngine - Teste de Publicacao
- Rota e Servico de Qualidade de Dados
- Rotas de Analise de Produtos
- CLAUDE.md - Instrucoes do Projeto
- Tela de Marketing Intelligence
- PreferenceService - Metodos (get/get_safe/update)
- Rota e Servico DRE (Financeiro)
- Rota de Health e Versao da API
- Migrations 0001/0002
- Tela ApprovalDetail (Marketing)
- Schemas de Observabilidade de Agentes
- Schemas da Fila de Publicacao
- Spec - Bloco App da Secao Mais (conceitos)
- PolicyEngine - Testes de Barreiras Absolutas
- PolicyEngine - Teste Aprovacao Humana
- PolicyEngine - Teste Promessa de Estoque
- main.py - Entry Point e CORS
- Doc Deploy VPS e Seguranca
- Rota de Regeneracao de Aprovacao
- Rota de Marketing Intelligence
- Pacote operational/ e Servico de Despesas
- Doc Testes Automatizados (Fase C)
- Config do Vite (versao e build hash)
- tsconfig.json Raiz
- Pacote core/ (Backend)
- Pacote app/ (Backend)
- Pacote agents/agents/
- Pacote approval/ (ApprovalAgent)
- Pacote modules/agents/
- Pacote knowledge/ (Knowledge Layer)
- Pacote marketing_ops/
- Roteador Principal de Agentes
- Pacote supervisor/
- Pacote analytics/
- Pacote auth/
- Pacote export/ (Exportacao de Dados)
- Pacote modules/ (Backend)
- Pacote routes/ (Operational)
- Pacote settings/ (Preferencias)
- Pacote system/ (Status do Sistema)
- Pacote shared/ (Backend)
- Pacote shared/schemas/
- No Isolado - AgentRun
- No Isolado - Product
- No Isolado - UploadFile
- No Isolado - Expense
- No Isolado - get

## God Nodes (most connected - your core abstractions)
1. `useNav()` - 54 edges
2. `useData()` - 39 edges
3. `AppBar()` - 38 edges
4. `api` - 38 edges
5. `ScreenBody()` - 37 edges
6. `Ico` - 33 edges
7. `Product` - 31 edges
8. `fmtBRL()` - 29 edges
9. `Base` - 28 edges
10. `PolicyEngine` - 28 edges

## Surprising Connections (you probably didn't know these)
- `Serviço web — Caddy (PWA + reverse proxy + HTTPS)` --shares_data_with--> `index.html — entrypoint do PWA LGD Mantos`  [INFERRED]
  docker-compose.prod.yml → frontend_pwa/index.html
- `FASE A — Validação E2E com Ollama real + Seed de Knowledge (concluída)` --conceptually_related_to--> `Serviço ollama — inferência local llama3.1:8b`  [INFERRED]
  docs/plans/PLAN-20260716-1846-consolidacao-agentes-marketing.md → docker-compose.prod.yml
- `Verificação manual ponta a ponta (seção 11)` --conceptually_related_to--> `FASE A — Validação E2E com Ollama real + Seed de Knowledge (concluída)`  [INFERRED]
  FABLE_CONSOLIDACAO_2026-07-16.md → docs/plans/PLAN-20260716-1846-consolidacao-agentes-marketing.md
- `Guia de Deploy em Produção — VPS único` --conceptually_related_to--> `Estrutura Alembic (migrations de schema)`  [INFERRED]
  docs/DEPLOY.md → FABLE_CONSOLIDACAO_2026-07-16.md
- `Plano — Consolidação e Finalização da Camada Multi-Agente de Marketing` --cites--> `.env com segredos reais commitado no git`  [EXTRACTED]
  docs/plans/PLAN-20260716-1846-consolidacao-agentes-marketing.md → FABLE_CONSOLIDACAO_2026-07-16.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **As três telas do bloco APP da seção Mais** — specs_bloco_app_mais_spec_configuracoes, specs_bloco_app_mais_spec_status_sistema, specs_bloco_app_mais_spec_sobre_app [EXTRACTED 1.00]
- **Fases do plano de consolidação da camada multi-agente de marketing** — docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fase0, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasea, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_faseb, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasec, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasee1, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fased, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasee2, docs_plans_plan_20260716_1846_consolidacao_agentes_marketing_fasee3 [EXTRACTED 1.00]
- **Correção do drift recharts v2→v3 no build do frontend** — fable_consolidacao_2026_07_16_recharts_v3_migration, frontend_pwa_src_screens_an_dre, frontend_pwa_src_screens_an_bychannel, frontend_pwa_src_screens_an_categorias, frontend_pwa_src_screens_an_categorydetail, frontend_pwa_src_screens_an_dashboard, frontend_pwa_src_components_analytics [EXTRACTED 1.00]

## Communities (102 total, 29 thin omitted)

### Community 0 - "Repositorios de Produtos e Financeiro"
Cohesion: 0.06
Nodes (71): expenses_by_category(), expenses_total(), monthly_cogs_evolution(), monthly_expenses_evolution(), monthly_revenue_evolution(), AsyncSession, datetime, Consultas financeiras sobre despesas. (+63 more)

### Community 1 - "Componentes de UI e Tipos Compartilhados"
Cohesion: 0.07
Nodes (48): App(), AppBar(), AppBarProps, FABProps, IcoFn, OP_TABS, OpScreen, ScreenBody() (+40 more)

### Community 2 - "CRUD de Catalogo (Servico)"
Cohesion: 0.05
Nodes (62): add_variant(), create_category(), create_channel(), create_product(), create_supplier(), deactivate_product(), delete_category(), delete_photo() (+54 more)

### Community 3 - "Rotas e Schemas de Analise de Categoria/Canal"
Cohesion: 0.05
Nodes (45): category_buying_patterns(), category_performance(), category_size_distribution(), category_size_stock(), category_stock_coverage(), product_attribute_analysis(), AsyncSession, Rotas de análise centradas em categoria. (+37 more)

### Community 4 - "Tipos e Componentes de Analytics (frontend)"
Cohesion: 0.07
Nodes (41): Correção do build — drift recharts v2→v3, AlertRow(), AlertRowProps, CovBadge(), MetricInfoProps, NavItem(), Period, periodLabel() (+33 more)

### Community 5 - "Modelos ORM e Fixtures de Teste - Marketing Ops"
Cohesion: 0.06
Nodes (40): Base, Classe base usada por todos os modelos ORM do projeto., AgentRun, Approval, Campaign, CreativeBrief, Post, Modelos ORM da camada Marketing Ops. Estes modelos são o workspace dos agentes:… (+32 more)

### Community 6 - "Knowledge Layer (Modelo, Rotas, Schemas)"
Cohesion: 0.05
Nodes (40): KnowledgeDocument, Modelo ORM para documentos da Knowledge Layer.  Armazena contexto de marca (to, Documento de conhecimento de marca consultado pelos agentes como contexto., create_document(), delete_document(), get_document(), list_documents(), AsyncSession (+32 more)

### Community 7 - "Repositorio Operacional (Getters)"
Cohesion: 0.06
Nodes (48): get_category(), get_channel(), get_entry(), get_expense(), get_product(), get_product_by_sku(), get_product_variant(), get_sale() (+40 more)

### Community 8 - "Agentes Agno (build_* e content/creative_agent.py)"
Cohesion: 0.05
Nodes (41): build_content_agent(), build_content_agent_input(), Agent, StrategyAgentOutput, ContentAgent — gera copy e textos para o post de marketing. Recebe a estratégia…, Cria uma instância fresca do ContentAgent para cada run., Monta o payload de entrada para o ContentAgent. `revision_feedback` é o…, build_creative_agent() (+33 more)

### Community 9 - "Servico de Catalogo (Metodos)"
Cohesion: 0.06
Nodes (28): CatalogService, AsyncSession, Category, Product, SaleChannel, Supplier, UploadFile, Serviços de negócio para cadastro e manutenção do catálogo. (+20 more)

### Community 10 - "Servico e Testes da Fila de Publicacao"
Cohesion: 0.09
Nodes (28): PublishingQueue, Fila de publicação de campanhas aprovadas. Ciclo: `approved` (enfileirada após…, list_queue(), mark_published(), AsyncSession, delete, get, post (+20 more)

### Community 11 - "Entrada de Mercadoria e Modelos de Operacoes"
Cohesion: 0.07
Nodes (38): create_entry(), get_entry(), list_entries(), AsyncSession, Rotas HTTP para entrada de mercadoria., Registra entrada de mercadoria, criando produtos e variantes inline., Lista entradas de mercadoria recentes., Detalhe de uma entrada de mercadoria com todos os itens. (+30 more)

### Community 12 - "Schemas Pydantic de Analytics"
Cohesion: 0.10
Nodes (35): AgentContextResponse, AttentionBlock, OpportunitiesBlock, BaseModel, Contratos de resposta do payload de contexto para agentes de IA., ShopHealth, DailyRevenue, DashboardResponse (+27 more)

### Community 13 - "Tipos TypeScript de Operacoes e Marketing (types.ts)"
Cohesion: 0.06
Nodes (35): KPI(), EntryDetail(), fmtDate(), VariantInfo, fmtDateTime(), SaleDetail(), VariantInfo, CartItem (+27 more)

### Community 14 - "Tipos TypeScript de Navegacao e Agentes (types.ts)"
Cohesion: 0.07
Nodes (31): Nav, NavCtx, NavEntry, TAB_ROOTS, TabId, APPROVAL_FILTERS, ApprovalFilter, AprovacoesTab() (+23 more)

### Community 15 - "Pipeline do SupervisorService"
Cohesion: 0.12
Nodes (31): AgentRun, _create_approval(), _extract_product_photos(), _fit(), _load_active_skus(), AsyncSession, ContentAgentOutput, CreativeAgentOutput (+23 more)

### Community 16 - "Telas de Cadastros e Operacional (frontend)"
Cohesion: 0.15
Nodes (27): BottomNav(), FAB(), OpSubNav(), ChannelChip(), ErrorBody(), SearchBar(), useData(), useNav() (+19 more)

### Community 17 - "Servico de Exportacao (CSV/ZIP)"
Cohesion: 0.12
Nodes (23): export_backup(), export_dataset(), AsyncSession, get, Rotas de exportação de dados — backup manual do operador em CSV/ZIP., Baixa um .zip com um CSV por conjunto — backup completo em um único arquivo.…, Baixa o CSV de um conjunto (produtos, vendas, compras, despesas, movimentacoes,…, _csv_bytes() (+15 more)

### Community 18 - "Core: Banco, Migrations e Modelos de Catalogo"
Cohesion: 0.09
Nodes (26): Configuração de conexão e sessão assíncrona com o banco de dados., Modelos ORM do catálogo de produtos, fornecedores e variantes., Fornecedor de produtos e compras da loja., Canal de venda pelo qual as transações podem ser realizadas., SaleChannel, Supplier, now(), datetime (+18 more)

### Community 19 - "Testes de Resolucao de SKU e Workflow"
Cohesion: 0.11
Nodes (15): _normalize_sku_tokens(), Normaliza um SKU em conjunto de tokens alfanuméricos maiúsculos. Permite…, Resolve o SKU indicado pelo StrategyAgent para um produto ativo do catálogo. O…, Persiste um novo AgentRun em estado pending e retorna o objeto., _resolve_campaign_product(), create_product(), Cria produto ativo com uma variante e o estoque informado., Testes da resolução tolerante de SKU do Supervisor. O StrategyAgent (LLM) pode… (+7 more)

### Community 20 - "package.json - Dependencias Frontend"
Cohesion: 0.06
Nodes (30): dependencies, react, react-dom, recharts, devDependencies, @types/node, @types/react, @types/react-dom (+22 more)

### Community 21 - "Tipos TypeScript dos Componentes de UI"
Cohesion: 0.08
Nodes (24): BadgeProps, BadgeTone, BtnKind, BtnProps, CardProps, ChannelChipProps, ErrorBodyProps, fmtBRL() (+16 more)

### Community 22 - "Servico de Estoque e Schemas Operacionais"
Cohesion: 0.09
Nodes (24): AsyncSession, StockMovement, Serviços de negócio para controle de estoque., Aplica movimentações de entrada e saída de estoque., Registra movimentação manual e ajusta o saldo da variante., StockService, ExpenseIn, ExpenseOut (+16 more)

### Community 23 - "Schemas Pydantic de Catalogo"
Cohesion: 0.11
Nodes (24): CategoryCreate, CategoryOut, ProductCreate, ProductOut, ProductUpdate, BaseModel, Schemas Pydantic usados pelas rotas de catálogo., Entrada para criação ou atualização de uma categoria. (+16 more)

### Community 24 - "tsconfig.app.json - Compiler Options"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+13 more)

### Community 25 - "Servico de Aprovacao (Human-in-the-loop)"
Cohesion: 0.16
Nodes (11): ApprovalService, AgentRun, AsyncSession, ApprovalService — lógica de negócio do human-in-the-loop.  Regras absolutas:, Rejeita a campanha. Comentário obrigatório., Solicita revisão. Comentário com o que deve ser ajustado é obrigatório., Retorna o estado atual de um agent_run para polling de status., Retorna todas as aprovações com status pending, com campaign carregada. (+3 more)

### Community 26 - "Servicos de Analise e Preferencias (usam PreferenceService)"
Cohesion: 0.18
Nodes (13): _load_context(), Carrega todo o contexto necessário para o pipeline de uma só vez., AgentContextService, AsyncSession, Empacota dados analíticos estruturados para consumo de agentes de IA. Regra:…, MarketingIntelligenceService, AsyncSession, Classifica produtos em listas de ação para decisões de conteúdo e promoção. (+5 more)

### Community 27 - "Repositorio de Qualidade de Dados"
Cohesion: 0.18
Nodes (17): count_active_products(), count_active_variants(), expenses_no_category(), products_no_category(), products_no_cost_price(), products_no_photo(), products_no_sale_price(), products_no_supplier() (+9 more)

### Community 28 - "Tela EntryForm (Entrada de Mercadoria)"
Cohesion: 0.15
Nodes (17): blankCard(), blankExtra(), blankVariant(), CardExtra, cellSelectStyle, EntryForm(), fieldLabelRow, parseNum() (+9 more)

### Community 29 - "Core get_db e Rotas HTTP de Vendas"
Cohesion: 0.14
Nodes (15): get_db(), AsyncSession, Entrega uma sessão de banco por requisição e controla commit/rollback., create_sale(), delete_sale(), list_sales(), AsyncSession, delete (+7 more)

### Community 30 - "Rotas do ApprovalAgent"
Cohesion: 0.17
Nodes (16): approve(), get_approval(), list_approvals(), list_pending_approvals(), AsyncSession, get, post, Solicita revisão da campanha. Comentário com o que ajustar é obrigatório. (+8 more)

### Community 31 - "PolicyEngine - Regras Absolutas"
Cohesion: 0.22
Nodes (9): PolicyEngine, PolicyResult, Agentes nunca podem alterar estoque., Agentes nunca podem alterar preço., Agentes nunca podem registrar vendas., Agentes nunca podem apagar produtos., Agentes não geram imagens localmente no MVP., Publicação automática bloqueada no MVP. (+1 more)

### Community 32 - "Rotas e Schemas do Supervisor"
Cohesion: 0.17
Nodes (14): create_run(), get_run(), list_runs(), AsyncSession, Rotas do Supervisor — entry point para criação e monitoramento de agent runs., Cria um agent run e dispara o pipeline de geração de campanha em background., Lista agent runs com paginação e filtro opcional por status., Retorna o status atual de um agent run — use para polling após criar um run. (+6 more)

### Community 33 - "Rotas e Servico do Dashboard/Contexto"
Cohesion: 0.12
Nodes (11): agent_context(), AsyncSession, Rota de contexto para agentes de IA — payload analítico agregado e curado., Retorna pacote estruturado com saúde da loja, alertas e oportunidades., dashboard(), AsyncSession, Rota do dashboard executivo., Roteador principal de analytics — agrega todos os sub-routers do módulo. (+3 more)

### Community 34 - "Rotas e Schemas de Preferencias de Alerta"
Cohesion: 0.17
Nodes (14): get_preferences(), AsyncSession, get, put, Rotas de preferências configuráveis do sistema — limiares de alerta., Retorna os limiares de alerta vigentes (valores padrão quando ainda não…, Atualiza os limiares de alerta usados pelas análises de estoque e ruptura., update_preferences() (+6 more)

### Community 35 - "tsconfig.node.json - Compiler Options"
Cohesion: 0.13
Nodes (14): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+6 more)

### Community 36 - "Autenticacao - Login e Token"
Cohesion: 0.22
Nodes (9): create_token(), Funções simples de autenticação baseada em token JWT., Cria um token de acesso para o usuário proprietário do sistema., Configurações carregadas do ambiente para o backend., login(), post, LoginIn, BaseModel (+1 more)

### Community 37 - "Core Auth e Rotas de Estoque"
Cohesion: 0.17
Nodes (12): Valida o token enviado no cabeçalho Authorization das rotas protegidas., verify_token(), AsyncSession, get, post, Rotas HTTP para movimentações e histórico de estoque., Registra uma movimentação manual de estoque., Retorna movimentações recentes de uma variante. (+4 more)

### Community 38 - "Config do Backend e init_db.py"
Cohesion: 0.17
Nodes (11): Config, Converte CORS_ORIGINS em lista, ignorando entradas vazias., Define o arquivo `.env` como fonte adicional de configuração local., Agrupa variáveis de ambiente usadas pela API. Segurança: DATABASE_URL,…, Settings, _detect_state(), main(), Rotina de inicialização do banco — agora baseada em Alembic. Cenários tratados:… (+3 more)

### Community 39 - "Schemas de Aprovacao"
Cohesion: 0.23
Nodes (12): ApprovalDetail, ApprovalListItem, CampaignSummary, CreativeBriefSummary, DecisionRequest, PostSummary, BaseModel, Schemas Pydantic para o módulo de aprovação (ApprovalAgent). (+4 more)

### Community 40 - "Rotas de Despesas"
Cohesion: 0.19
Nodes (12): create_expense(), list_expenses(), AsyncSession, ExpenseIn, get, post, put, Rotas HTTP para despesas operacionais. (+4 more)

### Community 41 - "Servico de Despesas"
Cohesion: 0.21
Nodes (10): delete_expense(), delete, Remove uma despesa existente., ExpenseService, AsyncSession, ExpenseIn, Cria e remove despesas usadas nos controles financeiros., Registra uma despesa operacional. (+2 more)

### Community 42 - "Navegacao e Service Worker (main.tsx, pwa.ts, nav.tsx)"
Cohesion: 0.19
Nodes (10): index.html — entrypoint do PWA LGD Mantos, NavProvider(), applyServiceWorkerUpdate(), getSnapshot(), listeners, PwaUpdateState, registerServiceWorker(), state (+2 more)

### Community 43 - "Doc Consolidacao 2026-07-16 (decisoes e fixes)"
Cohesion: 0.17
Nodes (11): Serviços de negócio para registro de vendas., Regra de ouro arquitetural — IA só na Agentic Layer, Remoção de AnalyticsService morto (zero consumidores), Consolidação da Base de Código — 2026-07-16, .env com segredos reais commitado no git, MerchandiseEntry — fluxo vivo de compras (/entries), PolicyEngine aplicado pelo Supervisor, Estado morto waiting_approval adiado (PublishingStatus) (+3 more)

### Community 44 - "Doc Plano de Consolidacao Multi-Agente (fases e bugs)"
Cohesion: 0.26
Nodes (12): Risco arquitetural: execute_workflow via BackgroundTasks sem retomada após crash, Bug: StringDataRightTruncationError em format (VARCHAR(100)), Bug: falso positivo do PolicyEngine em 'reais' (fotos reais do produto), Bug: alucinação de SKU pelo StrategyAgent (BR02-MANTO vs MANTO-BR02), Plano — Consolidação e Finalização da Camada Multi-Agente de Marketing, FASE A — Validação E2E com Ollama real + Seed de Knowledge (concluída), FASE B — Ciclo de revisão com re-geração por feedback (concluída), FASE D — Provedor LLM externo (opcional) (+4 more)

### Community 45 - "Tela de Sugestao de Reposicao de Compras"
Cohesion: 0.18
Nodes (8): classify(), ComprasReposicao(), EnrichedPattern, GROUP_META, GroupId, Signal, BuyingPattern, CategorySizeStock

### Community 46 - "PolicyEngine - Teste Preco Inventado"
Cohesion: 0.29
Nodes (3): Bloqueia copy que menciona preço sem contexto verificado. A palavra "reais" só…, Regressão: 'fotos reais do produto' não é preço — não pode bloquear., TestPrecoInventado

### Community 47 - "Doc Docker Compose de Producao e Dependencias"
Cohesion: 0.27
Nodes (11): agno==2.6.19 (framework de agentes), backend/requirements.txt — dependências de produção, ollama==0.6.2 (cliente Ollama), openai==2.44.0 (cliente compatível OpenAI usado pelo Ollama), Serviço backend — API FastAPI em modo produção, Serviço db — Postgres 16 (rede interna), Serviço ollama — inferência local llama3.1:8b, Stack de produção Docker Compose (VPS único) (+3 more)

### Community 48 - "PolicyEngine - Teste de Campanha"
Cohesion: 0.27
Nodes (3): Bloqueia campanha para produto sem estoque., Bloqueia campanha que inclui desconto não autorizado explicitamente., TestCampanha

### Community 49 - "PolicyEngine - Teste de Publicacao"
Cohesion: 0.27
Nodes (3): Bloqueia publicação sem aprovação humana., Bloqueia publicação em canal não autorizado., TestPublicacao

### Community 50 - "Rota e Servico de Qualidade de Dados"
Cohesion: 0.20
Nodes (7): data_quality(), AsyncSession, Rota de qualidade dos dados — score e problemas detectados., Retorna score de qualidade dos dados e lista de inconsistências por tipo., DataQualityService, AsyncSession, Avalia completude e consistência dos dados operacionais da loja.

### Community 51 - "Rotas de Analise de Produtos"
Cohesion: 0.24
Nodes (7): product_analysis(), AsyncSession, Rotas de análise de produtos., Análise completa de produtos: margem, parados e ruptura., top_products(), AsyncSession, Análise completa de produtos: margem, parados, risco de ruptura e categorias.

### Community 52 - "CLAUDE.md - Instrucoes do Projeto"
Cohesion: 0.20
Nodes (8): caveman, Claude - Contexto e Instruções, graphify, Regras de economia para fluxos com subagentes (implementador/revisor, Explore, Plan), Regras, Instruções de Execução e Uso de Tools (NÃO IGNORAR), Regras obrigatórias de economia, Sobre o Projeto *LGD Mantos*, Uso de Tools

### Community 53 - "Tela de Marketing Intelligence"
Cohesion: 0.22
Nodes (6): MetricInfo(), GroupConfig, GROUPS, MarketingIntel(), MarketingIntelligence, MarketingVariant

### Community 54 - "PreferenceService - Metodos (get/get_safe/update)"
Cohesion: 0.31
Nodes (6): AppPreference, AsyncSession, Retorna as preferências vigentes, ou os padrões se nada foi salvo ainda. Usado…, Como get(), mas nunca propaga erro — cai para os padrões em qualquer falha.…, Grava os limiares informados, criando o registro único na primeira vez (upsert)., PreferencesUpdate

### Community 55 - "Rota e Servico DRE (Financeiro)"
Cohesion: 0.22
Nodes (6): dre(), AsyncSession, Rotas de análise financeira e DRE., FinanceService, AsyncSession, DRE e métricas financeiras.

### Community 56 - "Rota de Health e Versao da API"
Cohesion: 0.25
Nodes (6): Versão da API — fonte única de verdade. Usada tanto em `FastAPI(version=...)`…, health(), AsyncSession, get, Rota pública de status do sistema — usada pela tela "Status do sistema" do PWA., Verifica conectividade real com o banco e devolve a versão em vigor da API.…

### Community 58 - "Tela ApprovalDetail (Marketing)"
Cohesion: 0.32
Nodes (6): Textarea(), ApprovalDetailScreen(), BadgeTone, riskBadge(), statusBadge(), AgentApprovalDetail

### Community 59 - "Schemas de Observabilidade de Agentes"
Cohesion: 0.33
Nodes (6): OpsMetrics, BaseModel, Schemas de observabilidade da camada de agentes., Entrada resumida de um agent run para o log de operações., Métricas consolidadas do sistema de agentes., RunLogEntry

### Community 60 - "Schemas da Fila de Publicacao"
Cohesion: 0.33
Nodes (6): PublishingQueueItem, BaseModel, QueueRequest, Schemas da fila de publicação., Item da fila de publicação., Payload para enfileirar uma campanha aprovada para publicação.

### Community 61 - "Spec - Bloco App da Secao Mais (conceitos)"
Cohesion: 0.43
Nodes (7): Modelo AppPreference (migration 0004_preferencias_de_alerta), Tela Configurações (alertas, exportação, segurança), Spec — Bloco App da seção Mais, Serviço de exportação de dados (CSV por conjunto + ZIP), Endpoint GET /api/v1/health, Tela Sobre o app (versão única de build), Tela Status do sistema (conexão, versão, atualização PWA)

### Community 62 - "PolicyEngine - Testes de Barreiras Absolutas"
Cohesion: 0.33
Nodes (3): Policy Engine — código determinístico que bloqueia ações perigosas. Regra: este…, Testes do PolicyEngine — todas as regras determinísticas da camada de agentes.…, TestBarreirasAbsolutas

### Community 65 - "main.py - Entry Point e CORS"
Cohesion: 0.33
Nodes (5): health(), Ponto de entrada HTTP da API LGD Mantos. Este módulo configura a aplicação…, Retorna um status simples para checagens de disponibilidade da API., CORS restrito via CORS_ORIGINS, get

### Community 66 - "Doc Deploy VPS e Seguranca"
Cohesion: 0.47
Nodes (6): Rotina de backup diário (pg_dump + retenção 14 dias), Guia de Deploy em Produção — VPS único, Migração Render/Vercel → VPS único, Rotação dos 3 segredos expostos no deploy, Master Plan Tracker — LGD Mantos, FASE 0 — Migração de servidor Render/Vercel → VPS

### Community 67 - "Rota de Regeneracao de Aprovacao"
Cohesion: 0.40
Nodes (4): Rotas do ApprovalAgent — human-in-the-loop da camada de agentes., Re-gera copy e direção criativa usando o comentário da revisão como feedback.…, regenerate_after_revision(), BackgroundTasks

### Community 68 - "Rota de Marketing Intelligence"
Cohesion: 0.40
Nodes (4): marketing_intelligence(), AsyncSession, Rota de inteligência de marketing — classificação de produtos para ações., Classifica produtos em listas de ação: postar, promover, destacar, evitar.

### Community 70 - "Doc Testes Automatizados (Fase C)"
Cohesion: 0.50
Nodes (4): backend/requirements-dev.txt — dependências de teste, pytest==8.4.2 + pytest-asyncio==1.2.0, FASE C — Rede mínima de testes (concluída, 56 testes verdes), Fase de testes automatizados pulada por decisão do usuário

## Knowledge Gaps
- **164 isolated node(s):** `IcoKey`, `NumberFieldProps`, `BadgeProps`, `BadgeTone`, `BtnKind` (+159 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 720 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Consolidação da Base de Código — 2026-07-16` connect `Doc Consolidacao 2026-07-16 (decisoes e fixes)` to `main.py - Entry Point e CORS`, `Doc Deploy VPS e Seguranca`, `Tipos e Componentes de Analytics (frontend)`, `Autenticacao - Login e Token`, `Doc Testes Automatizados (Fase C)`, `Doc Plano de Consolidacao Multi-Agente (fases e bugs)`, `Doc Docker Compose de Producao e Dependencias`, `Migrations 0001/0002`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Why does `Correção do build — drift recharts v2→v3` connect `Tipos e Componentes de Analytics (frontend)` to `Doc Consolidacao 2026-07-16 (decisoes e fixes)`?**
  _High betweenness centrality (0.174) - this node is a cross-community bridge._
- **Why does `PolicyEngine aplicado pelo Supervisor` connect `Doc Consolidacao 2026-07-16 (decisoes e fixes)` to `Pipeline do SupervisorService`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **What connects `IcoKey`, `NumberFieldProps`, `BadgeProps` to the rest of the system?**
  _164 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Repositorios de Produtos e Financeiro` be split into smaller, more focused modules?**
  _Cohesion score 0.06049213943950786 - nodes in this community are weakly interconnected._
- **Should `Componentes de UI e Tipos Compartilhados` be split into smaller, more focused modules?**
  _Cohesion score 0.06777493606138107 - nodes in this community are weakly interconnected._
- **Should `CRUD de Catalogo (Servico)` be split into smaller, more focused modules?**
  _Cohesion score 0.05478750640040963 - nodes in this community are weakly interconnected._