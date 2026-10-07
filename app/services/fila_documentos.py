"""Fila Redis/RQ e armazenamento temporario dos documentos.

O Redis guarda somente metadados. Entradas e resultados ficam em um volume
privado, identificados por UUID, e sao removidos por download ou expiracao.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import time
import uuid
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any

from docx import Document
from redis import Redis
from rq import Queue, get_current_job
from rq.exceptions import NoSuchJobError
from rq.job import Job

from app.core.config import settings
from app.formatter import (
    adicionar_capa,
    adicionar_sumario,
    formatar_abnt,
    formatar_titulos,
    validar_estrutura,
)
from app.services import metricas

ID_RE = re.compile(r"^[a-f0-9]{32}$")


class FilaIndisponivel(RuntimeError):
    """Redis ou a fila nao estao acessiveis."""


class FilaCheia(RuntimeError):
    """A fila atingiu o limite operacional."""


class JobNaoEncontrado(RuntimeError):
    """O job nao existe ou ja expirou."""


def _raiz() -> Path:
    raiz = Path(settings.jobs_dir)
    raiz.mkdir(parents=True, exist_ok=True, mode=0o700)
    return raiz


def _pasta_job(job_id: str) -> Path:
    if not ID_RE.fullmatch(job_id):
        raise JobNaoEncontrado(job_id)
    return _raiz() / job_id


@lru_cache(maxsize=1)
def conexao_redis() -> Redis:
    return Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=2,
        socket_timeout=2,
        health_check_interval=30,
        decode_responses=False,
    )


def obter_fila() -> Queue:
    return Queue(settings.fila_nome, connection=conexao_redis(), serializer="json")


def fila_disponivel() -> bool:
    if not settings.fila_habilitada:
        return False
    try:
        return bool(conexao_redis().ping())
    except Exception:
        return False


def validar_docx_bytes(nome: str, conteudo: bytes) -> None:
    nome_lower = nome.lower()
    if nome_lower.endswith(".doc") and not nome_lower.endswith(".docx"):
        raise ValueError(
            "Arquivos .doc antigos nao sao suportados. Salve como .docx para continuar."
        )
    if not nome_lower.endswith(".docx"):
        raise ValueError("Apenas arquivos .docx sao permitidos.")
    if not conteudo:
        raise ValueError("O arquivo enviado esta vazio.")
    if len(conteudo) > settings.max_upload_bytes:
        raise OverflowError(
            f"Arquivo acima do limite de {settings.max_upload_mb} MB."
        )
    try:
        with zipfile.ZipFile(io.BytesIO(conteudo)) as pacote:
            nomes = set(pacote.namelist())
            if "[Content_Types].xml" not in nomes or "word/document.xml" not in nomes:
                raise ValueError
    except (ValueError, zipfile.BadZipFile):
        raise ValueError(
            "Nao foi possivel ler o .docx. O arquivo pode estar corrompido."
        )


def _nome_saida(nome_original: str) -> str:
    nome = nome_original.replace("\\", "/").rsplit("/", 1)[-1]
    base = os.path.splitext(nome)[0] or "documento"
    return f"{base}_formatado.docx"


def enfileirar(
    *,
    conteudo: bytes,
    nome_original: str,
    modo: str,
    opcoes: dict[str, Any],
    ip_hash: str,
) -> dict[str, Any]:
    if not settings.fila_habilitada:
        raise FilaIndisponivel("Fila desabilitada.")
    validar_docx_bytes(nome_original, conteudo)

    try:
        fila = obter_fila()
        if fila.count >= settings.fila_max_jobs:
            raise FilaCheia("Fila temporariamente cheia.")
    except FilaCheia:
        raise
    except Exception as erro:
        raise FilaIndisponivel("Nao foi possivel acessar a fila.") from erro

    job_id = uuid.uuid4().hex
    pasta = _pasta_job(job_id)
    pasta.mkdir(mode=0o700)
    entrada = pasta / "entrada.docx"
    try:
        with entrada.open("xb") as arquivo:
            arquivo.write(conteudo)
        nome_saida = _nome_saida(nome_original)
        job = fila.enqueue_call(
            func="app.services.fila_documentos.processar_documento",
            args=(job_id, modo, opcoes, ip_hash),
            job_id=job_id,
            timeout=settings.job_timeout_segundos,
            ttl=settings.job_fila_ttl_segundos,
            result_ttl=settings.job_ttl_segundos,
            failure_ttl=settings.job_ttl_segundos,
            description=f"Formatacao {modo}",
            meta={
                "nome_saida": nome_saida,
                "tamanho": len(conteudo),
                "mensagem": "Documento aguardando processamento.",
            },
        )
        posicao = job.get_position()
        return {
            "id": job.id,
            "status": "na_fila",
            "posicao": (posicao + 1) if posicao is not None else 1,
            "nome_saida": nome_saida,
        }
    except Exception:
        shutil.rmtree(pasta, ignore_errors=True)
        raise FilaIndisponivel("Nao foi possivel adicionar o documento a fila.")


def processar_documento(
    job_id: str,
    modo: str,
    opcoes: dict[str, Any],
    ip_hash: str,
) -> dict[str, Any]:
    """Funcao executada pelo worker RQ em processo isolado."""
    inicio = time.perf_counter()
    tamanho: int | None = None
    resultado = "erro"
    pasta = _pasta_job(job_id)
    entrada = pasta / "entrada.docx"
    temporario = pasta / "saida.tmp"
    saida = pasta / "saida.docx"
    job = get_current_job()

    try:
        tamanho = entrada.stat().st_size
        if job is not None:
            job.meta["mensagem"] = "Documento em processamento."
            job.save_meta()

        documento = Document(str(entrada))
        if modo != "abnt":
            raise ValueError("Modo de formatacao invalido.")
        if opcoes.get("validar"):
            faltantes = validar_estrutura(documento)
            if faltantes:
                raise ValueError(
                    "Documento fora da estrutura minima. Secoes ausentes: "
                    + ", ".join(faltantes)
                )
        formatar_abnt(documento)
        formatar_titulos(documento)
        if opcoes.get("incluir_sumario"):
            adicionar_sumario(documento)
        if opcoes.get("incluir_capa"):
            adicionar_capa(documento, opcoes.get("dados") or {})
        resumo = {}

        documento.save(str(temporario))
        os.replace(temporario, saida)
        resultado = "sucesso"
        if job is not None:
            job.meta.update(
                {
                    "mensagem": "Documento pronto para download.",
                    "resumo": resumo,
                }
            )
            job.save_meta()
        return {"arquivo": "saida.docx"}
    except Exception as erro:
        if job is not None:
            mensagem = str(erro) if isinstance(erro, ValueError) else "Falha ao processar o documento."
            job.meta["mensagem"] = mensagem
            job.save_meta()
        raise
    finally:
        entrada.unlink(missing_ok=True)
        temporario.unlink(missing_ok=True)
        duracao_ms = int((time.perf_counter() - inicio) * 1000)
        metricas.registrar_evento(ip_hash, resultado, duracao_ms, tamanho)


def obter_job(job_id: str) -> Job:
    _pasta_job(job_id)
    try:
        return Job.fetch(job_id, connection=conexao_redis(), serializer="json")
    except NoSuchJobError as erro:
        raise JobNaoEncontrado(job_id) from erro
    except Exception as erro:
        raise FilaIndisponivel("Nao foi possivel consultar a fila.") from erro


def status_job(job_id: str) -> dict[str, Any]:
    job = obter_job(job_id)
    status_rq = str(job.get_status(refresh=True))
    meta = job.get_meta(refresh=True) or {}
    mapa = {
        "JobStatus.QUEUED": "na_fila",
        "JobStatus.STARTED": "processando",
        "JobStatus.FINISHED": "concluido",
        "JobStatus.FAILED": "erro",
        "JobStatus.CANCELED": "cancelado",
        "queued": "na_fila",
        "started": "processando",
        "finished": "concluido",
        "failed": "erro",
        "canceled": "cancelado",
        "stopped": "erro",
    }
    status = mapa.get(status_rq, status_rq.lower())
    posicao = None
    if status == "na_fila":
        valor = job.get_position()
        posicao = (valor + 1) if valor is not None else None

    return {
        "id": job.id,
        "status": status,
        "posicao": posicao,
        "mensagem": meta.get("mensagem") or "Aguardando atualizacao.",
        "nome_saida": meta.get("nome_saida") or "documento_formatado.docx",
        "download_url": f"/jobs/{job.id}/download" if status == "concluido" else None,
    }


def caminho_download(job_id: str) -> tuple[Path, str]:
    dados = status_job(job_id)
    if dados["status"] != "concluido":
        raise RuntimeError("Documento ainda nao esta pronto.")
    caminho = _pasta_job(job_id) / "saida.docx"
    if not caminho.is_file():
        raise JobNaoEncontrado(job_id)
    return caminho, str(dados["nome_saida"])


def remover_job(job_id: str, *, apagar_redis: bool = True) -> None:
    pasta = _pasta_job(job_id)
    shutil.rmtree(pasta, ignore_errors=True)
    if apagar_redis:
        try:
            job = obter_job(job_id)
            if str(job.get_status(refresh=True)) in {"queued", "JobStatus.QUEUED"}:
                job.cancel()
            job.delete()
        except (JobNaoEncontrado, FilaIndisponivel):
            pass


def limpar_expirados() -> int:
    raiz = _raiz()
    limite = time.time() - settings.job_fila_ttl_segundos
    removidos = 0
    for pasta in raiz.iterdir():
        try:
            if pasta.is_dir() and ID_RE.fullmatch(pasta.name) and pasta.stat().st_mtime < limite:
                shutil.rmtree(pasta, ignore_errors=True)
                removidos += 1
        except FileNotFoundError:
            continue
    return removidos
