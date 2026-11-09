# Resultado da execução — Arquitetura

Data: 2026-11-09. Base: `f67c59e`; implementação e evidências pertencem ao commit que versiona esta entrega.

Fonte: [Plano A0–A9](PLANO_MELHORIAS_ARQUITETURA.md). Decisões: [ADR 0001](decisions/0001-arquitetura-monolito.md) e [ADR 0002](decisions/0002-transacoes-consultas-recuperacao.md). Pendências: [registro central](QUALIDADE_SITUACAO_ATUAL.md).

## Entrega e limites

A arquitetura de aplicação foi implementada e verificada mantendo o monólito modular, as nove tabelas e a migração `0006`. Leituras compostas usam snapshot repetível sem advisory lock de gravação; confirmações preservam serialização global e transação única. Consultas da interface foram recortadas/paginadas; replay permanece integral. A prontidão operacional da implantação real continua pendente.

O dono informou não ter estimativa de volume. Os cenários de 1 mil/10 mil/50 mil operações e 10/100/500 variantes são hipóteses de investigação. Não há SLA ou promessa de capacidade em produção. O cenário de 50 mil operações evidenciou limites que permanecem explícitos abaixo; não foi declarado atendimento irrestrito às metas.

| Etapa | Entrega e evidência | Situação |
|---|---|---|
| A0 | Pipeline baseline consultado; 64 testes originais passaram; gerador e medidas em três escalas | Concluída com hipóteses, sem perfil real informado |
| A1 | JSON de requests/fases/travas, correlação, limites de espera, prontidão 503, teste de parada/recuperação real do banco sintético | Implementada/verificada; coleta e alertas da implantação continuam em OPS-03 |
| A2 | Interfaces públicas, sessão injetada no transporte, matriz de imports e ciclos backend/frontend com testes | Concluída |
| A3 | Serialização global mantida, commit/rollback explícitos por fluxo, repetição concorrente e timeout real testados | Concluída com limites de contenção registrados |
| A4 | Catálogo e Gestão em snapshot read-only; Gestão materializa valores, encerra transação e calcula fora do event loop | Concluída; testes intercalam escrita entre leituras |
| A5 | Movimentos por origem, produto por ID, operações por cursor, detalhes gerenciais por visão/página, origens acessíveis em lotes na UI | Concluída; contratos completos antigos preservados para compatibilidade |
| A6 | Leitura integral sem instanciar entidades ORM, agrupamento de origens em uma passagem, dependentes de correções carregados em lotes | Investigação encerrada mantendo replay completo; metas excedidas em cargas extensas registradas |
| A7 | Substituição no mesmo ID via backend, repetição por conteúdo, publicação atômica do arquivo, compensação com conferência de referência, reconciliação read-only | Implementada/verificada, inclusive falha de commit e interrupção injetada |
| A8 | Navegação local/JWT mantidos com limitações explícitas; proteção de tentativas de login; expiração/401 e recuperação testadas | Decisões registradas; sem troca de roteador, cookies ou multiusuário |
| A9 | Migração administrativa separada, imagem construída, backup e restauração ensaiados com dados sintéticos, instruções de release/recuperação | Ferramentas e ensaio concluídos; comprovação no servidor e política operacional real pendentes |

## Medidas reproduzíveis

Arquivos: [baseline](architecture-baseline.json) e [resultado](architecture-after.json). Executor: [architecture_benchmark.py](../backend/architecture_benchmark.py). Python 3.11.9 no Windows, PostgreSQL 16.15 no Docker Desktop, 14 CPUs lógicas reportadas pelo host, sem limites exclusivos de CPU/RAM e sem isolamento dos outros projetos do computador. Validação funcional final adicional no Python 3.12 Linux.

Cada consulta/prévia tem um aquecimento e três amostras; p95 usa o maior valor dessas três amostras. Confirmações novas e correção com propagação têm uma amostra, identificada como tal. Tempos são HTTP em processo via ASGITransport: não incluem rede, TLS ou renderização. `replay_peak_mib` mede somente alocações rastreadas do replay, não memória total da requisição; o rastreamento deixa esse replay mais lento que as chamadas sem rastreamento. Medidas são exploratórias, não teste de carga sustentada.

