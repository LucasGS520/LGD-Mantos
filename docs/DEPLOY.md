# Guia de Deploy em Produção — VPS único com Docker Compose

Este guia descreve o deploy do LGD Mantos completo (PostgreSQL + API FastAPI +
PWA React + Ollama) em um VPS, substituindo o modelo anterior Render + Vercel.

**Arquitetura de produção:**

```
Internet ──HTTPS──▶ Caddy (container web, portas 80/443)
                      ├── /            → PWA estático (build do Vite)
                      ├── /api/*       → backend FastAPI :8000
                      ├── /uploads/*   → backend (fotos de produtos)
                      └── /static/*    → backend
                    Rede interna do compose (sem portas expostas):
                      backend ──▶ db (Postgres 16) e ollama (llama3.1:8b)
```

Uma única origem pública (`https://SEU_DOMINIO`) serve frontend e API — por isso
o PWA usa caminho relativo `/api/v1` e o CORS deixa de ser um problema real.

---

## 1. Pré-requisitos (ações do usuário)

1. **Domínio**: registrar (ex.: Registro.br para `.com.br`, ~R$40/ano). Um
   subdomínio como `app.seudominio.com.br` é suficiente.
2. **VPS**: contratar com no mínimo **4 vCPU / 16 GB RAM / 100+ GB NVMe**
   (o llama3.1:8b consome ~6-8 GB de RAM durante a inferência).
   Recomendação avaliada em jul/2026: Hostinger KVM 4 (4 vCPU/16 GB/200 GB,
   data center São Paulo). Alternativas: Vultr São Paulo, Magalu Cloud.
   SO: **Ubuntu 24.04 LTS**.
3. **DNS**: criar registro `A` do domínio apontando para o IP do VPS.
   Propagação deve estar completa antes do primeiro `up` (o Caddy emite o
   certificado HTTPS na primeira subida).

## 2. Preparar o servidor

```bash
# Como root no VPS:
apt update && apt upgrade -y
curl -fsSL https://get.docker.com | sh

# Firewall: só SSH e web expostos.
ufw allow OpenSSH && ufw allow 80 && ufw allow 443 && ufw enable
```

## 3. Clonar e configurar

```bash
git clone https://github.com/LucasGS520/LGD-Mantos.git /opt/lgd-mantos
cd /opt/lgd-mantos
cp .env.example .env
nano .env
```

Preencher no `.env` (todos obrigatórios em produção):

| Variável | Valor |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:<senha-nova>@db:5432/lgd_mantos` |
| `POSTGRES_PASSWORD` | mesma `<senha-nova>` da linha acima |
| `APP_PASSWORD` | senha de login do PWA — **valor novo**, não reutilizar o exposto |
| `APP_SECRET` | `openssl rand -hex 32` — **valor novo**, não reutilizar o exposto |
| `DOMAIN` | `app.seudominio.com.br` |
| `CORS_ORIGINS` | `https://app.seudominio.com.br` |
| `OLLAMA_URL` | `http://ollama:11434` |

> ⚠️ Os segredos antigos vazaram no histórico do git (ver
> FABLE_CONSOLIDACAO_2026-07-16.md §3.3). Este deploy é o momento natural da
> rotação: use valores novos para os três.

## 4. Migrar os dados do Render (antes de desligar o serviço antigo)

```bash
# 1. No painel do Render, copie a "External Database URL" do Postgres.
# 2. Dump direto do banco do Render (roda no VPS):
docker run --rm postgres:16-alpine pg_dump "<EXTERNAL_DATABASE_URL_DO_RENDER>" \
  --no-owner --no-privileges > /opt/lgd-mantos/render_dump.sql

# 3. Suba apenas o banco novo e restaure:
docker compose -f docker-compose.prod.yml up -d db
docker exec -i lgd_db psql -U postgres -d lgd_mantos < /opt/lgd-mantos/render_dump.sql
```

Se o sistema no Render estiver vazio ou com dados descartáveis, pule esta etapa —
o `init_db.py` cria o schema do zero via Alembic no primeiro boot.

## 5. Subir a stack completa

```bash
cd /opt/lgd-mantos
docker compose -f docker-compose.prod.yml up -d --build

# Acompanhar o primeiro boot (migrations + download do modelo ~5 GB):
docker compose -f docker-compose.prod.yml logs -f backend model-init
```

Verificações pós-deploy:

| Checagem | Esperado |
|---|---|
| `https://SEU_DOMINIO` | PWA carrega com cadeado HTTPS |
| `https://SEU_DOMINIO/api/v1/...` (login no PWA) | Token emitido |
| `docker exec lgd_ollama ollama list` | `llama3.1:8b` listado |
| Aba Marketing → Novo Run | Run completa (Ollama em produção!) |

## 6. Rotina de backup (obrigatório antes de considerar produção pronta)

```bash
# /opt/lgd-mantos/backup.sh — dump diário com retenção de 14 dias.
#!/bin/sh
set -e
BACKUP_DIR=/opt/lgd-mantos/backups
mkdir -p "$BACKUP_DIR"
docker exec lgd_db pg_dump -U postgres lgd_mantos | gzip \
  > "$BACKUP_DIR/lgd_$(date +%F).sql.gz"
find "$BACKUP_DIR" -name "lgd_*.sql.gz" -mtime +14 -delete
```

```bash
chmod +x /opt/lgd-mantos/backup.sh
crontab -e   # adicionar: 0 4 * * * /opt/lgd-mantos/backup.sh
```

Recomendado: sincronizar `backups/` para fora do VPS (ex.: `rclone` para um
drive) — backup no mesmo disco não protege contra perda do servidor.

## 7. Atualizações do sistema

```bash
cd /opt/lgd-mantos
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

Migrations rodam automaticamente no boot do backend (`init_db.py` → Alembic).

## 8. Desligamento do Render/Vercel (só após validar tudo acima)

1. Confirmar que o dump foi restaurado e o sistema novo está operante.
2. Suspender/deletar o serviço web e o Postgres no Render.
3. Deletar o projeto no Vercel.
4. Confirmar a rotação dos 3 segredos (feita no passo 3 — os valores antigos
   do histórico do git morrem junto com os serviços antigos).

## Solução de problemas

| Sintoma | Causa provável | Ação |
|---|---|---|
| Caddy não emite certificado | DNS ainda não propagou / porta 80 bloqueada | `dig SEU_DOMINIO`, conferir ufw |
| Run de agente falha com timeout | Modelo ainda baixando ou RAM insuficiente | `docker logs lgd_model_init`, `free -h` |
| Backend reinicia em loop | `.env` incompleto (APP_SECRET/APP_PASSWORD são obrigatórios) | `docker logs lgd_mantos` |
| PWA carrega mas API falha | `DOMAIN`/`CORS_ORIGINS` divergentes | conferir `.env` |
