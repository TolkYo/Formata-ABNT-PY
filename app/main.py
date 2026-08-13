from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from docx import Document
import io
import os

from app.formatter import (
    formatar_abnt,
    formatar_titulos,
    adicionar_capa,
    adicionar_sumario,
    validar_estrutura,
)

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="Formatador ABNT API",
    description="API para formatar documentos .docx nas normas ABNT",
    version="1.0.0"
)


class DadosCapa(BaseModel):
    instituicao: Optional[str] = None
    curso: Optional[str] = None
    autor: Optional[str] = None
    titulo: Optional[str] = None
    subtitulo: Optional[str] = None
    cidade: Optional[str] = None
    ano: Optional[str] = None


@app.post("/formatar")
async def formatar_documento(
    file: UploadFile = File(...),
    dados: Optional[str] = Form(None),
    incluir_capa: bool = Form(False),
    incluir_sumario: bool = Form(False),
    validar: bool = Form(False),
):
    """
    Endpoint que recebe um arquivo .docx, aplica a formatação ABNT
    e retorna o arquivo modificado para download.

    Parâmetros opcionais (form):
    - dados: JSON com os dados da capa (instituicao, curso, autor, titulo, subtitulo, cidade, ano).
    - incluir_capa: se "true", insere a capa no início do documento.
    - incluir_sumario: se "true", insere um sumário automático (TOC).
    - validar: se "true", valida a estrutura mínima antes de formatar.
    """

    # 1. Validação da extensão do arquivo
    if not file.filename.endswith(('.docx', '.doc')):
        raise HTTPException(
            status_code=400,
            detail="Apenas arquivos com extensão .docx ou .doc são permitidos."
        )

    # 2. Interpreta os dados da capa (se fornecidos)
    dados_capa = {}
    if dados:
        try:
            dados_capa = DadosCapa.model_validate_json(dados).model_dump()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="O campo 'dados' deve ser um JSON válido."
            )

    try:
        # 3. Leitura do arquivo enviado (em memória)
        conteudo = await file.read()
        doc = Document(io.BytesIO(conteudo))

        # 4. Validação estrutural (opcional)
        if validar:
            faltantes = validar_estrutura(doc)
            if faltantes:
                raise HTTPException(
                    status_code=422,
                    detail=f"Documento fora da estrutura mínima. Seções ausentes: {', '.join(faltantes)}."
                )

        # 5. Aplica a formatação ABNT (margens, fonte, espaçamento e títulos)
        formatar_abnt(doc)
        formatar_titulos(doc)

        # 6. Insere elementos iniciais (sumário antes, para a capa ficar na frente)
        if incluir_sumario:
            adicionar_sumario(doc)
        if incluir_capa:
            adicionar_capa(doc, dados_capa)

        # 7. Salva o documento formatado em um buffer de memória (BytesIO)
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)  # Volta o ponteiro para o início do arquivo

        # 8. Define o nome do arquivo de saída
        nome_base = os.path.splitext(file.filename)[0]
        nome_saida = f"{nome_base}_formatado.docx"

        # 9. Retorna o arquivo via StreamingResponse (não salva no disco)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={nome_saida}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar o arquivo: {str(e)}"
        )


# (Opcional) Endpoint de saúde para verificar se a API está no ar
@app.get("/")
async def root():
    return {"mensagem": "API de Formatação ABNT está funcionando!"}
