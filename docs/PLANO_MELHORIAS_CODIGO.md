# Plano de melhorias — dimensão Código

Data: 2026-11-06. Status: executado e verificado (C0–C8).

Registro da implementação, testes e diferenças entre a árvore proposta e a organização final: [Resultado da qualidade do código](QUALIDADE_CODIGO_RESULTADO.md).

Fonte de produto: `PRODUTO_E_OBJETIVO.md`. Contratos preservados: `ALINHAMENTO_IMPLEMENTADO.md`.

## Resultado esperado e limites

Evoluir a base atual para um monólito modular, com organização por capacidade de negócio e separação explícita entre interface, aplicação, domínio e infraestrutura. Este documento preserva o plano aprovado; as fatias descritas abaixo foram implementadas e verificadas.

As três frentes são: estabilizar o comportamento existente; melhorar organização, contratos e testabilidade; evoluir a experiência dos fluxos existentes com recuperação de falhas e revisão segura. As cinco melhorias funcionais foram incluídas na execução autorizada deste plano.

Esta rodada não inclui mudanças de schema, normalização de itens/pagamentos, UUID/JSONB, novos índices, substituição do replay, alteração das travas, novo roteador, integrações ou módulos comerciais. Esses temas pertencem às avaliações posteriores de arquitetura e banco. A organização do código muda, mas as decisões transacionais e regras de negócio vigentes permanecem.

## Evidências e linha de base

| Evidência no worktree | Implicação para o plano |
|---|---|
| `Operations.tsx` reúne lista, detalhe, editor, itens, pagamentos e confirmação | Separar páginas, componentes e controlador do formulário |
| `Catalog.tsx` reúne produto, variante, fotos e substituição de arquivos | Separar catálogo e fotos, preservando cadastro inline na compra |
| `Management.tsx` reúne seis visões e carregamentos auxiliares | Separar página, filtros, visões e consultas |
| `services/domain.ts` reúne DTOs, transporte, autenticação, endpoints e apresentação | Distribuir contratos e APIs por módulo; compartilhar só transporte e formatos |
| `domain/service.py` reúne cadastros, candidato, assinatura, replay e persistência | Extrair casos de uso e políticas sem fragmentar a transação |
| `domain/routes.py` manipula imagens, disco, ORM, auditoria e commit | Mover fluxo de fotos para aplicação e armazenamento para infraestrutura |
| `useData.ts` não descarta respostas antigas nem possui cleanup da carga | Caracterizar e corrigir concorrência de carregamento |
| Há `catch` vazio em movimentos e consultas auxiliares | Tornar falha parcial visível e recuperável |
| `backend/tests/conftest.py` e `test_operation_contracts.py` estão excluídos localmente | Resolver a intenção dessas exclusões antes de usar os testes como baseline |
| CI ainda executa `backend/check.py` e E2E depende da preparação isolada | Não aceitar sucesso sem testes coletados e fixtures válidas |

A última tentativa de execução encontrou dependências locais ausentes (`dotenv`, `tsc`) e Compose sem variável obrigatória. Isso é uma limitação daquela verificação, não prova de defeito na aplicação. Revalidar o ambiente no início da execução. Não há benchmark que comprove gargalo de produção; tamanho de arquivo é sinal de investigação, não severidade automática.

As exclusões locais são alterações preexistentes: não restaurar nem substituir silenciosamente. Se forem intencionais, definir a suíte substituta; caso contrário, recuperar a versão escolhida com autorização para esses arquivos. Planejamento e inspeção podem avançar enquanto isso; refatoração ampla depende da baseline.

## Organização proposta

### Backend

