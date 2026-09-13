from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.quota import quota_limiter
from app.routers.formatar import router as formatar_router

app = FastAPI(
    title=settings.app_name,
    description="API para formatar documentos .docx nas normas ABNT",
    version=settings.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(formatar_router)


@app.get("/", tags=["Publico"])
async def root():
    return {"mensagem": "API de Formatação ABNT está funcionando!"}


@app.get("/health", tags=["Publico"])
async def health():
    return {
        "status": "ok",
        "version": settings.version,
        "quota_anonima_dia": settings.quota_anonima_dia,
        "quota_backend": quota_limiter.backend,
    }
