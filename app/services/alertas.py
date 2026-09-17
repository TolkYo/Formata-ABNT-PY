"""Alertas de anomalia (Fase 2).

Verifica periodicamente a janela recente de eventos e alerta quando:
- a taxa de erro passa de ``ALERTA_TAXA_ERRO``; ou
- o volume passa de ``ALERTA_VOLUME_MAX`` (quando > 0).

Os alertas saem no log, no Sentry (se configurado) e, opcionalmente, em um
webhook (``ALERTA_WEBHOOK_URL`` — compatível com Slack/Discord). Um cooldown
evita repetição em sequência.
"""

import json
import logging
import time
import urllib.request

from app.core.config import settings
from app.services import metricas

logger = logging.getLogger(__name__)

_ultimo_alerta: dict[str, float] = {}


def _cooldown_liberado(tipo: str) -> bool:
    agora = time.monotonic()
    ultimo = _ultimo_alerta.get(tipo, 0.0)
    if agora - ultimo < settings.alerta_cooldown_min * 60:
        return False
    _ultimo_alerta[tipo] = agora
    return True


def _notificar(mensagem: str, **contexto) -> None:
    logger.warning("ALERTA: %s | %s", mensagem, contexto)

    try:
        from app.core.observabilidade import capturar_mensagem

        capturar_mensagem(mensagem, nivel="warning", **contexto)
    except Exception as erro:  # pragma: no cover - depende de infra
        logger.debug("Falha ao enviar alerta ao Sentry: %s", erro)

    if settings.alerta_webhook_url:
        payload = json.dumps(
            {"text": mensagem, "content": mensagem, "detalhe": contexto}
        ).encode("utf-8")
        requisicao = urllib.request.Request(
            settings.alerta_webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(requisicao, timeout=10).close()
        except Exception as erro:  # pragma: no cover - depende de infra
            logger.warning("Falha ao enviar webhook de alerta: %s", erro)


def verificar_anomalias() -> None:
    """Executa uma checagem da janela recente (chamado pelo loop de background)."""
    if not settings.persistencia_habilitada:
        return

    resumo = metricas.resumo_janela(settings.alerta_janela_min)
    if resumo["total"] < settings.alerta_min_documentos:
        return

    if resumo["taxa_erro"] >= settings.alerta_taxa_erro and _cooldown_liberado("taxa_erro"):
        _notificar(
            "Taxa de erro acima do limite",
            janela_min=settings.alerta_janela_min,
            limite=settings.alerta_taxa_erro,
            **resumo,
        )

    if (
        settings.alerta_volume_max > 0
        and resumo["total"] >= settings.alerta_volume_max
        and _cooldown_liberado("volume")
    ):
        _notificar(
            "Volume de uso acima do esperado",
            janela_min=settings.alerta_janela_min,
            volume_max=settings.alerta_volume_max,
            **resumo,
        )