| Operações | Gestão antes p95 | Visão geral depois p95 | Payload antes → depois | Prévia depois p95 | Confirmação nova depois, 1 amostra |
|---|---:|---:|---|---:|---:|
| 1.000 | 183,58 ms | 43,16 ms | 2.587.731 → 12.369 bytes | 62,43 ms | 60,64 ms |
| 10.000 | 2.209,00 ms | 574,47 ms | 25.962.176 → 114.804 bytes | 503,54 ms | 438,50 ms |
| 50.000 | 21.071,41 ms | 2.944,83 ms | 130.149.763 → 570.813 bytes | 2.571,65 ms | 2.381,67 ms |

A comparação representa o trabalho necessário para abrir a interface: a baseline enviava todas as coleções; a visão nova preserva totais integrais e envia apenas os detalhes apropriados. Não é o mesmo corpo JSON serializado mais rápido. O endpoint sem `view` mantém o contrato completo e pode continuar produzindo respostas grandes; a interface usa `view`. Em 50 mil operações, a visão de vendas paginada ainda envia cerca de 5 MB porque preserva todas as origens dos agrupamentos.

A página de operações com até 50 vendas passou a 9,77 ms p95 e 84.151 bytes na maior escala; a coleção completa anterior tinha 75.225.275 bytes e 6.482,63 ms p95. O catálogo de 500 variantes permaneceu pequeno (152.425 bytes); não foi imposta paginação aos seletores de cadastro. A origem de movimentos foi medida sobre poucos movimentos e sua correção de filtro foi verificada em integração; não alegar benchmark de milhões de movimentos.

### Limites observados e decisão

- Em 10 mil operações, operações usuais ficaram abaixo das metas exploratórias de 1/2/5 segundos. Quatro prévias simultâneas retornaram 200, com a mais lenta em 1,79 s.
- Corrigir todos os custos do inventário e recalcular 5 mil resultados posteriores levou 5,48 s em uma confirmação; na escala de 50 mil, 25 mil impactos levaram 29,16 s e geraram resposta de 38,68 MB. Não é uma operação usual nem atende à meta original de cinco segundos. A UI mostra espera e permite percorrer os impactos em lotes, sem alterar o resultado nem cortar a revisão enviada pelo backend.
- Na escala de 50 mil, prévia/confirmação usuais ultrapassaram dois segundos. Quatro prévias concorrentes produziram três 200 e um 503 por limite de espera da trava; a mais lenta bem-sucedida levou 7,52 s. Esse cenário não atende à meta sob concorrência. O erro é visível e pode ser repetido, sem efeitos parciais ou repetição automática.
- Não foi introduzido checkpoint: não há necessidade real de volume informada, e correções arbitrárias exigem invalidação/equivalência adicionais. Replay e recálculo continuam custando proporcionalmente ao histórico e aos impactos. Antes de depender de 50 mil registros com várias abas ou correções extensas frequentes, retomar ARQ-11 com perfil real; limites não são um teto rígido de registros imposto pela aplicação.

Para repetir, configurar `TEST_DATABASE_URL` para a base isolada e executar, sem pytest/E2E concorrentes:

```sh
python backend/architecture_benchmark.py --replace-test-data lgd_mantos_alignment_test --presentation --impact --label architecture --output resultado.json
```

O script substitui somente os dados do banco `lgd_mantos_alignment_test`, após confirmação literal. A baseline foi medida antes das alterações, sem os parâmetros novos. Correções antigas/meio/fim originais eram alterações sem mudança de quantidade/custo; o caso `correction_cost_*` adicional muda efetivamente os custos e mede propagação. Não confundir esses cenários.

## Contratos implementados

