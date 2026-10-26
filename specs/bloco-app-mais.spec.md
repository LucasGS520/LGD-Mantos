# Spec — Bloco "App" da seção Mais

**Status:** aprovada para implementação
**Data:** 2026-09-03
**Escopo:** `frontend_pwa/src/screens/mais/`, `backend/app/modules/`, migration Alembic

---

## 1. Visão geral e valor

O bloco "App" da seção Mais tem hoje três itens, e os três são fachada:

| Item | Estado real hoje | Problema |
|---|---|---|
| Configurações | Tela placeholder "disponíveis em breve" | Hint promete "Senha, backup, notificações" — nada existe |
| Sincronização | `navigate('settings')` — vai para a mesma tela | Item duplicado; card "Conectado ao servidor" é estático, não checa nada |
| Sobre o app | Estático, `v1.0.0` hardcoded | Diverge da API (`version: "2.0"`); string repetida em 3 arquivos |

O valor do bloco é ser **o painel de controle do próprio sistema** para um operador único
que roda a loja sozinho: ajustar como o sistema o alerta, tirar seus dados de dentro do
servidor sem depender de acesso ao Postgres da VPS, e confirmar que o app está falando com
o servidor certo, na versão certa.

### Decisões de produto tomadas

1. **Senha permanece no `.env`** (`APP_PASSWORD`). Não haverá troca de senha pelo app —
   sem tabela de usuário, sem hash, sem migration de auth. A UI para de prometer isso e
   passa a explicar onde a senha vive e como trocá-la.
2. **"Sincronização" vira "Status do sistema"** — o app não tem offline real (não há
   IndexedDB nem fila de escrita), então o item passa a mostrar o que de fato existe:
   conexão, versão, atualização do PWA.
3. **Exportação para consulta** (CSV por conjunto + ZIP com os seis relatórios).
   Os arquivos não têm dados suficientes para restauração e não são backup do banco.
4. **Notificações push saem de escopo**; entram **preferências de alertas** — os limiares
   que hoje estão cravados no código passam a ser configuráveis.
5. **Versão passa a ter fonte única** — `package.json` + hash do commit, injetados em build time.

### Fora de escopo

- Troca de senha pelo app, multiusuário, papéis/permissões.
- Modo offline com fila de escrita (IndexedDB), resolução de conflitos.
- Notificações push (VAPID, subscriptions, agendador).
- Importação de dados (só exportação).

---

## 2. Desenho final do bloco

```
APP
├── Configurações          Alertas, exportação e segurança
├── Status do sistema      Conexão, versão e atualizações
└── Sobre o app            v1.2.0 · a3f91c2
```

### 2.1 Configurações (`settings`)

Três seções:

**Alertas** — três limiares hoje cravados no código, expostos como campos numéricos:

