import logging
from app.repositories.key_repository import KeyRepository
from app.repositories.blacklist_repository import BlacklistRepository
from app.models.key import Key

logger = logging.getLogger(__name__)


class KeyAlreadyActivatedError(Exception): pass
class KeyNotFoundError(Exception): pass
class KeyInvalidError(Exception): pass
class UserBlacklistedError(Exception): pass


class KeyService:
    def __init__(self, key_repo: KeyRepository,
                  blacklist_repo: BlacklistRepository):
        self._keys = key_repo
        self._bl = blacklist_repo

    async def ativar(self, key_str: str, telegram_id: str) -> Key:
        bl = await self._bl.check(telegram_id)
        if bl:
            raise UserBlacklistedError(bl.motivo or "Acesso bloqueado.")

        key = await self._keys.buscar_por_key(key_str)
        if not key:
            raise KeyNotFoundError("Key não encontrada.")
        if not key.ativa or key.usos_restantes <= 0:
            raise KeyInvalidError("Key inativa ou sem usos.")
        if key.telegram_id:
            if key.telegram_id == str(telegram_id):
                raise KeyAlreadyActivatedError("Você já ativou esta key.")
            raise KeyAlreadyActivatedError("Key já usada por outro usuário.")

        # Acumula saldo da key antiga
        antiga = await self._keys.buscar_por_telegram(telegram_id)
        saldo_acc = antiga.usos_restantes if antiga else 0
        if antiga:
            antiga.telegram_id = None
            antiga.ativa = False
            await self._keys._session.commit()

        key.telegram_id = str(telegram_id)
        if saldo_acc > 0:
            key.usos_restantes += saldo_acc
            key.limite_req += saldo_acc
        await self._keys._session.commit()
        return key

    async def validar(self, telegram_id: str) -> Key:
        key = await self._keys.buscar_por_telegram(telegram_id)
        if not key or not key.ativa or key.usos_restantes <= 0:
            raise KeyInvalidError("Sem key ativa ou saldo esgotado.")
        return key

    async def gerar(self, plano_id: str, quantidade: int,
                     limite: int, telegram_id: str | None = None) -> list[Key]:
        keys = []
        for _ in range(quantidade):
            k = await self._keys.criar(plano_id, telegram_id, limite)
            keys.append(k)
        return keys
