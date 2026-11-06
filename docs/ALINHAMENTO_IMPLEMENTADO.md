# Alinhamento ao produto definitivo

Fonte normativa: [PRODUTO_E_OBJETIVO.md](PRODUTO_E_OBJETIVO.md). Este documento
registra contratos e critérios de manutenção, sem substituir decisões de produto.

Situação de qualidade: Código (C0–C8) concluído; avaliação e melhorias de Arquitetura,
Banco e preparação operacional permanecem no [registro de pendências](QUALIDADE_SITUACAO_ATUAL.md).
As alternativas desse registro não substituem os contratos vigentes descritos aqui.

## Organização

O backend permanece um monólito FastAPI, organizado em `app/modules` por capacidade:
auxiliares, catálogo, fotos, operações, histórico, gestão, autenticação e disponibilidade.
Cada cadastro auxiliar possui contrato e entrada próprios. Regras comuns de cadastro
usam helpers sem acumular decisões específicas. Modelos ORM ficam em
`app/shared/models/entities.py`; o ledger puro fica em `modules/operations/domain`.
Rotas adaptam HTTP e delegam aos casos de uso. SQL e arquivos ficam em repositórios
e adaptadores; serviços de aplicação não dependem de exceções HTTP.

No frontend, `src/modules` agrupa APIs, contratos, páginas, componentes e hooks
por capacidade. Inventário, compra, venda e ajuste têm composições próprias;
prévia/confirmação compartilham o controlador. As seis visões de gestão são
arquivos próprios. Transporte, formatos e UI genérica ficam em `src/shared`.

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

Os testes HTTP/transacionais estão em `backend/tests/integration/`, incluindo a
suíte contratual recuperada e testes de falha de commit e compatibilidade HTTP.
Testes puros ficam em `backend/tests/unit/`; hooks e formulários têm testes
Vitest junto aos módulos. As jornadas reais de interface estão em
`frontend/e2e/operation.spec.ts` e `frontend/e2e/recovery.spec.ts`.

Uma prévia obsoleta é descartada com orientação de nova revisão, preservando o
formulário. Se a resposta de confirmação for interrompida, a repetição mantém
chave e conteúdo para obter o recibo idempotente. Mudanças no formulário invalidam
a prévia. Cargas antigas são descartadas; falhas em movimentos/histórico/fontes
gerenciais ficam visíveis e oferecem nova tentativa.

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
