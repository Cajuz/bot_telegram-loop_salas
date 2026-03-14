import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.payment import Payment
from app.repositories.base_repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Payment)

    async def salvar(self, payment_id: str, telegram_id: str,
                      plano_id: str, quantidade: int, valor: float,
                      cpf: str = None) -> Payment:
        p = Payment(
            payment_id=payment_id,
            telegram_id=str(telegram_id),
            plano_id=plano_id,
            quantidade=quantidade,
            valor=valor,
            cpf=cpf,
            status="pending",
            criado_em=int(time.time() * 1000),
        )
        return await self.save(p)

    async def buscar(self, payment_id: str) -> Payment | None:
        r = await self._session.execute(
            select(Payment).where(Payment.payment_id == payment_id)
        )
        return r.scalar_one_or_none()

    async def atualizar_status(self, payment_id: str, status: str) -> None:
        await self._session.execute(
            update(Payment).where(Payment.payment_id == payment_id)
            .values(status=status)
        )
        await self._session.commit()
