---
plan_id: PLAN-20260716-1846-consolidacao-agentes-marketing
title: Consolidação e Finalização da Camada Multi-Agente de Marketing
created: 2026-07-16 18:46
status: active
category: business
phase: planning
priority: high
---

# 🎯 Plano: Consolidação e Finalização da Camada Multi-Agente de Marketing

> Decisões de produto tomadas pelo usuário em 2026-07-16 e incorporadas neste plano:
> **(1)** provedor de LLM externo opcional para produção; **(2)** publicação com
> **integração real de canais** (não apenas fechamento manual); **(3)** ciclo de
> revisão com **re-geração por feedback**; **(4)** rede mínima de testes agora.

---

## 1. Visão & Objetivos

### Visão
A aba Marketing do LGD Mantos gera campanhas completas (estratégia + copy + direção
criativa) a partir de dados reais da loja, com aprovação humana obrigatória, ciclo de
revisão funcional e publicação rastreada nos canais reais — operando tanto em ambiente
local (Ollama) quanto em produção (provedor externo).

### Objetivo Primário
Fechar os 3 ciclos abertos do módulo (geração validada, revisão, publicação) até que
uma campanha percorra o caminho completo **dados → geração → aprovação → publicação
no Instagram** com registro de `published_at`.

### Objetivos Secundários
- Pipeline validado ponta a ponta com llama3.1:8b real (nunca foi executado após a consolidação de 2026-07-16).
- Regras do PolicyEngine protegidas por testes automatizados (12 regras).
- Knowledge Layer populada com documentos de marca reais (hoje está vazia — agentes geram sem identidade LGD).

### Contexto — estado real do módulo (verificado no código em 2026-07-16)
O DIAGNOSTICO_AGENTES.md (junho) está desatualizado. **Já implementado:** pipeline de
4 agentes Agno com PolicyEngine aplicado pelo Supervisor; `POST /agents/runs` +
polling + listagem; 7 endpoints de aprovação; CRUD de knowledge; métricas ops;
fila de publicação com validação de aprovação; frontend `mk/` integrado à API real
(NewRun, RunDetail, ApprovalDetail, KnowledgeDocForm, hub Marketing.tsx).

**Lacunas reais:** (a) pipeline nunca rodou E2E com Ollama; (b) produção sem LLM;
(c) revisão é beco sem saída (comentário não é consumido, nada re-gera);
(d) fila de publicação sem consumidor — nada transiciona para `published`;
(e) zero testes; (f) knowledge vazia.

---

## 2. Escopo & Entregáveis

### No escopo
- Validação e ajuste do pipeline com Ollama real (prompts, políticas, latência).
- Seed de documentos de marca na Knowledge Layer (conteúdo fornecido pelo usuário).
- Re-geração pós-revisão consumindo o comentário humano como instrução.
- Provedor LLM externo plugável em `agents/config.py` (`AGENT_LLM_PROVIDER`).
- Testes: PolicyEngine, ApprovalService, Supervisor com LLM stub.
- Publicação real: fundação da fila (transições de estado, migration do enum) + integração Instagram Graph API com **gatilho humano** (a política `block_auto_publish` permanece — o humano dispara, o sistema executa).

### Fora do escopo
- Geração local de imagens (bloqueada por política no MVP).
- Busca semântica pgvector na Knowledge Layer (adiada — busca por `doc_type` atende o volume atual).
- Múltiplas campanhas por run.
- IA nas camadas Operacional/Análise (regra de ouro arquitetural).
- WhatsApp/TikTok como canais de publicação automatizada (Instagram primeiro; demais ficam manuais).

### Entregáveis
1. **Relatório de validação E2E** — 3 runs consecutivos `completed` com conteúdo aprovável; ajustes de prompt documentados.
2. **Ciclo de revisão funcional** — endpoint de re-geração + UI; nova Approval criada a cada ciclo.
3. **Provedor externo operacional** — variáveis de ambiente documentadas, Marketing funcional no Render.
4. **Suíte de testes** — 12 regras do PolicyEngine + fluxos de decisão + pipeline com stub.
5. **Publicação Instagram** — campanha aprovada publicada via API com `published_at` gravado.

### Restrições
- **Orçamento**: custo por token do provedor externo (chave do usuário); app Meta gratuito.
- **Qualidade**: aprovação humana permanece obrigatória em 100% dos caminhos — inegociável.
- **Processo**: uma FASE por vez, com autorização do usuário entre fases (regra do projeto).

