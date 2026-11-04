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
- `backend/app/domain`: modelos, contratos, regras, consultas e reprodução do histórico.
- `frontend/src/screens/workspace/`: telas separadas por responsabilidade e componentes compartilhados.
- [Matriz de alinhamento](docs/ALINHAMENTO_IMPLEMENTADO.md): regras e critérios de verificação.

## Ambiente local

Preencha `.env` a partir de `.env.example`: `DATABASE_URL`, `POSTGRES_PASSWORD`,
`APP_PASSWORD` e `APP_SECRET`. No Docker, use host `db` na conexão PostgreSQL.
Nenhum segredo tem padrão de produção.

```sh
docker compose up -d --build
```

Interface: `http://localhost:5173`. API: `http://localhost:8000/api/v1`.
Documentação técnica HTTP: `http://localhost:8000/api/docs`.

As dependências do frontend ficam no volume Docker `frontend_node_modules`,
separadas dos arquivos locais e dos dados persistentes da loja.

O startup aplica migrações pendentes; não apaga operações e não cria inventário.
A migração 0006 cria o núcleo novo sem converter nem apagar registros legados.

## Verificação

As credenciais do banco de verificação vêm de `TEST_DATABASE_URL` ou de `.env`,
sempre com banco `lgd_mantos_alignment_test`. Nenhum teste usa a base operacional.

```sh
docker exec lgd_db psql -U postgres -d postgres -c "CREATE DATABASE lgd_mantos_alignment_test"
python -m pip install -r backend/requirements-dev.txt
python backend/check.py
cd frontend
npm ci
npm run build
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

## Limpeza para início real

A limpeza autorizada é administrativa, irreversível e separada da aplicação.
Pare o backend; aplique as migrações em um processo administrativo e execute:

```sh
docker compose stop backend
docker compose run --rm --no-deps backend python init_db.py
docker compose run --rm --no-deps backend python reset_operation.py --database lgd_mantos --host db --confirm "LIMPAR lgd_mantos"
docker compose up -d backend
```

O procedimento confere banco, host e tabelas reconhecidas; limpa os registros e
fotos associadas do projeto. Não confirma o inventário: o dono deve informar o
estoque físico conhecido. Não use esse procedimento como manutenção rotineira.

Backup, retenção e recuperação pertencem à infraestrutura e não têm fluxo na interface.
Veja [execução em produção](docs/DEPLOY.md). Planos antigos e grafos gerados foram
retirados do versionamento; seu conteúdo anterior permanece no histórico Git.
