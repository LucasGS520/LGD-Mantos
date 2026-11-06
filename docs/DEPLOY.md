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

```sh
docker compose -f docker-compose.prod.yml up -d --build
```

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

`/api/v1/health` verifica o banco e informa versão e horário. O status do banco está
no corpo da resposta. `/` é apenas uma verificação simples do processo HTTP.

Políticas de backup, retenção e restauração continuam sendo requisitos operacionais
de infraestrutura a definir. A aplicação não oferece exportação como backup.

## Pendências para comprovar a prontidão operacional

Este documento é uma referência de configuração, não um registro de deploy
validado. O acompanhamento está em [Qualidade e situação atual](QUALIDADE_SITUACAO_ATUAL.md):

- OPS-01: definir RPO/RTO, frequência, retenção, destino e responsável por backups
  de banco e fotos; comprovar restauração consistente em ambiente isolado antes
  de depender da implantação para dados reais.
- OPS-02: validar atualização, migrações, persistência dos volumes, HTTPS e
  recuperação de release em ambiente apropriado.
- OPS-03: definir os sinais mínimos de disponibilidade, erros e duração das
  operações, incluindo espera por locks e custo do replay.

Não há evidência de conclusão desses itens nesta documentação. A avaliação de
Banco também deve conferir o schema efetivamente implantado e sua manutenção;
a existência dos arquivos de migração não comprova o estado do servidor.
