"""Ponto de entrada da aplicação FastAPI."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import ai, auth, products
from modules.analytics.api.router import router as analytics_router
from modules.marketing.api.router import router as marketing_router
from modules.operational.api.router import router as operational_router

app = FastAPI(title="Loja Gestão", version="2.0", docs_url="/api/docs")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Rotas legadas permanecem em /api/v1 para auth, catálogo e IA central.
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")

# Módulos de domínio com prefixos explícitos para melhorar organização e leitura de contrato.
app.include_router(operational_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(marketing_router, prefix="/api/v1")

static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
uploads_dir = os.path.join(static_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
@app.get("/{full_path:path}", include_in_schema=False)
async def spa(full_path: str = ""):
    """Entrega o frontend SPA para rotas não-API."""
    if full_path.startswith("api/"):
        return {"detail": "Not Found"}
    return FileResponse(os.path.join(static_dir, "index.html"))
