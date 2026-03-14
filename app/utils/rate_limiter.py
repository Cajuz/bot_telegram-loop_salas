import time
from collections import defaultdict
from app.config.constants import RATE_LIMIT_MAX, RATE_LIMIT_BLOCK_SECONDS


class RateLimiter:
    """
    Rate limiter em memória.
    Substituível por Redis em produção — basta implementar a mesma interface.
    """
    def __init__(self, max_attempts: int = RATE_LIMIT_MAX,
                  block_duration: int = RATE_LIMIT_BLOCK_SECONDS):
        self._max = max_attempts
        self._block = block_duration
        self._state: dict[str, dict] = defaultdict(
            lambda: {"tentativas": 0, "bloqueado_ate": 0}
        )

    def check(self, user_id: str) -> tuple[bool, int]:
        """Retorna (bloqueado, segundos_restantes)."""
        agora = time.time()
        reg = self._state[user_id]

        if reg["bloqueado_ate"] > agora:
            return True, int(reg["bloqueado_ate"] - agora) + 1

        if reg["bloqueado_ate"] > 0:
            self._state[user_id] = {"tentativas": 0, "bloqueado_ate": 0}
            reg = self._state[user_id]

        reg["tentativas"] += 1
        if reg["tentativas"] >= self._max:
            reg["bloqueado_ate"] = agora + self._block
            reg["tentativas"] = 0
            return True, self._block

        return False, 0

    def reset(self, user_id: str) -> None:
        self._state.pop(user_id, None)
