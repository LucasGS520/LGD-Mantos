"""Ponto de entrada HTTP da API LGD Mantos.

Este módulo configura a aplicação FastAPI, registra os roteadores versionados e
os sinais de requisição/disponibilidade. Arquivos são entregues por rotas autenticadas.
"""

from app.core.config import settings
from app.core.version import API_VERSION
from app.http_telemetry import RequestTelemetry
from app.modules.auth.routes import router as auth_router
from app.modules.auxiliaries.router import router as auxiliaries_router
from app.modules.catalog.router import router as catalog_router
from app.modules.history.router import router as history_router
from app.modules.management.router import router as management_router
from app.modules.operations.router import router as operations_router
from app.modules.photos.router import router as photos_router
from app.modules.system.routes import router as system_router
from app.shared.application.errors import ApplicationError
from app.shared.application.telemetry import configure
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

configure()
app = FastAPI(title="LGD Mantos", version=API_VERSION, docs_url="/api/docs")
app.add_middleware(RequestTelemetry)

# Origens permitidas vêm da configuração (CORS_ORIGINS no ambiente).
# Em desenvolvimento local o padrão cobre o Vite (localhost:5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(auxiliaries_router, prefix="/api/v1")
app.include_router(catalog_router, prefix="/api/v1")
app.include_router(photos_router, prefix="/api/v1")
app.include_router(operations_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")
app.include_router(management_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")

# Fotos são entregues pelo endpoint autenticado; não há diretório público.


@app.get("/", include_in_schema=False)
async def health():
    """Retorna um status simples para checagens de disponibilidade da API."""
    return {"status": "ok", "service": "LGD Mantos API"}


@app.exception_handler(ApplicationError)
async def application_error_handler(request, exc: ApplicationError):
    """Mantém o contrato de erro HTTP na borda da aplicação."""
    headers = (
        {"Retry-After": "60" if exc.status_code == 429 else "1"}
        if exc.status_code in {429, 503}
        else None
    )
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}, headers=headers
    )
