# Qualidade e situação atual — pendências

Atualizado em 2026-11-09. Código: `6d8b98c`; execução de Arquitetura a partir de `f67c59e`, registrada no commit desta entrega.

Este é o registro central das pendências de qualidade. A fonte de regras de negócio continua sendo [Produto e objetivo](PRODUTO_E_OBJETIVO.md); este documento não aprova mudanças funcionais, de arquitetura ou de schema antecipadamente.

## Situação por dimensão

| Dimensão | Situação | Evidência e limite |
|---|---|---|
| Código | Plano C0–C8 concluído | Modularização, recuperação de falhas, contratos e gates descritos no [resultado da implementação](QUALIDADE_CODIGO_RESULTADO.md). Não é uma declaração de ausência de qualquer defeito futuro |
| Arquitetura | Aplicação implementada e verificada; limites de capacidade documentados | [Resultado de Arquitetura](QUALIDADE_ARQUITETURA_RESULTADO.md): snapshots, consultas, transações, fotos, fronteiras e medidas; preparação real de infraestrutura permanece separada |
| Banco | Avaliação e plano de execução pendentes | Schema preservado na refatoração; modelagem, invariantes e comportamento com volume ainda precisam de avaliação |
| Operação e disponibilidade | Ferramentas e ensaio sintético entregues; implantação real pendente | Backup/restauração e indisponibilidade foram ensaiados localmente; falta destino externo, política de RPO/RTO, coleta/alertas e ensaio do servidor real |

Na execução de Arquitetura passaram 84 testes backend no Python 3.12, 19 testes frontend, cinco jornadas Playwright, build, lint e fronteiras. Há medidas exploratórias em três escalas e ensaio de restauração sintética; detalhes e limites estão no resultado. Isso não mede disponibilidade de produção.

