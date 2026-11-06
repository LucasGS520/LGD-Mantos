# Qualidade e situação atual — pendências

Atualizado em 2026-11-06. Referência de código: commit `6d8b98c`.

Este é o registro central das pendências de qualidade. A fonte de regras de negócio continua sendo [Produto e objetivo](PRODUTO_E_OBJETIVO.md); este documento não aprova mudanças funcionais, de arquitetura ou de schema antecipadamente.

## Situação por dimensão

| Dimensão | Situação | Evidência e limite |
|---|---|---|
| Código | Plano C0–C8 concluído | Modularização, recuperação de falhas, contratos e gates descritos no [resultado da implementação](QUALIDADE_CODIGO_RESULTADO.md). Não é uma declaração de ausência de qualquer defeito futuro |
| Arquitetura | Avaliação e plano de execução pendentes | A separação de responsabilidades foi entregue; capacidade, contenção e estratégia de leitura/reprodução ainda precisam de avaliação |
| Banco | Avaliação e plano de execução pendentes | Schema preservado na refatoração; modelagem, invariantes e comportamento com volume ainda precisam de avaliação |
| Operação e disponibilidade | Preparação para uso real pendente de comprovação | Há configuração de deploy, mas backup, restauração e disponibilidade ainda não possuem critérios operacionais demonstrados |

A última verificação registrada na entrega de Código teve 64 testes backend no Python 3.12, 16 testes frontend, quatro jornadas Playwright, build, lint e verificações de fronteiras passando. Esses resultados são históricos daquela entrega; não foram reexecutados nesta atualização documental e não medem capacidade ou disponibilidade em produção.

O workflow foi atualizado e o commit enviado ao GitHub. O resultado remoto desse push não foi consultado nesta atualização: não presumir CI verde nem falha de CI. Volume e estado dos dados operacionais, desempenho real, backups existentes e implantação em produção também não foram inspecionados.

## Como ler as prioridades

- **P0:** requisito de proteção a resolver antes de depender da implantação para dados operacionais reais.
- **P1:** investigação ou melhoria prioritária para planejar Arquitetura/Banco com evidência.
- **P2:** decisão condicionada à investigação ou a uma necessidade concreta.
- **Aberta:** trabalho necessário ainda sem evidência de conclusão.
- **Condicional:** avaliar a necessidade; a solução sugerida não está aprovada nem é automaticamente obrigatória.

Prioridade não é severidade de incidente. Os itens abaixo não comprovam perda de dados, lentidão em produção ou corrupção da base.

## Arquitetura

| ID | Prioridade / estado | Fato atual e fonte | Trabalho pendente | Critério de encerramento |
|---|---|---|---|---|
| ARQ-01 | P1 / Aberta | Prévia e confirmação carregam acontecimentos e reproduzem o histórico; confirmação pode recalcular registros posteriores. `operations/service.py`, `_execute()` | Medir tempo, memória e custo de correções antigas com históricos representativos; definir o volume e a latência aceitáveis para a loja | Perfil reproduzível, limites de uso acordados e decisão registrada: manter estratégia ou planejar otimização com equivalência do replay |
| ARQ-02 | P1 / Aberta | Gravações usam advisory lock exclusivo; variantes são bloqueadas em ordem. `shared/persistence/base.py`, `lock()`; `catalog/repository.py`, `locked_variants()` | Medir duração/espera da trava em compras, vendas, correções e fotos; considerar múltiplas abas mesmo com um dono | Teste concorrente e tempos de espera registrados; manter ou alterar a granularidade com justificativa e proteção contra venda excedente |
| ARQ-03 | P1 / Aberta | Gestão usa trava compartilhada e também reproduz todo o histórico. `management/repository.py`, `read_lock()`; `management/service.py`, `report()` | Medir interferência de consultas gerenciais em gravações e documentar a consistência necessária por consulta | Evidência de concorrência entre gestão e operação; decisão de leitura coerente com latência aceitável |
| ARQ-04 | P1 / Aberta | Catálogo, operações e movimentos são consultados integralmente; agrupamentos/filtros ocorrem em memória em diversos pontos | Inventariar consultas e payloads; planejar filtros, consultas por origem e paginação das listagens que precisarem | Contratos de consulta definidos, medição antes/depois e jornadas preservadas; cálculos internos continuam recebendo o histórico completo necessário |
| ARQ-05 | P2 / Condicional | Navegação continua em contexto/pilha local. `frontend/src/app/nav.tsx` | Decidir se URL por tela, deep links, refresh com contexto e histórico do navegador são necessidades do uso real | Decisão explícita de manter a navegação atual ou especificação/testes da evolução; troca de roteador não é pré-requisito técnico automático |