```text
app/
  core/                         # configuração, sessão SQL e autenticação
  modules/
    auth/                       # acesso existente
    system/                     # disponibilidade existente
    auxiliaries/
      router.py                 # composição e compatibilidade HTTP existente
      suppliers/                # fornecedores: router, schemas, service, repository
      categories/               # categorias: router, schemas, service, repository
      purchase_channels/        # canais de compra: arquivos próprios por camada
      sale_channels/            # canais de venda: arquivos próprios por camada
      payment_methods/          # formas de pagamento: arquivos próprios por camada
      common/                   # normalização e persistência comuns efetivamente usadas
    catalog/
      router.py
      schemas.py
      products.py               # casos de uso de produto e similaridade
      variants.py               # casos de uso de variante e unicidade
      repository.py
    photos/
      router.py
      schemas.py
      service.py                # adicionar, organizar, excluir e compensar
      storage.py                # interface de armazenamento
      infrastructure/
        local_storage.py        # arquivos e validação de imagem com Pillow
    operations/
      router.py
      schemas.py
      service.py                # preview e confirmação explícitos
      candidate.py              # montagem e snapshots do candidato
      policies/
        inventory.py            # ponto zero e correção do inventário
        purchases.py            # fornecedor, canal, custo e data de compra
        sales.py                # canal, preço negociado e snapshots da venda
        adjustments.py          # direção, motivo e custo do ajuste
      payments.py               # IDs, formas e instantes dos recebimentos da venda
      signing.py                # fingerprint e assinatura da prévia
      repository.py             # operações e recibos idempotentes
      domain/
        ledger.py               # replay puro e regras de estoque/custo
        types.py                # estruturas internas tipadas
    management/
      router.py
      schemas.py
      service.py                # consulta coerente e composição do relatório
      views/                    # overview, stock, sales, receipts, purchases, buying
      calculations/             # cálculos por responsabilidade, reutilizados pelas visões
  shared/
    application/                # auditoria, versão e erros compartilhados
    persistence/                # trava/revisão e serialização comuns
    models/                     # modelos ORM existentes, mesma metadata/schema
```

Criar arquivos quando existir uma responsabilidade concreta; a árvore é um mapa de responsabilidades, não obrigação de criar interfaces ou classes vazias. Manter funções onde forem suficientes. Os modelos ORM podem permanecer no endereço atual durante a transição e ser movidos em uma fatia mecânica final, atualizando Alembic, init, reset e testes. Migrações históricas não serão reescritas.

Regras de dependência:

- Router valida o contrato HTTP, resolve dependências, chama um caso de uso e traduz a resposta. Não contém SQL, regras comerciais, disco, auditoria nem commit.
- Aplicação coordena regras, repositórios e efeitos. Erros próprios são traduzidos para HTTP na borda, preservando status e formato `detail`.
- Domínio puro não importa FastAPI, SQLAlchemy, configuração global ou arquivos. Dinheiro, tempo e estruturas usadas pelo ledger têm contratos explícitos.
- SQL fica em repositórios; disco/Pillow ficam no adaptador de fotos. Criar interfaces apenas nas fronteiras que precisam de substituição em testes.
- Operações consomem contratos públicos de catálogo/auxiliares, nunca seus routers. Gestão consulta registros e calcula indicadores; não altera acontecimentos.
- Auditoria registra revisões na mesma transação do caso de uso. Nenhum subserviço faz commit independente de produto, operação ou revisão.
- Preservar o dono da transação atual durante extrações. No fluxo de fotos, encapsular explicitamente commit e compensação no caso de uso/coordenador: arquivo novo é compensado também em falha de commit; exclusão física ocorre após commit. Definir e testar essa sequência antes de retirar os commits das rotas.
- Manter um pipeline comum de operação. Inventário, compra, venda e ajuste ganham políticas específicas, sem duplicar replay, idempotência ou persistência por tipo.

### Frontend

```text
src/
  app/                          # composição, registro de telas e navegação atual
  shared/
    api/                        # transporte HTTP e erro estruturado
    ui/                         # componentes visuais genéricos
    hooks/                      # carga segura e recursos reutilizados
    format/                     # moeda, datas e apresentação
  modules/
    auth/                       # sessão, API de login e tela
    auxiliaries/
      suppliers/                # contratos, API, página, formulário e hook próprios
      categories/               # contratos, API, página, formulário e hook próprios
      purchase-channels/        # canais de compra com interface pública própria
      sale-channels/            # canais de venda com interface pública própria
      payment-methods/          # formas de pagamento com interface pública própria
      components/               # campos e listas realmente comuns aos cadastros
    catalog/
      contracts.ts
      api.ts
      pages/                    # catálogo e detalhe do produto
      components/
        ProductForm.tsx         # identidade e dados do produto
        VariantForm.tsx         # tamanho, cor e referências da variante
      hooks/                    # dados e ações de catálogo
      index.ts                  # API pública, inclusive formulários inline
    photos/                     # galeria, organização, carga e substituição
    operations/
      contracts.ts
      api.ts
      pages/                    # lista, detalhe e formulário
      components/               # itens, pagamentos, prévia e resumo em arquivos próprios
      hooks/                    # controlador da edição/preview/confirmação
      model/                    # estado e transformações comuns
      flows/                    # inventory, purchases, sales, adjustments em arquivos próprios
    history/                    # revisões e apresentação antes/depois
    management/
      contracts.ts
      api.ts
      pages/
      components/               # filtros e evidências de origem
      views/                    # seis visões gerenciais existentes
```

