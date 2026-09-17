"""Métricas anônimas de uso (Fase 2)."""

import hashlib
import logging
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select

from app.core.config import settings
from app.db import db_disponivel, get_session_factory
from app.models import EventoFormatacao

logger = logging.getLogger(__name__)


def ip_para_hash(ip: str) -> str:
    """Retorna o hash do IP (nunca o IP puro)."""
    base = f"{settings.ip_hash_salt}:{ip or ''}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def registrar_evento(
    ip_hash: str,
    resultado: str,
    duracao_ms: int | None = None,
    tamanho_bytes: int | None = None,
) -> None:
    """Grava um evento de formatação. Best-effort: nunca quebra a requisição."""
    if not db_disponivel():
        return
    try:
        with get_session_factory()() as sessao:
            sessao.add(
                EventoFormatacao(
                    ip_hash=ip_hash,
                    resultado=resultado,
                    duracao_ms=duracao_ms,
                    tamanho_bytes=tamanho_bytes,
                )
            )
            sessao.commit()
    except Exception as erro:  # pragma: no cover - depende de infra
        logger.warning("Falha ao registrar evento de formatação: %s", erro)


def _montar_resumo(contagens: dict[str, int]) -> dict:
    sucesso = int(contagens.get("sucesso", 0))
    erro = int(contagens.get("erro", 0))
    estrutura = int(contagens.get("estrutura_invalida", 0))
    total = sucesso + erro + estrutura
    taxa_erro = round((erro + estrutura) / total, 4) if total else 0.0

    return {
        "total": total,
        "sucesso": sucesso,
        "erro": erro,
        "estrutura_invalida": estrutura,
        "taxa_erro": taxa_erro,
    }


def _filtro_periodo(stmt, de: date | None, ate: date | None):
    if de is not None:
        inicio = datetime.combine(de, time.min, tzinfo=timezone.utc)
        stmt = stmt.where(EventoFormatacao.created_at >= inicio)
    if ate is not None:
        fim = datetime.combine(ate, time.min, tzinfo=timezone.utc) + timedelta(days=1)
        stmt = stmt.where(EventoFormatacao.created_at < fim)
    return stmt


def resumo_uso(de: date | None = None, ate: date | None = None) -> dict:
    """Totais e taxa de erro no período informado."""
    stmt = _filtro_periodo(
        select(EventoFormatacao.resultado, func.count()).group_by(
            EventoFormatacao.resultado
        ),
        de,
        ate,
    )
    with get_session_factory()() as sessao:
        contagens = {resultado: total for resultado, total in sessao.execute(stmt).all()}
    return _montar_resumo(contagens)


def resumo_janela(minutos: int) -> dict:
    """Totais e taxa de erro nos últimos ``minutos`` (para alertas)."""
    desde = datetime.now(timezone.utc) - timedelta(minutes=max(minutos, 1))
    stmt = (
        select(EventoFormatacao.resultado, func.count())
        .where(EventoFormatacao.created_at >= desde)
        .group_by(EventoFormatacao.resultado)
    )
    with get_session_factory()() as sessao:
        contagens = {resultado: total for resultado, total in sessao.execute(stmt).all()}
    resumo = _montar_resumo(contagens)
    resumo["janela_min"] = minutos
    return resumo


def por_dia(de: date | None = None, ate: date | None = None) -> list[dict]:
    """Série diária de documentos processados."""
    dia = func.date(EventoFormatacao.created_at).label("dia")
    stmt = _filtro_periodo(
        select(dia, EventoFormatacao.resultado, func.count()).group_by(
            dia, EventoFormatacao.resultado
        ),
        de,
        ate,
    ).order_by(dia)

    agregado: dict[str, dict] = {}
    with get_session_factory()() as sessao:
        for data_ref, resultado, total in sessao.execute(stmt).all():
            chave = data_ref.isoformat() if hasattr(data_ref, "isoformat") else str(data_ref)
            linha = agregado.setdefault(
                chave,
                {"data": chave, "total": 0, "sucesso": 0, "erro": 0, "estrutura_invalida": 0},
            )
            linha[resultado] = linha.get(resultado, 0) + int(total)
            linha["total"] += int(total)

    return [agregado[chave] for chave in sorted(agregado)]
