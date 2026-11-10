# Plano aprovado — Banco de Dados

Data do plano: 2026-11-09. Referência: `960c07d`. B0–B6 concluídos no escopo
aprovado; ver [resultado e limites](QUALIDADE_BANCO_RESULTADO.md).

O dono confirmou que não existem dados reais e autorizou eliminar eventual conteúdo LGD. Escolheu reconstrução limpa e núcleo relacional com histórico JSON. Não há conversão de dados antigos, limpeza no startup, novo serviço ou mudança de produto. Fonte normativa: [Produto](PRODUTO_E_OBJETIVO.md).

## Diagnóstico B0 e dependências

A leitura direta do código de `960c07d` mostrou nove tabelas `lgd_*`, um cadastro
auxiliar discriminado por `kind`, IDs String(36), documentos JSON e itens e
pagamentos dentro do payload. A FK para auxiliar não protegia seu tipo; fotos
não tinham a garantia composta produto/variante ou unicidade parcial de
principal. Algumas regras já existiam no serviço/ledger e foram preservadas.
A metadata importava configuração da API. A cadeia ativa terminava em 0006.
Nenhuma conclusão do grafo local antigo foi usada como evidência atual.

As consultas examinadas foram catálogo composto, páginas de operações por
sequência/tipo, replay integral, movimentos por origem, revisões por entidade,
fotos por produto e gestão em snapshot. O novo repositório mantém filhos em
lotes e não introduz endpoints independentes para itens ou pagamentos.

Dependências adaptadas: `init_db.py`, prontidão, fixtures, `check.py`, gerador
de carga, `verify_restored.py`, backup/restore, Compose e CI. O diagnóstico
`database_inspect.py` compara metadata e schema efetivo e registra checks/ACLs.
Reconciliação de fotos continua usando a mesma tabela/contrato e somente leitura.
Antes não havia separação de credenciais no Compose; agora bootstrap, migrador
e API têm ambientes próprios. O schema definitivo e as permissões são
verificados no PostgreSQL, além das validações da aplicação.

## Desenho e dicionário

| Tabelas | Dados e responsabilidade |
|---|---|
| lgd_suppliers / lgd_categories / lgd_purchase_channels / lgd_sale_channels / lgd_payment_methods | UUID, nome normalizado único, atividade, observações, versão e criação. Cada vínculo aponta ao cadastro correto |
| lgd_products | Identidade comercial e categoria; sem saldo editável |
| lgd_variants | Produto, código, tamanho/cor normalizados, referências monetárias, atividade, versão e projeções stock/average_cost |
| lgd_photos | Produto, variante opcional do mesmo produto, arquivo, ordem e principal opcional |
| lgd_operations | Tipo, sequência BIGINT, datas, versão, cancelamento, fornecedor/canais tipados, direção, motivo e notas; labels/result JSONB derivados/históricos |
| lgd_operation_items | Operação/posição, variante única no agregado, quantidade, valores permitidos por tipo e snapshot JSONB |
| lgd_sale_payments | ID estável, venda, ordem, forma, nome histórico, valor e instante preservados |
| lgd_movements | Diferença imutável de quantidade por operação/variante/versão |
| lgd_revisions | Antes/depois JSONB com versão de documento, entidade, ação, motivo e instante; pode referenciar foto já removida |
| lgd_requests | Chave textual, fingerprint, operação, resposta JSONB versionada e instante; sem TTL |
| lgd_control | Singleton id=1, revisão global BIGINT não negativa e ponto inicial |

São 15 tabelas de negócio mais alembic_version. Identificadores/FKs usam UUID nativo; dinheiro relacional NUMERIC(14,2) finito; instantes TIMESTAMPTZ. Documento versão desconhecida é recusado. JSONB não substitui o replay nem promete desempenho por si só. Itens/pagamentos relacionais são canônicos; o payload da API é reconstruído, não duplicado como coluna editável.

## Matriz de invariantes