Páginas coordenam composição e navegação; componentes recebem dados e callbacks; hooks coordenam estado e efeitos; APIs de módulo conhecem endpoints; transporte compartilhado conhece fetch e autenticação. Formatações não dependem da API. Componentes genéricos não importam módulos de negócio.

Operações podem reutilizar a interface pública de cadastro do catálogo para criação inline. Não importar a página inteira nem componentes internos por caminhos profundos. Extrair `Shared.tsx` por responsabilidade: UI genérica em shared; resumo em operações; histórico em history; carga de fontes no consumidor apropriado. Evitar ciclos de barrels.

Valores monetários continuam texto decimal ou null no contrato. Conversão para número serve à apresentação, nunca para reconstruir regras financeiras. Backend permanece autoridade sobre estoque, custo, saldo e impactos.

### Separação por capacidade dentro de cada módulo

Auxiliares é um agrupamento de navegação e composição. Fornecedores, categorias, canais de compra, canais de venda e formas de pagamento terão arquivos próprios de contrato, ações/casos de uso e apresentação. Cada capacidade terá uma interface pública identificável e testes próprios; adicionar uma regra de fornecedor não deve exigir editar o formulário ou serviço de categorias. Quando houver consulta SQL específica, ela pertence ao repositório da capacidade. A persistência idêntica pode usar um helper comum sem gerar cinco cópias da mesma consulta.

Os contratos específicos fixam o tipo correto e não aceitam um `kind` arbitrário vindo de outra capacidade. Na transição, o endpoint genérico `/auxiliaries` e a tabela existente continuam compatíveis: um adaptador HTTP central faz somente o despacho para handlers específicos, e cada wrapper de API frontend fixa o tipo de seu cadastro. Os routers das capacidades fornecem handlers à composição existente; não registrar cinco rotas concorrentes com o mesmo método/path. Não criar novos endpoints ou tabelas apenas para refletir a separação de arquivos.

Componentes e funções comuns recebem dados/callbacks e executam somente o comportamento compartilhado. Não concentrar novamente todas as capacidades em um `service.py`, formulário universal ou arquivo de condicionais por tipo. Também não criar camadas vazias: compartilhar a implementação técnica idêntica, mantendo explícitos os pontos de entrada e as responsabilidades de cada capacidade.

Aplicar o mesmo critério aos demais agrupamentos:

| Agrupamento | Separação concreta | O que permanece compartilhado |
|---|---|---|
| Auxiliares | Fornecedores, categorias, canais de compra, canais de venda, formas de pagamento | Normalização, componentes básicos, transporte e persistência comum |
| Catálogo | Produto e variante: formulários, contratos específicos, ações e consultas identificáveis | Composição do detalhe e validações realmente comuns |
| Operações | Inventário, compras, vendas e ajustes: arquivos próprios de política e composição de formulário | Ledger, candidato comum, assinatura, idempotência e confirmação transacional |
| Recebimentos | Componentes e funções próprias de adicionar, editar e remover pagamentos | Documento e transação da venda; não criar um financeiro independente |
| Fotos | Galeria, imagem autenticada, organização, upload, substituição e remoção | Adaptador de armazenamento, validação e coordenador transacional |
| Gestão | Visão geral, estoque/giro, vendas/margens, recebimentos, compras/fornecedores e apoio à compra em arquivos próprios | Carregamento coerente, filtros, cálculos comuns e links de origem |
| Rastreabilidade | Histórico de revisões e movimentações com componentes/consultas próprios | Identificação da operação de origem e apresentação de datas |
| Infraestrutura frontend | Transporte HTTP, sessão, erros, moeda e datas em arquivos próprios | Utilitários técnicos sem regras específicas de negócio |

Uma capacidade merece arquivo próprio quando tem significado de negócio, regras, contrato, ciclo de interação ou testes próprios. Pastas por capacidade agrupam arquivos relacionados; separação por camada dentro delas mantém HTTP, aplicação e persistência reconhecíveis. Arquivos de composição apenas conectam partes. Revisar arquivos com múltiplos formulários, seletores por tipo, efeitos independentes ou grupos de funções sem relação direta durante C1, e registrar seu destino antes da extração.

## Sequência de execução

