import os


def _int_env(nome: str, padrao: int) -> int:
    try:
        return int(os.getenv(nome, str(padrao)))
    except (TypeError, ValueError):
        return padrao


class Settings:
    """Configurações da aplicação, lidas de variáveis de ambiente."""

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "Formatador ABNT API")
        self.version: str = os.getenv("APP_VERSION", "1.0.0")
        self.max_upload_mb: int = _int_env("MAX_UPLOAD_MB", 20)
        self.quota_anonima_dia: int = _int_env("QUOTA_ANONIMA_DIA", 3)
        self.redis_url: str | None = os.getenv("REDIS_URL") or None
        self.cors_origins: list[str] = [
            origem.strip()
            for origem in os.getenv("CORS_ORIGINS", "*").split(",")
            if origem.strip()
        ]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
