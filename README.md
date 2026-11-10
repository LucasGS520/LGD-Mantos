# LGD Mantos

Central interna da loja para um único dono: catálogo, inventário, estoque,
compras, vendas, recebimentos e consultas gerenciais. A fonte normativa é
[Produto e objetivo](docs/PRODUTO_E_OBJETIVO.md).

## Funcionamento

1. Organize fornecedores, categorias, canais e formas de pagamento em **Mais**.
2. Cadastre produtos por estampa e variantes por tamanho/cor.
3. Confirme o inventário inicial com as quantidades físicas conhecidas. Custos e
   referências desconhecidos podem ficar ausentes. Inventário vazio é permitido.
4. Registre cada compra, venda, recebimento e ajuste quando acontecer.
5. Consulte os registros e as seis visões de **Gestão**, seguindo os vínculos de origem.

Vendas retiram estoque na confirmação, mesmo sem recebimento. Pagamentos têm valor
e forma próprios. Saldo positivo significa pendência; saldo zero, conclusão financeira.
Preço negociado é informado por item. Desconto é a diferença para a referência.

Correções exigem motivo, revisão do impacto e confirmação. Anulações preservam o
registro e revertem os efeitos. Custo desconhecido nunca significa custo zero.

Não há despesas, DRE, caixa, clientes, taxas, metas, marketing, relatórios exportáveis
ou integrações externas. As consultas acontecem dentro do sistema. Quantidades
recomendadas para compras aguardam uma regra validada com histórico real.

## Stack e organização

- Frontend React 18 / TypeScript / Vite, navegação própria e tokens CSS existentes.
- API FastAPI / Python 3.12, SQLAlchemy assíncrono e PostgreSQL 16.
- Alembic para migrações; Docker Compose para execução.
- `backend/app/modules/`: auxiliares por capacidade, catálogo, fotos, operações, histórico, gestão, autenticação e disponibilidade.
- `backend/app/shared/`: modelos ORM, persistência e regras transversais de auditoria/versão.
- `frontend/src/modules/`: contratos, APIs, páginas, formulários e hooks por capacidade; cada cadastro auxiliar tem arquivos próprios.
- `frontend/src/shared/`: transporte HTTP, erros, formatos, carga segura e componentes genéricos; `src/app/` compõe a navegação.
- [Matriz de alinhamento](docs/ALINHAMENTO_IMPLEMENTADO.md): regras e critérios de verificação.

## Ambiente local

Preencha `.env` a partir de `.env.example`, incluindo as conexões e senhas
separadas de `lgd_app`, `lgd_migrator` e bootstrap, além de `APP_PASSWORD` e
`APP_SECRET`. No Docker, use host `db` na conexão PostgreSQL.
Nenhum segredo tem padrão de produção.

```sh
docker compose build backend migrate bootstrap
docker compose up -d db
docker compose run --rm bootstrap
docker compose run --rm migrate
docker compose up -d backend frontend
```

Interface: `http://localhost:5173`. API: `http://localhost:8000/api/v1`.
Documentação técnica HTTP: `http://localhost:8000/api/docs`.

As dependências do frontend ficam no volume Docker `frontend_node_modules`,
separadas dos arquivos locais e dos dados persistentes da loja.

A migração é administrativa e antecede a API em desenvolvimento e produção,
conforme [Deploy](docs/DEPLOY.md). A baseline independente `0007` instala 15
tabelas de negócio. Bases antigas são recusadas e exigem reconstrução explícita.
A inicialização não apaga dados nem confirma inventário. A API usa `lgd_app`,
sem DDL, TRUNCATE ou alteração de auditoria/recibos.

## Verificação

Defina `TEST_DATABASE_URL` com `lgd_app` e `TEST_MIGRATION_DATABASE_URL` com
`lgd_migrator`, ambas no banco `lgd_mantos_alignment_test`. Provisione esse banco
e suas roles com `bootstrap_database.py`, usando `BOOTSTRAP_DATABASE_URL`
específica do teste. Nenhum teste usa a base operacional.

```sh
docker exec lgd_db psql -U postgres -d postgres -c "CREATE DATABASE lgd_mantos_alignment_test"
python -m pip install -r backend/requirements-dev.txt
python -m ruff check backend
python backend/check_boundaries.py
python backend/check.py
cd frontend
npm ci
npm run build
npm run lint
npm run check:boundaries
npm test
npx playwright install chromium
```

