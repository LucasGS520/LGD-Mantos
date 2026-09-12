# Blueprint LGD Mantos — de três módulos para Operação + Inteligência

**Data:** 2026-09-10
**Status:** Aprovado. Próximo passo é o plano de implementação da Fase 1.
**Escopo deste documento:** arquitetura-alvo completa e ordem de fases. Cada fase
posterior à Fase 1 recebe sua própria spec antes de virar plano.

---

## 1. Problema

O sistema hoje se organiza em três módulos de produto — Operacional (`op`),
Analytics (`an`) e Marketing (`mk`) — mais uma aba de cadastros e configurações
(`mais`). Essa divisão está codificada diretamente na navegação
(`frontend_pwa/src/nav.tsx`).

O núcleo Operacional está saudável: catálogo com variantes, estoque com
movimentações, vendas com custo resolvido no servidor e trava de concorrência,
entrada de mercadoria consolidada em `MerchandiseEntry`, controle financeiro com
DRE e cadastros auxiliares. Nada disso é o problema.

O problema está na fronteira entre Analytics, Marketing e IA. Existe hoje um
domínio de marketing completo — campanhas, posts, briefings criativos,
aprovações, fila de publicação, camada de conhecimento de marca e um pipeline de
quatro agentes de IA (Data, Strategy, Content, Creative) com policy engine. São
2.612 linhas de backend e cerca de 1.200 linhas de telas. É, na prática, um
segundo produto dentro do produto.

Para uma loja como a LGD Mantos, esse não é o melhor uso do sistema central. A
pergunta que o sistema deve responder não é "como produzir conteúdo para o
Instagram", e sim "como ajudar o dono a tomar melhores decisões sobre estoque,
vendas, compras e dinheiro".

Há um segundo problema, independente do primeiro: mesmo a parte analítica que
funciona está fragmentada em onze telas isoladas (Dashboard, Top Products, By
Size, By Channel, Suggestions, DRE, Categorias, Alertas, Marketing Intelligence,
Compras, detalhe de categoria). O usuário sente uma coleção de relatórios, não um
sistema que mostra o que importa.

## 2. Decisões

Estas decisões foram tomadas em conjunto com o responsável pelo produto e
governam todo o blueprint.

1. **O domínio de Marketing é removido por completo e de imediato** — código,
   rotas, telas e tabelas. O histórico fica no Git.
2. **A navegação passa a ter três abas:** Operação, Inteligência e Mais. A aba
   `mk` desaparece; a aba `an` é renomeada para `intel`.
3. **A camada de inteligência se organiza em torno de um Motor de Sinais
   determinístico**, não de relatórios isolados.
4. **Toda a IA local é removida** — Ollama, os pacotes `agno`, `ollama` e
   `openai`, os containers de LLM nos dois arquivos de compose e as variáveis de
   ambiente correspondentes.
5. **Um Agente Analista conversacional existirá na última fase, sobre a API do
   Groq**, consumindo apenas sinais já calculados de forma determinística.
6. **A implementação começa pela remoção e pela nova navegação**, sem introduzir
   nenhuma métrica nova antes de a base estar limpa.

## 3. Arquitetura-alvo

### 3.1 Dois pilares

```
Operacional            → registra o que aconteceu
   ↓
Analytics              → calcula números
   ↓
Motor de Sinais        → transforma números em diagnóstico e recomendação
   ↓
Telas / Saúde da Loja  → apresenta decisões, não relatórios
```

A relação com a IA é invertida em relação ao desenho atual. Hoje a análise
alimenta agentes de marketing. No alvo, a análise alimenta a decisão do operador,
e a IA — quando entrar — apenas narra o que a camada determinística já concluiu.

### 3.2 Navegação

`TabId` passa a ser `'op' | 'intel' | 'mais'`.

O diretório `frontend_pwa/src/screens/an/` é renomeado para `screens/intel/`. O
rename é mecânico e acontece na mesma passada em que as telas são reescritas, de
modo que o custo marginal é próximo de zero.

**Aba `op`** — inalterada. Onze telas: lista e detalhe de produto, formulário de
produto, venda, histórico e detalhe de venda, entrada de mercadoria, lista e
detalhe de entrada, despesas, movimentações de estoque.

**Aba `intel`** — oito telas, contra onze hoje:

