import os


def _int_env(nome: str, padrao: int) -> int:
    try:
        return int(os.getenv(nome, str(padrao)))
    except (TypeError, ValueError):
        return padrao


def _float_env(nome: str, padrao: float) -> float:
    try:
        return float(os.getenv(nome, str(padrao)))
    except (TypeError, ValueError):
        return padrao


def _bool_env(nome: str, padrao: bool = False) -> bool:
    valor = os.getenv(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "sim", "yes", "on"}


class Settings:
    """Configurações da aplicação, lidas de variáveis de ambiente."""

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "Formatador ABNT API")
        self.version: str = os.getenv("APP_VERSION", "1.0.0")
        self.max_upload_mb: int = _int_env("MAX_UPLOAD_MB", 20)
        self.doacoes_url: str | None = os.getenv("DOACOES_URL") or None
        self.cors_origins: list[str] = [
            origem.strip()
            for origem in os.getenv("CORS_ORIGINS", "*").split(",")
            if origem.strip()
        ]

        # Fase 2 — persistência de métricas/auditoria
        self.database_url: str | None = os.getenv("DATABASE_URL") or None
        self.admin_api_key: str | None = os.getenv("ADMIN_API_KEY") or None
        self.ip_hash_salt: str = os.getenv("IP_HASH_SALT", "")
        self.auto_criar_tabelas: bool = _bool_env("AUTO_CRIAR_TABELAS", False)

        # Fase 2 — observabilidade (Sentry)
        self.sentry_dsn: str | None = os.getenv("SENTRY_DSN") or None
        self.sentry_environment: str = os.getenv("SENTRY_ENVIRONMENT", "production")
        self.sentry_traces_sample_rate: float = _float_env("SENTRY_TRACES_SAMPLE_RATE", 0.0)

        # Fase 2 — alertas de anomalia
        self.alerta_webhook_url: str | None = os.getenv("ALERTA_WEBHOOK_URL") or None
        self.alerta_intervalo_min: int = _int_env("ALERTA_INTERVALO_MIN", 15)
        self.alerta_janela_min: int = _int_env("ALERTA_JANELA_MIN", 15)
        self.alerta_taxa_erro: float = _float_env("ALERTA_TAXA_ERRO", 0.3)
        self.alerta_min_documentos: int = _int_env("ALERTA_MIN_DOCUMENTOS", 10)
        self.alerta_volume_max: int = _int_env("ALERTA_VOLUME_MAX", 0)
        self.alerta_cooldown_min: int = _int_env("ALERTA_COOLDOWN_MIN", 60)

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def persistencia_habilitada(self) -> bool:
        return bool(self.database_url)

    @property
    def admin_habilitado(self) -> bool:
        return bool(self.admin_api_key)

    @property
    def sentry_habilitado(self) -> bool:
        return bool(self.sentry_dsn)

    @property
    def alertas_ativos(self) -> bool:
        canal = bool(self.alerta_webhook_url) or self.sentry_habilitado
        return self.persistencia_habilitada and canal


settings = Settings()