O pipeline baseline `f67c59e` foi consultado e passou ([execução](https://github.com/LucasGS520/LGD-Mantos/actions/runs/42282745014)). O resultado remoto da entrega de Arquitetura deve ser conferido após sua publicação. Dados operacionais, backups e implantação real não foram inspecionados ou alterados.

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

As fontes de schema são [modelos ORM](../backend/app/shared/models/entities.py) e [migração 0006](../backend/migrations/versions/0006_nucleo_confiavel.py). A inspeção dos modelos não substitui uma conferência do banco efetivamente implantado.

| ID | Prioridade / estado | Fato atual | Trabalho pendente | Critério de encerramento |
|---|---|---|---|---|
| BD-01 | P1 / Aberta | Existem constraints de unicidade, saldo e referências monetárias; outras invariantes dependem da aplicação | Inventariar invariantes e avaliar checks de tipos/ações, versões/sequências positivas, custo médio não negativo, posição e unicidade de foto principal, além do vínculo produto/variante | Matriz regra → camada responsável; testes de violação e migrações somente das proteções escolhidas, após conferir dados existentes |
| BD-02 | P1 / Aberta | `payload`, `result`, revisões e recibos armazenam JSON; itens/pagamentos pertencem atomicamente à operação | Avaliar consultas necessárias, referências internas e validação/versionamento desses documentos; comparar manutenção do agregado com normalização seletiva | Decisão documentada com efeitos sobre snapshots, auditoria, atomicidade, consultas e migração; preservar o agregado continua sendo uma opção válida |
| BD-03 | P1 / Aberta | Há índices básicos, mas as consultas carregam muitos registros antes de filtrar | Levantar cardinalidades, tamanhos e padrões reais; coletar estatísticas e planos das consultas relevantes com `EXPLAIN (ANALYZE, BUFFERS)` em ambiente adequado | Relatório de planos/tempos e decisão para cada ajuste; nenhum índice criado apenas por suposição |
| BD-04 | P2 / Condicional | Identificadores são `String(36)`, não UUID nativo | Avaliar benefício, custo de migração de PK/FK e compatibilidade dos IDs em JSON e contratos | Decisão de manter ou migrar, com estratégia de validação e reversão quando aplicável; não classificar o tipo textual como falha de integridade comprovada |
| BD-05 | P2 / Condicional | Os documentos do núcleo usam `JSON`, não `JSONB` | Relacionar operações de consulta/índice necessárias aos documentos e medir alternativas | Escolha fundamentada pelo workload; mudar para JSONB sem mudar o padrão de leitura integral não comprova melhoria de desempenho |
| BD-06 | P1 / Aberta | Foreign keys não declaram políticas `ondelete`; aplicação usa desativação para cadastros | Documentar exclusão/restrição por relacionamento, inclusive fotos e histórico; distinguir comportamento padrão do banco de decisão intencional | Política explícita e testes; alterar FK somente se necessário, preservando referências históricas |
| BD-07 | P1 / Aberta | Operações, revisões, movimentos e recibos idempotentes podem crescer continuamente; recibos guardam respostas estruturadas | Medir crescimento, tamanho dos documentos e necessidade de manutenção; definir duração da garantia de repetição antes de discutir retenção de recibos | Projeção de crescimento e política documentada, sem expiração arbitrária de recibos nem remoção de histórico necessário ao replay/auditoria |
| BD-08 | P1 / Aberta | Há SQLAlchemy assíncrono e PostgreSQL; o estado operacional não foi diagnosticado | Conferir conexões/pool, estatísticas de uso, autovacuum, dead tuples e capacidade de armazenamento; verificar correspondência entre migrações e schema implantado | Diagnóstico registrado com contexto de carga e ações necessárias; configurações adicionais de pool/manutenção só quando justificadas |

Uma FK não garante, por si, que uma categoria tenha `kind=category` ou que uma variante de foto pertença ao mesmo produto. A matriz BD-01 deve explicitar essas regras e decidir onde protegê-las. As referências dentro de JSON também não recebem automaticamente a mesma integridade de uma FK relacional.

## Operação, disponibilidade e confirmação das evidências

| ID | Prioridade / estado | Pendência | Evidência necessária para encerrar |
|---|---|---|---|
| OPS-01 | P0 / Parcial, implantação aberta | Ferramentas e restauração sintética verificadas; falta política e captura real | Acordar RPO/RTO, frequência, retenção, destino externo e responsável; restaurar backup da implantação em ambiente separado, conferindo registros/fotos |
| OPS-02 | P1 / Parcial, implantação aberta | Migração separada, imagem e reinício sintético verificados; falta servidor real | Executar checklist da release escolhida, HTTPS/DNS/segredos/volumes, recuperação e compatibilidade de schema; rollback de imagem não reverte dados |
| OPS-03 | P1 / Parcial, implantação aberta | Telemetria JSON, fases, locks, timeouts e prontidão implementados e testados | Configurar coleta/retenção/alertas no servidor e comprovar recebimento de sinais sem dados sensíveis; medir perfil real |
| VER-01 | P1 / Baseline concluída; release atual pendente | Pipeline de `f67c59e` confirmado com sucesso; resultado remoto da entrega de Arquitetura ainda não conferido | Após publicação, conferir jobs/artefatos do SHA final; sucesso da baseline não equivale a CI das mudanças atuais |

[Deploy](DEPLOY.md) descreve a topologia e os volumes. Ter volumes persistentes e um health endpoint não comprova que existe backup restaurável, monitoramento ou prontidão operacional. Esses itens são infraestrutura; não criam funcionalidades de exportação, caixa ou gestão financeira na interface.

## Ordem recomendada para as próximas tarefas

1. Se já houver dados reais, resolver OPS-01 imediatamente: o ensaio sintético não é backup da loja.
2. Preparar o plano da dimensão Banco a partir de BD-01–08, usando as consultas/medidas da Arquitetura como insumo; manter UUID/JSONB/normalização condicionais.
3. Definir perfil real quando houver histórico de uso e acompanhar ARQ-11. Reconsiderar capacidade antes de depender de correções extensas ou do cenário de 50 mil com várias abas.
4. Finalizar configuração/ensaio do servidor em OPS-01/02/03 e validar CI do SHA final após publicação autorizada.
5. Para mudanças de Banco, planejar validação dos registros, backup e recuperação antes da migração, preservando o ledger e as garantias entregues. Atualizar este registro por evidência.

Não há estimativa de prazo ou promessa de capacidade antes do diagnóstico. O banco operacional não deve ser alterado para testar; a primeira rodada de medidas deve usar `lgd_mantos_alignment_test` e dados sintéticos representativos. Qualquer necessidade de inspeção de produção deve ser definida explicitamente, com escopo de leitura e proteção dos dados.

## Manutenção do registro

Cada item só muda para concluído com referência à decisão e à sua verificação. Uma decisão fundamentada de manter a solução atual pode encerrar uma investigação; uma implementação necessária não pode ser encerrada apenas com um documento de intenção. Novos defeitos de Código devem receber itens próprios, sem reabrir genericamente C0–C8 nem apagar o histórico da entrega.

Este documento substitui a lista informal de pendências da avaliação anterior. [Plano de Código](PLANO_MELHORIAS_CODIGO.md) e [resultado de Código](QUALIDADE_CODIGO_RESULTADO.md) permanecem como registro da etapa concluída; [Alinhamento implementado](ALINHAMENTO_IMPLEMENTADO.md) continua descrevendo os contratos em vigor.