| Tela nova | Absorve hoje |
| --- | --- |
| `intel-overview` (raiz da aba) | Dashboard + topo de Alertas |
| `intel-health` | Nova. Sucede o `AgentContextService` invertido + qualidade de dados |
| `intel-products` | TopProducts + BySize + Categorias + classificações do MarketingIntel |
| `intel-category-detail` | CategoryDetail |
| `intel-stock` | ComprasReposicao + Suggestions + "repor primeiro" e "parado" do MarketingIntel |
| `intel-finance` | DRE |
| `intel-channels` | ByChannel |
| `intel-signal-detail` | Nova, Fase 4. A tela do "Por quê?" |

Top Products e By Size deixam de ser telas próprias e viram seções filtráveis
dentro de `intel-products`. Essa é a consolidação que resolve a sensação de
coleção de relatórios.

**Aba `mais`** — inalterada. Dez telas: menu, fornecedores e formulário,
categorias e formulário, canais de venda e formulário, configurações, status do
sistema e sobre.

O enum `ScreenId` cai de 38 para 29 entradas (login, mais onze de `op`, oito de
`intel` e dez de `mais`).

### 3.3 Backend: o módulo `intelligence`

Camada nova, com dependência estritamente unidirecional: `intelligence` importa
`analytics`; `analytics` nunca importa `intelligence`. Analytics continua sendo
exclusivamente a camada de números.

```
backend/app/modules/intelligence/
├── __init__.py
├── signals/
│   ├── __init__.py
│   ├── types.py          # Signal, Severidade, Area, DrillItem, SignalContext
│   ├── registry.py       # catálogo de regras registradas
│   └── rules/
│       ├── __init__.py
│       ├── finance_rules.py
│       ├── stock_rules.py
│       ├── product_rules.py
│       └── channel_rules.py
├── services/
│   ├── signal_engine.py  # monta o contexto uma vez, roda as regras
│   ├── health_service.py # agrega sinais por área e produz o semáforo
│   └── explain_service.py # decomposição determinística do "Por quê?" (Fase 4)
├── schemas/
└── routes/
```

### 3.4 O Sinal

O Sinal é a unidade central da camada de inteligência. É um objeto estruturado,
sempre determinístico, que carrega o número, a comparação, o diagnóstico e a
recomendação juntos.

```python
class Signal(BaseModel):
    codigo: str                 # identificador estável, ex.: "margem_em_queda"
    area: Area                  # financeiro | estoque | produtos | canais | cadastro
    severidade: Severidade      # bom | atencao | critico
    titulo: str
    metrica: str
    valor_atual: float
    valor_anterior: float | None
    variacao_pct: float | None
    diagnostico: str            # texto gerado por template, sem LLM
    recomendacao: str | None
    evidencia: list[dict]       # itens concretos: SKUs, categorias, canais
    drill: list[DrillItem]      # decomposição do "Por quê?" (preenchida na Fase 4)
```

Uma **regra** é uma função pura com a assinatura
`(ctx: SignalContext) -> Signal | None`, registrada no `registry`. O
`SignalContext` é montado **uma única vez por requisição** e reúne tudo que as
regras podem precisar: dashboard do período atual, dashboard do período anterior,
análise de produtos, situação de estoque, desempenho de canais e qualidade de
dados. Isso evita que cada regra dispare suas próprias consultas.

O fato de a regra ser função pura sobre um contexto é deliberado: torna cada uma
testável isoladamente, sem banco, o que faz do Motor de Sinais o melhor alvo de
TDD do projeto.

### 3.5 Endpoints

| Método e rota | Responsabilidade | Fase |
| --- | --- | --- |
| `GET /api/v1/intelligence/overview` | KPIs do período + sinais mais severos, em uma chamada | 3 |
| `GET /api/v1/intelligence/signals?area=&severidade=` | Catálogo de sinais filtrável | 3 |
| `GET /api/v1/intelligence/health` | Semáforo por área para a Saúde da Loja | 3 |
| `GET /api/v1/intelligence/signals/{codigo}/explain` | Decomposição do "Por quê?" | 4 |

### 3.6 Comparação de períodos

Requisito transversal: todo indicador relevante deve mostrar variação contra o
período anterior. Sem isso, os campos `valor_anterior` e `variacao_pct` do Sinal
ficam vazios — por isso a comparação é implementada **antes** do Motor de Sinais.

Implementação:

- `backend/app/modules/analytics/utils.py` ganha
  `resolve_comparison_period(period) -> (atual, anterior)`, irmã da já existente
  `resolve_period`.
