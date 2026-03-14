import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_or_create(self, telegram_id: str, username: str = None,
                             first_name: str = None) -> User:
        r = await self._session.execute(
            select(User).where(User.telegram_id == str(telegram_id))
        )
        user = r.scalar_one_or_none()
        if user:
            user.last_seen = int(time.time() * 1000)
            await self._session.commit()
            return user
        user = User(
            telegram_id=str(telegram_id),
            username=username,
            first_name=first_name,
            created_at=int(time.time() * 1000),
            last_seen=int(time.time() * 1000),
        )
        return await self.save(user)
