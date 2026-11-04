# Alinhamento ao produto definitivo

Fonte normativa: [PRODUTO_E_OBJETIVO.md](PRODUTO_E_OBJETIVO.md). Este documento
registra contratos e critérios de manutenção, sem substituir decisões de produto.

## Organização

O backend permanece um monólito FastAPI. `app/domain` contém contratos, modelos,
consultas, serviços de gravação, reprodução do histórico e consultas gerenciais.
Autenticação e disponibilidade permanecem módulos pequenos separados.

As nove tabelas `lgd_*` representam controle inicial, auxiliares, produtos,
variantes, fotos, operações, movimentações, revisões e recibos de requisição.
Itens e pagamentos são documentos estruturados pertencentes à operação: isso
permite validar e versionar o acontecimento inteiro numa única transação. Cada
pagamento tem ID estável, valor, forma e momento próprios. Relacionamentos de
variantes e auxiliares são validados no serviço; as versões preservam seus nomes.

Não há serviços externos, filas, motor de agentes, snapshots mensais ou sistema
financeiro geral. A API é o contrato interno do frontend, não uma integração externa.

## Regras técnicas explícitas

- Moeda BRL, `Decimal`, duas casas, `ROUND_HALF_UP`; contratos transportam dinheiro
  como texto decimal. Não converter ausência de custo/preço em zero.
- Estoque e custo são projeções reconstruíveis da sequência de operações válidas.
- Cada compra usa a data informada em São Paulo. No dia do inventário, seu instante
  efetivo é limitado ao ponto zero; demais acontecimentos usam o instante automático.
  Empates são resolvidos pela sequência persistida.
- Unidades com custo desconhecido são consumidas primeiro. Unidades conhecidas
  usam média ponderada. Uma compra conhecida não apaga a lacuna das anteriores.
- Preço de referência é capturado por variante na confirmação da venda e preservado
  nas correções; uma variante nova na venda recebe a referência vigente.
- Toda edição de acontecimento exige versão e motivo. Prévia retorna efeitos e
  alterações de custos em registros posteriores. Confirmação verifica assinatura
  da prévia e revisão global; base alterada exige nova revisão do impacto.
- Gravações são serializadas por uma trava PostgreSQL transacional, proporcional
  ao acesso único, e variantes são bloqueadas em ordem de ID. Consultas gerenciais
  usam trava compartilhada para não misturar versões do catálogo e da operação.
- `Idempotency-Key` é obrigatório na confirmação. Repetir a mesma chave e conteúdo
  devolve o primeiro resultado; reutilizar a chave com outro conteúdo é conflito.
- Movimentações são imutáveis. Correção de quantidade registra a diferença; correção
  de custo registra versões e recálculos, sem inventar movimentação de quantidade.
- Quantidades repetidas da mesma variante são recusadas com orientação para agrupar.
- Normalização: NFKD sem acentos, casefold e espaços agrupados. Produto semelhante:
  `SequenceMatcher` sobre nome e estampa normalizados, razão mínima 0,85. O alerta
  exige confirmação de que as peças são distintas; não há fusão automática.
- Cadastros utilizados não são apagados. A interface oferece renomeação/desativação.
- Fotos: JPEG, PNG ou WebP verificados, até 10 MB; conteúdo autenticado. Arquivo novo
  é compensado se a gravação falhar; exclusão física só ocorre depois do commit.
- Intervalos de consulta incluem os dias escolhidos em `America/Sao_Paulo`.
  Vendas seguem a ocorrência da venda; recebimentos seguem o pagamento; pendência
  e estoque são sempre atuais. Sem filtro, todo o histórico confiável.
- Permanência é o tempo desde a primeira entrada conhecida da variante. Não se
  afirma a idade individual de peças agregadas e não há atribuição de venda a lote.
- Apoio à compra é descritivo e mostra extensão do histórico, estoque, saída e margem
  conhecida. Quantidades recomendadas aguardam regra validada com uso real.

## Matriz de requisitos e verificação

Os testes HTTP estão em `backend/tests/test_operation_contracts.py`; a jornada
real de interface está em `frontend/e2e/operation.spec.ts`.

| Seção do produto | Comportamento | Verificação |
|---|---|---|
| Identidade do item | Variante única e código automático | normalização, duplicidade e catálogo |
| Cadastros auxiliares | Nome único, desativação e nome histórico | renomeação e snapshots |
| Inventário inicial | Ponto zero único; custo ausente permitido | bloqueio anterior e unicidade |
| Estoque e ajustes | Motivo e custo quando necessário | ajuste com lacuna de custo |
| Validações | Quantidade inteira positiva e dinheiro válido | casos parametrizados inválidos |
| Validações | Repetição não contorna disponibilidade | variante repetida e concorrência |
| Compra | Custo médio e detalhe com itens | compra, média e anulação impossível |
| Venda | Referência, preço efetivo, custo e saída | jornada e diferença comercial |
| Pagamentos | Saldo, inclusão, edição e remoção | jornada e pagamento excedente |
| Correções | Versão e confirmação do impacto | prévia obsoleta e histórico |
| Custo | Desconhecido não equivale a zero | venda incompleta e recálculo auditado |
| Anulações | Preservar registro e reverter efeitos | jornada com venda anulada |
| Fotos | Conteúdo válido e vínculo com produto | upload, organização e remoção |
| Tempo | Recorte histórico separado de saldo atual | intervalo sem vendas com saldo pendente |
| Fronteiras | Sem despesas, exportação, DRE ou agentes | rotas removidas retornam 404 |
| Fundação | Instalação reproduzível | cadeia Alembic até 0006 desde base vazia |
| Uso real | Registrar, receber, corrigir e consultar | Playwright em navegador móvel |

## Transição

A migração 0006 só cria o núcleo novo. Não apaga registros legados no startup.
`reset_operation.py` é um procedimento administrativo separado, com conferência
literal do banco e host. Ele limpa o núcleo, remove tabelas antigas reconhecidas
e apaga somente fotos associadas dentro do armazenamento gerenciado. Recusa
tabelas desconhecidas e destinos diferentes de `lgd_mantos`.

O início real não usa dados de teste e não confirma inventário automaticamente.
Os planos anteriores foram retirados do diretório e permanecem no histórico Git.
As decisões desta rodada prevalecem, incluindo limpeza da base,
venda com custo ausente e recálculo auditado de custos históricos.
