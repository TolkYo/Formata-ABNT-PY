"""Geracao do BR Code PIX estatico no padrao EMV/Bacen.

O payload nao contem dados sensiveis alem da chave escolhida: use uma chave
aleatoria (EVP) para nao expor CPF/telefone/e-mail. A geracao do QR acontece no
servidor (segno), sem enviar o payload a servicos de terceiros.
"""

from functools import lru_cache
import unicodedata

LIMITE_NOME = 25
LIMITE_CIDADE = 15
LIMITE_DESCRICAO = 72
LIMITE_TXID = 25


def _campo(id_campo: str, valor: str) -> str:
    return f"{id_campo}{len(valor):02d}{valor}"


def _normalizar(texto: str, limite: int) -> str:
    """Remove acentos, colapsa espacos e limita o tamanho (ASCII maiusculo)."""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return " ".join(sem_acento.upper().split())[:limite]


def _crc16(payload: str) -> str:
    """CRC16-CCITT (polinomio 0x1021, inicial 0xFFFF), conforme EMV/Bacen."""
    crc = 0xFFFF
    for caractere in payload:
        crc ^= ord(caractere) << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def montar_payload(
    chave: str,
    nome: str,
    cidade: str,
    descricao: str | None = None,
    txid: str | None = None,
) -> str:
    """Monta o BR Code (PIX copia e cola) de valor aberto."""
    conta = _campo("00", "br.gov.bcb.pix") + _campo("01", chave.strip())
    if descricao:
        conta += _campo("02", _normalizar(descricao, LIMITE_DESCRICAO))

    partes = [
        _campo("00", "01"),
        _campo("26", conta),
        _campo("52", "0000"),
        _campo("53", "986"),
        _campo("58", "BR"),
        _campo("59", _normalizar(nome, LIMITE_NOME)),
        _campo("60", _normalizar(cidade, LIMITE_CIDADE)),
        _campo("62", _campo("05", (txid or "***").strip()[:LIMITE_TXID] or "***")),
    ]
    base = "".join(partes) + "6304"
    return base + _crc16(base)


@lru_cache(maxsize=8)
def gerar_svg_data_uri(payload: str) -> str | None:
    """Retorna o QR como data URI SVG; None se a lib `segno` nao estiver disponivel."""
    try:
        import segno
    except ImportError:  # pragma: no cover - depende de instalacao
        return None

    qr = segno.make_qr(payload, error="m")
    return qr.svg_data_uri(scale=4, border=2, dark="#1b4d89")
