from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.bot.container import Container

import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from app.services.key_service import (
    KeyAlreadyActivatedError, KeyNotFoundError,
    KeyInvalidError, UserBlacklistedError
)
from app.utils.validators import validar_key_format
from app.utils.formatters import saldo_bar


logger = logging.getLogger(__name__)


class KeyHandler:
    AGUARDANDO_KEY = 10

    def __init__(self, container: Container):
        self._c = container

    async def iniciar(self, update: Update, context: CallbackContext) -> int:
        args = context.args
        if args:
            return await self._processar(update, context, args[0])
        await update.message.reply_text("Digite sua key de acesso:\nex: FFSK-XXXXXXXX-XXXXXXXX-XXXXXXXX")
        return self.AGUARDANDO_KEY

    async def receber_key(self, update: Update, context: CallbackContext) -> int:
        return await self._processar(update, context, update.message.text.strip())

    async def _processar(self, update: Update, context: CallbackContext, key_str: str) -> int:
        if not validar_key_format(key_str):
            await update.message.reply_text("Formato invalido. Use: FFSK-XXXXXXXX-XXXXXXXX-XXXXXXXX")
            return ConversationHandler.END

        uid = str(update.effective_user.id)
        try:
            key = await self._c.key_service.ativar(key_str, uid)
            sb = saldo_bar(key.usos_restantes, key.limite_req)
            texto = "*Key ativada!*\n\n" + sb["texto"] + "\n\nUse /criar para criar sua primeira sala."
            await update.message.reply_text(texto, parse_mode="Markdown")
        except KeyAlreadyActivatedError as e:
            await update.message.reply_text("Key ja ativada: " + str(e))
        except KeyNotFoundError:
            await update.message.reply_text("Key nao encontrada.")
        except KeyInvalidError as e:
            await update.message.reply_text("Key invalida: " + str(e))
        except UserBlacklistedError as e:
            await update.message.reply_text("Acesso bloqueado: " + str(e))
        except Exception as e:
            logger.error("[KEY] erro: " + str(e))
            await update.message.reply_text("Erro ao ativar key. Contate o suporte.")

        return ConversationHandler.END

    async def cancelar(self, update: Update, context: CallbackContext) -> int:
        await update.message.reply_text("Operacao cancelada.")
        return ConversationHandler.END
