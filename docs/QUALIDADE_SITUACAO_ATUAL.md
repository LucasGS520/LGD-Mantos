# Qualidade e situação atual — pendências

Atualizado em 2026-11-10. Código: `6d8b98c`; Arquitetura: `960c07d`;
Banco implementado nesta sessão a partir dessa baseline.

Este é o registro central das pendências de qualidade. A fonte de regras de negócio continua sendo [Produto e objetivo](PRODUTO_E_OBJETIVO.md); este documento não aprova mudanças funcionais, de arquitetura ou de schema antecipadamente.

## Situação por dimensão

| Dimensão | Situação | Evidência e limite |
|---|---|---|
| Código | Plano C0–C8 concluído | Modularização, recuperação de falhas, contratos e gates descritos no [resultado da implementação](QUALIDADE_CODIGO_RESULTADO.md). Não é uma declaração de ausência de qualquer defeito futuro |
| Arquitetura | Aplicação implementada e verificada; limites de capacidade documentados | [Resultado de Arquitetura](QUALIDADE_ARQUITETURA_RESULTADO.md): snapshots, consultas, transações, fotos, fronteiras e medidas; preparação real de infraestrutura permanece separada |
| Banco | Plano B0–B6 implementado e verificado no ambiente isolado | [Resultado](QUALIDADE_BANCO_RESULTADO.md): baseline 0007, 15 tabelas, constraints, ACLs, restauração e medidas; servidor real permanece em OPS |
| Operação e disponibilidade | Ferramentas e ensaio sintético entregues; implantação real pendente | Backup/restauração e indisponibilidade foram ensaiados localmente; falta destino externo, política de RPO/RTO, coleta/alertas e ensaio do servidor real |

Na execução de Arquitetura passaram 84 testes backend no Python 3.12, 19 testes frontend, cinco jornadas Playwright, build, lint e fronteiras. Há medidas exploratórias em três escalas e ensaio de restauração sintética; detalhes e limites estão no resultado. Isso não mede disponibilidade de produção.

Na entrega de Banco passaram 124 testes backend em Python 3.12/Linux, 19 testes
frontend, cinco jornadas Playwright, build, lint e fronteiras. Instalação,
reconstrução, permissões e restauração do schema 0007 foram comprovadas na base
isolada. As três escalas foram medidas; correção extensa em 50 mil levou cerca
de 36 s e duas de quatro prévias concorrentes retornaram 503 recuperável. O
[resultado de Banco](QUALIDADE_BANCO_RESULTADO.md) registra as evidências completas.