- Um value object `Comparado[T]` com os campos `atual`, `anterior` e
  `variacao_pct`.
- Os services de dashboard, finanças, produtos e canais ganham um parâmetro
  opcional `compare: bool`.

## 4. O que é removido

### 4.1 Domínio de Marketing — backend

Apaga-se o diretório `backend/app/modules/agents/` por inteiro (2.612 linhas):
os quatro agentes, `supervisor/service.py` (580 linhas), `policy_engine.py` (165),
`marketing_ops/models.py` (187), `approval/`, `publishing/`, `knowledge/`, `ops/`,
`routes.py` e `config.py`.

Diferente do que se cogitou no desenho inicial, **`config.py` não é preservado**.
Ele é um wrapper de Ollama, e a decisão de remover a IA local o torna inútil. O
arquivo `app/core/llm.py` não chega a existir.

Também saem do módulo Analytics:

- `routes/agent_context.py`, `schemas/agent_context.py` e
  `services/agent_context_service.py` (44 linhas). A lógica de agregação renasce
  na Fase 3 como `intelligence/services/health_service.py`. Reconstruir é mais
  barato do que manter acoplado.

O arquivo `routes/marketing_intelligence.py` não é apagado, e sim renomeado para
`routes/product_classification.py` — ver seção 5.1. O que desaparece é o
vocabulário de marketing, não o endpoint.

Em `backend/main.py`, saem o import e o `include_router(agents_router)`.

### 4.2 Domínio de Marketing — banco

Migration `0005_remove_marketing.py`:

- `DROP TABLE` em `agent_runs`, `campaigns`, `posts`, `creative_briefs`,
  `approvals`, `publishing_queue` e `knowledge_documents`.
- `DROP TYPE` nos enums `agent_run_status`, `content_status`, `approval_status`,
  `publishing_status` e `knowledge_doc_type`.

O `downgrade()` recria a estrutura vazia. Não recupera conteúdo.

### 4.3 Domínio de Marketing — frontend

- `src/screens/Marketing.tsx` (445 linhas) e todo o diretório `src/screens/mk/`
  (756 linhas: ApprovalDetail, KnowledgeDocForm, NewRun, RunDetail).
- Em `src/nav.tsx`: a aba `mk`, a entrada `marketing` e os quatro `ScreenId`
  `mk-*`.
- Em `src/components/Chrome.tsx`: a entrada de `TABS` correspondente e o ícone
  `megaphone`.
- Em `src/services/api.ts`: as dezesseis funções de agents (runs, approvals,
  publishing, ops metrics, knowledge), aproximadamente entre as linhas 179 e 257.
- Em `src/services/types.ts`: `AgentRun`, `AgentApprovalItem`,
  `AgentApprovalDetail`, `OpsMetrics`, `KnowledgeDoc`, `PublishingQueueItem` e
  `MarketingIntelligence`.
- Em `src/App.tsx`: as rotas das telas removidas.

### 4.4 IA local

Remoção independente da remoção do Marketing, com footprint próprio:

**Infraestrutura**

- `docker-compose.yml`: serviço `ollama`, serviço de pull do modelo
  `llama3.1:8b`, volume `ollama_data` e o `depends_on: ollama` do backend.
- `docker-compose.prod.yml`: o mesmo conjunto.
- `.env.example`: `OLLAMA_URL` e `OLLAMA_MODEL`.
- `backend/app/core/config.py`, linhas 17-18: as duas settings correspondentes.
- `docs/DEPLOY.md`: a seção que descreve o Ollama.

**Dependências** — saem dos dois arquivos de requirements:

| Pacote | `requirements.txt` | `backend/requirements.txt` |
| --- | --- | --- |
| `agno` | 2.6.19 | 2.6.19 |
| `ollama` | 0.6.2 | 0.6.2 |
| `openai` | 2.45.0 | 2.44.0 |

A divergência de versão do `openai` entre os dois arquivos é um drift existente
que desaparece com a remoção.

Os documentos históricos `FABLE_CONSOLIDACAO_2026-07-16.md` e
`docs/plans/PLAN-20260716-1846-consolidacao-agentes-marketing.md` permanecem como
registro do que foi construído. Não são reescritos.

### 4.5 Testes

Os cinco arquivos de teste do projeto são de agents, incluindo
`test_sku_resolution.py`, que importa `supervisor.service`. A remoção zera a
suíte.

