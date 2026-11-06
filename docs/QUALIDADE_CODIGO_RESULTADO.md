# Resultado — qualidade do código

Data: 2026-11-06. Escopo: C0–C8 do [plano de melhorias](PLANO_MELHORIAS_CODIGO.md).

Este documento preserva as evidências da entrega concluída no commit `6d8b98c`.
As pendências ainda abertas são mantidas no [registro central de qualidade e situação atual](QUALIDADE_SITUACAO_ATUAL.md).

## Entregas e evidências

| Etapa | Resultado implementado | Evidência no repositório |
|---|---|---|
| C0 | Baseline executável recuperada sem sobrescrever os dois caminhos de testes excluídos no início | `backend/tests/integration/conftest.py`, `test_operation_contracts.py`; baseline original de 35 testes passou antes da extração |
| C1 | Proteção de regras, contratos e falhas transacionais | `backend/tests/unit/`, `backend/tests/integration/test_http_contract.py`, `test_failure_recovery.py` |
| C2 | Transporte, erros, formatos, sessão, DTOs e endpoints separados | `frontend/src/shared/api`, `shared/format`, `modules/*/contracts.ts`, `modules/*/api.ts` |
| C3 | Cinco cadastros auxiliares independentes; produto e variante separados | Diretórios próprios em `modules/auxiliaries` no backend/frontend; `catalog/products.py`, `variants.py` e formulários próprios |
| C4 | Fotos com casos de uso, contrato de armazenamento e adaptador local | `backend/app/modules/photos/service.py`, `storage.py`, `infrastructure/local_storage.py`; ação frontend `photos/actions/replace.ts` |
| C5 | Operações com políticas por tipo, preparação, pagamentos, assinatura e confirmação compartilhada | `backend/app/modules/operations`; `frontend/src/modules/operations/flows`, `hooks`, `model` e `components` |
| C6 | Gestão, histórico e UI genérica decompostos | Seis arquivos em `frontend/src/modules/management/views`; cálculos puros em `backend/app/modules/management/calculations`; `modules/history`; componentes próprios em `shared/ui` |
| C7 | Falhas recuperáveis, prévia obsoleta, retry idempotente, formulário preservado e carga coerente | Testes de `useData`, `useOperationEditor`, cinco formulários auxiliares e jornadas `operation.spec.ts`/`recovery.spec.ts` |
| C8 | Verificação automatizada e documentação atualizadas | `pyproject.toml`, `backend/check_boundaries.py`, `frontend/eslint.config.mjs`, `frontend/scripts/check-boundaries.mjs`, `.github/workflows/verify.yml`, README e matriz de alinhamento |

## Organização resultante

O backend é um monólito modular. Cada capacidade possui sua borda HTTP e seus casos de uso; persistência fica em repositórios e armazenamento de arquivos em adaptador próprio. Erros de aplicação são traduzidos para o formato HTTP existente em `backend/main.py`. Autenticação e disponibilidade também delegam sua lógica aos serviços; nenhuma rota executa SQL, commit ou manipulação física de arquivo.

Auxiliares é apenas um agrupamento. Fornecedores, categorias, canais de compra, canais de venda e formas de pagamento possuem contratos e entradas específicos, com testes próprios. O endpoint `/auxiliaries` continua despachando pela capacidade, preservando compatibilidade. Normalização, controle de versão, campos comuns e persistência idêntica são compartilhados, sem condicionais comerciais das cinco capacidades no helper. Os contratos frontend também fixam o tipo de cada cadastro.

O frontend está organizado por capacidade em `src/modules`, composição em `src/app` e recursos técnicos em `src/shared`. Os antigos arquivos `Operations.tsx`, `Catalog.tsx`, `Management.tsx`, `Shared.tsx`, `services/domain.ts` e o agrupamento `components/UI.tsx` foram substituídos por responsabilidades próprias. Componentes genéricos sem consumidores no código anterior foram removidos junto ao agrupamento; o histórico Git permite recuperá-los. Não foi mantida uma fachada para os módulos antigos.

Inventário, compra, venda e ajuste têm arquivos próprios de política e composição visual. Pagamentos têm preparação e transformações próprias, mas continuam pertencendo à venda. O replay e a confirmação transacional continuam únicos. As interfaces `public.py` no backend e `api`/`contracts`/`index` no frontend explicitam os pontos de colaboração entre módulos.

