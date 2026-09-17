"""Modelos SQLAlchemy (Fase 2).

Conforme o modelo de dados das specs:
- ``EVENTO_FORMATACAO``: métricas anônimas de uso (sem conteúdo, IP em hash).
- ``ADMIN_AUDITORIA``: trilha de auditoria das ações administrativas.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class EventoFormatacao(Base):
    __tablename__ = "evento_formatacao"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ip_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    resultado: Mapped[str] = mapped_column(String(20), nullable=False)
    duracao_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tamanho_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AdminAuditoria(Base):
    __tablename__ = "admin_auditoria"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    acao: Mapped[str] = mapped_column(String(60), nullable=False)
    alvo_tipo: Mapped[str | None] = mapped_column(String(40), nullable=True)
    alvo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    detalhe: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
