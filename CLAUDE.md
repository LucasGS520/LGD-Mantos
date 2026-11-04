# Contexto do LGD Mantos

A fonte normativa é `docs/PRODUTO_E_OBJETIVO.md`. Consulte também
`docs/ALINHAMENTO_IMPLEMENTADO.md` para contratos, decisões técnicas e testes.

## Estrutura atual

- Backend FastAPI e SQLAlchemy assíncrono em `backend/app/domain`.
- Catálogo, inventário inicial, compras, estoque, vendas e recebimentos.
- Frontend React e TypeScript em `frontend/src/screens/workspace`.
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

## Verificação

`python backend/check.py` executa os testes de backend em PostgreSQL isolado.
O README descreve build, jornada Playwright e execução por Docker Compose.
Com o ambiente Docker ativo, `docker compose exec frontend npm run build`
verifica a interface sem instalar dependências no host.
