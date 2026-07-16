# Consolidação da Base de Código — 2026-07-16

Documento de contexto das mudanças realizadas na etapa de revisão e consolidação
do projeto LGD Mantos. Serve como referência para as próximas ações de
desenvolvimento — o que mudou, por quê, o que foi verificado e o que ficou pendente.

---

## 1. Contexto da etapa

Uma revisão completa da base identificou que o miolo operacional do sistema
(catálogo, entradas, vendas, despesas, analytics, pipeline de agentes) **já existia
e funcionava**, mas convivia com três categorias de problema:

1. **Código morto/quebrado**: módulo de pedidos de compra com imports de modelos
   inexistentes; build do frontend quebrado; dependência Python faltante que impedia
   o backend de subir.
2. **Regras declaradas mas não aplicadas**: ~70% do PolicyEngine nunca era chamado;
   `Campaign.product_id` nunca era gravado; custo de venda vinha do cliente.
3. **Fundação frágil**: sem migrations, sem índices, segredos versionados no git,
   race conditions em estoque.

Esta etapa corrigiu os três grupos. **Testes automatizados foram explicitamente
pulados a pedido do usuário** — a verificação foi feita manualmente ponta a ponta
(seção 11).

---

## 2. Fase 1 — Remoção do módulo de compras morto

**Decisão de produto**: o fluxo vivo de compras do sistema é `MerchandiseEntry`
(entrada de mercadoria via `/entries`). O `App.tsx` já roteava a tela
`purchase-form` para `<EntryForm />`, e `PurchaseForm.tsx` não era importado em
lugar nenhum. O módulo `PurchaseOrder` era um esqueleto paralelo quebrado
(importava modelos `PurchaseOrder`/`PurchaseOrderItem` e schemas `POIn`/`POOut`
que **nunca existiram**). Foi removido, não implementado.

**Arquivos deletados:**
- `backend/app/modules/operational/services/purchase_service.py`
- `backend/app/modules/operational/routes/purchase_routes.py`
- `frontend_pwa/src/screens/op/PurchaseForm.tsx`

**Nota para o futuro**: se um dia o ciclo formal de pedido de compra
(rascunho → enviado → recebido) virar requisito real, implementar do zero com
modelo próprio — não havia nada aproveitável no código removido.

### 2.1 Correção do build do frontend (achado colateral)

O `npm run build` estava quebrado **antes desta etapa** — 7 erros de tipagem
causados por drift do recharts v3 (formatters de Tooltip escritos para a API do v2).
Corrigidos em:

- `frontend_pwa/src/screens/an/DRE.tsx` (2 formatters)
- `frontend_pwa/src/screens/an/ByChannel.tsx` (formatter + comparação redundante de tipo narrowed)
- `frontend_pwa/src/screens/an/Categorias.tsx` (formatter + labelFormatter)
- `frontend_pwa/src/screens/an/CategoryDetail.tsx` (formatter)
- `frontend_pwa/src/screens/an/Dashboard.tsx` (formatter)
- `frontend_pwa/src/components/Analytics.tsx` (prop `target` de `NavItem` tipada como `ScreenId`)

Padrão aplicado: `formatter={(v) => [fmt(Number(v ?? 0)), ...]}` — o recharts v3
passa `ValueType | undefined`, não `number`.

**Estado final**: `tsc -b` com 0 erros, `npm run build` gera `dist/` com PWA completo.

---

## 3. Fase 2 — Segurança

### 3.1 Segredos obrigatórios

`backend/app/core/config.py`: `APP_PASSWORD` e `APP_SECRET` **não têm mais valor
padrão** — a aplicação se recusa a subir sem eles no ambiente. Antes, um deploy
sem essas variáveis rodava silenciosamente com `"minhaloja123"` e
`"dev-secret-change-in-production"`, permitindo forjar tokens JWT.

### 3.2 CORS restrito

`backend/main.py`: `allow_origins=["*"]` substituído por lista vinda de
`settings.cors_origins_list` (nova config `CORS_ORIGINS`, separada por vírgula).
Padrão de desenvolvimento: `http://localhost:5173,http://127.0.0.1:5173`.

### 3.3 `.env` removido do versionamento — ⚠️ AÇÃO PENDENTE DO USUÁRIO

**Achado grave**: o `.env` com segredos reais estava **commitado no git** (aparece
nos commits `44d2c08`, `141326b`, `d7ecddf`, publicados no GitHub). O `.gitignore`
listava `.env`, mas ignore não vale para arquivo já rastreado.

- Feito: `git rm --cached .env` (arquivo local preservado, sai do índice).
- Criado `.env.example` como modelo documentado.
- **Pendente (responsabilidade do usuário)**: rotacionar os 3 segredos expostos —
  `APP_SECRET` (gerar novo: `openssl rand -hex 32`), `APP_PASSWORD` e a senha do
  PostgreSQL no Render. O histórico do git continua expondo os valores antigos;
  a rotação é o que neutraliza o vazamento. Limpeza de histórico
  (`git filter-repo`) é opcional após a rotação.

