# Contexto do LGD Mantos

A fonte normativa é `docs/PRODUTO_E_OBJETIVO.md`. Consulte também
`docs/ALINHAMENTO_IMPLEMENTADO.md` para contratos, decisões técnicas e testes.
O registro central de pendências é `docs/QUALIDADE_SITUACAO_ATUAL.md`.
Código (C0–C8) e a implementação da arquitetura de aplicação estão verificados;
as próximas decisões são de Banco, perfil real de capacidade e preparação operacional.
Atualize os itens com evidência ao avançar e não trate
alternativas condicionais (UUID, JSONB, checkpoints ou roteador) como mudanças já aprovadas.
O plano de Arquitetura está em `docs/PLANO_MELHORIAS_ARQUITETURA.md` (A0–A9):
execução registrada em `docs/QUALIDADE_ARQUITETURA_RESULTADO.md` e `docs/decisions/`.
Preserve suas garantias transacionais e registre decisões antes de otimizações
condicionais. O plano de Banco continua pendente.

## Estrutura atual

- Backend modular FastAPI/SQLAlchemy em `backend/app/modules`; modelos ORM em `backend/app/shared/models/entities.py`.
- Catálogo, inventário inicial, compras, estoque, vendas e recebimentos.
- Frontend React/TypeScript em `frontend/src/modules`, infraestrutura em `shared` e composição em `app`.
- PostgreSQL 16 e migrações Alembic preservadas em `backend/migrations`.
- Acesso único do dono; gestão baseada em evidências dos registros operacionais.

## Regras de manutenção

- Não reintroduzir despesas, DRE, lucro líquido, metas, taxas, exportações,
  marketing, motores de agentes ou integrações externas sem nova decisão de produto.
- Saldo só muda por inventário, compra, venda ou ajuste; nunca pelo cadastro.
- Dinheiro usa Decimal no backend; ausência de custo ou preço não significa zero.
- Correções exigem motivo, prévia de impacto, confirmação e histórico preservado.
- Comentários e docstrings devem ser explicativos e em português.
- Não versionar segredos, dependências instaladas, grafos, caches ou builds.
- Não alterar o banco operacional para testar. Use apenas o banco isolado
  `lgd_mantos_alignment_test`, conforme as instruções do README.
- Nunca executar limpeza de dados no startup ou como manutenção rotineira.
- Cada cadastro auxiliar tem contratos e entradas próprios; compartilhar apenas mecânica comum.
- Rotas não contêm SQL, commit, disco ou regras de negócio. Serviços de aplicação usam erros próprios.
- O ledger permanece puro e a confirmação de operações permanece uma única transação.
- Catálogo/Gestão usam snapshot read-only; Gestão encerra a sessão antes do cálculo puro. Nunca compartilhar a sessão com a thread de cálculo.
- Imports entre capacidades backend passam por `public.py` conforme a matriz de `check_boundaries.py`; compartilhado frontend não importa módulos de negócio.
- Em produção, aplicar migrações com API parada antes de iniciar a release; imagem não migra no startup.
- Reconciliação de fotos é somente leitura. Commit incerto exige prova de ausência de referência antes de remover arquivo.
- Consumir interfaces públicas (`api`, `contracts`, `index`) ao cruzar módulos frontend; não importar páginas internas.

## Verificação

`python backend/check.py` executa os testes de backend em PostgreSQL isolado.
Execute também `python -m ruff check backend` e `python backend/check_boundaries.py`.
No frontend: `npm run build`, `npm run lint`, `npm run check:boundaries`, `npm test`;
depois da suíte backend, rode a API isolada e `npm run test:e2e`.
O README descreve build, jornada Playwright e execução por Docker Compose.
Com o ambiente Docker ativo, `docker compose exec frontend npm run build`
verifica a interface sem instalar dependências no host.
