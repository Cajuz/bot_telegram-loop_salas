import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.room import RoomLog
from app.repositories.base_repository import BaseRepository


class RoomRepository(BaseRepository[RoomLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RoomLog)

    async def log_sala(self, telegram_id: str, room_id: str,
                        sshash: str, modo: int, key_str: str | None) -> RoomLog:
        entry = RoomLog(
            telegram_id=str(telegram_id),
            room_id=room_id,
            sshash=sshash,
            modo=modo,
            key_str=key_str,
            criado_em=int(time.time() * 1000),
        )
        return await self.save(entry)

    async def historico_usuario(self, telegram_id: str, limite: int = 50) -> list[RoomLog]:
        r = await self._session.execute(
            select(RoomLog)
            .where(RoomLog.telegram_id == str(telegram_id))
            .order_by(RoomLog.criado_em.desc())
            .limit(limite)
        )
        return list(r.scalars().all())

    async def clientes_ativos_hoje(self) -> list[dict]:
        inicio = int(time.time() * 1000) - 24 * 3600 * 1000
        r = await self._session.execute(
            select(RoomLog.telegram_id, func.count().label("total"))
            .where(RoomLog.criado_em >= inicio)
            .group_by(RoomLog.telegram_id)
            .order_by(func.count().desc())
        )
        return [{"telegram_id": row[0], "total": row[1]} for row in r.all()]

    async def total_salas_periodo(self, desde_ms: int = 0) -> int:
        r = await self._session.execute(
            select(func.count()).where(RoomLog.criado_em >= desde_ms)
        )
        return r.scalar() or 0
