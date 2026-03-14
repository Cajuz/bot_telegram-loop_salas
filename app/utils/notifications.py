import logging
from telegram import Bot
from app.config.settings import settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, bot: Bot):
        self._bot = bot

    async def notify_owner(self, text: str) -> None:
        for owner_id in (settings.OWNER_ID, settings.NOTIF_ID):
            try:
                await self._bot.send_message(chat_id=int(owner_id), text=text,
                                              parse_mode="Markdown")
            except Exception as e:
                logger.warning(f"[NOTIF] owner {owner_id}: {e}")

    async def dm_user(self, telegram_id: str | int, text: str) -> None:
        try:
            await self._bot.send_message(chat_id=int(telegram_id), text=text,
                                          parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"[DM] {telegram_id}: {e}")

    async def log_venda(self, telegram_id: str, quantidade: int,
                         valor: float, payment_id: str) -> None:
        msg = (
            f"💰 *Nova Compra*
"
            f"Usuário: `{telegram_id}`
"
            f"Salas: *{quantidade}*
"
            f"Valor: R$ {valor:.2f}
"
            f"Payment ID: `{payment_id}`"
        )
        try:
            await self._bot.send_message(
                chat_id=int(settings.LOG_VENDAS_CHAT_ID),
                text=msg, parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"[LOG_VENDAS] {e}")
        await self.notify_owner(msg)
