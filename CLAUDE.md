# Contexto de manutenção

- Monólito modular FastAPI/React, PostgreSQL 16, 15 tabelas e baseline independente 0007.
- Backend em `app/modules`; ORM por responsabilidade em `app/shared/models`.
  Metadata independente de autenticação; payload reconstruído do núcleo relacional.
- Frontend em `src/modules`, infraestrutura em `src/shared`, composição em `src/app`.
- Acesso único do dono. Respeitar fronteiras do produto, sem acrescentar capacidades
  externas ou financeiras por inferência.
- Ledger puro; confirmação em uma transação; preservar motivo, prévia, revisão,
  auditoria, idempotência e custo desconhecido distinto de zero.
- Rotas não executam SQL, commit ou disco. Colaborações backend usam `public.py`;
  frontend usa `api`/`contracts`/`index`. Preservar gates de fronteiras/ciclos.
- Catálogo/Gestão usam snapshot read-only. Gestão encerra a sessão antes do cálculo
  puro; não compartilhar sessão ORM com threads.
- API usa `lgd_app`, migração `lgd_migrator`. Não entregar segredos administrativos à API.
- Migração/reconstrução é administrativa, com escritores parados; nunca limpar no startup.
- Ensaios usam somente `lgd_mantos_alignment_test`; nunca testar no banco operacional.
- Compensação de foto em commit incerto exige provar ausência de referência antes de apagar.
- Comentários/docstrings explicativos em português. Não versionar segredos, uploads,
  dependências, caches, builds, grafos, logs ou saídas brutas de ensaios.
- Atualizar as cinco referências ativas, sem recriar planos/relatórios concluídos.

Verificação e variáveis estão no [README](README.md). Rodar gates proporcionais
à alteração; dados operacionais e testes com banco exigem os procedimentos descritos.