| ID | Frente e entrega | Dependência | Critério de aceite |
|---|---|---|---|
| C0 | Estabilização: resolver suíte ausente, preparar ambiente isolado e registrar baseline | Nenhuma | Testes coletados e executados; build e jornada existentes passam, ou defeitos prévios são reproduzidos e corrigidos em fatias próprias |
| C1 | Estabilização: caracterizar contratos e falhas sensíveis | C0 | Matriz abaixo coberta; resultados de referência determinísticos; nenhum teste aponta à base operacional |
| C2 | Melhoria técnica: separar transporte, DTOs, formatos e erros frontend | C1 | Cada módulo possui contratos/API; login, upload e endpoints mantêm contrato; `domain.ts` deixa de concentrar responsabilidades |
| C3 | Melhoria técnica: separar cada cadastro auxiliar e modularizar produto/variante backend/frontend | C2 | Cinco capacidades auxiliares com arquivos e testes próprios; contrato genérico compatível; duplicidade, desativação e criação inline equivalentes; imports antigos migrados |
| C4 | Melhoria técnica: extrair fluxo de fotos e armazenamento | C3 | Rotas finas; rollback/commit compensados; autenticação e organização preservadas |
| C5 | Melhoria técnica: decompor casos de uso de operações e editor por fluxo | C4 | Inventário, compra, venda, ajuste e pagamentos com arquivos próprios; pipeline comum de prévia/confirmação, ledger e persistência separados; invariantes transacionais verificadas |
| C6 | Melhoria técnica: modularizar gestão, histórico e composição | C5 | Seis visões equivalentes e vínculos de origem preservados; Shared e façades transitórias removidos |
| C7 | Evolução funcional: recuperação de falhas e revisão segura | C2–C6 | Cenários funcionais abaixo demonstrados na interface |
| C8 | Estabilização final: gates, documentação e limpeza da transição | C7 | Testes, build, lint e checagem de dependências passam; documentação aponta para estrutura real |

Cada entrega deve ser pequena o bastante para revisão e reversão isoladas. Se uma fatia exigir alterações simultâneas em muitos módulos, subdividir por caso de uso. Não misturar formatação massiva com extração semântica. Usar fachadas de compatibilidade temporárias apenas com consumidores e remoção identificados; o aceite final exige que não preservem o módulo central antigo.

## Evolução funcional proposta para esta rodada

| Melhoria | Comportamento observável | Limite |
|---|---|---|
| Falhas parciais recuperáveis | Erro ao buscar movimentos, histórico ou auxiliares informa a seção afetada e oferece tentar novamente | Não apresentar seção incompleta como lista vazia válida |
| Recuperação de prévia obsoleta | Conflito invalida a prévia e orienta revisão; mantém dados digitados e exige nova confirmação humana | Não confirmar automaticamente depois do conflito |
| Confirmação com resultado incerto | Falha de rede permite repetir a mesma confirmação com a mesma chave e conteúdo | Mudança nos dados invalida prévia e exige nova chave; conflito exige nova revisão |
| Formulário resistente a recargas | Cadastro inline e atualização de fontes mantêm fornecedor, itens e pagamentos já preenchidos | Rascunho em memória; persistência local e retomada após logout ficam fora desta proposta |
| Carregamento coerente | Mudança rápida de filtro/tela não deixa resposta antiga substituir a nova; desmontagem descarta resultado | Cancelar leitura quando possível; não cancelar gravação fingindo que o backend não a executou |

Esses comportamentos devem entrar em commits posteriores às extrações correspondentes, permitindo distinguir reorganização de alteração funcional.

## Matriz de proteção e verificação

| Área | Cenários obrigatórios | Nível |
|---|---|---|
| Ledger | Inventário vazio/único; custo ausente; média ponderada; consumo de desconhecidos; ordem histórica; estoque insuficiente; anulação | Unitário puro |
| Operações | Prévia sem gravação de acontecimento; assinatura obsoleta; mesma chave repetida; chave com conteúdo diferente; edição/anulação; recálculo dependente | Integração HTTP/PostgreSQL |
| Concorrência e rollback | Duas confirmações disputando estoque; falha após escrita parcial sem operação/movimento/revisão/recibo parcial | Integração PostgreSQL real |
| Catálogo/auxiliares | Normalização, similaridade, tamanho/cor únicos, versão, motivo, desativação e snapshots históricos | Unidade de política + integração |
| Capacidades auxiliares | Contratos e formulários específicos dos cinco cadastros; tipo correto fixado; despacho HTTP sem rotas duplicadas; rejeição de referência cruzada e unicidade por tipo preservadas | Unidade por capacidade + integração do endpoint compatível |
| Fotos | Tipo/tamanho inválido, acesso, vínculo cruzado, principal/ordem, falha de commit, compensação e falha de remoção física | Unidade com adaptador + integração com pasta temporária |
| Contrato | Paths/métodos, autenticação, cabeçalhos, DTOs monetários, status e `detail` | Comparação OpenAPI e testes HTTP |
| Gestão | Seis visões, origem, período São Paulo, pagamentos no próprio instante, pendência/estoque atuais e custo desconhecido | Cálculos unitários + integração |
| UI | Alteração invalida prévia, duplo clique, retry idempotente, erros parciais, resposta fora de ordem e preservação do formulário | Testes de hooks/componentes + E2E seletivo |
| Jornada | Catálogo → inventário → compra com cadastro inline → venda parcial → recebimento → correção → histórico → gestão | Playwright existente e extensões necessárias |

