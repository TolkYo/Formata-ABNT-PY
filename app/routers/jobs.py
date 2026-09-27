"""API assincrona para enfileirar, acompanhar e baixar documentos."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.core.config import settings
from app.routers.formatar import DOCX_MIME, DadosCapa, _client_ip
from app.services import fila_documentos, metricas

router = APIRouter(prefix="/jobs", tags=["Fila"])


def _dados_capa(dados: Optional[str]) -> dict:
    if not dados:
        return {}
    try:
        return DadosCapa.model_validate_json(dados).model_dump()
    except Exception:
        raise HTTPException(status_code=400, detail="O campo 'dados' deve ser um JSON valido.")


def _disposition(nome: str) -> str:
    seguro = Path(nome.replace("\\", "/")).name.replace('"', "")
    fallback = seguro.encode("ascii", "ignore").decode("ascii")
    fallback = re.sub(r"[^A-Za-z0-9._-]+", "_", fallback).strip("._") or "documento.docx"
    return f'attachment; filename="{fallback}"; filename*=UTF-8\'\'{quote(seguro)}'


def _traduzir_erro(erro: Exception) -> HTTPException:
    if isinstance(erro, fila_documentos.FilaCheia):
        return HTTPException(
            status_code=429,
            detail="A fila esta cheia. Aguarde alguns minutos e tente novamente.",
            headers={"Retry-After": "30"},
        )
    if isinstance(erro, fila_documentos.FilaIndisponivel):
        return HTTPException(
            status_code=503,
            detail="A fila esta temporariamente indisponivel.",
            headers={"Retry-After": "15"},
        )
    if isinstance(erro, fila_documentos.JobNaoEncontrado):
        return HTTPException(status_code=404, detail="Trabalho nao encontrado ou expirado.")
    if isinstance(erro, OverflowError):
        return HTTPException(status_code=413, detail=str(erro))
    if isinstance(erro, ValueError):
        return HTTPException(status_code=400, detail=str(erro))
    return HTTPException(status_code=500, detail="Nao foi possivel enfileirar o documento.")


@router.post("/formatar", status_code=202)
def criar_job_formatacao(
    request: Request,
    file: UploadFile = File(...),
    modo: str = Form("abnt"),
    dados: Optional[str] = Form(None),
    incluir_capa: bool = Form(False),
    incluir_sumario: bool = Form(False),
    validar: bool = Form(False),
):
    if modo not in {"abnt", "fametro"}:
        raise HTTPException(status_code=400, detail="Modo deve ser 'abnt' ou 'fametro'.")
    conteudo = file.file.read(settings.max_upload_bytes + 1)
    opcoes = {
        "dados": _dados_capa(dados),
        "incluir_capa": incluir_capa,
        "incluir_sumario": incluir_sumario,
        "validar": validar,
    }
    try:
        retorno = fila_documentos.enfileirar(
            conteudo=conteudo,
            nome_original=file.filename or "documento.docx",
            modo=modo,
            opcoes=opcoes,
            ip_hash=metricas.ip_para_hash(_client_ip(request)),
        )
        retorno["status_url"] = f"/jobs/{retorno['id']}"
        return retorno
    except Exception as erro:
        raise _traduzir_erro(erro)


@router.get("/{job_id}")
def consultar_job(job_id: str):
    try:
        return fila_documentos.status_job(job_id)
    except Exception as erro:
        raise _traduzir_erro(erro)


@router.get("/{job_id}/download", response_class=FileResponse)
def baixar_job(job_id: str):
    try:
        caminho, nome = fila_documentos.caminho_download(job_id)
    except RuntimeError as erro:
        raise HTTPException(status_code=409, detail=str(erro))
    except Exception as erro:
        raise _traduzir_erro(erro)
    return FileResponse(
        caminho,
        media_type=DOCX_MIME,
        filename=nome,
        headers={"Content-Disposition": _disposition(nome)},
        background=BackgroundTask(fila_documentos.remover_job, job_id),
    )


@router.delete("/{job_id}", status_code=204)
def cancelar_job(job_id: str):
    try:
        dados = fila_documentos.status_job(job_id)
        if dados["status"] == "processando":
            raise HTTPException(status_code=409, detail="Documento ja esta em processamento.")
        fila_documentos.remover_job(job_id)
    except HTTPException:
        raise
    except Exception as erro:
        raise _traduzir_erro(erro)
    return None
