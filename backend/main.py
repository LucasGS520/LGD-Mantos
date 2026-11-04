""" Ponto de entrada HTTP da API LGD Mantos.

Este módulo configura a aplicação FastAPI, registra os roteadores versionados e
expõe os diretórios estáticos usados para arquivos enviados pelo sistema.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.version import API_VERSION
from app.domain.routes import router as domain_router
from app.modules.auth.routes import router as auth_router
from app.modules.system.routes import router as system_router

app = FastAPI(title="LGD Mantos", version=API_VERSION, docs_url="/api/docs")

# Origens permitidas vêm da configuração (CORS_ORIGINS no ambiente).
# Em desenvolvimento local o padrão cobre o Vite (localhost:5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(domain_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")

# Fotos são entregues pelo endpoint autenticado; não há diretório público.


@app.get("/", include_in_schema=False)
async def health():
    """Retorna um status simples para checagens de disponibilidade da API."""
    return {"status": "ok", "service": "LGD Mantos API"}
