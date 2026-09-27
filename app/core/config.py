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
        # Doacao via PIX (BR Code estatico). A chave fica so no servidor.
        self.pix_chave: str | None = os.getenv("PIX_CHAVE") or None
        self.pix_nome: str = os.getenv("PIX_NOME", "").strip()
        self.pix_cidade: str = os.getenv("PIX_CIDADE", "").strip()
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

        # Fase 3 — fila de processamento de documentos
        self.fila_habilitada: bool = _bool_env("FILA_HABILITADA", False)
        self.redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.fila_nome: str = os.getenv("FILA_NOME", "documentos")
        self.fila_max_jobs: int = _int_env("FILA_MAX_JOBS", 20)
        self.job_timeout_segundos: int = _int_env("JOB_TIMEOUT_SEGUNDOS", 180)
        self.job_ttl_segundos: int = _int_env("JOB_TTL_SEGUNDOS", 900)
        self.job_fila_ttl_segundos: int = _int_env("JOB_FILA_TTL_SEGUNDOS", 1800)
        self.jobs_dir: str = os.getenv("JOBS_DIR", "/data/jobs")

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def pix_habilitado(self) -> bool:
        return bool(self.pix_chave and self.pix_nome and self.pix_cidade)

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
