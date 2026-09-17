import io
import os
import time
from typing import Optional

from docx import Document
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.config import settings
from app.formatter import (
    adicionar_capa,
    adicionar_sumario,
    formatar_abnt,
    formatar_titulos,
    validar_estrutura,
)
from app.services import metricas

router = APIRouter(tags=["Publico"])

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class DadosCapa(BaseModel):
    instituicao: Optional[str] = None
    curso: Optional[str] = None
    autor: Optional[str] = None
    titulo: Optional[str] = None
    subtitulo: Optional[str] = None
    cidade: Optional[str] = None
    ano: Optional[str] = None


def _client_ip(request: Request) -> str:
    encaminhado = request.headers.get("x-forwarded-for")
    if encaminhado:
        return encaminhado.split(",")[0].strip()
    return request.client.host if request.client else "desconhecido"


async def _ler_docx(file: UploadFile) -> tuple[Document, int]:
    nome = (file.filename or "").lower()

    if nome.endswith(".doc") and not nome.endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail=(
                "Arquivos .doc antigos não são suportados. Abra o documento no "
                "Word e salve como .docx para continuar."
            ),
        )
    if not nome.endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail="Apenas arquivos .docx são permitidos.",
        )

    conteudo = await file.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")
    if len(conteudo) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo acima do limite de {settings.max_upload_mb} MB.",
        )

    try:
        return Document(io.BytesIO(conteudo)), len(conteudo)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível ler o .docx. O arquivo pode estar corrompido.",
        )


def _parse_dados(dados: Optional[str]) -> dict:
    if not dados:
        return {}
    try:
        return DadosCapa.model_validate_json(dados).model_dump()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="O campo 'dados' deve ser um JSON válido.",
        )


@router.post("/formatar")
async def formatar_documento(
    request: Request,
    file: UploadFile = File(...),
    dados: Optional[str] = Form(None),
    incluir_capa: bool = Form(False),
    incluir_sumario: bool = Form(False),
    validar: bool = Form(False),
):
    """Formata um .docx nas normas ABNT e devolve o arquivo para download.

    Uso livre e ilimitado, sem cota de negócio. Um rate limit técnico contra
    abuso é aplicado na borda (nginx), podendo responder 429 temporariamente.
    """
    inicio = time.perf_counter()
    ip_hash = metricas.ip_para_hash(_client_ip(request))
    tamanho: Optional[int] = None
    resultado = "erro"

    try:
        doc, tamanho = await _ler_docx(file)
        dados_capa = _parse_dados(dados)

        if validar:
            faltantes = validar_estrutura(doc)
            if faltantes:
                resultado = "estrutura_invalida"
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Documento fora da estrutura mínima. "
                        f"Seções ausentes: {', '.join(faltantes)}."
                    ),
                )

        formatar_abnt(doc)
        formatar_titulos(doc)

        if incluir_sumario:
            adicionar_sumario(doc)
        if incluir_capa:
            adicionar_capa(doc, dados_capa)

        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        nome_base = os.path.splitext(file.filename or "documento")[0]
        nome_saida = f"{nome_base}_formatado.docx"

        resultado = "sucesso"
        return StreamingResponse(
            output,
            media_type=DOCX_MIME,
            headers={"Content-Disposition": f'attachment; filename="{nome_saida}"'},
        )
    except HTTPException as exc:
        resultado = "estrutura_invalida" if exc.status_code == 422 else "erro"
        raise
    except Exception as erro:
        resultado = "erro"
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar o arquivo: {erro}",
        )
    finally:
        duracao_ms = int((time.perf_counter() - inicio) * 1000)
        metricas.registrar_evento(ip_hash, resultado, duracao_ms, tamanho)


@router.post("/formatar/validar")
async def validar_documento(file: UploadFile = File(...)):
    """Valida a estrutura mínima do documento sem formatar."""
    doc, _ = await _ler_docx(file)
    faltantes = validar_estrutura(doc)
    return {"valido": not faltantes, "secoes_ausentes": faltantes}
