"""Cliente CLI do normalizador FAMETRO usado pela API.

Uso básico:
    python normalizar_fametro.py artigo.docx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from docx import Document

from app.services.normalizacao_fametro import normalizar_documento


def caminho_padrao(entrada: Path) -> Path:
    return entrada.with_name(f"{entrada.stem} - normalizado.docx")


def argumentos(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Normaliza estilos de um artigo DOCX conforme o modelo FAMETRO."
    )
    parser.add_argument("entrada", type=Path, help="documento .docx a normalizar")
    parser.add_argument("-o", "--saida", type=Path, help="caminho do documento resultante")
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="permite substituir um arquivo de saída já existente",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = argumentos(argv)
    entrada = args.entrada.resolve()
    saida = (args.saida or caminho_padrao(args.entrada)).resolve()

    if entrada.suffix.lower() != ".docx":
        print("Erro: a entrada precisa ser um arquivo .docx.", file=sys.stderr)
        return 2
    if not entrada.is_file():
        print(f"Erro: arquivo não encontrado: {entrada}", file=sys.stderr)
        return 2
    if entrada == saida:
        print("Erro: use um caminho de saída diferente para preservar o original.", file=sys.stderr)
        return 2
    if saida.exists() and not args.sobrescrever:
        print(
            f"Erro: a saída já existe: {saida}\nUse --sobrescrever para substituí-la.",
            file=sys.stderr,
        )
        return 2
    if not saida.parent.is_dir():
        print(f"Erro: diretório de saída inexistente: {saida.parent}", file=sys.stderr)
        return 2

    try:
        documento = Document(entrada)
        totais = normalizar_documento(documento)
        documento.save(saida)
    except Exception as erro:
        print(f"Erro ao normalizar o documento: {erro}", file=sys.stderr)
        return 1

    usados = ", ".join(
        f"{nome}: {quantidade}" for nome, quantidade in totais.items() if quantidade
    )
    print(f"Documento normalizado: {saida}")
    print(f"Parágrafos classificados — {usados}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
