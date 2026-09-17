import secrets
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.core.config import settings
from app.db import db_disponivel
from app.services import auditoria, metricas

router = APIRouter(prefix="/admin", tags=["Admin"])


def exigir_admin(x_admin_key: Optional[str] = Header(default=None, alias="X-Admin-Key")) -> None:
    """Valida a chave administrativa (sem contas de usuário)."""
    if not settings.admin_habilitado:
        raise HTTPException(
            status_code=503,
            detail="Painel admin não configurado (defina ADMIN_API_KEY).",
        )
    if not x_admin_key or not secrets.compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(
            status_code=401,
            detail="Chave administrativa inválida.",
            headers={"WWW-Authenticate": "X-Admin-Key"},
        )


def exigir_persistencia() -> None:
    if not db_disponivel():
        raise HTTPException(
            status_code=503,
            detail="Persistência não configurada (defina DATABASE_URL).",
        )


@router.get("/metricas/uso", dependencies=[Depends(exigir_admin), Depends(exigir_persistencia)])
def metricas_uso(
    de: Optional[date] = Query(None, description="Data inicial (inclusive)"),
    ate: Optional[date] = Query(None, description="Data final (inclusive)"),
):
    """Métricas de uso (documentos, erros) no período."""
    resultado = {
        "resumo": metricas.resumo_uso(de, ate),
        "por_dia": metricas.por_dia(de, ate),
    }
    auditoria.registrar(
        "metricas.consultar",
        detalhe={"de": de.isoformat() if de else None, "ate": ate.isoformat() if ate else None},
    )
    return resultado


@router.get("/auditoria", dependencies=[Depends(exigir_admin), Depends(exigir_persistencia)])
def listar_auditoria(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """Trilha de auditoria administrativa (mais recentes primeiro)."""
    resultado = auditoria.listar(page, per_page)
    auditoria.registrar("auditoria.consultar", detalhe={"page": page})
    return resultado
