import logging
from telegram import Update
from telegram.ext import BaseHandler, CallbackContext
from app.repositories.blacklist_repository import BlacklistRepository
from app.utils.rate_limiter import RateLimiter
from app.config.settings import settings

logger = logging.getLogger(__name__)


class BlacklistMiddleware(BaseHandler):
    def __init__(self, blacklist_repo: BlacklistRepository):
        super().__init__(self._check)
        self._bl = blacklist_repo

    async def _check(self, update: Update, context: CallbackContext):
        if not update.effective_user:
            return
        uid = str(update.effective_user.id)
        if uid in (settings.OWNER_ID, settings.OWNER2_ID):
            return
        bl = await self._bl.check(uid)
        if bl:
            if update.message:
                await update.message.reply_text(
                    "🚫 *Acesso Bloqueado*
Você foi bloqueado e não pode usar este bot.",
                    parse_mode="Markdown"
                )
            raise StopIteration

    def check_update(self, update):
        return isinstance(update, Update)