---

## 4. Fase 3 — Alembic (migrations de schema)

### 4.1 Estrutura criada

- `backend/alembic.ini` — configuração; a URL do banco NÃO fica aqui.
- `backend/migrations/env.py` — ambiente async (asyncpg); lê `DATABASE_URL` do
  `settings` da aplicação e importa todos os módulos de modelos para o autogenerate.
- `backend/migrations/script.py.mako` — template de novas revisions.
- `backend/migrations/versions/0001_baseline.py` — schema completo atual (18 tabelas),
  gerado por autogenerate contra banco vazio.
- `backend/migrations/versions/0002_indices_operacionais.py` — 23 índices (ver 4.3).

### 4.2 `init_db.py` reescrito

Substituiu `Base.metadata.create_all` por lógica de 3 cenários:

1. **Banco vazio** → `alembic upgrade head` (cria tudo).
2. **Banco legado** (tem `products`, não tem `alembic_version` — caso do banco de
   produção no Render criado pelo antigo `create_all`) → `alembic stamp 0001` +
   `upgrade head`. O primeiro boot em produção após o deploy fará isso
   automaticamente e criará os índices da 0002.
3. **Banco já gerenciado** → apenas `upgrade head` (migrations pendentes).

Ambos os cenários 1 e 2 foram testados contra Postgres real (seção 11).

### 4.3 Índices adicionados (migration 0002 + `index=True` nos modelos)

FKs e colunas de consulta frequente: `products.category_id/supplier_id`,
`product_variants.product_id`, `stock_movements.variant_id/created_at`,
`sales.sold_at/sale_channel_id`, `sale_items.sale_id/variant_id`,
`expenses.date/supplier_id`, `merchandise_entries.supplier_id/entry_date`,
`merchandise_entry_items.entry_id/variant_id`, `agent_runs.status`,
`campaigns.agent_run_id`, `posts.campaign_id`, `creative_briefs.campaign_id`,
`approvals.campaign_id/status`, `publishing_queue.campaign_id`,
`knowledge_documents.doc_type`.

### 4.4 Regra a partir de agora

**Toda mudança de schema deve gerar migration** (`alembic revision --autogenerate`),
nunca editar tabela manualmente nem confiar no `create_all`. Os modelos e as
migrations estão sincronizados neste commit.

### 4.5 Infra de desenvolvimento

- `docker-compose.yml`: serviço `db` agora publica a porta **55432** no host
  (evita conflito com outros Postgres locais). Uso:
  `postgresql+asyncpg://postgres:lgdmantos123@localhost:55432/lgd_mantos`.
- Criado venv local em `backend/.venv` com todas as dependências (gitignorado).
- `alembic==1.18.5` adicionado ao `requirements.txt`.

---

## 5. Fase 4 — PolicyEngine aplicado e integridade de dados

### 5.1 Supervisor agora valida de verdade (`backend/app/modules/agents/supervisor/service.py`)

Antes, as validações de conteúdo do PolicyEngine existiam mas **nunca eram chamadas**.
Agora o `execute_workflow`:

1. **Após o StrategyAgent**: resolve o `product_sku` retornado pelo LLM contra o
   catálogo real (`_resolve_campaign_product`, produto ativo + variantes carregadas).
   SKU inexistente/inativo → run falha com erro claro (LLM pode alucinar SKU).
2. Calcula estoque total das variantes e aplica
   `PolicyEngine.validate_campaign_product_has_stock` — produto sem estoque bloqueia
   a campanha antes de gerar qualquer conteúdo.
3. **Após o ContentAgent**: `_validate_content_policies` roda
   `validate_content_has_no_invented_price` e `validate_content_has_no_stock_promise`
   sobre caption, headline, cta_text e todas as variações. Bloqueio → run failed
   com o motivo (visível no polling de status).
4. **`Campaign.product_id` agora é gravado** — campanhas ficam ligadas ao produto
   real do catálogo (antes a FK existia mas nunca era preenchida).
5. `_load_product_photos` (consulta duplicada por SKU) substituído por
   `_extract_product_photos(product)` sobre o produto já resolvido.

### 5.2 Custo de venda resolvido no servidor

`backend/app/modules/operational/services/sales_service.py`: o `unit_cost` do
`SaleItem` vem de `variant.product.cost_price` — **o valor enviado pelo cliente é
ignorado** (alimenta margem e DRE, não pode ser confiado ao frontend). O campo
`unit_cost` permanece aceito em `SaleItemIn` só por compatibilidade (documentado
no schema). O frontend (`SaleModal.tsx`) continua enviando o campo — inofensivo.

### 5.3 Dependência faltante que impedia o boot — `openai`