---

## 3. Fases de Execução

### FASE 0 — Migração de servidor: Render/Vercel → VPS único (decidida em 2026-07-16)
- **Descrição**: sair do Render (backend+banco) e Vercel (frontend) para um VPS no Brasil (recomendado: Hostinger KVM 4 — 4 vCPU/16GB, DC São Paulo) rodando a stack completa via `docker-compose.prod.yml` com Caddy (HTTPS automático + PWA estático + proxy da API). **Código já preparado** (2026-07-16): fallback do Render removido de `api.ts` (agora caminho relativo `/api/v1` + proxy dev no Vite), `vercel.json` deletado, `deploy/Caddyfile` + `deploy/Dockerfile.web` + `docker-compose.prod.yml` criados e validados, guia completo em `docs/DEPLOY.md`.
- **Pendências do usuário**: comprar domínio (~R$40/ano, Registro.br), contratar o VPS, apontar DNS. A execução do deploy segue o guia e **inclui a rotação dos 3 segredos expostos** (resolve a pendência da consolidação).
- **Efeito no plano**: com Ollama rodando no VPS, produção passa a ter LLM nativo — a FASE D deixa de ser necessária e vira opcional.
- **Verificação**: PWA com HTTPS no domínio; login OK; run de agente completo em produção; dados migrados do Render (pg_dump); backup diário agendado; serviços antigos desligados.

### FASE A — Validação E2E com Ollama real + Seed de Knowledge (gate de qualidade) — ✅ CONCLUÍDA 2026-07-17
- **Descrição**: subir Ollama com llama3.1:8b, cadastrar documentos mínimos de marca (brand_voice, persona, commercial_rules — conteúdo do usuário), executar runs completos via `POST /agents/runs`. Medir: conformidade dos outputs com os schemas Pydantic, falsos positivos das validações de conteúdo (ex.: bloqueio indevido de "R$"), qualidade do PT-BR, latência por agente. Ajustar prompts conforme necessário.
- **Resultado**: 5 runs completos executados (2 falharam por bugs reais, 3 `completed`). Latência 8-10 min/run em CPU. Detalhe completo no relatório de validação (seção 8).
- **Verificação**: ✅ runs consecutivos `completed` com campanha aprovável (copy coerente, políticas aplicadas, sem preço/estoque inventado).

### FASE B — Ciclo de revisão com re-geração por feedback — ✅ CONCLUÍDA 2026-07-17
- **Descrição**: novo fluxo no Supervisor que re-executa Content/Creative (Strategy preservada) injetando o comentário da revisão como instrução adicional; atualiza Post/Brief, cria nova Approval. Endpoint novo + botão na tela ApprovalDetail com estado `revision_requested`.
- **Implementado**: `SupervisorService.execute_revision_workflow`; `POST /agents/approvals/{id}/regenerate` (409 se já houver aprovação pendente); UI no ApprovalDetail.
- **Verificação**: ✅ validado com LLM real — feedback "legenda mais curta, sem exclamações" reduziu a legenda de ~220 para 54 caracteres, 1 frase, zero exclamações. Nova aprovação criada; dupla re-geração bloqueada com 409.

### FASE C — Rede mínima de testes — ✅ CONCLUÍDA 2026-07-17
- **Descrição**: pytest para as 12 regras do PolicyEngine (puro, sem banco), ApprovalService (approve/reject/revision, 409 em re-decisão), Supervisor com modelo LLM stub (pipeline sem Ollama). Protege as regras de segurança ligadas na consolidação e o fluxo novo da FASE B.
- **Resultado**: 56 testes, 100% verde. Cobre PolicyEngine (13 regras, incl. regressão do falso positivo "fotos reais"), resolução tolerante de SKU (4 camadas), ApprovalService (cascatas + 409), workflows do Supervisor com stubs (geração + revisão), PublishingService (E1).
- **Infra**: `backend/tests/conftest.py` (banco `lgd_mantos_test` isolado), `pytest.ini`, `requirements-dev.txt`. Comando: `pytest tests/ -q` (a partir de `backend/`).