| Regra | Banco | Aplicação / verificação |
|---|---|---|
| Tipos de referência | FKs para os cinco cadastros distintos | Atividade e manutenção de referência histórica |
| Variante no mesmo produto da foto | FK composta | Mensagem de negócio antes do SQL |
| Um inventário não anulável | Índice único parcial e CHECK | Ledger valida ponto zero e sequência |
| Item pertence à operação/tipo | FK composta id/kind, quantidade positiva, variante única e checks monetários | Agregado não vazio exceto inventário; ordem e snapshots |
| Pagamento pertence a venda | FK composta e tipo fixo sale; valor positivo | IDs/instantes preservados; soma não excede venda |
| Principal opcional, no máximo uma | Índice único parcial | Desmarcar/flush antes de promover; exclusão promove remanescente |
| Valores finitos e não negativos quando cabível | NUMERIC, checks e rejeição de NaN | Decimal, duas casas, custo desconhecido diferente de zero |
| Normalização Unicode / similaridade | Unicidade sobre chave normalizada | Função normativa e alerta de similaridade; sem extensão adicional |
| Estoque/custo historicamente válidos | Projeção não negativa e referências válidas | Ledger puro integral, correções e verificação por replay |
| Confirmação atômica | Uma transação; FKs e constraints | Trava global, assinatura, versões, recibo e rollback |
| Histórico/recibos imutáveis pela API | lgd_app sem UPDATE/DELETE nesses registros | Auditoria append-only, recibo repetido sem nova escrita |
| Histórico JSON | Estrutura object e versão positiva | Versão suportada e equivalência dos snapshots/contratos |

## Execução

- B0: inventário, dicionário, matriz e dependências dos scripts.
- B1: baseline independente `0007`; 0001–0006 retiradas da cadeia ativa e preservadas no Git. Base antiga é recusada, sem stamp. Reconstrução explícita confere host/banco e API parada.
- B2: modelos, persistência relacional em lote, payloads compatíveis, validação UUID, erros controlados e credenciais app/migrator separadas. Metadata não importa configuração da API.
- B3: medir candidatos kind/sequence, origem/data/ID de movimentos/revisões e produto/posição/ID de fotos com EXPLAIN ANALYZE BUFFERS; incorporar só com benefício demonstrado, sem índices redundantes/GIN preventivo.
- B4: diagnóstico somente leitura de schema, permissões, tamanhos, estatísticas, autovacuum e conexões; crescimento de auditoria/recibos medido após correção extensa. Sem retenção automática, VACUUM FULL rotineiro ou tuning sem evidência.
- B5: fixtures, carga, backup/restauração, reconciliação, Compose/CI e documentação adaptados; containers da API não recebem segredo migrator/bootstrap.
- B6: instalação limpa, violações SQL, permissões, regressão/concorrência/rollback, equivalência do replay, restauração, três escalas e gates completos; atualizar BD-01–08 com evidência e limites.

As verificações usam apenas lgd_mantos_alignment_test em PostgreSQL isolado. Não executar suítes, carga ou reconstrução simultâneas na mesma base. Ao finalizar, remover recursos Docker temporários LGD sem afetar outros projetos.

## Compatibilidade e encerramento

Endpoints, representação monetária textual, IDs textuais, payload/result e ordenação dos filhos são mantidos. Não surgem endpoints independentes para alterar partes da operação. Exclusões de filhos são explícitas na mesma transação; FKs RESTRICT preservam vínculos. Recibos e revisões mantêm formatos históricos com metadados internos fora da resposta pública.

O resultado deve registrar schema físico e ACLs, planos SQL antes/depois, medidas comparáveis, testes e dependências reais. OPS-01/02/03 (destino externo, RPO/RTO, coleta/alertas e servidor real) não serão declarados concluídos por ensaio sintético. Limites de replay/correção em ARQ-11 permanecem mensurados, sem promessa de capacidade ilimitada.
