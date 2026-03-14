import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.blacklist import Blacklist
from app.repositories.base_repository import BaseRepository


class BlacklistRepository(BaseRepository[Blacklist]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Blacklist)

    async def add(self, telegram_id: str, motivo: str = "") -> None:
        existing = await self.check(telegram_id)
        if existing:
            return
        entry = Blacklist(
            telegram_id=str(telegram_id),
            motivo=motivo,
            criado_em=int(time.time() * 1000),
        )
        await self.save(entry)

    async def remove(self, telegram_id: str) -> None:
        await self._session.execute(
            delete(Blacklist).where(Blacklist.telegram_id == str(telegram_id))
        )
        await self._session.commit()

    async def check(self, telegram_id: str) -> Blacklist | None:
        r = await self._session.execute(
            select(Blacklist).where(Blacklist.telegram_id == str(telegram_id))
        )
        return r.scalar_one_or_none()

    async def listar(self) -> list[Blacklist]:
        return await self.get_all()
