# Execução em produção

Referência de produto: [PRODUTO_E_OBJETIVO.md](PRODUTO_E_OBJETIVO.md).
Este documento descreve configuração técnica; não cria funcionalidades de negócio.

## Topologia

Docker Compose executa PostgreSQL 16, FastAPI e Caddy. O Caddy serve a aplicação
React compilada e encaminha `/api/*` ao backend. Fotos são obtidas por endpoints
autenticados da API. Não há diretório público de uploads, PWA ou serviço de IA.

Apenas portas 80/443 são publicadas na configuração de produção; banco e backend
permanecem na rede interna do Compose. O domínio precisa apontar para o servidor.

## Configuração

Preencha `.env` no servidor, sem versioná-lo:

| Variável | Finalidade |
|---|---|
| `DOMAIN` | Domínio atendido pelo Caddy |
| `POSTGRES_PASSWORD` | Senha do banco |
| `DATABASE_URL` | Conexão `postgresql+asyncpg` com host `db`, banco `lgd_mantos` |
| `APP_PASSWORD` | Senha exclusiva do dono |
| `APP_SECRET` | Segredo de assinatura de tokens e prévias |
| `CORS_ORIGINS` | Origem HTTPS da aplicação |
| `LGD_RELEASE` | Identificador da release, preferencialmente SHA, para imagens backend/web |
| `DB_LOCK_TIMEOUT_MS` | Espera máxima por lock no PostgreSQL; padrão 5.000 ms |
| `DB_STATEMENT_TIMEOUT_MS` | Limite por statement; padrão 30.000 ms, não duração total da confirmação |
| `DB_POOL_TIMEOUT_SECONDS` | Espera por conexão do pool; padrão 5 s |

Na instalação nova, com base vazia e API ainda parada:

```sh
export LGD_RELEASE=sha-da-release
docker compose -f docker-compose.prod.yml build backend web
docker compose -f docker-compose.prod.yml up -d db
docker compose -f docker-compose.prod.yml run --rm migrate
docker compose -f docker-compose.prod.yml up -d backend web
```

Falha em qualquer etapa impede avançar para a seguinte. A imagem não executa
migrações ao iniciar. `migrate` usa a mesma imagem da release; execute apenas uma
instância administrativa, com API parada e sem outros escritores. O backend
possui healthcheck, e o Caddy aguarda sua prontidão inicial.

Em atualização, construa as imagens antes da manutenção; pare a API, capture backup
consistente e só então aplique a migração e inicie a release. Preserve o identificador
da imagem anterior. Reiniciar a imagem anterior só é válido se o schema continuar
compatível; isso não reverte dados. Não executar downgrade automático.

As imagens utilizam `requirements.txt` como fonte única de dependências Python de
execução e `npm ci` para o frontend. Ferramentas de testes ficam separadas.

## Transição da versão antiga

O esquema novo começa na migração 0006. Sua aplicação cria tabelas novas e mantém
o legado intacto até o procedimento administrativo de transição.

A limpeza da base escolhida deve ser executada separadamente, depois da validação
em ambiente isolado, com o backend parado. Use os comandos do README com
`-f docker-compose.prod.yml` quando o destino for produção. A ferramenta confere o
nome do banco, o host e todas as tabelas presentes antes de apagar registros.

Não copie dados de teste, não invente recebimentos e não confirme automaticamente
o inventário inicial. Depois da transição, o dono inicia o controle pelas quantidades
físicas conhecidas. Nenhuma limpeza ocorre em inicializações futuras.

## Persistência e disponibilidade

`pgdata` contém o banco e `uploads_data` contém as fotos. `caddy_data` e
`caddy_config` preservam o estado da borda HTTPS.

`/api/v1/health` verifica banco/revisão Alembic esperada e informa versão/horário.
Retorna 200 com `database=ok` e 503 com `status=error` se não estiver pronto.
Não expõe detalhes da conexão. `/` verifica somente o processo HTTP.

## Backup consistente e ensaio de restauração

A captura administrativa disponível exige que a única API esteja parada e que
ninguém grave por scripts, SQL ou outra instância. Registre início/fim da janela.
O script recusa backend em execução, destino existente e banco desconhecido:

```sh
docker compose -f docker-compose.prod.yml stop backend
python3 deploy/backup.py --destination /destino-seguro/backup-novo
```

O diretório contém `database.dump`, `uploads.tar` e manifesto com hashes,
contagens, imagem e horário. Falha deixa `INCOMPLETE`; não use essa cópia para
restaurar. A ferramenta não reinicia a API automaticamente. Após captura bem-sucedida,
copie o diretório para destino seguro fora do host e confira integridade; antes
de migrar, assegure que a cópia está recuperável. Esse destino, suas permissões,
criptografia, retenção e agendamento devem ser configurados pelo operador.

