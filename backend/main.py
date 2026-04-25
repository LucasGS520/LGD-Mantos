"""Ponto de entrada HTTP da API LGD Mantos.

Este módulo configura a aplicação FastAPI, registra os roteadores versionados e
expõe os diretórios estáticos usados para arquivos enviados pelo sistema.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.ai.routes import router as ai_router
from app.modules.analytics.routes.routes import router as analytics_router
from app.modules.auth.routes import router as auth_router
from app.modules.marketing.routes.routes import router as marketing_router
from app.modules.operational.routes import router as operational_router

app = FastAPI(title="LGD Mantos", version="2.0", docs_url="/api/docs")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router, prefix="/api/v1")
app.include_router(operational_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(marketing_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")

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
