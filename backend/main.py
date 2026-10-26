""" Ponto de entrada HTTP da API LGD Mantos.

Este módulo configura a aplicação FastAPI, registra os roteadores versionados e
expõe os diretórios estáticos usados para arquivos enviados pelo sistema.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.version import API_VERSION
from app.modules.agents.routes import router as agents_router
from app.modules.analytics.routes.routes import router as analytics_router
from app.modules.auth.routes import router as auth_router
from app.modules.export.routes import router as export_router
from app.modules.operational.routes import router as operational_router
from app.modules.settings.routes import router as settings_router
from app.modules.system.routes import router as system_router

app = FastAPI(title="LGD Mantos", version=API_VERSION, docs_url="/api/docs")

# Origens permitidas vêm da configuração (CORS_ORIGINS no ambiente).
# Em desenvolvimento local o padrão cobre o Vite (localhost:5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
    # Sem isso, o Content-Disposition chega na resposta HTTP mas o navegador não
    # deixa o fetch() do frontend ler o header em requisições cross-origin (ex.:
    # dev com VITE_API_URL apontando para outra porta) — o nome do arquivo some e
    # o download cai no fallback genérico (ver app.modules.export.routes).
    expose_headers=["Content-Disposition"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(operational_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")

# Garante que a pasta de uploads exista antes de montar os arquivos estáticos.
static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
uploads_dir = os.path.join(static_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
async def health():
    """Retorna um status simples para checagens de disponibilidade da API."""
    return {"status": "ok", "service": "LGD Mantos API"}
