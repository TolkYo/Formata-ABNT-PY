"""Conexão com o PostgreSQL (Fase 2).

A persistência é opcional: se ``DATABASE_URL`` não estiver definida, os eventos
de uso e a auditoria simplesmente não são gravados, e o núcleo de formatação
continua funcionando normalmente.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

_engine = None
_session_factory: sessionmaker[Session] | None = None


class Base(DeclarativeBase):
    """Base declarativa compartilhada pelos modelos."""


def db_disponivel() -> bool:
    return settings.persistencia_habilitada


def get_engine():
    global _engine
    if _engine is None:
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL não configurada.")
        _engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
        logger.info("Engine PostgreSQL inicializada.")
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            expire_on_commit=False,
            future=True,
        )
    return _session_factory


def criar_tabelas() -> None:
    """Cria as tabelas do metadata (uso opcional em dev; produção via Alembic)."""
    from app import models  # noqa: F401  (registra os modelos no metadata)

    Base.metadata.create_all(bind=get_engine())
