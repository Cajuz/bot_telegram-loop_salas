import logging
from app.repositories.key_repository import KeyRepository
from app.repositories.blacklist_repository import BlacklistRepository
from app.repositories.room_repository import RoomRepository

logger = logging.getLogger(__name__)


class AdminService:
    def __init__(self, key_repo: KeyRepository,
                  blacklist_repo: BlacklistRepository,
                  room_repo: RoomRepository):
        self._keys = key_repo
        self._bl = blacklist_repo
        self._rooms = room_repo

    async def blacklist_add(self, telegram_id: str, motivo: str) -> None:
        await self._bl.add(telegram_id, motivo)

    async def blacklist_remove(self, telegram_id: str) -> None:
        await self._bl.remove(telegram_id)

    async def blacklist_list(self):
        return await self._bl.listar()

    async def listar_keys(self):
        return await self._keys.listar()

    async def deletar_nao_resgatadas(self) -> int:
        return await self._keys.deletar_nao_resgatadas()

    async def clientes_ativos_hoje(self):
        return await self._rooms.clientes_ativos_hoje()
