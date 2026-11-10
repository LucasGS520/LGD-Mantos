# Resultado da dimensão Banco

Execução B0–B6 sobre `960c07d`, conforme o [plano aprovado](PLANO_MELHORIAS_BANCO.md).
O núcleo foi reconstruído, as ferramentas adaptadas e as verificações executadas
somente em `lgd_mantos_alignment_test`. Não houve reconstrução do banco
operacional, publicação de release ou implantação no servidor real.

## Desenho entregue

A única baseline ativa é [0007](../backend/migrations/versions/0007_banco_canonico.py),
sem ancestral, com DDL congelado independente do ORM. As revisões 0001–0006
saíram da cadeia ativa e continuam recuperáveis no Git. A metadata não importa
autenticação ou configuração da API. Instalação antiga é recusada, sem stamp.

São 15 tabelas de negócio mais `alembic_version`:

- Cinco cadastros: `lgd_suppliers`, `lgd_categories`, `lgd_purchase_channels`,
  `lgd_sale_channels`, `lgd_payment_methods`.
- Catálogo: `lgd_products`, `lgd_variants`, `lgd_photos`.
- Agregados: `lgd_operations`, `lgd_operation_items`, `lgd_sale_payments`.
- Rastreabilidade: `lgd_movements`, `lgd_revisions`, `lgd_requests`, `lgd_control`.

UUID nativo mantém strings no HTTP; dinheiro relacional usa NUMERIC(14,2), datas
de compra DATE e instantes TIMESTAMPTZ. Sequência/revisão global são BIGINT.
Colunas, itens e pagamentos são canônicos. O repositório reconstrói payloads
em lotes; não existe uma segunda cópia editável do payload. Pagamentos são
conciliados por ID, com exclusão apenas dos removidos. A unicidade diferível da
posição permite reordenação preservando ID e instante.

Snapshots, resultados, antes/depois e recibos usam JSONB com versão de formato
e estrutura de objeto. Versões desconhecidas produzem recusa explícita. Retratos
preservam nomes, preços e referências históricos. Correções, custo desconhecido,
anulação, ledger puro e transação única permanecem. Não há endpoints independentes
de escrita de itens ou pagamentos.

Checks nomeados protegem tipos, versões, quantidades, valores, posições e campos
por operação. Há inventário único/não anulável, FK composta para foto do mesmo
produto e no máximo uma principal. Todas as FKs são RESTRICT. Regras temporais,
normalização Unicode, atividade de referências, disponibilidade e soma de
pagamentos continuam na aplicação/ledger, conforme a matriz do plano.

`lgd_app` executa a API; não pode criar tabelas temporárias, alterar schema,
TRUNCATE, excluir operações/cadastros ou alterar/remover movimentos, revisões e
recibos. `lgd_migrator` possui o schema. O bootstrap administrativo cria as roles
e não cria dados. O container da API foi inspecionado sem imprimir segredos:
não recebe variáveis administrativas e não pode assumir `lgd_migrator`.

O [schema restaurado efetivo](database-restored-schema.json) registra tabelas,
checks, permissões, tamanhos e comparação ORM sem divergência. A decisão está
na [ADR 0003](decisions/0003-banco-relacional-historico.md).

## Índices e planos SQL

O [artefato de planos](database-index-plans.json) contém SQL e EXPLAIN
(ANALYZE, BUFFERS) antes/depois, após ANALYZE, cinco amostras com aquecimento.
Base sintética: 50 mil operações, 100 mil movimentos, 100 mil revisões e 10 mil
fotos. Esse conjunto isola padrões de acesso; não simula histórico de ledger.

| Candidato | Mediana antes → depois | Decisão |
|---|---|---|
| operações `(kind, sequence)` | 0,045 → 0,041 ms | Descartado; unicidade de sequence já atende a página medida |
| movimentos `(operation_id, created_at, id)` | 2,626 → 0,943 ms | Incorporado; ordenação por origem atendida |
| revisões `(entity_id, created_at, id)` | 2,999 → 0,860 ms | Incorporado; desempate estável na consulta |
| fotos `(product_id, position, id)` | 0,229 → 0,052 ms | Incorporado; consulta e índice alinhados |

Não foram acrescentados índices redundantes de FK, GIN, particionamento ou
índices genéricos de documentos. Esses planos justificam os índices nesse
workload, sem prometer o mesmo ganho em qualquer instalação.

## Volume, persistência e crescimento

[Medições completas](database-benchmark.json): Windows/Python 3.11.9, PostgreSQL
16.15 em Docker, três amostras e um aquecimento para leituras/prévias. p95 de três
amostras é exploratório. Confirmações são amostras únicas. A suíte funcional
também é executada em Python 3.12/Linux. Não há estimativa real ou SLA acordado.

| Operações / variantes | Gestão p95 | Prévia p95 | Confirmação única | Correção extensa única / dependentes |
|---|---|---|---|---|
| 1.000 / 10 | 88 ms | 48 ms | 332 ms | 460 ms / 500 |
| 10.000 / 100 | 750 ms | 700 ms | 703 ms | 7.408 ms / 5.000 |
| 50.000 / 500 | 4.081 ms | 3.532 ms | 3.606 ms | 35.859 ms / 25.000 |