`backend/tests/conftest.py` **é reescrito**, não preservado: as linhas 22-23
definem variáveis de ambiente do Ollama, e há fixtures que criam
`AgentRun`/`Campaign`/`Post`/`CreativeBrief`/`Approval` e um `TRUNCATE` que
alcança as sete tabelas de marketing além de `products` e `product_variants`.
Sobrevive apenas o helper `create_product`, e o `TRUNCATE` precisa ser reduzido às
tabelas que continuam existindo.

A reposição de cobertura é parte obrigatória da Fase 1 (seção 7).

## 5. O que é reaproveitado

### 5.1 Classificação de produtos

`MarketingIntelligenceService` (76 linhas) classifica variantes cruzando
velocidade de venda em 30 dias, estoque e margem. A lógica é boa; apenas o
vocabulário é de marketing.

Ele é renomeado **na Fase 1**, e não na Fase 3 — se esperasse, ficaria órfão por
duas fases, que é exatamente o tipo de código morto que este trabalho existe para
eliminar. Passa a ser
`analytics/services/product_classification_service.py`, e o endpoint
`/analytics/marketing-intelligence` passa a `/analytics/product-classification`.

As listas trocam de vocabulário:

| Chave atual | Chave na Fase 1 |
| --- | --- |
| `post_candidates` | `alta_saida_estoque_saudavel` |
| `highlight_candidates` | `margem_alta` |
| `promotion_candidates` | `baixa_saida_estoque_alto` |
| `restock_first` | `estoque_critico` |
| `avoid_post` | `sem_estoque` |
| (já existe em `product_analysis.stopped`) | `produto_parado` |

São as seis situações de "oportunidades de estoque" que o produto precisa
expor. Na Fase 3 o service se dissolve nas regras de `product_rules.py` e
`stock_rules.py` e é removido.

### 5.2 Agregação de saúde da loja

`AgentContextService` já empacota saúde financeira, pontos de atenção,
oportunidades e qualidade de dados. Essa estrutura é o embrião da tela Saúde da
Loja. O arquivo não sobrevive — é removido na Fase 1 e sua lógica é reescrita na
Fase 3 como `health_service.py`, agora agregando sinais em vez de listas soltas.

### 5.3 Todo o restante de Analytics

Dashboard, finanças/DRE, análise de produtos, categorias, canais e qualidade de
dados continuam como estão. São a camada de números sobre a qual o Motor de
Sinais é construído.

## 6. Fases de implementação

Regra que governa a ordem: **nenhuma fase termina deixando código morto**. Cada
fase entrega a base consistente para a seguinte.

### Fase 1 — Fundação limpa

Nenhuma métrica nova. O objetivo é uma base honesta.

1. Remoção do domínio de Marketing: backend, banco e frontend (seções 4.1 a 4.3).
2. Salvamento da classificação de produtos: rename para
   `ProductClassificationService` e novo vocabulário de chaves (seção 5.1).
3. Remoção da IA local: infraestrutura, dependências e settings (seção 4.4).
4. Rename de `an` para `intel` e barra de abas com três alvos.
5. Consolidação das onze telas analíticas nas cinco áreas, consumindo
   exclusivamente endpoints que já existem — incluindo o
   `/analytics/product-classification` renomeado no passo 2. Nenhum endpoint
   novo é criado nesta fase.
6. Reposição de cobertura de testes e reescrita do `conftest.py`.

**Critérios de verificação.** Cada um exige evidência real — comando executado e
saída, não raciocínio:

- `alembic upgrade head` aplica a `0005` sem erro.
- Qualquer rota sob `/api/v1/agents/` responde 404.
- A API sobe sem erro de import.
- As cinco áreas navegam e exibem dado real.
- `docker compose up` sobe sem nenhum container de LLM.
- A suíte de testes está verde e não está vazia.

### Fase 2 — Comparação de períodos

`resolve_comparison_period`, o value object `Comparado[T]` e o parâmetro
`compare` nos services de dashboard, finanças, produtos e canais. As cinco áreas
passam a exibir variação contra o período anterior.

Precede a Fase 3 porque os campos comparativos do Sinal dependem dela.

### Fase 3 — Motor de Sinais