- `GET /products/{id}` consulta somente o produto. Listagem e detalhe usam snapshot coerente de produto/variantes/fotos; cadastro continua sem alterar saldo.
- `GET /operations?kind=sale&limit=50&before_sequence=N` retorna lista em sequência decrescente. Cursor exclusivo/imutável evita duplicação por inserções mais recentes; correções preservam sequência. Sem parâmetros, o contrato integral anterior permanece.
- `GET /movements?operation_id=ID` filtra no servidor e ordena por criação/ID. Sem parâmetro, preserva a listagem anterior.
- `GET /analytics?view=overview|stock|sales|receipts|purchases|buying&offset=0&limit=50` mantém totais integrais e retorna metadados de página/revisão. Fornecedor e ordenação de estoque são aplicados antes de paginar. Cada resposta é coerente; páginas sucessivas consultam a base atual, sem snapshot persistido entre requests. A UI substitui a página e informa essa limitação, sem concatenar resultados de revisões diferentes.
- Limite de página entre 1 e 100; offset não negativo; kind/view/sort inválidos são recusados. Seletores do formulário continuam indicativos, com validação na prévia/confirmação.
- `PUT /photos/{id}/content` troca o arquivo mantendo identidade, ordem, destaque e vínculos. Mesmo conteúdo/ID repetido não gera nova foto/auditoria/revisão; outra substituição concorrente segue a ordem serializada. Não é um recibo de operações nem promessa de repetir uma intenção antiga sobre alterações posteriores.
- `GET /api/v1/health` retorna 200 quando banco responde e 503 com `status=error` quando indisponível. `/` é vivacidade HTTP. Timeout de trava/statement/pool gera 503 recuperável; corpo/Idempotency-Key não são repetidos automaticamente. Tentativas excessivas de login geram 429, com janela local por processo.

## Recuperação e implantação

A imagem de produção não executa migrações no startup. Compose oferece `migrate` administrativo e healthcheck do backend; a borda depende de prontidão inicial. Desenvolvimento conserva migração no comando de reload. A sequência de atualização está em [Deploy](DEPLOY.md).

Ensaio local: imagem Python 3.12 construída, migração completa até `0006` em base vazia, fixture com inventário, compra, venda parcial, correção retroativa e foto. API parada para capturar banco/arquivos; hashes SHA-256 e contagens no manifesto. Restauração em outro PostgreSQL vazio, explicitamente rotulado `restore-drill`, usando somente a base de testes. Extração recusa caminhos inseguros/links e destino existente.

Resultado: 3 operações, 12 revisões, 3 movimentos, 4 recibos, 1 foto, 1 produto, 1 variante, 4 auxiliares e 1 controle restaurados. Restore/check de arquivos levou 1,76 s nesse conjunto pequeno, excluindo provisionamento e verificação posterior: isso não é RTO de produção. A conferência posterior reproduziu os três resultados, verificou projeção/movimentos, os quatro recibos e o conteúdo da foto. Reinício preservou estoque 3 e pendência `35.00`. Parada real do banco produziu prontidão 503 e vivacidade 200; reinício recuperou prontidão 200.

Não houve deploy no servidor real, validação de DNS/certificados, configuração de agendamento externo, destino de backup fora do host, retenção ou acordo de RPO/RTO. Esses requisitos continuam em OPS-01/02/03. Arquivos sintéticos locais não são backup dos dados operacionais. Não há restauração automática nem limpeza de fotos no startup; reconciliação é somente inventário administrativo de leitura.

## Verificação final

- **84 testes backend passaram** no Python 3.12 Linux/PostgreSQL isolado; incluem venda concorrente, recibo simultâneo, snapshots, timeout real, compensação de commit, interrupção, revisão do schema e segurança dos scripts. Houve um aviso de depreciação do Alembic sobre `path_separator`, sem falha de migração/teste.
- **19 testes frontend passaram**, além de TypeScript/Vite, ESLint e gates de fronteiras/ciclos.
- **Cinco jornadas Playwright passaram**: fluxo completo e seis visões, prévia obsoleta, resposta de operação perdida, falha de movimentos e substituição de foto com resposta perdida.
- Ruff e fronteiras backend passaram; migração continua `0006`; nenhum ajuste de schema foi introduzido.
- Baseline remota: [execução 42282745014](https://github.com/LucasGS520/LGD-Mantos/actions/runs/42282745014), SHA `f67c59e8bc737e4fd3afb01c4599d53f0854c9bf`, job `verify` bem-sucedido. O pipeline desta entrega deve ser conferido pelo SHA de publicação; a baseline não comprova seu resultado remoto.

Os testes verificam a arquitetura entregue, não ausência de defeitos futuros ou disponibilidade de produção. Alterações de Banco permanecem na próxima dimensão, com as dependências e os limites descritos no registro central.

Os containers, volumes sintéticos, rede e imagens identificadas do ensaio foram
removidos ao encerrar a execução. Outras stacks foram preservadas. Medidas JSON
permanecem versionáveis em `docs`; cópia sintética local em `.verification/` é
ignorada pelo Git. Uma nova verificação exige preparar novamente o PostgreSQL isolado.