### FASE E1 — Fundação da fila de publicação — ✅ CONCLUÍDA 2026-07-17 (adiantada)
- **Descrição**: transições de estado completas (`approved → published | failed`), endpoint de marcação manual, remoção do estado morto `waiting_approval`.
- **Implementado**: `PublishingService.mark_published`/`remove_from_queue`; rotas `POST /publishing/{id}/published` e `DELETE /publishing/{id}`; migration `0003_publishing_status_sem_estado_morto` (aplicada); aba "Fila" no hub Marketing + botão "Enfileirar publicação" no ApprovalDetail.
- **Verificação**: ✅ 8 testes cobrindo o ciclo completo; migration aplicada no banco de dev; build TS verde.

### FASE D — Provedor LLM externo (OPCIONAL após a FASE 0)
- **Descrição**: com o VPS rodando Ollama, produção já tem LLM nativo — esta fase vira contingência: implementar provedor externo em `agents/config.py` (ponto único `get_agent_model()` já preparado) apenas se a qualidade/latência do llama3.1:8b em CPU se mostrar insuficiente na FASE A, ou como upgrade de qualidade futuro.
- **Dependências**: resultado da FASE A; chave de API fornecida pelo usuário.
- **Verificação**: run completo com `AGENT_LLM_PROVIDER` externo.

### FASE E — Publicação real (Instagram)
- **E1 — Fundação da fila**: ✅ CONCLUÍDA (ver acima).
- **E2 — Integração Instagram Graph API**: pré-requisitos externos do usuário (conta Instagram Business vinculada a Página do Facebook, app no Meta for Developers, token de longa duração). Publicação disparada por ação humana explícita ("Publicar agora"/agendar) — `block_auto_publish` segue estrutural: nenhum caminho sem clique humano. **BLOQUEADA até o usuário criar os pré-requisitos Meta.**
- **E3 — Agendamento** (opcional): worker que consome `scheduled_at` de itens já autorizados por humano.
- **Dependências**: FASES A-D (concluídas); pré-requisitos Meta (ação do usuário — app review da Meta pode levar semanas).
- **Verificação**: campanha aprovada publicada no feed real com `published_at` + id do post retornado pela API.

### Caminho crítico
FASE 0 (deploy — ação do usuário) → ~~FASE A~~ → ~~FASE B~~ → ~~FASE C~~ →
~~FASE E1~~ → **FASE E2 (bloqueada — pré-requisitos Meta)**. D permanece opcional.
Restam ativos: FASE 0 (domínio + VPS) e os pré-requisitos Meta da E2 — ambos
são ações externas do usuário, iniciáveis em paralelo desde já.

---

## 4. Recursos Necessários

### Pessoas
- **Usuário (Lucas)**: conteúdo de marca da FASE A (tom de voz, persona, regras comerciais); chave de API na FASE D; conta Business + app Meta na FASE E; aprovações entre fases.
- **Claude Code**: implementação, verificação com evidência real, migrations.

### Orçamento
| Categoria | Item | Custo estimado | Status |
|---|---|---|---|
| Serviços | API LLM externa (produção) | por token, uso baixo | Pendente decisão de provedor |
| Serviços | Meta for Developers | gratuito | Pendente criação |
| Infra | VPS Brasil 16GB (ex.: Hostinger KVM 4, DC São Paulo) | ~R$60-120/mês | Pendente contratação |
| Infra | Domínio (.com.br no Registro.br) | ~R$40/ano | Pendente compra |

### Ferramentas & Sistemas
- Ollama + llama3.1:8b local (FASE A); Docker Postgres 16 porta 55432; Alembic (migration enum na E1); pytest (FASE C); Instagram Graph API (E2).

### Conhecimento
- Regras de content publishing da Instagram Graph API (limites de rate, formatos) — pesquisar na E2.

---

## 5. Cronograma & Marcos

**Início**: 2026-07-17 · **Duração estimada**: 4-6 semanas (E2 depende de prazo externo da Meta)

| Marco | Alvo | Critério |
|---|---|---|
| M1 — Pipeline validado | Semana 1 | 3 runs aprováveis consecutivos com Ollama |
| M2 — Ciclo de revisão fechado | Semana 2 | Revisão → re-geração → nova aprovação |
| M3 — Testes verdes | Semana 2-3 | 12 regras + fluxos cobertos |
| M0 — Sistema no VPS | Semana 1 | HTTPS + dados migrados + run em produção |
| M4 — (opcional) LLM externo | se necessário | Run completo com provedor externo |
| M5 — Primeira publicação real | Semana 4-6 | Post no Instagram com published_at |