**Achado crítico**: `agno==2.6.19` exige o pacote `openai` para instanciar o modelo
Ollama (usa cliente OpenAI-compatível internamente). O `requirements.txt` não o
incluía — **o backend atual não subia nem no Docker** (ImportError na cadeia
`main.py → agents.routes → supervisor → data_agent → agno.models.ollama`).
Adicionado `openai==2.45.0`.

---

## 6. Fase 5 — Testes (PULADA)

Pulada por decisão explícita do usuário. Consequência assumida: as verificações
desta etapa foram manuais (seção 11) e mudanças futuras não têm rede de regressão.
Se a decisão mudar, prioridade sugerida: PolicyEngine (puro, sem banco),
SalesService (venda/estorno), EntryService, ApprovalService.

---

## 7. Fase 6 — Configuração de LLM com ponto único de troca

`backend/app/modules/agents/config.py`:

- Nova variável de ambiente `AGENT_LLM_PROVIDER` (padrão `"ollama"`).
- `get_agent_model()` é o **único ponto de troca de provedor** — nenhum agente
  precisa mudar quando um provedor externo for adicionado.
- Provedor desconhecido → `ValueError` com mensagem orientando onde implementar.

**Limitação documentada**: produção no Render não roda Ollama (llama3.1:8b local).
Runs de agentes em produção falham com erro de conexão registrado no `AgentRun`
(status `failed`); o restante da API opera normalmente. Para destravar a aba
Marketing em produção: adicionar provedor de API externa aqui (exige chave do usuário).

---

## 8. Fase 7 — Locks de estoque

`backend/app/modules/operational/repositories.py`: `get_variant` e
`get_variant_with_product` ganharam parâmetro `for_update: bool` que aplica
`SELECT ... FOR UPDATE` (lock de linha até o fim da transação).

Aplicado em **todos os fluxos que mutam `stock_quantity`**:
- `SalesService.create_sale` (baixa por venda)
- `SalesService.delete_sale` (estorno)
- `StockService.stock_movement` (movimentação manual)
- `EntryService.create_entry` (entrada em variante existente)

Elimina a race condition de duas operações simultâneas lerem o mesmo saldo e
gravarem por cima (ex.: duas vendas da última unidade passando juntas).

---

## 9. Fase 8 — Limpeza

- `backend/app/modules/analytics/services/services.py` (classe `AnalyticsService`
  "mantida para compatibilidade") deletado — grep confirmou zero consumidores.
- Adiado conscientemente: remoção do estado morto `waiting_approval` do enum
  `PublishingStatus` (exigiria migration de enum no Postgres, valor baixo enquanto
  o PublishingAgent não é real).

---

## 10. Decisões adiadas (com justificativa)

| Item | Motivo do adiamento |
|---|---|
| Conversão `Expense.date` e `MerchandiseEntry.entry_date` de `String(10)` para `Date` | Mexeria em queries do analytics (comparações de tipo com asyncpg) sem rede de testes; ordenação lexicográfica ISO funciona corretamente hoje |
| Provedor LLM externo para produção | Exige chave de API do usuário; ponto de extensão pronto em `agents/config.py` |
| Padronização completa `Float` → `Numeric/Decimal` (`SaleChannel.fee_pct`, `monthly_goal`) | Invasivo, baixo risco atual; fazer junto com a conversão de datas |
| Enum `PublishingStatus` com estado morto | Migration de enum Postgres, valor baixo no MVP |
| Refresh/revogação de token (hoje: JWT 30 dias) | Aceitável para sistema single-user; decisão consciente |

---

## 11. Verificação executada (evidência real)

Ambiente: Postgres 16 via Docker (`lgd_db`, porta 55432), API uvicorn local
(venv `backend/.venv`), banco `lgd_mantos` zerado.

| Verificação | Resultado |
|---|---|
| `init_db.py` em banco vazio | 19 tabelas criadas (18 + alembic_version), 0001→0002 aplicadas |
| `init_db.py` em banco legado simulado (schema sem alembic_version) | Detectou legado, stamp 0001, upgrade 0002, 23 índices `ix_*` criados |
| Boot da API (`import main` + uvicorn) | OK após adição do `openai` |
| `GET /` (health) | `{"status":"ok"}` |
| `POST /api/v1/auth/login` | Token JWT emitido |
| `POST /api/v1/products` (produto + variante, estoque 5) | Criado |
| `POST /api/v1/sales` com `unit_cost: 999` forjado pelo cliente | Servidor gravou `unit_cost: 50.0` (custo do cadastro) — spoof ignorado |
| Estoque pós-venda | 5 → 3, movimento `saida 2` no ledger `stock_movements` |
| `GET /api/v1/analytics/dashboard` | Payload correto |
| `tsc -b` + `npm run build` (frontend) | 0 erros, dist/ + PWA gerados |
| Dados de teste | Limpos (TRUNCATE) após verificação |
| Grafo graphify | Atualizado (`graphify update .`) |

**Não verificado** (sem ambiente): pipeline de agentes com Ollama real (exige
modelo llama3.1:8b rodando); deploy no Render.
