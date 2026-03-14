from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.bot.container import Container

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from app.config.constants import MODOS, PLANOS, SUPORTE_LINK
from app.utils.formatters import saldo_bar, ts_now


logger = logging.getLogger(__name__)


class UserCommands:
    def __init__(self, container: Container):
        self._c = container

    async def start(self, update: Update, context: CallbackContext):
        user = update.effective_user
        await self._c.user_service.get_or_create(str(user.id), user.username, user.first_name)
        keyboard = [[InlineKeyboardButton("Menu Principal", callback_data="menu:abrir")]]
        nome = user.first_name or "usuario"
        await update.message.reply_text(
            "Ola " + nome + "!\n\nBem-vindo ao Salas FF Bot!\nUse /menu para acessar o painel.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def menu(self, update: Update, context: CallbackContext):
        uid = str(update.effective_user.id)
        key = await self._c.key_repo.buscar_por_telegram(uid)
        if key:
            sb = saldo_bar(key.usos_restantes, key.limite_req)
            saldo_txt = sb["texto"]
        else:
            saldo_txt = "Sem key ativa - use /ativar"

        keyboard = [
            [
                InlineKeyboardButton("Criar Sala", callback_data="menu:criar"),
                InlineKeyboardButton("Meu Saldo", callback_data="menu:saldo"),
            ],
            [
                InlineKeyboardButton("Comprar Salas", callback_data="pay:comprar"),
                InlineKeyboardButton("Ativar Key", callback_data="menu:ativar"),
            ],
            [
                InlineKeyboardButton("Historico", callback_data="menu:historico"),
                InlineKeyboardButton("Salas Ativas", callback_data="menu:ativas"),
            ],
            [
                InlineKeyboardButton("Produtos", callback_data="menu:produtos"),
                InlineKeyboardButton("Ajuda", callback_data="menu:ajuda"),
            ],
        ]
        await update.message.reply_text(
            "*Menu Principal*\n\n" + saldo_txt + "\n\n" + ts_now(),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def criar(self, update: Update, context: CallbackContext):
        uid = str(update.effective_user.id)
        bloqueado, restante = self._c.rate_limiter.check(uid)
        if bloqueado:
            await update.message.reply_text("Muitas tentativas. Tente em " + str(restante) + "s.")
            return
        keyboard = [
            [InlineKeyboardButton(m["emoji"] + " " + m["nome"], callback_data="room:modo:" + str(k))]
            for k, m in MODOS.items()
        ]
        await update.message.reply_text("Selecione o modo de jogo:",
                                        reply_markup=InlineKeyboardMarkup(keyboard))

    async def historico(self, update: Update, context: CallbackContext):
        uid = str(update.effective_user.id)
        salas = await self._c.room_repo.historico_usuario(uid, 25)
        if not salas:
            await update.message.reply_text("Voce ainda nao criou nenhuma sala.")
            return
        linhas = []
        for s in salas:
            modo_info = MODOS.get(s.modo, {"nome": "Modo " + str(s.modo), "emoji": "🎮"})
            linhas.append("`" + s.room_id + "` - " + modo_info["emoji"] + " " + modo_info["nome"])
        await update.message.reply_text(
            "Ultimas " + str(len(salas)) + " salas:\n\n" + "\n".join(linhas),
            parse_mode="Markdown",
        )

    async def comprar(self, update: Update, context: CallbackContext):
        linhas = [p["emoji"] + " " + p["label"] + " - " + p["preco"] for p in PLANOS]
        keyboard = [[InlineKeyboardButton("Iniciar Compra", callback_data="pay:comprar")]]
        await update.message.reply_text(
            "Produtos Disponiveis\n\n" + "\n".join(linhas),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def ajuda(self, update: Update, context: CallbackContext):
        texto = (
            "Comandos Disponiveis\n\n"
            "/start - Iniciar bot\n"
            "/menu - Painel principal\n"
            "/criar - Criar sala Free Fire\n"
            "/ativar - Ativar key de acesso\n"
            "/historico - Ver ultimas salas\n"
            "/comprar - Ver planos e comprar\n"
            "/suporte - Link de suporte\n"
            "/cancelar - Cancelar acao atual"
        )
        await update.message.reply_text(texto)

    async def suporte(self, update: Update, context: CallbackContext):
        keyboard = [[InlineKeyboardButton("Entrar no Suporte", url=SUPORTE_LINK)]]
        await update.message.reply_text("Precisa de ajuda?",
                                        reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_menu_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        action = query.data.split(":")[1]

        if action == "criar":
            keyboard = [
                [InlineKeyboardButton(m["emoji"] + " " + m["nome"],
                                      callback_data="room:modo:" + str(k))]
                for k, m in MODOS.items()
            ]
            await query.edit_message_text("Selecione o modo:",
                                          reply_markup=InlineKeyboardMarkup(keyboard))
        elif action == "saldo":
            uid = str(update.effective_user.id)
            key = await self._c.key_repo.buscar_por_telegram(uid)
            if key:
                sb = saldo_bar(key.usos_restantes, key.limite_req)
                txt = "*Seu Saldo*\n\n" + sb["texto"]
            else:
                txt = "Sem key ativa. Use /ativar"
            await query.edit_message_text(txt, parse_mode="Markdown")
        elif action == "ativas":
            uid = str(update.effective_user.id)
            salas = self._c.room_service.get_salas_ativas(uid)
            if not salas:
                await query.edit_message_text("Nenhuma sala ativa no momento.")
                return
            linhas = ["`" + s.room_id + "` - Modo " + str(s.modo) for s in salas]
            await query.edit_message_text("*Salas Ativas:*\n\n" + "\n".join(linhas),
                                          parse_mode="Markdown")
        elif action == "produtos":
            linhas = [p["emoji"] + " " + p["label"] + " - " + p["preco"] for p in PLANOS]
            await query.edit_message_text("Produtos:\n\n" + "\n".join(linhas))