```
Sem 1 : [████████░░░░] FASE A (validação + knowledge)  ← usuário inicia app Meta em paralelo
Sem 2 : [████████░░░░] FASE B (revisão)
Sem 2-3: [░░░░████████] FASE C (testes)
Sem 3 : [████████░░░░] FASE D (provedor externo)
Sem 4-6: [████████████] FASE E (fila + Instagram)
```

---

## 6. Riscos & Contingências

### R1 — llama3.1:8b falha em produzir JSON válido ou copy de qualidade
**Categoria**: Técnico · **Prob.**: Alta · **Impacto**: Alto
**Mitigação**: FASE A é gate dedicado a isso; ajuste de prompts; retry no schema.
**Contingência**: trocar `OLLAMA_MODEL` por modelo maior, ou antecipar FASE D e usar provedor externo também localmente.
**Sinal precoce**: runs `failed` com erro de parsing na FASE A.

### R2 — Falsos positivos das políticas de conteúdo bloqueiam runs legítimos
**Categoria**: Técnico · **Prob.**: Média · **Impacto**: Médio
**Mitigação**: FASE A mede exatamente isso; refinar regex/regras do PolicyEngine (com testes da FASE C garantindo que os bloqueios reais continuam).
**Contingência**: whitelist de padrões verificados contra dados do catálogo.

### R3 — App review da Meta atrasa ou nega permissão de publicação
**Categoria**: Externo · **Prob.**: Alta (prazo) · **Impacto**: Alto para E2
**Mitigação**: iniciar processo Meta na semana 1; E1 entrega fechamento manual como fallback permanente — o ciclo fecha mesmo sem a API.
**Contingência**: operar com marcação manual até a aprovação sair.

### R4 — Custo/dependência do provedor externo
**Categoria**: Recurso · **Prob.**: Baixa · **Impacto**: Baixo (volume pequeno)
**Mitigação**: provedor é opcional por env; Ollama continua padrão local.

### R5 — Mudanças nas fases B/E quebram pipeline sem rede de regressão
**Categoria**: Técnico · **Prob.**: Média · **Impacto**: Médio
**Mitigação**: FASE C posicionada antes das mudanças mais invasivas (D/E); verificação manual com evidência real em toda fase (regra do projeto).

---

## 7. Métricas de Sucesso

### Primárias
- **Taxa de sucesso de runs** (`/agents/ops/metrics`): ≥ 80% `completed` · medição contínua · baseline atual: sem dados (pipeline nunca rodou).
- **Ciclo completo fechado**: ≥ 1 campanha percorrendo geração → aprovação → publicação Instagram com `published_at` · verificação na FASE E.
- **Cobertura de regras**: 12/12 regras do PolicyEngine com teste automatizado.

### Secundárias
- Tempo objetivo → aprovação pendente < 10 min (latência do pipeline local).
- Revisões consumidas: 100% dos `revision_requested` com caminho de re-geração disponível.
- Marketing operante em produção no VPS (0 runs falhando por ausência de LLM).

### Critérios de conclusão
- [ ] 5 entregáveis aceitos pelo usuário
- [ ] Métricas primárias atingidas
- [ ] Nenhum ciclo aberto (geração, revisão, publicação)
- [ ] Documentos de marca ativos na Knowledge Layer

---

## Notas & Considerações
- Regras de ouro arquiteturais permanecem invioláveis: IA só na Agentic Layer; aprovação sempre humana; PolicyEngine determinístico; Operacional/Análise sem imports de LLM.
- Pendência herdada da consolidação de 2026-07-16 (fora deste plano, mas urgente): **rotacionar os 3 segredos expostos no histórico do git** (`APP_SECRET`, `APP_PASSWORD`, senha do Postgres no Render). A FASE 0 (deploy no VPS) é o momento natural de fazer isso — ver `docs/DEPLOY.md`.
- Cada FASE segue a regra do projeto: executar, parar, pedir autorização para a próxima.
- **Arquitetural (anotado em 2026-07-17, não é bug a corrigir agora)**: `execute_workflow`/`execute_revision_workflow` rodam via `BackgroundTasks` no processo do próprio servidor. Se o processo cair no meio de um run, o `AgentRun` fica travado em `running` para sempre — não há retomada. Em produção (VPS com Docker sempre ativo) o risco é baixo, mas se o volume de runs crescer vale migrar para uma fila real (ex.: worker separado) que sobrevive a restart.