Em 50 mil, catálogo e página de operações ficaram abaixo de 24 ms p95. A resposta
da correção extensa tem aproximadamente 38,7 MB. Quatro prévias simultâneas
produziram quatro 200 em 1 mil/10 mil; em 50 mil, dois 200 e dois 503 recuperáveis
de espera. Não se removeu trava ou auditoria para reduzir essa duração.

Comparação exploratória com [Arquitetura](architecture-after.json): prévia p95
de 50 mil passou de 2.572 para 3.532 ms; confirmação única de 2.382 para 3.606 ms;
correção extensa de 29.157 para 35.859 ms. Em 10 mil, respectivamente 504 → 700,
439 → 703 e 5.479 → 7.408 ms. O novo fluxo carrega filhos relacionais e aplica
FKs/constraints, acrescentando custo. São sessões distintas e fixtures ajustadas
para defaults explícitos do contrato; isso não isola causalidade nem constitui
um benchmark A/B controlado. Não se afirma ganho de desempenho do JSONB.

| Escala | Relações antes → depois | Auditoria depois | Recibos depois |
|---|---|---|---|
| 1 mil | 2,31 → 4,59 MiB | 1,62 MiB | 0,13 MiB |
| 10 mil | 16,37 → 37,59 MiB | 15,11 MiB | 0,72 MiB |
| 50 mil | 78,71 → 184,34 MiB | 75,38 MiB | 3,38 MiB |

Os tamanhos incluem índices/TOAST e espaço retido por atualizações, não apenas
dados vivos. O antes é uma carga sintética sem auditoria pregressa; o depois
inclui uma confirmação e uma correção ampla. Em 50 mil, itens/pagamentos ocupam
cerca de 28,5 MiB antes da correção. Uma nova correção ampla acrescenta revisões
e recibo; não extrapolar linearmente espaço físico devido a reutilização,
compressão e autovacuum. Dead/live tuples são estimativas estatísticas.

O [diagnóstico após a carga](database-growth-diagnostic.json) registra documentos,
tamanhos, sessões e autovacuum ativo. Histórico/recibos não expiram. Pool e
autovacuum foram mantidos; não há limpeza automática ou VACUUM FULL rotineiro.
Acompanhar crescimento, transações longas, p95 e contenção com o perfil real
em ARQ-11/OPS-03. Amostras afetadas por suspensão do ambiente foram recusadas
e substituídas por uma execução completa válida.

## Instalação, reconstrução e recuperação

Bootstrap + migração em base vazia resultaram em 16 tabelas públicas, zero
operações e zero fotos. A reconstrução foi ensaiada explicitamente no banco de
teste, com host/banco/confirmador conferidos; removeu o schema e todos os arquivos
gerenciados do volume. API ativa foi recusada sem limpeza. Nenhum inventário
ou dado demonstrativo é criado por inicialização ou reconstrução.

O ensaio criou inventário, compra, venda parcial, correção retroativa e foto pela
API; parou a API, capturou manifesto v2/dump/fotos e restaurou em outro PostgreSQL
vazio. Bootstrap provisionou roles no destino; pg_restore executou como migrator
preservando ACLs. Foram conferidas as 15 contagens, 3 operações/itens, 1 pagamento,
12 revisões, 3 movimentos, 4 recibos e 1 foto. Replay/projeções e conteúdo da foto
passaram usando lgd_app. Saldo final: 3 unidades, pendência R$ 35,00 e custo
histórico R$ 22,40. Restore da fixture levou 2,50 s; não é RTO de produção.
As contagens e verificações estão no [registro de recuperação](database-recovery-evidence.json).

Comandos e credenciais estão no [Deploy](DEPLOY.md) e no README. As evidências
anteriores de Código/Arquitetura permanecem como histórico das versões respectivas.
Backup externo, RPO/RTO, agendamento, alertas e validação do servidor real continuam
abertos em OPS-01/02/03. O pipeline de `960c07d` passou; o CI da nova release deve
ser conferido depois da publicação autorizada.

## Gates e encerramento

- Backend: 124 testes passaram em Python 3.12/Linux, incluindo regressão de
  contratos, replay, correções, concorrência, idempotência, rollback/falha de
  commit, constraints SQL e permissões efetivas. Ruff e fronteiras passaram.
- Dois testes direcionados passaram novamente após a última ampliação de
  cobertura de UUID canônico em correção e upload de fotos.
- Frontend: 19 testes em 10 arquivos, build TypeScript/Vite, ESLint sem avisos
  e fronteiras/ciclos em 126 arquivos passaram.
- Playwright: cinco jornadas passaram, incluindo operação completa, prévia
  obsoleta, resposta perdida com repetição idempotente, falha recuperável na
  consulta de movimentos e repetição da substituição de foto no mesmo ID.
- Instalação, reconstrução isolada, recusa de instalação antiga e de destinos
  divergentes, restore e schema/ACL sem divergência foram verificados.
- Planos SQL e medidas em 1 mil, 10 mil e 50 mil foram registrados. Os limites
  observados permanecem em ARQ-11; não são falhas ocultadas para encerrar a dimensão.

BD-01–08 possuem implementação/evidência no [registro central](QUALIDADE_SITUACAO_ATUAL.md).
B0–B6 estão concluídos no escopo aprovado. As dependências do servidor e os
limites de capacidade permanecem explícitos. Containers, volumes, rede e imagem
Docker temporários LGD do ensaio foram removidos; as evidências textuais ficam
no repositório.
