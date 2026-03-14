from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.bot.container import Container

import io
import logging
import base64
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from app.config.constants import PLANOS
from app.utils.formatters import price_calc
from app.utils.validators import validar_cpf


logger = logging.getLogger(__name__)

AGUARDANDO_QUANTIDADE = 1
AGUARDANDO_CPF = 2


class PaymentHandler:
    def __init__(self, container: Container):
        self._c = container

    async def iniciar(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        await query.answer()
        keyboard = []
        for p in PLANOS:
            label = p["emoji"] + " " + p["label"] + " - " + p["preco"]
            keyboard.append([InlineKeyboardButton(label, callback_data="pay:qtd:" + str(p["reqs"]))])
        keyboard.append([InlineKeyboardButton("Cancelar", callback_data="pay:qtd:0")])
        await query.edit_message_text("Selecione a quantidade de salas:",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        return AGUARDANDO_QUANTIDADE

    async def selecionar_qtd(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        await query.answer()
        qtd = int(query.data.split(":")[2])
        if qtd == 0:
            await query.edit_message_text("Compra cancelada.")
            return ConversationHandler.END
        valor = price_calc(qtd)
        context.user_data["pay_qtd"] = qtd
        context.user_data["pay_valor"] = valor
        texto = str(qtd) + " salas - R$ " + "{:.2f}".format(valor) + "\n\nDigite seu CPF (apenas numeros):"
        await query.edit_message_text(texto)
        return AGUARDANDO_CPF

    async def receber_cpf(self, update: Update, context: CallbackContext) -> int:
        cpf = update.message.text.strip()
        if not validar_cpf(cpf):
            await update.message.reply_text("CPF invalido. Digite apenas os 11 numeros.")
            return AGUARDANDO_CPF

        qtd = context.user_data["pay_qtd"]
        valor = context.user_data["pay_valor"]
        uid = str(update.effective_user.id)

        await update.message.reply_text("Gerando PIX...")
        try:
            data = await self._c.payment_service.iniciar_compra(uid, qtd, valor, cpf)
        except Exception as e:
            logger.error("[PIX] erro: " + str(e))
            await update.message.reply_text("Erro ao gerar PIX. Tente novamente.")
            return ConversationHandler.END

        inner = data.get("data") or data
        pix_code = inner.get("pixCode", "")
        qr_b64 = inner.get("qrCode", "")
        payment_id = inner.get("id", data.get("id", ""))

        keyboard = [[InlineKeyboardButton("Verificar Pagamento",
                                          callback_data="pay:checar:" + payment_id)]]

        if qr_b64:
            try:
                img_bytes = base64.b64decode(qr_b64)
                await update.message.reply_photo(
                    photo=io.BytesIO(img_bytes),
                    caption="PIX gerado! Copie o codigo abaixo:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
            except Exception:
                pass

        if pix_code:
            await update.message.reply_text("`" + pix_code + "`", parse_mode="Markdown")

        async def on_success():
            await update.message.reply_text(
                "Pagamento confirmado! " + str(qtd) + " salas adicionadas. Use /criar."
            )

        async def on_failure(reason: str):
            await update.message.reply_text(
                "Pagamento " + reason + ". Use /comprar para tentar novamente."
            )

        self._c.payment_service.iniciar_polling(payment_id, uid, qtd, on_success, on_failure)
        return ConversationHandler.END

    async def cancelar(self, update: Update, context: CallbackContext) -> int:
        await update.message.reply_text("Compra cancelada.")
        return ConversationHandler.END