Implementação completa de `modules/intelligence/`: tipos, registry, engine e as
regras de finanças, estoque, produtos e canais. O
`ProductClassificationService` se dissolve nas regras e é removido ao fim da
fase. Nasce a tela `intel-health` (Saúde da Loja), e `intel-overview` passa a
exibir os sinais mais severos.

### Fase 4 — "Por quê?"

`explain_service` e preenchimento do campo `drill[]` nas regras que admitem
decomposição: variação de lucro, de receita, de margem, mix de canal e mix de
categoria. Nasce a tela `intel-signal-detail`. Continua inteiramente
determinístico, sem LLM.

### Fase 5 — Agente Analista

Agente conversacional sobre a API do Groq, consumindo apenas o que as fases 3 e 4
já calcularam.

**Decisão de arquitetura: sem framework de agentes.** O `agno` existia para
orquestrar quatro agentes encadeados com policy engine. A Fase 5 é um agente
único, com quatro ferramentas somente-leitura, sobre um catálogo de sinais já
determinístico. O SDK do Groq, com tool calling nativo, cobre o caso com menos
superfície. Se durante a spec da Fase 5 o loop de ferramentas se mostrar complexo
demais, a decisão se reabre — mas o padrão é o SDK puro.

- Dependência nova: `groq`.
- Settings novas: `GROQ_API_KEY` e `GROQ_MODEL`, ambas vindas do ambiente. A
  chave nunca entra no repositório.
- Ferramentas, todas somente-leitura: `listar_sinais()`,
  `explicar_sinal(codigo)`, `kpis_periodo()` e
  `produtos_por_classificacao()`.
- O agente não escreve no banco e não executa SQL cru.
- O modelo específico é escolhido na spec da Fase 5. O catálogo do Groq muda com
  frequência demais para ser fixado agora.
- A superfície de interface do agente também é definida na spec da fase.

## 7. Estratégia de testes

A remoção zera a suíte. A reposição é distribuída por fase, cada uma testando o
que ela própria introduz.

**Fase 1.** Testes de contrato dos endpoints de Analytics que sobrevivem —
dashboard, finanças/DRE, produtos, categorias, canais, qualidade de dados e
classificação de produtos — mais a asserção de que rotas sob `/api/v1/agents/`
respondem 404. Esses testes são a rede de segurança das Fases 2 a 4, que vão
alterar exatamente esses services.

**Fase 2.** `resolve_comparison_period` é função pura: TDD direto nas bordas —
virada de mês, virada de ano, período customizado e período sem dado anterior.

**Fase 3.** O coração da cobertura. Cada regra é uma função pura
`(ctx) -> Signal | None`; o teste monta um `SignalContext` sintético e afirma o
sinal resultante, sem banco. Uma regra, um teste, escrito antes da regra.

**Fase 4.** Invariante numérica: a soma das parcelas de `drill[]` reconcilia com
o delta total declarado pelo sinal.

**Fase 5.** Não se testa saída de LLM. Testa-se que cada ferramenta devolve o
que promete e que o agente não expõe nenhuma ferramenta de escrita.

## 8. Riscos

1. **A migration `0005` é irreversível quanto a dados.** O `downgrade()` recria a
   estrutura, nunca o conteúdo. Se houver campanha, post ou documento de
   conhecimento que valha preservar, exportar antes de aplicar.
2. **A partir da Fase 5, dado de negócio sai da VPS.** KPIs, sinais, nomes de
   produto e margens trafegam para a API do Groq, fora do Brasil. A chave de API
   passa a ser um segredo de produção a gerenciar. É o custo consciente da
   escolha por provedor em nuvem.
3. **A Fase 1 é grande** — seis blocos, backend e frontend simultâneos. O plano de
   implementação precisa fatiá-la. As Fases 2 a 5 recebem spec própria antes do
   plano.
4. **Efeito positivo do lado da infraestrutura:** o compose de produção perde um
   container de LLM e um volume de aproximadamente 5 GB. Como a VPS ainda não foi
   contratada, o requisito de memória da máquina cai de forma relevante —
   `llama3.1:8b` era o item mais pesado do ambiente.

## 9. Fora de escopo

- Qualquer alteração no núcleo Operacional. Catálogo, estoque, vendas, entrada de
  mercadoria e financeiro permanecem como estão.
- Qualquer alteração na aba `mais`.
- Refatoração não relacionada a esta reformulação.
- A escolha do modelo específico do Groq e a superfície de interface do Agente
  Analista, ambas definidas na spec da Fase 5.