## Verificação executada

| Verificação | Resultado |
|---|---|
| Backend completo em Python 3.12/Linux, PostgreSQL 16 exclusivo de testes | 64 testes passaram: 45 de integração/contrato e 19 unitários |
| Testes unitários sem banco, configuração ou `.env` | 19 testes passaram |
| Frontend, Vitest/React Testing Library | 16 testes passaram em nove arquivos |
| Playwright/Chromium, viewport móvel 390 × 844 | Quatro jornadas passaram e o processo terminou com código zero |
| TypeScript e Vite | Build passou |
| Ruff e ESLint com regras de hooks | Passaram |
| Fronteiras de backend e imports/ciclos de frontend | Passaram |
| Dependências frontend instaladas, `npm audit` | Nenhuma vulnerabilidade reportada nesta execução |
| `git diff --check` | Sem erros de whitespace |

O PostgreSQL usado foi criado exclusivamente para esta verificação, com banco `lgd_mantos_alignment_test`. Nenhuma verificação utilizou a base operacional. A instalação inicial percorreu a cadeia Alembic até 0006; os testes conferem as nove tabelas ativas. As migrações de versões não foram alteradas e o schema permanece compatível. A verificação no Python 3.12 foi executada localmente em Docker; o workflow GitHub foi atualizado, mas não foi disparado remotamente nesta tarefa.

Os testes de contrato verificam os 24 pares de método/path públicos já existentes, autenticação dos endpoints operacionais, cabeçalho de idempotência e contratos estritos. Login e disponibilidade mantêm seus endpoints públicos. Os testes HTTP preservam os valores de dinheiro, saldos, histórico e snapshots; não substituem valores desconhecidos por zero.

Os testes transacionais provocam falha de commit para comprovar rollback de operações, movimentos, revisões, projeções e recibo idempotente; a mesma chave pode ser confirmada após o rollback. Para fotos, falha de commit remove o arquivo novo. Falha na remoção física depois do commit não torna a foto excluída acessível novamente. A substituição conserva a foto antiga até salvar e organizar a nova.

As jornadas de navegador cobrem:

1. Catálogo, inventário, compra com cadastro inline e falha/recuperação de fontes sem perder fornecedor ou custo digitado; venda parcial, recebimento, histórico e valores/origens nas seis visões de gestão.
2. Prévia obsoleta: preserva os campos, remove a confirmação antiga e exige nova revisão humana.
3. Resposta interrompida depois do commit: repete chave e conteúdo, retorna a mesma venda e baixa estoque somente uma vez.
4. Movimentos indisponíveis: mostra a falha na seção e permite recuperar os dados por nova tentativa.

## Ajustes do ambiente de verificação

Windows/OneDrive bloqueou a limpeza de resultados e cache de execuções anteriores. Playwright e Vite agora usam diretórios de resultado/cache específicos por execução. Traces ficam desligados por padrão no Windows porque seu encerramento bloqueou a execução local; `E2E_TRACE=1` permite ativá-los. No CI Linux, traces de falha continuam habilitados. A jornada captura sua imagem na pasta de resultados da própria execução.

Vitest, Testing Library, ESLint, Ruff e Prettier foram adicionados como ferramentas de desenvolvimento. O override de `minimatch` no parser do lint fixa uma faixa corrigida; lint, build e testes passaram com essa resolução. Nenhuma nova dependência de runtime foi adicionada.

## Fechamento e limites

Todos os quatro achados da dimensão Código possuem implementação e evidência de verificação. As cinco melhorias funcionais escolhidas no plano estão incluídas. README, instruções de manutenção e matriz de alinhamento refletem os caminhos e comandos novos.

Permanecem para as próximas dimensões as decisões sobre volume do replay, serialização global, paginação, modelagem JSON, UUIDs, índices, constraints e operação do banco. As investigações, prioridades e critérios de encerramento estão em `QUALIDADE_SITUACAO_ATUAL.md`, itens ARQ, BD e OPS. Esta entrega não modifica essas decisões nem constitui uma medição de desempenho em produção. O código está pronto para a avaliação seguinte de arquitetura e banco, com sua base modular e os gates de regressão estabelecidos.
