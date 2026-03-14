# Handlers de admin adicionais (callbacks inline de painéis admin)
import logging
from telegram import Update
from telegram.ext import CallbackContext
from app.bot.container import Container

logger = logging.getLogger(__name__)


class AdminHandler:
    def __init__(self, container: Container):
        self._c = container

    async def handle(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        # Extensível para callbacks de painéis admin inline
        action = query.data.split(":")[1] if ":" in query.data else ""
        logger.info(f"[ADMIN_CALLBACK] action={action}")