Snapshots/checkpoints, projeções incrementais, cache ou alteração da trava só entram em um plano de implementação se ARQ-01–03 demonstrarem necessidade. Qualquer alternativa deve manter correções retroativas, custo desconhecido, ordenação histórica, assinatura de prévia e idempotência. A modularização entregue não autoriza enfraquecer essas garantias.

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
| OPS-01 | P0 / Aberta | Definir e comprovar backup/restauração de banco e fotos | RPO/RTO acordados, frequência, retenção, destino, responsável e restauração ensaiada em ambiente isolado, com conferência de registros e arquivos relacionados |
| OPS-02 | P1 / Aberta | Validar deploy, atualização e recuperação da implantação | Checklist executado em ambiente apropriado, migrações verificadas, volumes/HTTPS/segredos conferidos e procedimento de recuperação de release sem prometer reversão automática de dados |
| OPS-03 | P1 / Aberta | Instrumentar o suficiente para avaliar as pendências de desempenho e diagnosticar falhas | Evidência de duração de requests/replay, espera de locks, erros e disponibilidade; sinais sem senha, token ou payload sensível nos logs |
| VER-01 | P1 / Aberta | Consultar o resultado remoto do pipeline do commit enviado | Execução correspondente ao SHA, resultado dos jobs e artefatos relevantes; investigar divergências do ambiente local se houver |

[Deploy](DEPLOY.md) descreve a topologia e os volumes. Ter volumes persistentes e um health endpoint não comprova que existe backup restaurável, monitoramento ou prontidão operacional. Esses itens são infraestrutura; não criam funcionalidades de exportação, caixa ou gestão financeira na interface.

## Ordem recomendada para as próximas tarefas

1. Confirmar VER-01 e estabelecer o ambiente/dados de diagnóstico. Se o sistema já sustentar registros reais, tratar OPS-01 imediatamente em paralelo ao planejamento.
2. Definir limites esperados de uso e cenários de teste; levantar consultas, volumes, payloads e invariantes (ARQ-01–04 e BD-01–03/07–08).
3. Medir replay, correções retroativas, gestão concorrente e tempo de espera de gravações. Registrar a configuração usada e resultados comparáveis.
4. Fechar decisões de Arquitetura e Banco com alternativas, justificativa e critérios de aceite. Avaliar UUID/JSONB/normalização/navegação apenas onde houver valor demonstrável.
5. Produzir o próximo plano de execução em fatias verificáveis. Se houver migração de dados, definir validação, tratamento de registros incompatíveis, backup e recuperação antes da aplicação.
6. Executar as melhorias aprovadas, repetir os gates de Código e acrescentar testes/medições específicos da mudança. Atualizar este registro com as evidências.

Não há estimativa de prazo ou promessa de capacidade antes do diagnóstico. O banco operacional não deve ser alterado para testar; a primeira rodada de medidas deve usar `lgd_mantos_alignment_test` e dados sintéticos representativos. Qualquer necessidade de inspeção de produção deve ser definida explicitamente, com escopo de leitura e proteção dos dados.

## Manutenção do registro

Cada item só muda para concluído com referência à decisão e à sua verificação. Uma decisão fundamentada de manter a solução atual pode encerrar uma investigação; uma implementação necessária não pode ser encerrada apenas com um documento de intenção. Novos defeitos de Código devem receber itens próprios, sem reabrir genericamente C0–C8 nem apagar o histórico da entrega.

Este documento substitui a lista informal de pendências da avaliação anterior. [Plano de Código](PLANO_MELHORIAS_CODIGO.md) e [resultado de Código](QUALIDADE_CODIGO_RESULTADO.md) permanecem como registro da etapa concluída; [Alinhamento implementado](ALINHAMENTO_IMPLEMENTADO.md) continua descrevendo os contratos em vigor.