Para ensaiar uma cópia em ambiente separado, provisione PostgreSQL 16 vazio com
o banco `lgd_mantos_alignment_test` e label Docker `com.lgd.purpose=restore-drill`.
Use um diretório de fotos novo:

```sh
python3 deploy/verify_backup.py --source /backup-copiado --database-container container-do-ensaio --photos-destination /diretorio-novo
```

Esse comando é exclusivo de ensaio: recusa banco com tabelas, label ausente,
hash divergente, destinos existentes e membros de tar inseguros. Restaura no
banco de teste, confere as nove contagens e referências de fotos. Execute depois
`backend/verify_restored.py` com configuração apontando exclusivamente para essa
base e `PHOTO_ROOT` para `products` restaurado: verifica replay, projeções,
movimentos, recibos e conteúdo das imagens. Não apontar a API pública para a base
de ensaio. Contagens não substituem essa conferência de consistência.

Em desastre real, provisionar destino novo, restaurar/conferir fora do tráfego,
definir a perda de registros desde a captura e somente depois planejar a troca
da implantação. Não há script que sobrescreva automaticamente o banco real.
Preserve a origem para investigação. Um rollback de imagem não recupera registros
apagados nem desfaz migração incompatível.

O ensaio sintético está no [resultado de Arquitetura](QUALIDADE_ARQUITETURA_RESULTADO.md).
RPO/RTO reais ainda devem ser acordados; 1,76 s de restore de fixture pequena não
é RTO do servidor. A aplicação não oferece exportação como backup.

## Sinais, erros e acesso

Logs do logger `lgd` são JSON: rota parametrizada, método, status, duração e
request ID; fases informam carga/replay/cálculo e espera/retenção da trava. O
header `X-Request-ID` permite correlacionar uma falha. Não são registrados senha,
token, chave idempotente ou corpo de negócio; parâmetros SQL ficam ocultos nos
erros do engine. O comando da imagem desliga access log com URL bruta. Docker
limita logs do backend a três arquivos de 10 MB; coleta externa ainda precisa de
configuração e comprovação.

Configurar monitor para prontidão não 200 e alerta após três verificações
consecutivas com falha; acompanhar proporção de 5xx, timeouts, p95 e limpeza de
fotos adiada. Metas de latência e limites observados constam no resultado; não
alertar a cada conflito de prévia esperado. Validar entrega de alertas ao
responsável e revisar limiares com uso real. Healthcheck Docker isolado não envia
alerta nem comprova disponibilidade ponta a ponta.

Timeout de espera/statement/pool gera 503 com orientação e Retry-After. Não
automatizar repetição de gravações: confirmação incerta deve manter chave e
conteúdo; prévia obsoleta exige nova revisão. A duração da correção pode exceder
o timeout de um statement porque ela contém vários statements; não definir
timeout de proxy que induza repetição sem recibo.

Reconciliação de fotos: `python backend/reconcile_photos.py` com configuração da
implantação e uploads suspensos produz inventário estável de ausentes/órfãos.
Não remove arquivos e não deve ser usada como autorização automática de limpeza.

A sessão permanece JWT de 30 dias em localStorage. Logout apaga a cópia local,
sem revogar token copiado. Rotacionar APP_SECRET invalida sessões e prévias em
todos os dispositivos; exigir novo login e revisão. Login recusa após dez falhas
em 60 segundos por processo, sem confiar em IP de proxy; reinício perde esse
contador e várias réplicas não compartilham o limite. HTTPS e proteção dos
segredos/dispositivo permanecem obrigatórios. Se mudar a fronteira de acesso,
reavaliar revogação e modelo de sessão.

## Pendências para comprovar a prontidão operacional

Este documento registra configuração e ferramentas ensaiadas localmente, não um
deploy real validado. O acompanhamento está no [registro central](QUALIDADE_SITUACAO_ATUAL.md):

- OPS-01: definir RPO/RTO, frequência, retenção, destino e responsável por backups
  de banco e fotos; comprovar restauração consistente em ambiente isolado antes
  de depender da implantação para dados reais.
- OPS-02: validar atualização, migrações, persistência dos volumes, HTTPS e
  recuperação de release em ambiente apropriado.
- OPS-03: configurar e comprovar coleta/alertas dos sinais implementados no servidor.

Esses itens reais continuam abertos apesar do ensaio sintético. A avaliação de
Banco também deve conferir o schema efetivamente implantado e sua manutenção;
a existência dos arquivos de migração não comprova o estado do servidor.

O [Plano de Arquitetura](PLANO_MELHORIAS_ARQUITETURA.md) detalha sinais de
vivacidade/prontidão em A1, recuperação de fotos em A7 e backup/release em A9.
Implementação e ensaio estão no resultado; requisitos reais permanecem pendentes.
