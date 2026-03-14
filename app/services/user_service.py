from app.repositories.user_repository import UserRepository
from app.models.user import User


class UserService:
    def __init__(self, user_repo: UserRepository):
        self._users = user_repo

    async def get_or_create(self, telegram_id: str, username: str = None,
                              first_name: str = None) -> User:
        return await self._users.get_or_create(telegram_id, username, first_name)
