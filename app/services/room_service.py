import logging
from dataclasses import dataclass, field
from app.api_clients.freefire_client import FreeFireClient
from app.repositories.key_repository import KeyRepository
from app.repositories.room_repository import RoomRepository
from app.config.constants import MAX_SALAS_SIMULTANEAS

logger = logging.getLogger(__name__)


class InsufficientBalanceError(Exception): pass
class RoomLimitError(Exception): pass
class RoomNotFoundError(Exception): pass
class UnauthorizedError(Exception): pass


@dataclass
class ActiveRoom:
    room_id: str
    sshash: str
    senha: str
    modo: int
    criado_por: str
    go_foi: bool = False
    players: list = field(default_factory=list)


class RoomService:
    def __init__(self, ff_client: FreeFireClient,
                  key_repo: KeyRepository, room_repo: RoomRepository):
        self._ff = ff_client
        self._key_repo = key_repo
        self._room_repo = room_repo
        self._active: dict[str, ActiveRoom] = {}

    async def criar_sala(self, telegram_id: str, modo: int) -> ActiveRoom:
        key = await self._key_repo.buscar_por_telegram(telegram_id)
        if not key or not key.ativa or key.usos_restantes <= 0:
            raise InsufficientBalanceError("Saldo insuficiente ou key inativa.")

        user_rooms = [r for r in self._active.values()
                      if r.criado_por == telegram_id]
        if len(user_rooms) >= MAX_SALAS_SIMULTANEAS:
            raise RoomLimitError(f"Limite de {MAX_SALAS_SIMULTANEAS} salas simultâneas.")

        data = await self._ff.create_room(modo)
        room = ActiveRoom(
            room_id=data["room_id"],
            sshash=data["sshash"],
            senha=data.get("senha", ""),
            modo=modo,
            criado_por=str(telegram_id),
        )

        await self._key_repo.decrementar_uso(key.key_str)
        await self._room_repo.log_sala(
            telegram_id, room.room_id, room.sshash, modo, key.key_str
        )
        self._active[room.sshash] = room
        return room

    async def iniciar_sala(self, sshash: str, telegram_id: str) -> dict:
        room = self._active.get(sshash)
        if not room:
            raise RoomNotFoundError("Sala não encontrada na memória.")
        if room.criado_por != str(telegram_id):
            raise UnauthorizedError("Essa não é sua sala.")
        result = await self._ff.start_room(room.room_id, sshash)
        room.go_foi = True
        return result

    async def info_sala(self, sshash: str, telegram_id: str) -> dict:
        room = self._active.get(sshash)
        if not room or room.criado_por != str(telegram_id):
            raise RoomNotFoundError("Sala não encontrada.")
        return await self._ff.get_room_info(room.room_id, sshash)

    async def expulsar_player(self, sshash: str, telegram_id: str,
                               player_id: str) -> dict:
        room = self._active.get(sshash)
        if not room or room.criado_por != str(telegram_id):
            raise RoomNotFoundError("Sala não encontrada.")
        return await self._ff.kick_player(room.room_id, sshash, player_id)

    def get_salas_ativas(self, telegram_id: str) -> list[ActiveRoom]:
        return [r for r in self._active.values()
                if r.criado_por == str(telegram_id)]

    def remover_sala(self, sshash: str) -> None:
        self._active.pop(sshash, None)

    def get_sala(self, sshash: str) -> ActiveRoom | None:
        return self._active.get(sshash)
