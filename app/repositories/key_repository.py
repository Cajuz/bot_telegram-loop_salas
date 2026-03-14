import time
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.key import Key
from app.repositories.base_repository import BaseRepository


def gerar_key() -> str:
    p = lambda: secrets.token_hex(4).upper()
    return f"FFSK-{p()}-{p()}-{p()}"


class KeyRepository(BaseRepository[Key]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Key)

    async def buscar_por_telegram(self, telegram_id: str) -> Key | None:
        r = await self._session.execute(
            select(Key).where(Key.telegram_id == str(telegram_id))
        )
        return r.scalar_one_or_none()

    async def buscar_por_key(self, key_str: str) -> Key | None:
        r = await self._session.execute(
            select(Key).where(Key.key_str == key_str)
        )
        return r.scalar_one_or_none()

    async def criar(self, plano_id: str, telegram_id: str | None,
                    limite: int, descricao: str = "Gerada via bot") -> Key:
        key = Key(
            key_str=gerar_key(),
            descricao=descricao,
            plano_id=plano_id,
            telegram_id=telegram_id,
            limite_req=limite,
            usos_restantes=limite,
            ativa=True,
            criada_em=int(time.time() * 1000),
        )
        return await self.save(key)

    async def decrementar_uso(self, key_str: str) -> None:
        agora = int(time.time() * 1000)
        await self._session.execute(
            update(Key)
            .where(Key.key_str == key_str)
            .values(
                usos_restantes=Key.usos_restantes - 1,
                ultimo_uso=agora,
                ativa=(Key.usos_restantes - 1) > 0,
            )
        )
        await self._session.commit()

    async def adicionar_usos(self, telegram_id: str, quantidade: int) -> None:
        k = await self.buscar_por_telegram(telegram_id)
        if k:
            k.usos_restantes += quantidade
            k.limite_req = max(k.limite_req, k.usos_restantes)
            k.ativa = True
            await self._session.commit()

    async def listar(self) -> list[Key]:
        return await self.get_all()

    async def deletar_nao_resgatadas(self) -> int:
        keys = await self._session.execute(
            select(Key).where(Key.ativa == True, Key.telegram_id == None)
        )
        items = list(keys.scalars().all())
        for k in items:
            await self._session.delete(k)
        await self._session.commit()
        return len(items)