O pipeline baseline de Arquitetura `960c07d` foi consultado e passou
([execução](https://github.com/LucasGS520/LGD-Mantos/actions/runs/42688125615)).
O CI remoto das mudanças de Banco depende de sua publicação; os gates locais
constam no resultado. O banco operacional não foi usado nos ensaios.

## Como ler as prioridades

- **P0:** requisito de proteção a resolver antes de depender da implantação para dados operacionais reais.
- **P1:** investigação ou melhoria prioritária para planejar Arquitetura/Banco com evidência.
- **P2:** decisão condicionada à investigação ou a uma necessidade concreta.
- **Aberta:** trabalho necessário ainda sem evidência de conclusão.
- **Condicional:** avaliar a necessidade; a solução sugerida não está aprovada nem é automaticamente obrigatória.

Prioridade não é severidade de incidente. Os itens abaixo não comprovam perda de dados, lentidão em produção ou corrupção da base.

## Arquitetura

O [plano A0–A9](PLANO_MELHORIAS_ARQUITETURA.md) e o [resultado](QUALIDADE_ARQUITETURA_RESULTADO.md) detalham a execução. ARQ-01–10 estão encerrados no escopo da aplicação por implementação verificada ou decisão de manutenção com limites explícitos. Acompanhamento de capacidade real fica em ARQ-11; infraestrutura real continua em OPS.

| ID | Prioridade / estado | Fato atual e fonte | Trabalho pendente | Critério de encerramento |
|---|---|---|---|---|
| ARQ-01 | P1 / Investigação encerrada com limites | Replay integral medido em três escalas; leitura sem entidades e dependentes em lotes | Acompanhar necessidade real em ARQ-11 | A0/A6 e ADRs; 50 mil não atende todas as metas, sem SLA acordado |
| ARQ-02 | P1 / Encerrada com limites | Trava global mantida, espera/tempo instrumentados e timeout recuperável | Reconsiderar contenção conforme ARQ-11 | Concorrência/idempotência testadas; quatro prévias em 50 mil tiveram um 503, publicado no resultado |
| ARQ-03 | P1 / Concluída na aplicação | Gestão em snapshot read-only, sem trava compartilhada; cálculo após encerrar sessão | Coleta no servidor em OPS-03 | Teste intercala confirmação entre leituras sem misturar base ou bloquear escritor |
| ARQ-04 | P1 / Concluída no escopo medido | Produto por ID, movimentos por origem, operações por cursor, gestão por visão/página | Consultas completas legadas e origens ainda podem crescer; reavaliar com ARQ-11/BD-03 | Redução de payload e jornadas verificadas; replay permanece integral |
| ARQ-05 | P2 / Encerrada por decisão | Pilha local mantida | Reabrir diante de necessidade concreta de deep link/refresh com contexto | ADR 0001 registra perda de contexto e ausência de histórico de navegador |
| ARQ-06 | P1 / Concluída | Interfaces públicas, sessão injetada, matriz e ciclos nos gates | Manter gates ao evoluir | Testes aceitam fronteiras válidas e recusam imports privados/ciclos |
| ARQ-07 | P1 / Concluída | Unidade transacional por fluxo e snapshots compostos | Preservar políticas em alterações futuras | Testes de commit/rollback, leituras intercaladas e ADR 0002 |
| ARQ-08 | P1 / Concluída na aplicação | Substituição backend no mesmo ID, compensação segura e reconciliação read-only | Rotina operacional e backups reais em OPS | Falhas/interrupção injetadas, repetição no browser e restauração sintética verificadas |
| ARQ-09 | P1 / Concluída na aplicação | Prontidão 503 para banco indisponível; vivacidade separada | Monitor/alertas reais em OPS-03 | Parada e recuperação do PostgreSQL de ensaio comprovadas |
| ARQ-10 | P2 / Encerrada por decisão | JWT/localStorage mantidos; proteção de tentativas por processo | Reabrir diante de nova fronteira de acesso ou demanda de revogação | ADR 0001 e Deploy registram rotação, limites e risco de token copiado |
| ARQ-11 | P2 / Acompanhamento condicional | Não existe estimativa real; 50 mil/500 variantes e correções extensas ultrapassam metas exploratórias | Observar volume real, p95 e impactos; avaliar mais otimizações, resumos de impacto ou checkpoints antes de depender desse perfil | Perfil/objetivos acordados e nova decisão com equivalência de replay; não há promessa de capacidade irrestrita |

Snapshot transacional de leitura foi implementado; não é checkpoint do ledger. Checkpoints, projeções incrementais, cache ou nova granularidade de trava continuam condicionados ao perfil real e à equivalência do replay. Correções, custo desconhecido, ordenação, assinatura e idempotência permanecem obrigatórios.

## Banco de dados

As fontes são os [modelos ORM](../backend/app/shared/models/entities.py) e a
[baseline 0007](../backend/migrations/versions/0007_banco_canonico.py). O
[plano](PLANO_MELHORIAS_BANCO.md) contém dicionário e matriz de invariantes; o
[resultado](QUALIDADE_BANCO_RESULTADO.md) reúne evidências físicas e limitações.
BD-01–08 foram encerrados no escopo da aplicação e do ensaio sintético. A
verificação do banco implantado permanece explicitamente em OPS-02/03.

| ID | Prioridade / estado | Fato atual | Trabalho pendente | Critério de encerramento |
|---|---|---|---|---|
| BD-01 | P1 / Concluída | Matriz regra/camada, constraints nomeadas, inventário único e FK composta de fotos | Preservar regras no ledger | Rejeições SQL diretas e correspondência ORM/baseline verificadas |
| BD-02 | P1 / Concluída | Operações, itens e pagamentos relacionais; payload reconstruído em lote | Acompanhar custo de replay em ARQ-11 | Ordem, IDs, nomes/preços históricos, correções e atomicidade verificados |
| BD-03 | P1 / Concluída no cenário medido | Quatro candidatos comparados por EXPLAIN; três incorporados | Reavaliar consultas com perfil real | [Planos antes/depois](database-index-plans.json), sem GIN ou índices redundantes |
| BD-04 | P2 / Concluída | UUID nativo nas PKs/FKs, strings no HTTP | Manter validação antes do SQL | UUID canônico, referências inválidas e contratos testados |
| BD-05 | P2 / Concluída | Documentos históricos JSONB com versão explícita; desconhecida recusada | Sem otimização preventiva dos documentos | Estrutura object, versões e restauração verificados; JSONB não resolve replay |
| BD-06 | P1 / Concluída | Todas as FKs RESTRICT; histórico append-only por privilégios | Manter exclusões explícitas de filhos | ACLs efetivas e tentativas proibidas testadas com lgd_app |
| BD-07 | P1 / Concluída com acompanhamento | Crescimento após correções extensas medido em três escalas; sem expiração | Acompanhar armazenamento real em OPS-03 | [Medições](database-benchmark.json), recibos datados/vinculados e política sem TTL |
| BD-08 | P1 / Concluída no ensaio | Diagnóstico read-only de schema/ACL, conexões, tamanhos, documentos e autovacuum | Executar diagnóstico no servidor em OPS-02/03 | [Schema restaurado](database-restored-schema.json); pool/autovacuum mantidos sem tuning especulativo |

Os cadastros separados protegem o tipo da referência; a FK composta protege o
produto da variante da foto. Snapshots históricos JSONB preservam fatos do
passado e não são substituídos pelo cadastro atual. Disponibilidade histórica,
soma de pagamentos e normalização Unicode continuam na aplicação/ledger.

## Operação, disponibilidade e confirmação das evidências

| ID | Prioridade / estado | Pendência | Evidência necessária para encerrar |
|---|---|---|---|
| OPS-01 | P0 / Parcial, implantação aberta | Ferramentas e restauração sintética verificadas; falta política e captura real | Acordar RPO/RTO, frequência, retenção, destino externo e responsável; restaurar backup da implantação em ambiente separado, conferindo registros/fotos |
| OPS-02 | P1 / Parcial, implantação aberta | Migração separada, imagem e reinício sintético verificados; falta servidor real | Executar checklist da release escolhida, HTTPS/DNS/segredos/volumes, recuperação e compatibilidade de schema; rollback de imagem não reverte dados |
| OPS-03 | P1 / Parcial, implantação aberta | Telemetria JSON, fases, locks, timeouts e prontidão implementados e testados | Configurar coleta/retenção/alertas no servidor e comprovar recebimento de sinais sem dados sensíveis; medir perfil real |
| VER-01 | P1 / Baseline concluída; release atual pendente | Pipeline de `960c07d` confirmado com sucesso; gates locais de Banco registrados | Após publicação, conferir jobs/artefatos do SHA final; sucesso da baseline não equivale a CI das mudanças atuais |

[Deploy](DEPLOY.md) descreve a topologia e os volumes. Ter volumes persistentes e um health endpoint não comprova que existe backup restaurável, monitoramento ou prontidão operacional. Esses itens são infraestrutura; não criam funcionalidades de exportação, caixa ou gestão financeira na interface.

## Ordem recomendada para as próximas tarefas

1. Se já houver dados reais, resolver OPS-01 imediatamente: o ensaio sintético não é backup da loja.
2. Na instalação escolhida, executar bootstrap e reconstrução explícita da baseline 0007 conforme Deploy; nunca usar a base operacional para testes.
3. Definir perfil real quando houver histórico de uso e acompanhar ARQ-11. Reconsiderar capacidade antes de depender de correções extensas ou do cenário de 50 mil com várias abas.
4. Finalizar configuração/ensaio do servidor em OPS-01/02/03 e validar CI do SHA final após publicação autorizada.
5. Preservar as evidências de Banco e as garantias do ledger em evoluções futuras. Atualizar este registro por evidência.

Não há estimativa de prazo ou promessa de capacidade antes do diagnóstico. O banco operacional não deve ser alterado para testar; a primeira rodada de medidas deve usar `lgd_mantos_alignment_test` e dados sintéticos representativos. Qualquer necessidade de inspeção de produção deve ser definida explicitamente, com escopo de leitura e proteção dos dados.

## Manutenção do registro

Cada item só muda para concluído com referência à decisão e à sua verificação. Uma decisão fundamentada de manter a solução atual pode encerrar uma investigação; uma implementação necessária não pode ser encerrada apenas com um documento de intenção. Novos defeitos de Código devem receber itens próprios, sem reabrir genericamente C0–C8 nem apagar o histórico da entrega.

Este documento substitui a lista informal de pendências da avaliação anterior. [Plano de Código](PLANO_MELHORIAS_CODIGO.md) e [resultado de Código](QUALIDADE_CODIGO_RESULTADO.md) permanecem como registro da etapa concluída; [Alinhamento implementado](ALINHAMENTO_IMPLEMENTADO.md) continua descrevendo os contratos em vigor.
