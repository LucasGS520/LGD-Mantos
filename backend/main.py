from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import auth, products, operations, analytics, ai

app = FastAPI(title="Loja Gestão", version="2.0", docs_url="/api/docs")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router,       prefix="/api/v1")
app.include_router(products.router,   prefix="/api/v1")
app.include_router(operations.router, prefix="/api/v1")
app.include_router(analytics.router,  prefix="/api/v1")
app.include_router(ai.router,         prefix="/api/v1")

static_dir  = os.path.join(os.path.dirname(__file__), "app", "static")
uploads_dir = os.path.join(static_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/static",  StaticFiles(directory=static_dir),  name="static")

@app.get("/", include_in_schema=False)
@app.get("/{full_path:path}", include_in_schema=False)
async def spa(full_path: str = ""):
    if full_path.startswith("api/"): return {"detail": "Not Found"}
    return FileResponse(os.path.join(static_dir, "index.html"))
