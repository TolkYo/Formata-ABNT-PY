"""Integração com Sentry (Fase 2), opcional via SENTRY_DSN."""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def init_sentry() -> bool:
    """Inicializa o SDK do Sentry. Sem DSN, é um no-op."""
    if not settings.sentry_habilitado:
        return False
    try:
        import sentry_sdk
    except ImportError:  # pragma: no cover - dependência opcional
        logger.warning("SENTRY_DSN definido, mas o pacote sentry-sdk não está instalado.")
        return False

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        release=f"{settings.app_name}@{settings.version}",
        traces_sample_rate=settings.sentry_traces_sample_rate,
        send_default_pii=False,
    )
    logger.info("Sentry inicializado (environment=%s).", settings.sentry_environment)
    return True


def capturar_mensagem(mensagem: str, nivel: str = "warning", **contexto) -> None:
    """Envia uma mensagem ao Sentry, se configurado."""
    if not settings.sentry_habilitado:
        return
    try:
        import sentry_sdk
    except ImportError:  # pragma: no cover
        return

    with sentry_sdk.push_scope() as escopo:
        for chave, valor in contexto.items():
            escopo.set_extra(chave, valor)
        sentry_sdk.capture_message(mensagem, level=nivel)
