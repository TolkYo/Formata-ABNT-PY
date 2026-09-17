import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import observabilidade
from app.core.config import settings
from app.routers.admin import router as admin_router
from app.routers.formatar import router as formatar_router

logger = logging.getLogger(__name__)


async def _loop_alertas() -> None:
    from app.services import alertas

    intervalo = max(settings.alerta_intervalo_min, 1) * 60
    while True:
        try:
            await asyncio.to_thread(alertas.verificar_anomalias)
        except Exception as erro:  # pragma: no cover - depende de infra
            logger.warning("Falha no verificador de alertas: %s", erro)
        await asyncio.sleep(intervalo)


@asynccontextmanager
async def lifespan(app: FastAPI):
    observabilidade.init_sentry()

    if settings.auto_criar_tabelas and settings.persistencia_habilitada:
        try:
            from app.db import criar_tabelas

            criar_tabelas()
            logger.info("Tabelas verificadas/criadas via metadata (AUTO_CRIAR_TABELAS).")
        except Exception as erro:  # pragma: no cover - depende de infra
            logger.warning("Falha ao criar tabelas automaticamente: %s", erro)

    tarefa_alertas: asyncio.Task | None = None
    if settings.alertas_ativos:
        tarefa_alertas = asyncio.create_task(_loop_alertas())
        logger.info(
            "Verificador de alertas ativo (a cada %s min, janela de %s min).",
            settings.alerta_intervalo_min,
            settings.alerta_janela_min,
        )

    try:
        yield
    finally:
        if tarefa_alertas is not None:
            tarefa_alertas.cancel()
            with suppress(asyncio.CancelledError):
                await tarefa_alertas


app = FastAPI(
    title=settings.app_name,
    description="API para formatar documentos .docx nas normas ABNT",
    version=settings.version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(formatar_router)
app.include_router(admin_router)


@app.get("/", tags=["Publico"])
async def root():
    return {"mensagem": "API de Formatação ABNT está funcionando!"}


@app.get("/health", tags=["Publico"])
async def health():
    return {
        "status": "ok",
        "version": settings.version,
        "doacoes_url": settings.doacoes_url,
        "persistencia": settings.persistencia_habilitada,
    }
