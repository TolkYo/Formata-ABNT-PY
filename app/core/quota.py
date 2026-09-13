import logging
import threading
import time
from collections import defaultdict, deque

from app.core.config import settings

try:  # redis é opcional
    import redis as _redis
except ImportError:  # pragma: no cover - ambiente sem redis
    _redis = None

logger = logging.getLogger(__name__)

JANELA_SEGUNDOS = 24 * 60 * 60


class QuotaLimiter:
    """Cota anônima por chave (IP).

    Usa Redis se ``REDIS_URL`` estiver configurado e o pacote ``redis`` estiver
    instalado; caso contrário, mantém a contagem em memória (janela deslizante).
    """

    def __init__(self, limite: int, redis_url: str | None = None) -> None:
        self.limite = limite
        self._memoria: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        self._redis = self._conectar(redis_url)
        self.backend = "redis" if self._redis is not None else "memoria"

    def _conectar(self, redis_url: str | None):
        if not redis_url:
            return None
        if _redis is None:
            logger.warning(
                "REDIS_URL definido, mas o pacote 'redis' não está instalado; "
                "usando cota em memória."
            )
            return None
        try:
            cliente = _redis.Redis.from_url(redis_url, decode_responses=True)
            cliente.ping()
            return cliente
        except Exception as erro:  # pragma: no cover - depende de infra
            logger.warning("Falha ao conectar no Redis (%s); usando memória.", erro)
            return None

    def hit(self, chave: str) -> tuple[bool, int]:
        """Registra um uso e devolve ``(permitido, restante)``."""
        if self._redis is not None:
            return self._hit_redis(chave)
        return self._hit_memoria(chave)

    def restante(self, chave: str) -> int:
        """Consulta o restante sem consumir."""
        if self._redis is not None:
            usado = int(self._redis.get(self._chave_redis(chave)) or 0)
            return max(self.limite - usado, 0)
        agora = time.time()
        with self._lock:
            fila = self._memoria[chave]
            while fila and fila[0] <= agora - JANELA_SEGUNDOS:
                fila.popleft()
            return max(self.limite - len(fila), 0)

    def _hit_memoria(self, chave: str) -> tuple[bool, int]:
        agora = time.time()
        with self._lock:
            fila = self._memoria[chave]
            while fila and fila[0] <= agora - JANELA_SEGUNDOS:
                fila.popleft()
            if len(fila) >= self.limite:
                return False, 0
            fila.append(agora)
            return True, self.limite - len(fila)

    @staticmethod
    def _chave_redis(chave: str) -> str:
        dia = time.strftime("%Y-%m-%d", time.gmtime())
        return f"quota:{chave}:{dia}"

    def _hit_redis(self, chave: str) -> tuple[bool, int]:
        chave_redis = self._chave_redis(chave)
        with self._redis.pipeline() as pipe:
            pipe.incr(chave_redis)
            pipe.expire(chave_redis, JANELA_SEGUNDOS)
            usado, _ = pipe.execute()
        usado = int(usado)
        permitido = usado <= self.limite
        return permitido, max(self.limite - usado, 0)


quota_limiter = QuotaLimiter(settings.quota_anonima_dia, settings.redis_url)
