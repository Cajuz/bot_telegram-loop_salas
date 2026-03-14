from app.api_clients.base_client import BaseAPIClient
from app.config.settings import settings


class FreeFireClient(BaseAPIClient):
    def __init__(self):
        super().__init__(
            base_url=settings.FREEFIRE_BASE_URL,
            api_key=settings.FREEFIRE_OAUTH_KEY,
        )

    def _build_headers(self) -> dict:
        return {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

    async def create_room(self, modo: int, senha: str | None = None) -> dict:
        body = {"modo": modo}
        if senha:
            body["senha"] = senha
        return await self._request("POST", "/api/v1/create:room", body)

    async def get_room_info(self, room_id: str, sshash: str) -> dict:
        return await self._request("POST", "/api/v2/info:room",
                                    {"room_id": room_id, "sshash": sshash})

    async def start_room(self, room_id: str, sshash: str) -> dict:
        return await self._request("POST", "/api/v2/start:room",
                                    {"room_id": room_id, "sshash": sshash})

    async def check_room(self, room_id: str, sshash: str) -> dict:
        return await self._request("POST", "/api/v2/check:room",
                                    {"room_id": room_id, "sshash": sshash})

    async def kick_player(self, room_id: str, sshash: str,
                           player_id: str) -> dict:
        return await self._request("POST", "/api/v2/expulsar-player",
                                    {"room_id": room_id, "sshash": sshash,
                                     "player_id": player_id})