Comparações determinísticas normalizam somente UUIDs e instantes gerados; nunca descartam dinheiro, estoque, referências, versão ou efeitos da auditoria. Fakes ajudam nas regras e efeitos de disco, mas não substituem PostgreSQL nos testes de concorrência.

Durante C0/C1, organizar testes backend por unidade e integração e adicionar runner de testes de componente ao frontend (proposta: Vitest + React Testing Library). Adicionar lint Python e TypeScript/React, verificando regras de hooks e imports. Instalação deve respeitar o ambiente escolhido e atualizar manifestos/lockfile somente na implementação. A versão das ferramentas será verificada nessa etapa.

Comandos de referência já existentes: `python backend/check.py`; `npm run build` em frontend; `python backend/check.py --serve` seguido de `npm run test:e2e`. Backend e E2E não rodam simultaneamente porque compartilham o banco isolado. Novos comandos de lint/unidade entram no README e CI quando forem implementados; não são apresentados como disponíveis hoje.

## Critérios de conclusão da implementação

- Os quatro achados possuem solução rastreável: telas decompostas; serviço central substituído; contratos/API/apresentação separados; rotas sem lógica de aplicação ou infraestrutura.
- Fornecedores, categorias, canais de compra, canais de venda e formas de pagamento possuem arquivos e testes específicos no frontend/backend. Helpers compartilhados não acumulam regras das cinco capacidades.
- A matriz de separação por capacidade foi aplicada a catálogo, operações, pagamentos, fotos, gestão e rastreabilidade; diferenças de negócio não ficaram ocultas em novos arquivos genéricos. A confirmação transacional e o ledger permanecem únicos.
- A redução de linhas é consequência, não meta: cada arquivo tem responsabilidade nomeável, dependências claras e testes no nível apropriado. Arquivos que continuem extensos exigem revisão de responsabilidade, não corte artificial.
- Domínio puro não depende de HTTP/ORM/disco; módulos não importam routers entre si; componentes genéricos não dependem de negócio; checagem automatizada detecta violações dessas fronteiras.
- Preview, confirmação, idempotência, snapshots, dinheiro desconhecido, histórico e compensação de fotos mantêm seus contratos e garantias.
- Todas as melhorias funcionais escolhidas possuem evidência de teste e jornada verificável; funcionalidades não escolhidas ficam explicitamente fora da entrega implementada.
- Suíte tem testes realmente coletados, sem tornar casos críticos opcionais por skip; falhas prévias permanecem rastreáveis até resolução.
- Não há fachadas permanentes para esconder os arquivos centrais antigos, imports quebrados, endpoints duplicados ou documentação com caminhos antigos.
- README, matriz de alinhamento e instruções de manutenção descrevem a organização e os comandos finais. Dados e migrações existentes permanecem compatíveis.

## Riscos e mitigação na execução

O principal risco está na extração do ciclo transacional: um commit antecipado pode romper a atomicidade de operações ou fotos. Fazer extração mecânica primeiro e introduzir novas abstrações somente com teste de falha de commit. O segundo risco é mudar a identidade do editor React e perder rascunho/chave de idempotência; mantê-los no controlador estável e testar recarga de fontes. O terceiro é duplicar regras entre os quatro tipos de operação; preservar um único ledger e um único fluxo de confirmação.

A ordem favorece cadastros antes de operações, pois permite validar as fronteiras em fluxos menores. Nenhuma estimativa de dias é fixada antes da baseline; dimensionar cada fatia após C0/C1 usando complexidade e evidências, sem converter quantidade de arquivos em prazo.

## Aceite deste planejamento

O plano cobre os quatro achados, propõe responsabilidades e dependências concretas, ordena as entregas e define a verificação de cada mudança. C0–C8 foram implementados. A matriz de evidências e os resultados dos gates estão em `QUALIDADE_CODIGO_RESULTADO.md`; o documento diferencia a baseline histórica da organização efetivamente entregue.