| Preferência | Valor atual (hardcoded) | Origem | Efeito |
|---|---|---|---|
| `rupture_days` | 15 | [product_analysis_service.py:78](backend/app/modules/analytics/services/product_analysis_service.py#L78) | Dias de cobertura abaixo dos quais a variante entra em "Risco de ruptura" |
| `stopped_days` | 60 | [product_analysis_service.py:33](backend/app/modules/analytics/services/product_analysis_service.py#L33) | Dias sem venda para o produto ser considerado "parado" |
| `critical_stock` | 3 | [marketing_intelligence_service.py:11](backend/app/modules/analytics/services/marketing_intelligence_service.py#L11) | Estoque que dispara alerta de reposição antes de postar |

**Dados** — exportação:
- Botão por conjunto: Produtos, Vendas, Compras, Despesas, Movimentações de estoque, Cadastros.
- Botão "Exportar relatórios (.zip)" — todos os CSVs num único arquivo.

**Segurança** — bloco informativo (sem campos):
- Explica que a senha de acesso é definida no servidor (`APP_PASSWORD`) e que a troca é
  feita no `.env` da VPS seguida de reinício do container.
- Mostra a validade da sessão atual (data de expiração lida do JWT).
- Botão "Sair de todos os dispositivos" **não existe** — não há como invalidar tokens sem
  tabela de sessão; não prometer.

### 2.2 Status do sistema (`system-status`)

Nova tela, novo `ScreenId`, substitui o destino do item "Sincronização".

- **Conexão**: ping em `GET /api/v1/health`, com latência em ms e semáforo
  (verde online, vermelho offline). Reflete também `navigator.onLine`.
- **Banco de dados**: status vindo do health (`ok` / `error`).
- **Versões**: versão do app (build), hash do commit, versão da API.
- **Atualização do app**: estado do service worker. Quando há nova versão em espera,
  mostra botão "Atualizar agora" que ativa o novo SW e recarrega.
- **Última verificação**: horário do último ping bem-sucedido.

### 2.3 Sobre o app (`about`)

- Versão e build vindos de constantes injetadas em build time (fonte única).
- Versão da API vinda do health.
- Linhas informativas: plataforma, stack.

---

## 3. Requisitos funcionais (EARS)

### Preferências de alertas

- **RF-01** — When o usuário abre Configurações, the sistema shall carregar as preferências
  de alerta persistidas via `GET /api/v1/settings/preferences`.
- **RF-02** — Where nenhuma preferência foi salva ainda, the sistema shall retornar os
  valores padrão (`rupture_days=15`, `stopped_days=60`, `critical_stock=3`) sem exigir
  inserção prévia de linha no banco.
- **RF-03** — When o usuário salva as preferências, the sistema shall validar que cada valor
  é inteiro dentro do intervalo permitido (`rupture_days` 1–90, `stopped_days` 7–365,
  `critical_stock` 0–100) e rejeitar com HTTP 422 fora desses limites.
- **RF-04** — When as preferências são alteradas, the sistema shall aplicá-las nas análises
  subsequentes de risco de ruptura, produtos parados e estoque crítico, sem reinício da API.
- **RF-05** — The sistema shall manter no máximo uma linha de preferências (registro único),
  criando-a na primeira gravação.

### Exportação de dados

- **RF-06** — When o usuário solicita a exportação de um conjunto, the sistema shall responder
  com `text/csv` codificado em UTF-8 com BOM e cabeçalho `Content-Disposition: attachment`
  com nome no formato `lgd-{conjunto}-{AAAA-MM-DD}.csv`.
- **RF-07** — The sistema shall oferecer os conjuntos: `produtos`, `vendas`, `compras`,
  `despesas`, `movimentacoes`, `cadastros`.
- **RF-08** — When o usuário solicita os relatórios em ZIP, the sistema shall responder com um
  `application/zip` contendo um CSV por conjunto, nomeado `lgd-relatorios-{AAAA-MM-DD}.zip`.
- **RF-09** — The sistema shall exigir token válido em todos os endpoints de exportação.
- **RF-10** — Where um conjunto não possui registros, the sistema shall retornar um CSV
  contendo apenas a linha de cabeçalho, nunca HTTP 404.
- **RF-11** — When o download termina no cliente, the sistema shall liberar a object URL criada,
  evitando retenção de memória no PWA.

### Status do sistema

- **RF-12** — The sistema shall expor `GET /api/v1/health` retornando `status`, `version`,
  `database` e `server_time`.
- **RF-13** — The endpoint de health shall verificar a conectividade real com o banco
  (`SELECT 1`) e reportar `database: "error"` sem derrubar a resposta quando o banco falhar.
- **RF-14** — When a tela Status do sistema é aberta, the sistema shall medir e exibir a
  latência do health em milissegundos.
- **RF-15** — When o ping falha ou o dispositivo está offline, the sistema shall exibir estado
  "Sem conexão" com opção de tentar novamente, sem derrubar a tela.
- **RF-16** — The sistema shall registrar o service worker do PWA na inicialização.
- **RF-17** — When o service worker detecta uma nova versão em espera, the sistema shall
  exibir a ação "Atualizar agora" na tela Status do sistema.
- **RF-18** — When o usuário aciona "Atualizar agora", the sistema shall ativar o novo service
  worker e recarregar a aplicação.

### Versão

- **RF-19** — The sistema shall derivar a versão exibida no app de `package.json` e o hash do
  commit do git, injetados em tempo de build.
- **RF-20** — Where o hash do commit não estiver disponível no ambiente de build, the sistema
  shall exibir `dev` no lugar do hash, sem falhar o build.
- **RF-21** — The versão exibida shall vir de uma única constante, sem strings de versão
  duplicadas nas telas.

### Navegação e rótulos

- **RF-22** — The bloco APP shall conter exatamente três itens: Configurações, Status do
  sistema e Sobre o app, cada um com destino distinto.
- **RF-23** — The hint de Configurações shall descrever apenas funcionalidades existentes
  ("Alertas, exportação e segurança").

---

## 4. Requisitos não funcionais

| # | Requisito |
|---|---|
| RNF-01 | O health responde em até 500 ms em operação normal; a tela de status trata timeout de 5 s. |
| RNF-02 | O endpoint de health é público (sem token) — não expõe nome de banco, host, credenciais ou stack trace. |
| RNF-03 | Exportação de dados exige token; nenhum dado sai sem autenticação. |
| RNF-04 | A exportação usa streaming/geração em memória e não carrega todas as tabelas simultaneamente em estruturas Python duplicadas. |
| RNF-05 | CSV usa UTF-8 com BOM e separador `,`, abrindo corretamente no Excel pt-BR. |
| RNF-06 | Preferências inválidas nunca chegam ao banco — validação por Pydantic no schema. |
| RNF-07 | Todo comentário e docstring novo em PT-BR, explicativo (regra do projeto). |
| RNF-08 | Nenhuma tela do bloco quebra quando a API está fora — degradam para estado de erro com retry. |

---

## 5. Critérios de aceitação

**CA-01 — Preferências persistem e afetam análise**
Given as preferências estão nos valores padrão e existe uma variante com 20 dias de cobertura,
When o usuário define `rupture_days = 25` e salva,
Then a variante passa a aparecer em "Risco de ruptura" na tela Alertas sem reinício da API.

**CA-02 — Validação de limiar**
Given o usuário está em Configurações,
When informa `rupture_days = 0` e tenta salvar,
Then a API responde 422 e a tela exibe a mensagem de erro sem persistir alteração.

**CA-03 — Padrões sem linha no banco**
Given a tabela de preferências está vazia,
When o cliente chama `GET /api/v1/settings/preferences`,
Then recebe 200 com os valores padrão (15 / 60 / 3).

**CA-04 — Exportação de conjunto**
Given existem vendas registradas,
When o usuário toca em "Vendas" na seção Dados,
Then o navegador baixa `lgd-vendas-AAAA-MM-DD.csv` com cabeçalho e uma linha por venda.

**CA-05 — Exportação de conjunto vazio**
Given não existe nenhuma despesa registrada,
When o usuário exporta "Despesas",
Then recebe um CSV válido contendo apenas a linha de cabeçalho.

**CA-06 — Relatórios em ZIP**
When o usuário toca em "Exportar relatórios",
Then baixa um `.zip` contendo os seis CSVs, todos abríveis.

**CA-07 — Exportação exige token**
Given uma requisição sem cabeçalho Authorization,
When chama qualquer rota de exportação,
Then a API responde 401 e nenhum dado é retornado.

**CA-08 — Status online**
Given a API está no ar,
When o usuário abre Status do sistema,
Then vê indicador verde, latência em ms, versão do app, hash do build e versão da API.

**CA-09 — Status offline**
Given a API está fora do ar,
When o usuário abre Status do sistema,
Then vê indicador vermelho com "Sem conexão" e botão "Tentar novamente", sem tela em branco.

**CA-10 — Health reporta banco fora**
Given o Postgres está indisponível,
When se chama `GET /api/v1/health`,
Then a resposta é 200 com `database: "error"` e nenhuma stack trace no corpo.

**CA-11 — Atualização do PWA**
Given uma nova versão foi publicada e o service worker está em espera,
When o usuário abre Status do sistema,
Then vê "Atualizar agora"; ao tocar, o app recarrega na versão nova.

**CA-12 — Versão única**
Given `package.json` está em `1.2.0`,
When se abre Sobre o app e Status do sistema,
Then ambas mostram `v1.2.0` com o mesmo hash de build, e não existe string `v1.0.0` no código.

**CA-13 — Bloco APP coerente**
When o usuário abre a seção Mais,
Then o bloco APP tem três itens com destinos distintos, e nenhum hint cita funcionalidade
inexistente (senha alterável, notificações).

---

## 6. Tratamento de erros

| Situação | Comportamento | HTTP / UI |
|---|---|---|
| Limiar fora do intervalo | Rejeita e mantém valor anterior | 422 + mensagem no campo |
| Payload de preferências malformado | Rejeita | 422 |
| Preferências sem token | Bloqueia | 401 → logout automático (handler já existente) |
| Banco fora ao ler preferências | Análises usam os valores padrão em memória | Tela de Alertas segue funcionando |
| Banco fora no health | `database: "error"` | 200, semáforo vermelho no status |
| Exportação sem token | Bloqueia | 401 |
| Conjunto de exportação inexistente na URL | Rejeita | 404 com nome dos conjuntos válidos |
| Exportação falha no meio | Erro registrado; cliente mostra "Falha ao exportar" | 500 + toast |
| Download bloqueado pelo navegador | Mensagem orientando permitir downloads | UI |
| Ping do health com timeout (>5s) | Trata como offline | UI "Sem conexão" |
| Service worker não suportado | Oculta a ação de atualização | UI |
| Hash do git indisponível no build | Usa `dev` | Build passa |

---

## 7. Modelo de dados

Migration Alembic `0004_preferencias_de_alerta`:

```
app_preference
├── id              INTEGER  PK, sempre 1 (registro único, CHECK id = 1)
├── rupture_days    INTEGER  NOT NULL DEFAULT 15
├── stopped_days    INTEGER  NOT NULL DEFAULT 60
├── critical_stock  INTEGER  NOT NULL DEFAULT 3
└── updated_at      TIMESTAMPTZ NOT NULL
```

Registro único garantido por `CHECK (id = 1)`; leitura devolve padrões quando a linha não
existe, gravação faz upsert.

---

## 8. Checklist de implementação

### Fase A — Backend: preferências
- [ ] Modelo `AppPreference` em `app/shared/models/` com docstring PT-BR
- [ ] Migration `0004_preferencias_de_alerta` (tabela + CHECK de registro único)
- [ ] Schemas Pydantic com validação de intervalo (`ge`/`le`)
- [ ] Service de leitura com fallback para padrões e gravação por upsert
- [ ] Rotas `GET`/`PUT /api/v1/settings/preferences` protegidas por `verify_token`
- [ ] `product_analysis_service` passa a ler `rupture_days` e `stopped_days`
- [ ] `marketing_intelligence_service` passa a ler `critical_stock`

### Fase B — Backend: exportação e health
- [ ] Serviço de exportação: um gerador de CSV por conjunto (produtos, vendas, compras, despesas, movimentações, cadastros)
- [ ] Rota `GET /api/v1/export/{conjunto}` → CSV com `Content-Disposition`
- [ ] Rota `GET /api/v1/export/reports` → ZIP em memória (`zipfile`, stdlib)
- [ ] Rota `GET /api/v1/health` pública com checagem `SELECT 1` e versão da API
- [ ] Versão da API vinda de uma constante única (mesma usada no `FastAPI(version=...)`)

### Fase C — Frontend: infraestrutura
- [ ] `vite.config.ts` injeta `__APP_VERSION__` (package.json) e `__BUILD_HASH__` (git, fallback `dev`)
- [ ] Tipagem das constantes em `vite-env.d.ts`
- [ ] Registro do service worker em `main.tsx` com estado de atualização exposto
- [ ] Tipos e métodos novos em `services/api.ts` (preferências, health, download autenticado)
- [ ] Helper de download com header Authorization → blob → revoke da object URL

### Fase D — Frontend: telas
- [ ] `Settings.tsx` reescrita: seções Alertas (formulário), Dados (exportação), Segurança (informativo)
- [ ] `SystemStatus.tsx` nova tela
- [ ] `About.tsx` usando constantes de versão + versão da API
- [ ] `nav.tsx`: novo `ScreenId` `system-status`
- [ ] `App.tsx`: rota da nova tela
- [ ] `More.tsx`: item "Sincronização" → "Status do sistema"; hints corrigidos; versão dinâmica

### Fase E — Verificação
- [ ] `GET`/`PUT` de preferências via curl, incluindo caso 422
- [ ] Exportação de cada conjunto + ZIP verificados abrindo os arquivos
- [ ] Health com banco no ar e com banco derrubado
- [ ] Build do frontend passando (`tsc -b && vite build`) com versão correta
- [ ] Grep confirmando que `v1.0.0` não existe mais hardcoded
- [ ] `graphify update .`
