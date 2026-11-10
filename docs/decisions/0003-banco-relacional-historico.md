# ADR 0003 — Núcleo relacional e histórico documental

Estado: aceita e implementada. Referência: plano aprovado de Banco, baseline
de código `960c07d`. Evidências em [resultado](../QUALIDADE_BANCO_RESULTADO.md).

O produto precisa preservar operações como agregados atômicos e impedir
referências inválidas mesmo fora do HTTP. O dono confirmou ausência de dados
reais e autorizou reconstrução limpa. A escolha é PostgreSQL 16 com 15 tabelas
de negócio, UUID nativo e baseline independente 0007, sem conversão ou stamp
de instalações antigas. A cadeia anterior é recuperável pelo Git.

Cadastros auxiliares, operações, itens e pagamentos são relacionais. Colunas e
filhos são a fonte canônica; o payload contratual é reconstruído em lote.
Snapshots, resultados, auditoria e respostas idempotentes são JSONB com versão
explícita. Nomes e preços históricos não dependem de consultas ao cadastro atual.
Dinheiro é NUMERIC(14,2), sem confundir NULL com zero. Datas de compra são DATE;
instantes são TIMESTAMPTZ. O ledger puro continua reconstruindo saldos e custos.

FKs RESTRICT, checks locais, unicidades e permissões reforçam integridade.
Não são usados checks com consultas a outras tabelas. Soma de pagamentos,
disponibilidade histórica, atividade de referências, normalização Unicode e
validade temporal continuam na aplicação. A unicidade diferível da posição de
pagamentos permite reordenação transacional sem recriar seus IDs ou instantes.

A API usa lgd_app sem DDL/TRUNCATE ou alteração de histórico. lgd_migrator é dono
do schema e executa migrações. Bootstrap administrativo provisiona roles; seus
segredos não são entregues à API. Reconstrução é explícita, com banco/host
conferidos e escritores parados, e remove somente schema e uploads LGD.

Foram medidos quatro candidatos a índice; apenas três com benefício entram na
baseline. Não há GIN, particionamento, serviço adicional ou alteração preventiva
do pool/autovacuum. Histórico e recibos não expiram. Isso implica crescimento
persistente e exige acompanhamento operacional.

A representação relacional acrescenta leitura de filhos e escrita de constraints;
JSONB não resolve o custo do replay. Correções extensas mantêm auditoria e
recibos integrais e podem custar dezenas de segundos. Capacidade real permanece
em ARQ-11; backup externo, RPO/RTO e servidor real permanecem em OPS. A decisão
nunca autoriza remover garantias do ledger para cumprir uma meta sintética.
