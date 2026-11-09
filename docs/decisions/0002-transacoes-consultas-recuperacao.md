# ADR 0002 — Consistência de leitura e recuperação de recursos

Data: 2026-11-09. Estado: implementado e verificado. Relaciona A1/A3–A7/A9.

## Leituras e comandos

Manter serialização exclusiva global em prévias e mutações. A confirmação depende da revisão global, de várias variantes e do recálculo de acontecimentos posteriores; reduzir a trava por variante exigiria outra prova de consistência. Prévia continua sem reservar saldo. Timeout de espera é um erro recuperável, não permissão para remover validação ou gerar outra chave idempotente.

Catálogo e Gestão usam sessão própria por request, com `SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY` antes da primeira consulta. O objetivo é uma única base para consultas compostas sem bloquear escritores por advisory lock. Esse nível mantém o snapshot entre consultas conforme a [documentação do PostgreSQL 16](https://www.postgresql.org/docs/16/transaction-iso.html). Não aplicar esse nível aos comandos já serializados sem nova análise.

Gestão materializa dicionários, nomes e revisão antes de encerrar a transação; replay e cálculos rodam em thread com valores, sem sessão ORM. Comandos podem executar apenas o replay puro em thread, mantendo a transação na coroutine original. A sessão não é compartilhada entre tarefas, em conformidade com o [contrato de concorrência do SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks). Thread libera o event loop de execução direta do cálculo, mas não cria paralelismo ilimitado de CPU nem elimina o GIL.

Mutações usuais fazem um commit na dependência de sessão; erro desfaz a transação. Fotos fazem commit explícito porque há efeitos posteriores no disco; o commit final da dependência não acrescenta mutação. Não há commit intermediário no núcleo de operações. Cancelamento desfaz o estado não confirmado; replay em thread é puro e não grava após cancelamento.

## Consultas e capacidade

Separar consultas completas internas do replay de consultas paginadas de apresentação. Totais gerenciais sempre usam a base inteira; detalhes usam páginas e mantêm vínculo de origem. A API antiga integral continua disponível para compatibilidade, sem alegar que seu payload foi limitado. Gestão não mantém snapshot entre páginas: revisão explícita e substituição da página evitam apresentar soma parcial como total.

Modelos ORM compartilhados permanecem: mover tabelas ou normalizar documentos não é necessário para essa decisão. Leitura de operações usa mappings sem instanciação de entidades; correção carrega dependentes em lotes. Não adicionar índices/JSONB sem avaliação de Banco.

Resultados em 50 mil registros mostram limites em prévia, contenção e correções extensas. Manter replay completo com os limites publicados, acompanhando o perfil real em ARQ-11. Checkpoints e projeções assíncronas permanecem alternativas, não requisito oculto de conclusão desta implementação.

## Arquivos e recuperação

Arquivo novo é publicado por escrita temporária, flush/fsync e replace no mesmo diretório. Só depois os metadados são confirmados. Na substituição, conservar ID e metadados e usar nome derivado de ID/conteúdo: repetição imediata da mesma tentativa é segura. Arquivo antigo só é removido depois do commit.

Falha de commit pode ter resultado incerto. Compensação primeiro faz rollback e retoma a trava global; só apaga o novo arquivo se uma consulta provar que não há referência. Sem conexão/prova, manter arquivo e emitir evento de reconciliação. Falha de limpeza após commit é observável, sem transformar sucesso confirmado em erro que induza repetição.

Interrupção do processo pode deixar arquivo órfão; banco e disco não são transação distribuída. A ferramenta `reconcile_photos.py` apenas relata órfãos/ausentes e não segue links nem remove dados. A publicação atômica protege contra arquivo parcialmente visível durante interrupção de escrita, mas não promete durabilidade absoluta do filesystem diante de falha física.

Backup exige parar a única API escritora e impedir escritores administrativos durante toda a captura. Capturar dump e fotos, registrar imagem, hashes e contagens; reiniciar só após sucesso ou decisão operacional sobre falha. O script deixa marcador INCOMPLETE e não reinicia serviços automaticamente. Cópia fora do host e retenção são tarefas operacionais explícitas.

Migração de produção passa a comando administrativo com API parada. Falha de migração impede retomar tráfego. Reverter imagem não reverte dados/schema; restauração implica considerar os registros criados depois do backup. O ensaio sintético prova o mecanismo disponível, não a política ou o backup da implantação real.

## Verificação e reconsideração

Testes e medidas estão no [resultado](../QUALIDADE_ARQUITETURA_RESULTADO.md). Reavaliar quando houver volume real, várias sessões concorrentes, consumidor externo ou necessidade concreta de deep links; mudanças exigem novos critérios de equivalência/compatibilidade. OPS permanece aberto até ensaio e configuração na implantação real.
