import asyncio
import logging
from app.payments.wallet_client import WalletClient
from app.repositories.payment_repository import PaymentRepository
from app.repositories.key_repository import KeyRepository

logger = logging.getLogger(__name__)


class PaymentService:
    POLL_INTERVAL = 10
    POLL_MAX = 60

    def __init__(self, wallet: WalletClient, payment_repo: PaymentRepository,
                  key_repo: KeyRepository):
        self._wallet = wallet
        self._payments = payment_repo
        self._keys = key_repo

    async def iniciar_compra(self, telegram_id: str, quantidade: int,
                              valor: float, cpf: str) -> dict:
        ts = int(asyncio.get_event_loop().time())
        ext_id = f"salasff-{telegram_id}-{ts}"
        data = await self._wallet.criar_pagamento(
            amount=valor,
            payer_name=f"Telegram {telegram_id}",
            payer_document=cpf,
            description=f"Salas FF — {quantidade} salas",
            external_id=ext_id,
        )
        await self._payments.salvar(
            payment_id=data["id"],
            telegram_id=telegram_id,
            plano_id="",
            quantidade=quantidade,
            valor=valor,
            cpf=cpf,
        )
        return data

    def iniciar_polling(self, payment_id: str, telegram_id: str,
                         quantidade: int, on_success, on_failure) -> None:
        asyncio.create_task(
            self._poll(payment_id, telegram_id, quantidade, on_success, on_failure)
        )

    async def _poll(self, payment_id, telegram_id, quantidade,
                     on_success, on_failure):
        for _ in range(self.POLL_MAX):
            await asyncio.sleep(self.POLL_INTERVAL)
            try:
                data = await self._wallet.consultar(payment_id)
                inner = data.get("data") or data
                status = inner.get("status", "").upper()
                logger.info(f"[POLLING] {payment_id} → {status}")

                if status == "COMPLETO":
                    existing = await self._payments.buscar(payment_id)
                    if existing and existing.status == "completed":
                        return
                    await self._payments.atualizar_status(payment_id, "completed")
                    await self._keys.adicionar_usos(telegram_id, quantidade)
                    await on_success()
                    return

                if status in {"CANCELADO", "FALHOU", "EXPIRADO", "FAILED", "EXPIRED"}:
                    await self._payments.atualizar_status(payment_id, status.lower())
                    await on_failure(status)
                    return
            except Exception as e:
                logger.warning(f"[POLLING] erro: {e}")

        await on_failure("TIMEOUT")
