"""Trilha de auditoria administrativa (Fase 2)."""

import logging
import uuid

from sqlalchemy import func, select

from app.db import db_disponivel, get_session_factory
from app.models import AdminAuditoria

logger = logging.getLogger(__name__)


def registrar(
    acao: str,
    alvo_tipo: str | None = None,
    alvo_id: uuid.UUID | None = None,
    detalhe: dict | None = None,
) -> None:
    """Grava um registro de auditoria. Best-effort."""
    if not db_disponivel():
        return
    try:
        with get_session_factory()() as sessao:
            sessao.add(
                AdminAuditoria(
                    acao=acao,
                    alvo_tipo=alvo_tipo,
                    alvo_id=alvo_id,
                    detalhe=detalhe,
                )
            )
            sessao.commit()
    except Exception as erro:  # pragma: no cover - depende de infra
        logger.warning("Falha ao registrar auditoria administrativa: %s", erro)


def _serializar(registro: AdminAuditoria) -> dict:
    return {
        "id": str(registro.id),
        "acao": registro.acao,
        "alvo_tipo": registro.alvo_tipo,
        "alvo_id": str(registro.alvo_id) if registro.alvo_id else None,
        "detalhe": registro.detalhe,
        "created_at": registro.created_at.isoformat() if registro.created_at else None,
    }


def listar(page: int = 1, per_page: int = 20) -> dict:
    """Lista paginada, mais recentes primeiro."""
    offset = (page - 1) * per_page
    with get_session_factory()() as sessao:
        total = sessao.scalar(select(func.count()).select_from(AdminAuditoria)) or 0
        registros = sessao.scalars(
            select(AdminAuditoria)
            .order_by(AdminAuditoria.created_at.desc())
            .limit(per_page)
            .offset(offset)
        ).all()

    return {
        "total": int(total),
        "page": page,
        "per_page": per_page,
        "itens": [_serializar(registro) for registro in registros],
    }
