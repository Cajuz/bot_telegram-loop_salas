from app.repositories.room_repository import RoomRepository
from app.repositories.key_repository import KeyRepository


class MetricsCollector:
    def __init__(self, room_repo: RoomRepository, key_repo: KeyRepository):
        self._rooms = room_repo
        self._keys = key_repo

    async def resumo(self) -> dict:
        total_salas = await self._rooms.total_salas_periodo()
        ativos_hoje = await self._rooms.clientes_ativos_hoje()
        keys = await self._keys.listar()
        ativas = sum(1 for k in keys if k.ativa and k.usos_restantes > 0)
        return {
            "total_salas": total_salas,
            "clientes_ativos_hoje": len(ativos_hoje),
            "keys_ativas": ativas,
            "keys_total": len(keys),
        }
