from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.bot.container import Container

import io
import logging
from telegram import Update
from telegram.ext import CallbackContext
from app.config.settings import settings
from app.config.constants import PLANOS


logger = logging.getLogger(__name__)


def is_owner(user_id) -> bool:
    return str(user_id) in (settings.OWNER_ID, settings.OWNER2_ID)


class AdminCommands:
    def __init__(self, container: Container):
        self._c = container

    async def _guard(self, update: Update) -> bool:
        if not is_owner(update.effective_user.id):
            await update.message.reply_text("Apenas administradores.")
            return False
        return True

    async def gerar_key(self, update: Update, context: CallbackContext):
        if not await self._guard(update):
            return
        args = context.args
        if not args:
            await update.message.reply_text("Uso: /gerarkey <plano_id> [qtd]\nEx: /gerarkey p100 3")
            return
        plano_id = args[0]
        qtd = int(args[1]) if len(args) > 1 else 1
        plano = next((p for p in PLANOS if p["id"] == plano_id), None)
        if not plano:
            await update.message.reply_text("Plano " + plano_id + " nao encontrado.")
            return
        keys = await self._c.key_service.gerar(plano_id, qtd, plano["reqs"])
        linhas = ["`" + k.key_str + "`" for k in keys]
        await update.message.reply_text(
            str(qtd) + " key(s) gerada(s):\n\n" + "\n".join(linhas), parse_mode="Markdown"
        )

    async def dar_key(self, update: Update, context: CallbackContext):
        if not await self._guard(update):
            return
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Uso: /darkey <telegram_id> <plano_id>")
            return
        tid, plano_id = args[0], args[1]
        plano = next((p for p in PLANOS if p["id"] == plano_id), None)
        if not plano:
            await update.message.reply_text("Plano nao encontrado.")
            return
        keys = await self._c.key_service.gerar(plano_id, 1, plano["reqs"])
        key = keys[0]
        try:
            await context.bot.send_message(
                chat_id=int(tid),
                text="Key recebida:\n`" + key.key_str + "`\n\nUse /ativar para ativar.",
                parse_mode="Markdown"
            )
            await update.message.reply_text("Key enviada para " + tid + ".")
        except Exception as e:
            await update.message.reply_text("Nao foi possivel enviar DM: " + str(e))

    async def listar_keys(self, update: Update, context: CallbackContext):
        if not await self._guard(update):
            return
        keys = await self._c.admin_service.listar_keys()
        if not keys:
            await update.message.reply_text("Nenhuma key cadastrada.")
            return
        linhas = []
        for k in keys[:30]:
            status = "OK" if k.ativa else "XX"
            linhas.append("[" + status + "] `" + k.key_str + "` - " + str(k.usos_restantes) + " usos")
        await update.message.reply_text(
            "Keys (" + str(len(keys)) + " total):\n\n" + "\n".join(linhas), parse_mode="Markdown"
        )

    async def analytics(self, update: Update, context: CallbackContext):
        if not await self._guard(update):
            return
        await update.message.reply_text("Gerando analytics...")
        img = await self._c.analytics_service.gerar_grafico_salas()
        await update.message.reply_photo(photo=io.BytesIO(img), caption="Analytics")

    async def broadcast(self, update: Update, context: CallbackContext):
        if not await self._guard(update):
            return
        if not context.args:
            await update.message.reply_text("Uso: /broadcast <mensagem>")
            return
        mensagem = " ".join(context.args)
        keys = await self._c.key_repo.listar()
        enviados = falhos = 0
        for k in keys:
            if not k.telegram_id or not k.ativa:
                continue
            try:
                await context.bot.send_message(
                    chat_id=int(k.telegram_id),
                    text="Aviso:\n" + mensagem
                )
                enviados += 1
            except Exception:
                falhos += 1
        await update.message.reply_text(
            "Broadcast concluido!\nEntregues: " + str(enviados) + "\nFalhos: " + str(falhos)
        )

    async def blacklist(self, update: Update, context: CallbackContext):
        if not await self._guard(update):
            return
        args = context.args
        if not args:
            lista = await self._c.admin_service.blacklist_list()
            if not lista:
                await update.message.reply_text("Blacklist vazia.")
                return
            linhas = ["`" + b.telegram_id + "` - " + (b.motivo or "") for b in lista]
            await update.message.reply_text("Blacklist:\n\n" + "\n".join(linhas), parse_mode="Markdown")
            return
        action = args[0]
        if action == "add" and len(args) >= 2:
            motivo = " ".join(args[2:]) if len(args) > 2 else ""
            await self._c.admin_service.blacklist_add(args[1], motivo)
            await update.message.reply_text(args[1] + " adicionado a blacklist.")
        elif action == "rm" and len(args) >= 2:
            await self._c.admin_service.blacklist_remove(args[1])
            await update.message.reply_text(args[1] + " removido da blacklist.")

    async def rankadm(self, update: Update, context: CallbackContext):
        if not await self._guard(update):
            return
        ativos = await self._c.admin_service.clientes_ativos_hoje()
        if not ativos:
            await update.message.reply_text("Nenhum cliente ativo nas ultimas 24h.")
            return
        medals = ["1.", "2.", "3."]
        linhas = [
            (medals[i] if i < 3 else str(i + 1) + ".") + " `" + c["telegram_id"] + "` - " + str(c["total"]) + " salas"
            for i, c in enumerate(ativos)
        ]
        await update.message.reply_text("Ranking 24h:\n\n" + "\n".join(linhas), parse_mode="Markdown")

    async def delete_keys(self, update: Update, context: CallbackContext):
        if not await self._guard(update):
            return
        total = await self._c.admin_service.deletar_nao_resgatadas()
        await update.message.reply_text(str(total) + " keys nao resgatadas deletadas.")