Para a jornada no navegador, primeiro execute na raiz, em um terminal separado:

```sh
python backend/check.py --serve
```

Depois, em `frontend/`, execute `npm run test:e2e`. A suíte usa API na porta 8001,
Vite na 5174 e fotos temporárias. Execute após os testes do backend, sem concorrência
entre suítes: ambas usam o mesmo banco isolado. Antes de repetir a jornada, execute
novamente os testes de backend para limpar seus dados. CI executa essa sequência.

Testes puros ficam em `backend/tests/unit/`; testes HTTP e transacionais ficam em
`backend/tests/integration/`. Para executar só os testes puros, sem banco ou `.env`:
`python -m pytest -c backend/pytest.ini backend/tests/unit`.
Testes de componentes e hooks ficam junto ao módulo (`*.test.tsx`) e usam Vitest.
Resultados e cache de E2E são isolados por execução. No Windows, traces ficam
desativados por padrão; `E2E_TRACE=1` os ativa. CI Linux preserva traces de falha.
A jornada `recovery.spec.ts` verifica prévia obsoleta, resposta interrompida depois
do commit e recuperação de falha parcial. O endpoint público `/health` permanece
sem autenticação; as capacidades operacionais exigem JWT.

As fronteiras são verificadas automaticamente: domínio puro sem HTTP/ORM,
rotas sem SQL/commit/disco, interfaces públicas entre módulos frontend e ausência
de ciclos de imports. Cada módulo oferece sua API própria; regras específicas
não devem voltar a um formulário ou serviço universal.

Veja o [plano executado](docs/PLANO_MELHORIAS_CODIGO.md) e o
[registro de verificação](docs/QUALIDADE_CODIGO_RESULTADO.md).

## Qualidade e situação atual

A dimensão Código teve o plano C0–C8 implementado e verificado. A arquitetura
de aplicação também foi implementada e verificada. As próximas
pendências estão no [registro central de qualidade](docs/QUALIDADE_SITUACAO_ATUAL.md):
acompanhamento de capacidade real e preparação operacional. A dimensão Banco
foi implementada conforme o [plano B0–B6](docs/PLANO_MELHORIAS_BANCO.md) e o
[resultado verificado](docs/QUALIDADE_BANCO_RESULTADO.md). O registro distingue investigações
obrigatórias de mudanças condicionadas a medição ou decisão, com prioridades,
fontes no código e critérios de encerramento. A conclusão de Código não equivale
a uma validação de capacidade ou disponibilidade em produção.

O [plano de Arquitetura](docs/PLANO_MELHORIAS_ARQUITETURA.md) descreve o desenho
e as etapas A0–A9. O [resultado da execução](docs/QUALIDADE_ARQUITETURA_RESULTADO.md)
registra mudanças, decisões, medidas em três escalas, testes e ensaio de backup/restauração.
O monólito modular foi preservado. Há limites medidos para correções extensas e
concorrência em 50 mil registros; backup externo, RPO/RTO e implantação real
continuam pendentes. O resultado local não comprova prontidão de produção.

## Limpeza para início real

A limpeza autorizada é administrativa, irreversível e separada da aplicação.
Pare o backend e todos os escritores. Confira as conexões do `.env`, execute o
bootstrap de permissões e reconstrua o destino explicitamente:

```sh
docker compose stop backend
docker compose run --rm bootstrap
docker compose run --rm migrate python reset_operation.py --database lgd_mantos --host db --confirm "RECRIAR lgd_mantos"
docker compose run --rm migrate
docker compose up -d backend
```

O procedimento confere banco e host, recusa sessões ativas da API e remove o
schema `public` LGD e seus arquivos gerenciados de fotos. Não confirma o inventário: o dono deve informar o
estoque físico conhecido. Não use esse procedimento como manutenção rotineira.

Backup, retenção e recuperação pertencem à infraestrutura e não têm fluxo na interface.
Veja [execução em produção](docs/DEPLOY.md). Planos antigos e grafos gerados foram
retirados do versionamento; seu conteúdo anterior permanece no histórico Git.