---

## 8. Relatório de Validação — FASES A, B, C, E1 (2026-07-17)

### Ambiente de validação
Local: Docker (Postgres 16 + Ollama/llama3.1:8b) + backend em `venv` Python 3.11,
depois migrado para o container Docker do backend reconstruído. Seed: 3 produtos
(1 deliberadamente sem estoque), 2 vendas, 3 documentos de knowledge (brand_voice,
persona, commercial_rules — rascunhos meus, **pendente revisão do usuário**).

### Bugs reais encontrados e corrigidos (pipeline nunca havia rodado E2E antes)
1. **`.env` nunca preenchido de verdade** — `DATABASE_URL` tinha o placeholder literal `SENHA_AQUI` e `APP_SECRET` o texto `gere-um-segredo-aleatorio-longo`. Provável causa raiz original do container do backend nunca ter subido. Corrigido com valores de dev reais.
2. `backend/requirements.txt` sem `alembic` — causava crash loop do container (`ModuleNotFoundError` no `init_db.py`).
3. `backend/requirements.txt` sem `python-jose[cryptography]` — quebrava o import do módulo de auth.
4. `AgentContextService` chamava `ProductAnalysisService.purchase_suggestions`, método que **nunca existiu** no histórico do git — derrubava runs em 0,1s e também a rota `GET /analytics/agent-context`.
5. **Alucinação de SKU pelo StrategyAgent** (`BR02-MANTO` em vez de `MANTO-BR02`) — corrigido com lista fechada de SKUs no prompt + resolução tolerante em 4 camadas (exato → case-insensitive → tokens normalizados → nome do produto), coberta por 10 testes.
6. **`StringDataRightTruncationError`** — o LLM devolveu uma descrição de 159 chars no campo `format` (`VARCHAR(100)`), derrubando o `INSERT`. Corrigido com sanitização (`_fit`) + instrução de prompt restringindo o campo a um rótulo curto.
7. **Falso positivo do PolicyEngine**: a regra de preço bloqueava qualquer menção à palavra "reais", inclusive "fotos reais do produto" (expressão usada nos próprios prompts). Corrigido para exigir número antes de "reais".
8. **CreativeAgent devolvia rótulos em vez de conteúdo** (ex.: `image_prompt = "Prompt de Imagem para Geração"`). Corrigido com instrução explícita e exemplo errado/certo no prompt — confirmado nos runs seguintes (prompts de imagem completos, roteiros de reels com timestamps).

### Runs executados
| # | Objetivo | Resultado | Observação |
|---|---|---|---|
| 1 | destaque | failed (0,1s) | bug #4 |
| 2 | destaque | failed (13min) | bug #5 (SKU alucinado) |
| 3 | destaque | **completed** (8,1min) | 1º E2E da história do projeto |
| gate 1/3 | destaque | **completed** (10,1min) | copy limpo, sem typos |
| gate 2/3 | carrossel | **completed** (9,1min) | CreativeBrief com conteúdo real |
| gate 3/3 | reels/estoque parado | failed (5,8min) | bug #6 (format truncado) |
| revalidação | reels/estoque parado | **completed** (9,5min) | bug #6 confirmado corrigido |
| revisão E2E | re-geração pós-feedback | **completed** (9,5min) | ver FASE B acima |

Latência típica: 8-10 min por run completo (4 agentes, CPU). Nenhum truncamento de
contexto no Ollama (prompts de 1,2-1,5k tokens, limite 4096).

### Qualidade de conteúdo observada
Pontos fortes: copy comercialmente coerente, políticas de preço/estoque nunca
violadas nos runs bem-sucedidos, direção criativa completa e utilizável (slides
de carrossel, roteiro de reels com timing, prompt de imagem descritivo).
Limitação conhecida do modelo 8B local: 1-2 typos ocasionais em português
("REIVIVIR", "COLECAIONADOR") e um deslize factual observado (referência a
"anos 90" num contexto de 2002/1999) — não classificados como bloqueadores,
mas o motivo pelo qual a FASE D (LLM externo) continua disponível como opção
caso a qualidade incomode na revisão humana.

### Estado final do ambiente
Container Docker do backend reconstruído e estável (primeira vez que sobe sem
crash loop). Suíte de testes: 56/56 verde. Build do frontend: verde.
